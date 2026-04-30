import { generateStar } from '../lib/starGenerator.js';

class StarfieldBackground extends HTMLElement {
  wrapper: HTMLElement | null = null;
  texSize: number = 1024;
  starCount: number = 800;
  ticking: boolean = false;
  scrollY: number = 0;

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
    
    // Delay initialization slightly to ensure UI is interactive first
    setTimeout(() => this.init(), 50);
  }

  disconnectedCallback() {
    window.removeEventListener('scroll', this.handleScroll);
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

  init() {
    // Base density scaling for performance
    const isLowEnd = navigator.hardwareConcurrency <= 4 || window.innerWidth < 768;
    let count = isLowEnd ? Math.floor(this.starCount * 0.5) : this.starCount;
    
    // Multiply to guarantee a rich sky since 90% of stars are faint background stars
    count = Math.floor(count * 1.5);
    
    // Partition stars into 3 depth layers for parallax
    const layers: { id: string, stars: any[] }[] = [
      { id: 'starfield-bg', stars: [] },
      { id: 'starfield-md', stars: [] },
      { id: 'starfield-fg', stars: [] }
    ];

    for (let i = 0; i < count; i++) {
      const star = generateStar(this.texSize, this.texSize);
      const depth = Math.random(); // Distribute across planes
      
      if (depth < 0.33) layers[0].stars.push(star);
      else if (depth < 0.66) layers[1].stars.push(star);
      else layers[2].stars.push(star);
    }

    // Render each layer to a data URL
    const canvas = document.createElement("canvas");
    canvas.width = this.texSize;
    canvas.height = this.texSize;
    
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    for (const layer of layers) {
      // Reset globalAlpha to 1.0 to guarantee a completely opaque black fill, 
      // preventing previous layer's stars from ghosting.
      ctx.globalAlpha = 1.0;
      ctx.fillStyle = "#000000";
      ctx.fillRect(0, 0, this.texSize, this.texSize);
      
      layer.stars.forEach(star => this.drawSeamless(ctx, star));
      
      const dataUrl = canvas.toDataURL("image/png");
      const el = this.querySelector(`#${layer.id}`);
      if (el instanceof HTMLElement) {
        el.style.backgroundImage = `url(${dataUrl})`;
      }
    }

    // Cleanup large objects
    canvas.width = 0;
    canvas.height = 0;

    this.setupListeners();
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
