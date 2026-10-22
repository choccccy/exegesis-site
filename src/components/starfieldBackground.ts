import { generateStar } from '../lib/starGenerator.js';

// Generated textures are cached per tab session so the sky stays consistent across pages.
// Bump the version when the generator's look changes.
const CACHE_KEY = 'starfield-layers-v1';
const LAYER_IDS = ['starfield-bg', 'starfield-md', 'starfield-fg'];

class StarfieldBackground extends HTMLElement {
  wrapper: HTMLElement | null = null;
  texSize: number = 1024;
  starCount: number = 800;
  ticking: boolean = false;
  scrollY: number = 0;
  objectUrls: string[] = [];

  constructor() {
    super();
    this.wrapper = this.querySelector("#starfield-wrapper");
    this.texSize = 1024; // 1024x1024 seamless tiles for optimal VRAM usage
    this.handleScroll = this.handleScroll.bind(this);
    this.updateCSSVars = this.updateCSSVars.bind(this);
    this.ticking = false;
    this.scrollY = 0;
  }

  connectedCallback() {
    if (!this.wrapper) return;
    this.starCount = parseInt(this.dataset.starCount || "800", 10);
    
    this.setupListeners();

    const cached = this.readCache();
    if (cached) {
      // Show the cached sky immediately, with no fade
      cached.forEach((url, i) => this.setLayerImage(LAYER_IDS[i], url));
      this.wrapper.classList.add('is-ready', 'no-fade');
      return;
    }

    // Defer to the next frame so first paint isn't blocked by generation
    requestAnimationFrame(() => this.init());
  }

  readCache(): string[] | null {
    try {
      const parsed = JSON.parse(sessionStorage.getItem(CACHE_KEY) || 'null');
      if (Array.isArray(parsed) && parsed.length === LAYER_IDS.length && parsed.every(u => typeof u === 'string' && u.startsWith('data:image/png'))) {
        return parsed;
      }
    } catch {
      // Storage blocked or corrupt entry; fall through to generation
    }
    return null;
  }

