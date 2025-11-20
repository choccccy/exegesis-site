from pathlib import Path

from PIL import Image, ImageColor

from tiny5mk2 import bitmap as ORIGINAL_FONT


# ━━━━━━ Rendering configuration ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WIDTH = 320
HEIGHT = 240

CHAR_SPACING = 1
LINE_SPACING = 1
BG_COLOR = (0, 0, 0)

# DELAY_CHAR_MS = 30
DELAY_PROMPT_MS = 480
SEGMENT_DELAY_MS = 240
DELAY_NEWLINE_MS = 600
DELAY_FINAL_MS = 7200

PADDING_X = 6
PADDING_Y = 6

START_FROM_BOTTOM = False  # False = start at top, True = start at bottom and "push up"
TRANSPARENT_BG = False     # True = fully transparent background in GIF

PROMPT_FG = (160, 160, 160)
TEXT_FG = (160, 160, 160)

PIXEL_COLORS = {  # Map emoji cells to RGB colors
    '⬛': None,
    '⬜': TEXT_FG,
    # Colored squares for emoji glyphs
    '🟥': (255, 0, 0),
    '🟩': (0, 255, 0),
    '🟨': (255, 255, 0),
    '🟦': (0, 0, 255),
    '🟧': (255, 165, 0),
    '🟪': (128, 0, 128),
    '🟫': (139, 69, 19),
}

# ━━━━━━ Unicode / variation selector handling ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VARIATION_SELECTORS = {'\ufe0f', '\ufe0e'}  # Variation selectors to ignore (emoji/text style markers)


def strip_variation_selectors(s):
    return ''.join(ch for ch in s if ch not in VARIATION_SELECTORS)


def build_normalized_font(font):
    """
    Normalize font keys by stripping variation selectors, so both '⚠' and '⚠️'
    resolve to the same glyph key. Emits a warning if any keys had selectors
    or if there are collisions after normalization.
    """
    normalized = {}
    had_vs_keys = set()
    collisions = []

    for key, glyph in font.items():
        norm_key = strip_variation_selectors(key)

        if norm_key != key:
            had_vs_keys.add(key)

        if norm_key in normalized and normalized[norm_key] is not glyph:
            collisions.append((norm_key, key))
        else:
            normalized[norm_key] = glyph

    if had_vs_keys:
        print(
            'Warning: font keys contained variation selectors and were normalized: '
            + ' '.join(had_vs_keys)
        )

    if collisions:
        print('Warning: collisions after normalizing variation selectors for keys:')
        for norm_key, key in collisions:
            print(f'  normalized key {repr(norm_key)} had multiple glyphs (including {repr(key)})')

    return normalized


FONT = build_normalized_font(ORIGINAL_FONT)

def parse_color(value):
    """
    Accepts either an (R, G, B) tuple or a hex string like '#ffcc00'.
    Returns an (R, G, B) tuple, or None if value is falsy.
    """
    if not value:
        return None

    if isinstance(value, tuple) and len(value) == 3:
        return value

    if isinstance(value, str):
        return ImageColor.getrgb(value)

    raise TypeError(f'Unsupported color format: {value!r}')

# ━━━━━━ Font configuration ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FONT_HEIGHT = len(next(iter(FONT.values())))

ERROR_GLYPH = [  # Loud error glyph: used when a character is missing from the bitmap
    '⬛',
    '⬜',
    '🟥',
    '🟩',
    '🟦',
    '🟫',
    '🟧',
    '🟪',
    '🟨',
]


# ━━━━━━ Low-level drawing helpers ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def make_base_image():
    if TRANSPARENT_BG:
        return Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    return Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)


def scroll_up(img, line_height):
    """
    Scroll the entire terminal image up by one line_height,
    filling the new bottom area with background.
    """
    width, height = img.size
    cropped = img.crop((0, line_height, width, height))
    new_img = make_base_image()
    new_img.paste(cropped, (0, 0))
    return new_img


def draw_glyph(img, glyph_rows, x, y, fg_override=None):
    """
    Draw a single glyph (list of emoji-rows) at (x, y).
    Each row is a string of emoji, one per logical pixel.
    If fg_override is provided, plain white cells (⬜) use that color.
    """
    width, height = img.size
    pixels = img.load()

    for row_index, row in enumerate(glyph_rows):
        py = y + row_index
        if py < 0 or py >= height:
            continue

        for col_index, cell in enumerate(row):  # Iterating the string yields individual emoji codepoints
            px = x + col_index
            if px < 0 or px >= width:
                continue

            if cell == '⬜' and fg_override is not None:
                color = fg_override
            else:
                color = PIXEL_COLORS.get(cell)

            if color is None:
                continue  # Background pixel; leave whatever is already there

            pixels[px, py] = color


