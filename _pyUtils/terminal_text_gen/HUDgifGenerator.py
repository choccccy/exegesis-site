from pathlib import Path

from PIL import Image, ImageColor

from tiny5mk2 import bitmap as ORIGINAL_FONT


# ━━━━━━ Rendering configuration ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WIDTH = 320
HEIGHT = 240

CHAR_SPACING = 1
LINE_SPACING = 1
BG_COLOR = (0, 0, 0)

DELAY_CHAR_MS = 30
DELAY_PROMPT_MS = 480
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
def apply_line(img, line, cursor_x, cursor_y, text_left, text_right, text_bottom,
               frames, durations, record_frames, missing):
    """
    Render one prompt+text line:
    - Prompt is drawn instantly in gray, then one frame is captured (DELAY_PROMPT_MS).
    - Body text is typed out character by character, wrapping as needed.
    - If line['color'] is set, body text white pixels (⬜) are recolored to that RGB/hex,
      while colored emoji squares (🟥, etc.) keep their own colors.
    - After the body finishes, a newline-style pause (DELAY_NEWLINE_MS) is added
      before moving to the next prompt.
    Returns updated (img, cursor_x, cursor_y).
    """
    line_height = FONT_HEIGHT + LINE_SPACING
    prompt = line.get('prompt', '')
    body = line.get('text', '')
    body_color = parse_color(line.get('color'))  # None = default TEXT_FG as in PIXEL_COLORS

    # Draw full prompt in gray, no per-char frames
    for ch in prompt:
        if ch in VARIATION_SELECTORS:
            continue

        glyph = get_glyph(ch, missing)
        glyph_width = len(glyph[0]) if glyph else 0

        if cursor_x + glyph_width > text_right:
            cursor_x = text_left
            cursor_y += line_height
            if cursor_y + FONT_HEIGHT > text_bottom:
                img = scroll_up(img, line_height)
                cursor_y -= line_height

        draw_glyph(img, glyph, cursor_x, cursor_y, fg_override=PROMPT_FG)
        cursor_x += glyph_width + CHAR_SPACING

    # After prompt, capture a single frame if recording, with prompt delay
    if record_frames:
        frames.append(img.copy())
        durations.append(DELAY_PROMPT_MS)

    # Now type out body text character by character
    for ch in body:
        if ch in VARIATION_SELECTORS:
            continue

        if ch == '\n':
            cursor_x = text_left
            cursor_y += line_height
            if cursor_y + FONT_HEIGHT > text_bottom:
                img = scroll_up(img, line_height)
                cursor_y -= line_height

            if record_frames:
                frames.append(img.copy())
                durations.append(DELAY_NEWLINE_MS)
            continue

        glyph = get_glyph(ch, missing)
        glyph_width = len(glyph[0]) if glyph else 0

        if cursor_x + glyph_width > text_right:
            cursor_x = text_left
            cursor_y += line_height
            if cursor_y + FONT_HEIGHT > text_bottom:
                img = scroll_up(img, line_height)
                cursor_y -= line_height

        # For body text, recolor only ⬜ when body_color is set; emoji squares keep their colors
        fg_for_body = body_color if body_color is not None else None
        draw_glyph(img, glyph, cursor_x, cursor_y, fg_override=fg_for_body)

        if record_frames:
            frames.append(img.copy())
            durations.append(DELAY_CHAR_MS)

        cursor_x += glyph_width + CHAR_SPACING

    # After finishing the body text, pause before the next prompt
    if record_frames and frames:
        frames.append(img.copy())
        durations.append(DELAY_NEWLINE_MS)

    # Move to next line
    cursor_x = text_left
    cursor_y += line_height
    if cursor_y + FONT_HEIGHT > text_bottom:
        img = scroll_up(img, line_height)
        cursor_y -= line_height

    return img, cursor_x, cursor_y


def apply_event(img, event, cursor_x, cursor_y, text_left, text_top, text_right, text_bottom,
                frames, durations, record_frames, missing):
    """
    Apply a whole event (possibly multiple lines) to img.
    If record_frames is False, this only updates img and cursor.
    """
    for line in event['lines']:
        img, cursor_x, cursor_y = apply_line(
            img, line, cursor_x, cursor_y,
            text_left, text_right, text_bottom,
            frames, durations, record_frames, missing,
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
            text_left, text_top, text_right, text_bottom,
            frames, durations, record_frames=False, missing=missing,
        )

    # Animated part
    for e in events[start_index:]:
        img, cursor_x, cursor_y = apply_event(
            img, e, cursor_x, cursor_y,
            text_left, text_top, text_right, text_bottom,
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
        out_path = output_dir / (txt_path.stem + '.gif')
        render_frames_to_gif(frames, durations, out_path)
        print(f'wrote {out_path.absolute()}')


def process_script_module(module_name, start_event_id=None, out_name=None):
    """
    Load a script from input/<module_name>.py that defines events = [...]
    and render it to a GIF. Optional start_event_id enables checkpointing.
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

    frames, durations = render_events_to_frames(events, start_event_id=start_event_id)

    name = out_name or module_name
    if start_event_id is not None:
        name = f'{name}_{start_event_id}'

    out_path = output_dir / (name + '.gif')
    render_frames_to_gif(frames, durations, out_path)
    print(f'wrote {out_path.absolute()}')


# ━━━━━━ Entrypoint ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == '__main__':
    # process_plain_text_directory()
    # For script mode (scripts live in ./input):
    process_script_module('boot_script', start_event_id=None)