  async writeCache(blobs: Blob[]) {
    try {
      const urls = await Promise.all(blobs.map(blob => new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result as string);
        reader.onerror = () => reject(reader.error);
        reader.readAsDataURL(blob);
      })));
      sessionStorage.setItem(CACHE_KEY, JSON.stringify(urls));
    } catch {
      // Quota exceeded or storage blocked; caching is best-effort
    }
  }

  setLayerImage(id: string, url: string) {
    const el = this.querySelector(`#${id}`);
    if (el instanceof HTMLElement) {
      el.style.backgroundImage = `url(${url})`;
    }
  }

  disconnectedCallback() {
    window.removeEventListener('scroll', this.handleScroll);
    this.objectUrls.forEach(url => URL.revokeObjectURL(url));
    this.objectUrls = [];
  }

  drawStar(ctx: CanvasRenderingContext2D, star: any, renderX: number, renderY: number) {
    const px = Math.round(renderX);
    const py = Math.round(renderY);

    ctx.globalAlpha = star.baseOpacity;
    ctx.fillStyle = star.color;
    ctx.beginPath();
    ctx.arc(px, py, 1, 0, Math.PI * 2);
    ctx.fill();

    if (!star.spikeAlpha || star.spikeAlpha <= 0) return;

    const len = star.spikeLength;
    const baseRGBA = `rgba(${star.r},${star.g},${star.b},`;
    const alphas = [0, star.spikeAlpha * 0.2, star.spikeAlpha * 0.5, star.spikeAlpha, star.spikeAlpha * 0.5, star.spikeAlpha * 0.2, 0];
    const stops = [0, 0.35, 0.45, 0.5, 0.55, 0.65, 1];
    const arms = [
      { x1: px - len, y1: py - len, x2: px + len, y2: py + len },
      { x1: px + len, y1: py - len, x2: px - len, y2: py + len },
    ];

    ctx.lineWidth = 1;
    arms.forEach((arm) => {
      const grad = ctx.createLinearGradient(arm.x1, arm.y1, arm.x2, arm.y2);
      stops.forEach((stop, i) => {
        grad.addColorStop(stop, `${baseRGBA}${alphas[i]})`);
      });
      ctx.strokeStyle = grad;
      ctx.beginPath();
      ctx.moveTo(arm.x1, arm.y1);
      ctx.lineTo(arm.x2, arm.y2);
      ctx.stroke();
    });
  }

  drawSeamless(ctx: CanvasRenderingContext2D, star: any) {
    const margin = (star.spikeAlpha && star.spikeAlpha > 0) ? star.spikeLength : 2;
    const texSize = this.texSize;
    
    // Draw primary instance
    this.drawStar(ctx, star, star.x, star.y);

    // Check edges and draw mirrored copies to ensure perfect seamless wrapping
    const nearLeft = star.x < margin;
    const nearRight = star.x > texSize - margin;
    const nearTop = star.y < margin;
    const nearBottom = star.y > texSize - margin;

    if (nearLeft) this.drawStar(ctx, star, star.x + texSize, star.y);
    if (nearRight) this.drawStar(ctx, star, star.x - texSize, star.y);
    if (nearTop) this.drawStar(ctx, star, star.x, star.y + texSize);
    if (nearBottom) this.drawStar(ctx, star, star.x, star.y - texSize);

    // Corners
    if (nearLeft && nearTop) this.drawStar(ctx, star, star.x + texSize, star.y + texSize);
    if (nearRight && nearTop) this.drawStar(ctx, star, star.x - texSize, star.y + texSize);
    if (nearLeft && nearBottom) this.drawStar(ctx, star, star.x + texSize, star.y - texSize);
    if (nearRight && nearBottom) this.drawStar(ctx, star, star.x - texSize, star.y - texSize);
  }

  async init() {
    // Base density scaling for performance
    const isLowEnd = navigator.hardwareConcurrency <= 4 || window.innerWidth < 768;
    let count = isLowEnd ? Math.floor(this.starCount * 0.5) : this.starCount;
    
    // Multiply to guarantee a rich sky since 90% of stars are faint background stars
    count = Math.floor(count * 1.5);
    
    // Partition stars into 3 depth layers for parallax
    const layers: { id: string, stars: any[] }[] = LAYER_IDS.map(id => ({ id, stars: [] }));

    for (let i = 0; i < count; i++) {
      const star = generateStar(this.texSize, this.texSize);
      const depth = Math.random(); // Distribute across planes
      
      if (depth < 0.33) layers[0].stars.push(star);
      else if (depth < 0.66) layers[1].stars.push(star);
      else layers[2].stars.push(star);
    }

    // Render each layer to its own canvas, then encode asynchronously to a blob URL
    const blobs = await Promise.all(layers.map(layer => this.renderLayer(layer.id, layer.stars)));

    // Fade all layers in together once every texture is decoded
    requestAnimationFrame(() => this.wrapper?.classList.add('is-ready'));

    if (blobs.every((b): b is Blob => b !== null)) {
      this.writeCache(blobs);
    }
  }

  async renderLayer(id: string, stars: any[]): Promise<Blob | null> {
    const canvas = document.createElement("canvas");
    canvas.width = this.texSize;
    canvas.height = this.texSize;

    const ctx = canvas.getContext("2d");
    if (!ctx) return null;

    ctx.fillStyle = "#000000";
    ctx.fillRect(0, 0, this.texSize, this.texSize);
    stars.forEach(star => this.drawSeamless(ctx, star));

    const blob = await new Promise<Blob | null>(resolve => canvas.toBlob(resolve, "image/png"));

    // Cleanup large objects
    canvas.width = 0;
    canvas.height = 0;
    if (!blob) return null;

    const url = URL.createObjectURL(blob);
    this.objectUrls.push(url);

    // Decode up front so the fade-in doesn't stutter on first paint
    const img = new Image();
    img.src = url;
    try {
      await img.decode();
    } catch {
      // Decode failure is non-fatal; the background will still load normally
    }

    this.setLayerImage(id, url);
    return blob;
  }

  setupListeners() {
    this.scrollY = window.scrollY;
    window.addEventListener('scroll', this.handleScroll, { passive: true });
    this.requestUpdate();
  }

  handleScroll() {
    this.scrollY = window.scrollY;
    this.requestUpdate();
  }

  updateCSSVars() {
    // Pass the scroll offset into the hardware-accelerated compositor via CSS variables
    if (this.wrapper) {
      this.wrapper.style.setProperty('--scroll-y', `${this.scrollY}px`);
    }
    this.ticking = false;
  }

  requestUpdate() {
    if (!this.ticking) {
      requestAnimationFrame(this.updateCSSVars);
      this.ticking = true;
    }
  }
}

// Register Web Component to naturally handle Astro ClientRouter lifecycle and avoid memory leaks
customElements.define('starfield-background', StarfieldBackground);