# ━━━━━━ Glyph lookup with error handling ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def get_glyph(ch, missing):
    """
    Lookup glyph for ch in FONT, with fallbacks:
    - Try exact character
    - Try uppercase version (for ASCII letters)
    - If still missing, use ERROR_GLYPH and record ch in missing set
    """
    glyph = FONT.get(ch)

    if glyph is None:
        upper = ch.upper()
        if upper != ch:
            glyph = FONT.get(upper)

    if glyph is None:
        glyph = ERROR_GLYPH
        missing.add(ch)

    return glyph


# ━━━━━━ Event normalization ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def normalize_events(raw_events):
    """
    Accepts events in either shorthand:
        {'id': '...', 'prompt': '...', 'text': '...'}
    or full:
        {'id': '...', 'lines': [{'prompt': '...', 'text': '...'}, ...]}
    and normalizes everything to the full form.
    """
    normalized = []

    for e in raw_events:
        if 'lines' in e:
            normalized.append(e)
            continue

        if 'prompt' in e or 'text' in e:
            line = {
                'prompt': e.get('prompt', ''),
                'text': e.get('text', ''),
            }
            e = {
                'id': e.get('id'),
                'lines': [line],
            }

        normalized.append(e)

    return normalized


# ━━━━━━ Core rendering over events ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def apply_line(img, line, cursor_x, cursor_y, text_left, text_right, baseline_limit,
               frames, durations, record_frames, missing, prompt_only=False):
    """
    Render one prompt+text line:

    - Prompt is drawn instantly in gray, then one frame is captured (DELAY_PROMPT_MS).
    - line['text'] may be either:
        * a string  -> rendered as a single segment
        * a list of strings -> rendered as segments; after each segment, a segment-like
          pause (SEGMENT_DELAY_MS) is added before the next segment.
    - If line['char_delay'] is set and > 0, each segment is typed out one
      character at a time with that delay (ms) between characters.
      If missing or falsy, the segment appears all at once.
    - If line['color'] is set, body text white pixels (⬜) are recolored to that
      RGB/hex, while colored emoji squares (🟥, etc.) keep their own colors.
    - After the entire body (all segments) finishes, a newline-style pause
      (DELAY_NEWLINE_MS) is added before moving to the next prompt.
    - baseline_limit is the maximum allowed cursor_y for the baseline; if the
      cursor would go past it, the image is scrolled up by one line_height.
    """
    line_height = FONT_HEIGHT + LINE_SPACING
    prompt = line.get('prompt', '')
    raw_body = line.get('text', '')
    body_color = parse_color(line.get('color'))
    char_delay = line.get('char_delay')  # ms or None/0

    # Normalize body into segments list
    if isinstance(raw_body, list):
        segments = raw_body
    else:
        segments = [raw_body]

    # Draw full prompt in gray, no per-char frames
    for ch in prompt:
        if ch in VARIATION_SELECTORS:
            continue

        glyph = get_glyph(ch, missing)
        glyph_width = len(glyph[0]) if glyph else 0

        if cursor_x + glyph_width > text_right:
            cursor_x = text_left
            cursor_y += line_height
            if cursor_y > baseline_limit:
                img = scroll_up(img, line_height)
                cursor_y -= line_height

        draw_glyph(img, glyph, cursor_x, cursor_y, fg_override=PROMPT_FG)
        cursor_x += glyph_width + CHAR_SPACING

    # After prompt, capture a single frame if recording, with prompt delay
    if record_frames:
        frames.append(img.copy())
        durations.append(DELAY_PROMPT_MS)

    def draw_body_char(ch, record_frame, frame_delay):
        nonlocal img, cursor_x, cursor_y

        if ch in VARIATION_SELECTORS:
            return

        if ch == '\n':
            cursor_x = text_left
            cursor_y += line_height
            if cursor_y > baseline_limit:
                img = scroll_up(img, line_height)
                cursor_y -= line_height
            if record_frame and record_frames:
                frames.append(img.copy())
                durations.append(DELAY_NEWLINE_MS)
            return

        glyph = get_glyph(ch, missing)
        glyph_width = len(glyph[0]) if glyph else 0

        if cursor_x + glyph_width > text_right:
            cursor_x = text_left
            cursor_y += line_height
            if cursor_y > baseline_limit:
                img = scroll_up(img, line_height)
                cursor_y -= line_height

        fg_for_body = body_color if body_color is not None else None
        draw_glyph(img, glyph, cursor_x, cursor_y, fg_override=fg_for_body)

        cursor_x += glyph_width + CHAR_SPACING

        if record_frame and record_frames:
            frames.append(img.copy())
            durations.append(frame_delay)

    # Render each segment in order
    for idx, seg in enumerate(segments):
        if char_delay:
            # Typewriter mode: one frame per character
            for ch in seg:
                # record_frame = not prompt_only
                draw_body_char(ch, record_frame=(not prompt_only), frame_delay=char_delay)
        else:
            # Instant mode: draw whole segment, then a single frame for that segment
            for ch in seg:
                draw_body_char(ch, record_frame=False, frame_delay=0)

            if record_frames and not prompt_only:
                frames.append(img.copy())
                durations.append(SEGMENT_DELAY_MS)

        # Between segments (except after the last), add a segment-style pause
        if idx != len(segments) - 1 and record_frames and not prompt_only:
            frames.append(img.copy())
            durations.append(SEGMENT_DELAY_MS)

    # After finishing the body text (all segments), pause before the next prompt
    if record_frames and frames and not prompt_only:
        frames.append(img.copy())
        durations.append(DELAY_NEWLINE_MS)

    # Move to next line
    cursor_x = text_left
    cursor_y += line_height
    if cursor_y > baseline_limit:
        img = scroll_up(img, line_height)
        cursor_y -= line_height

    return img, cursor_x, cursor_y


