from pathlib import Path

from PIL import Image
from tiny5mk2 import bitmap as ORIGINAL_FONT


# ━━━━━━ Rendering configuration ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WIDTH = 320
HEIGHT = 240

CHAR_SPACING = 1
LINE_SPACING = 1
BG_COLOR = (0, 0, 0)

DELAY_CHAR_MS = 30
DELAY_NEWLINE_MS = 240
DELAY_FINAL_MS = 7200

PADDING_X = 4
PADDING_Y = 4

START_FROM_BOTTOM = False  # False = start at top, True = start at bottom and "push up"

PIXEL_COLORS = {  # Map emoji cells to RGB colors
    '⬛': None,
    '⬜': (255, 255, 255),
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

    if had_vs_keys:  # Keep the first definition; just warn.
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
def scroll_up(img, line_height, bg_color=BG_COLOR):
    """
    Scroll the entire terminal image up by one line_height,
    filling the new bottom area with bg_color.
    """
    width, height = img.size
    cropped = img.crop((0, line_height, width, height))
    new_img = Image.new('RGB', (width, height), bg_color)
    new_img.paste(cropped, (0, 0))
    return new_img

def draw_glyph(img, glyph_rows, x, y):
    """
    Draw a single glyph (list of emoji-rows) at (x, y).
    Each row is a string of emoji, one per logical pixel.
    """
    width, height = img.size
    pixels = img.load()

    for row_index, row in enumerate(glyph_rows):
        py = y + row_index
        if py < 0 or py >= height:
            continue

        # Iterating the string yields individual emoji codepoints
        for col_index, cell in enumerate(row):
            px = x + col_index
            if px < 0 or px >= width:
                continue

            color = PIXEL_COLORS.get(cell)
            if color is None:
                # Background pixel; leave whatever is already there
                continue

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

# ━━━━━━ Main rendering logic ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def render_text_to_frames(text):
    """
    Render the given text into a sequence of frames and per-frame durations.
    - Adds one character per frame.
    - On '\\n', performs a terminal-style newline (with scroll when needed)
      and emits a frame with a longer delay.
    """
    img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)

    frames = []
    durations = []

    # Text area bounds (respect padding)
    text_left = PADDING_X
    text_top = PADDING_Y
    text_right = WIDTH - PADDING_X
    text_bottom = HEIGHT - PADDING_Y

    line_height = FONT_HEIGHT + LINE_SPACING
    missing = set()
    seen_variation_input = set()

    # Initial cursor position: top or bottom mode
    if START_FROM_BOTTOM:
        cursor_x = text_left
        cursor_y = text_bottom - FONT_HEIGHT
    else:
        cursor_x = text_left
        cursor_y = text_top

    for ch in text:
        # Skip variation selectors in input, but remember that they occurred
        if ch in VARIATION_SELECTORS:
            seen_variation_input.add(ch)
            continue

        if ch == '\n':  # Move to next line
            cursor_x = text_left
            cursor_y += line_height

            # Scroll if we go past the bottom of the text area
            if cursor_y + FONT_HEIGHT > text_bottom:
                img = scroll_up(img, line_height, BG_COLOR)
                cursor_y -= line_height

            # Capture a frame with the newline state, long delay
            frames.append(img.copy())
            durations.append(DELAY_NEWLINE_MS)
            continue

        glyph = get_glyph(ch, missing)
        glyph_width = len(glyph[0]) if glyph else 0

        # Auto-wrap if the glyph would cross the right text boundary
        if cursor_x + glyph_width > text_right:
            cursor_x = text_left
            cursor_y += line_height

            if cursor_y + FONT_HEIGHT > text_bottom:
                img = scroll_up(img, line_height, BG_COLOR)
                cursor_y -= line_height

        draw_glyph(img, glyph, cursor_x, cursor_y)

        # Snapshot frame after drawing this character
        frames.append(img.copy())
        durations.append(DELAY_CHAR_MS)

        # Advance cursor: glyph width in pixels plus spacing
        cursor_x += glyph_width + CHAR_SPACING

    if missing:
        for ch in sorted(missing):
            code = f'U+{ord(ch):04X}'
            print(f'Missing glyph: {repr(ch)} ({code})')

    if seen_variation_input:
        vs_list = ' '.join(repr(vs) for vs in seen_variation_input)
        print(f'Note: input text contained variation selectors that were ignored: {vs_list}')

    # Hold on the final frame using the dedicated final delay
    if durations:
        durations[-1] = DELAY_FINAL_MS

    return frames, durations

def render_text_to_gif(text, output_path):
    frames, durations = render_text_to_frames(text)

    if not frames:
        raise ValueError('No frames generated; text may be empty.')

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        optimize=False,
        duration=durations,  # ms per frame
        loop=0,
        disposal=2,
    )

# ━━━━━━ Batch driver: input/*.txt -> output/*.gif ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def process_input_directory():
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

        out_path = output_dir / (txt_path.stem + '.gif')
        render_text_to_gif(text, out_path)
        print(f'wrote {out_path.absolute()}')

# ━━━━━━ Example usage ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == '__main__':
    process_input_directory()