def apply_event(img, event, cursor_x, cursor_y,
                text_left, text_top, text_right, baseline_limit,
                frames, durations, record_frames, missing,
                prompt_only=False):
    lines = event['lines']
    for line in lines:
        img, cursor_x, cursor_y = apply_line(
            img, line, cursor_x, cursor_y,
            text_left, text_right, baseline_limit,
            frames, durations, record_frames, missing,
            prompt_only=prompt_only,
        )
    return img, cursor_x, cursor_y


def render_events_to_frames(events, start_event_id=None):
    """
    Render a normalized list of events to frames.
    If start_event_id is provided, pre-roll all events before that ID
    without recording frames, then record from that event onward.
    """
    events = normalize_events(events)
    img = make_base_image()

    frames = []
    durations = []

    text_left = PADDING_X
    text_top = PADDING_Y
    text_right = WIDTH - PADDING_X
    text_bottom = HEIGHT - PADDING_Y
    baseline_limit = text_bottom - (FONT_HEIGHT - 1)

    missing = set()

    if START_FROM_BOTTOM:
        cursor_x = text_left
        cursor_y = text_bottom - FONT_HEIGHT
    else:
        cursor_x = text_left
        cursor_y = text_top

    # Find start index, if any
    start_index = 0
    if start_event_id is not None:
        for i, e in enumerate(events):
            if e.get('id') == start_event_id:
                start_index = i
                break

    # Pre-roll
    for e in events[:start_index]:
        img, cursor_x, cursor_y = apply_event(
            img, e, cursor_x, cursor_y,
            text_left, text_top, text_right, baseline_limit,
            frames, durations,
            record_frames=True,    # so we can keep the prompt frames
            missing=missing,
            prompt_only=True,      # but only keep prompt frames, no body timing
        )

    # Animated part
    for e in events[start_index:]:
        img, cursor_x, cursor_y = apply_event(
            img, e, cursor_x, cursor_y,
            text_left, text_top, text_right, baseline_limit,
            frames, durations, record_frames=True, missing=missing,
        )

    if missing:
        for ch in sorted(missing):
            code = f'U+{ord(ch):04X}'
            print(f'Missing glyph: {repr(ch)} ({code})')

    # Final frame hold
    if durations:
        durations[-1] = DELAY_FINAL_MS

    return frames, durations


# ━━━━━━ GIF saving (with optional transparency) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def render_frames_to_gif(frames, durations, output_path):
    if not frames:
        raise ValueError('No frames generated; nothing to save.')

    pal_frames = []
    transparency_index = None

    for frame in frames:
        if TRANSPARENT_BG:
            pal = frame.convert('P', palette=Image.ADAPTIVE)
            trans_idx = pal.getpixel((0, 0))
            pal_frames.append(pal)
            transparency_index = trans_idx
        else:
            pal = frame.convert('P', palette=Image.ADAPTIVE)
            pal_frames.append(pal)

    save_kwargs = dict(
        save_all=True,
        append_images=pal_frames[1:],
        optimize=False,
        duration=durations,
        loop=0,
        disposal=2,
    )

    if transparency_index is not None:
        save_kwargs['transparency'] = transparency_index

    pal_frames[0].save(output_path, **save_kwargs)


def render_frames_to_webp(frames, durations, output_path):
    """
    Save an animated WebP from a list of RGBA/RGB frames and per-frame
    durations (in ms). Transparency from RGBA frames is preserved.
    """
    if not frames:
        raise ValueError('No frames generated; nothing to save.')

    # Pillow expects duration in ms; we already have that.
    # save_all=True is required for animated WebP.
    frames[0].save(
        output_path,
        format='WEBP',
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,    # 0 = infinite loop
        lossless=True,
        quality=100,
        method=6,  # 0–6, higher is slower but better compression
    )


# ━━━━━━ Batch drivers ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def process_plain_text_directory():
    base_dir = Path(__file__).resolve().parent
    input_dir = base_dir / 'input'
    output_dir = base_dir / 'output'

    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    txt_files = sorted(input_dir.glob('*.txt'))
    if not txt_files:
        print(f'No .txt files found in {input_dir}; nothing to do.')
        return

    for txt_path in txt_files:
        text = txt_path.read_text(encoding='utf-8')
        if not text:
            print(f'Skipping empty file: {txt_path}')
            continue

        events = [
            {
                'id': txt_path.stem,
                'prompt': '',
                'text': text,
            }
        ]

        frames, durations = render_events_to_frames(events)

        # out_path = output_dir / (txt_path.stem + '.gif')
        # render_frames_to_gif(frames, durations, out_path)

        out_path = output_dir / (txt_path.stem + '.webp')
        render_frames_to_webp(frames, durations, out_path)

        print(f'wrote {out_path.absolute()}')


def process_script_module(module_name, start_event_id=None, out_name=None, render_all_events=False):
    """
    Load a script from input/<module_name>.py that defines events = [...]
    and render it to one or more GIFs.

    - If render_all_events is False (default):
        * If start_event_id is None: render all events in one pass.
        * If start_event_id is set:  pre-roll events before that ID, animate from that
          event onward, and stop at the end of the script.

    - If render_all_events is True:
        * Ignore start_event_id.
        * For each event i:
            - Pre-roll events 0..i-1 without recording frames.
            - Animate only event i, stopping at the end of that event.
            - Write output as <module_name>_<event_id>.gif
    """
    import importlib.util
    import sys

    base_dir = Path(__file__).resolve().parent
    input_dir = base_dir / 'input'
    output_dir = base_dir / 'output'

    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    module_path = input_dir / f'{module_name}.py'
    if not module_path.exists():
        raise FileNotFoundError(f'No script module {module_path} found')

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    events = getattr(module, 'events', None)
    if events is None:
        raise ValueError(f'Module {module_path} has no "events" variable.')

    if not render_all_events:
        # Single GIF, optional checkpoint: reuse your existing pipeline
        frames, durations = render_events_to_frames(events, start_event_id=start_event_id)

        name = out_name or module_name
        if start_event_id is not None:
            name = f'{name}_{start_event_id}'

        # out_path = output_dir / (name + '.gif')
        # render_frames_to_gif(frames, durations, out_path)

        out_path = output_dir / (name + '.webp')
        render_frames_to_webp(frames, durations, out_path)

        print(f'wrote {out_path.absolute()}')
        return

    normalized = normalize_events(events)

    for idx, ev in enumerate(normalized):
        ev_id = ev.get('id') or f'event{idx:03d}'

        img = make_base_image()

        text_left = PADDING_X
        text_top = PADDING_Y
        text_right = WIDTH - PADDING_X
        text_bottom = HEIGHT - PADDING_Y
        baseline_limit = text_bottom - (FONT_HEIGHT - 1)

        if START_FROM_BOTTOM:
            cursor_x = text_left
            cursor_y = baseline_limit
        else:
            cursor_x = text_left
            cursor_y = text_top

        frames = []
        durations = []
        missing = set()

        # Pre-roll previous events without recording frames
        for prev in normalized[:idx]:
            img, cursor_x, cursor_y = apply_event(
                img, prev, cursor_x, cursor_y,
                text_left, text_top, text_right, baseline_limit,
                frames, durations, record_frames=False, missing=missing,
            )

        # Animate only this event
        img, cursor_x, cursor_y = apply_event(
            img, ev, cursor_x, cursor_y,
            text_left, text_top, text_right, baseline_limit,
            frames, durations, record_frames=True, missing=missing,
        )

        if missing:
            for ch in sorted(missing):
                code = f'U+{ord(ch):04X}'
                print(f'Missing glyph: {repr(ch)} ({code})')

        if durations:
            durations[-1] = DELAY_FINAL_MS

        name = out_name or module_name

        # out_path = output_dir / f'{name}_{ev_id}.gif'
        # render_frames_to_gif(frames, durations, out_path)

        out_path = output_dir / f'{name}_{ev_id}.webp'
        render_frames_to_webp(frames, durations, out_path)

        print(f'wrote {out_path.absolute()}')


# ━━━━━━ Entrypoint ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == '__main__':
    # process_plain_text_directory()  # Render plaintext in /input

    # process_script_module('black_tangent')  # Render formatted .py in /input
    # process_script_module('black_tangent', start_event_id='boot-final-obi')  # Render whole thing starting from event
    process_script_module('black_tangent', render_all_events=True)  # Render all events discretely
