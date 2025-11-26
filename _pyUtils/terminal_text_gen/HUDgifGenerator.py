from pathlib import Path
from PIL import Image, ImageColor
from tiny5mk2 import bitmap as ORIGINAL_FONT

# ━━━━━━ Rendering configuration ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WIDTH = 320
HEIGHT = 240

CHAR_SPACING = 1
LINE_SPACING = 1
BG_COLOR = (0, 0, 0)

START_FRAME_DELAY_MS = 960
DELAY_PROMPT_MS = 480
SEGMENT_DELAY_MS = 240
DELAY_NEWLINE_MS = 960
DELAY_FINAL_MS = 7200

# CURSOR_CHAR = '_'
CURSOR_CHAR = '█'
CURSOR_BLINK_DELAY_MS = 360

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


# ━━━━━━ Cursor blinking helper ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def blink_cursor(img, cursor_x, cursor_y, color, total_ms, frames, durations, missing, start_on=True):
    """
    Append blinking cursor frames for total_ms at (cursor_x, cursor_y).
    start_on: if True, starts with ON frame. If False, starts with OFF frame.
    """
    if total_ms <= 0:
        return

    if CURSOR_BLINK_DELAY_MS <= 0:
        frame_on = img.copy()
        cursor_glyph = get_glyph(CURSOR_CHAR, missing)
        draw_glyph(frame_on, cursor_glyph, cursor_x, cursor_y, fg_override=color)
        frames.append(frame_on)
        durations.append(total_ms)
        return

    cursor_glyph = get_glyph(CURSOR_CHAR, missing)
    remaining_ms = total_ms
    is_on = start_on

    while remaining_ms > 0:
        current_dur = min(remaining_ms, CURSOR_BLINK_DELAY_MS)
        
        if is_on:
            frame = img.copy()
            draw_glyph(frame, cursor_glyph, cursor_x, cursor_y, fg_override=color)
            frames.append(frame)
        else:
            frames.append(img.copy())
            
        durations.append(current_dur)
        remaining_ms -= current_dur
        is_on = not is_on


# ━━━━━━ Core rendering over events ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def apply_line(img, line, cursor_x, cursor_y, text_left, text_right, baseline_limit,
               frames, durations, record_frames, missing, prompt_only=False, is_first_line=False):
    """
    Render one prompt+text line, with optional blinking cursor logic.

    - If is_first_line is True, holds the initial state for START_FRAME_DELAY_MS
      (with cursor visible) before doing anything else.
    - Cursor is drawn at current position for every captured frame (delays, typing).
    - Cursor takes the same color as the line text if specified.
    """
    line_height = FONT_HEIGHT + LINE_SPACING
    prompt = line.get('prompt', '')
    raw_body = line.get('text', '')
    body_color = parse_color(line.get('color'))
    char_delay = line.get('char_delay')

    # Normalize body into segments list
    if isinstance(raw_body, list):
        segments = raw_body
    else:
        segments = [raw_body]

    def check_and_scroll(curr_img, cy):
        if cy > baseline_limit:
            curr_img = scroll_up(curr_img, line_height)
            cy -= line_height
        return curr_img, cy

    def draw_one_char(ch, curr_img, cx, cy, color_override):
        if ch in VARIATION_SELECTORS:
            return curr_img, cx, cy

        if ch == '\n':
            cx = text_left
            cy += line_height
            curr_img, cy = check_and_scroll(curr_img, cy)
            if not prompt_only and record_frames:
                blink_cursor(curr_img, cx, cy, PROMPT_FG, DELAY_NEWLINE_MS, frames, durations, missing)
            return curr_img, cx, cy

        glyph = get_glyph(ch, missing)
        glyph_width = len(glyph[0]) if glyph else 0

        if cx + glyph_width > text_right:
            cx = text_left
            cy += line_height
            curr_img, cy = check_and_scroll(curr_img, cy)

        draw_glyph(curr_img, glyph, cx, cy, fg_override=color_override)
        cx += glyph_width + CHAR_SPACING
        return curr_img, cx, cy

    def snapshot_with_cursor(duration_ms, blink=True, color_override=None):
        if not (record_frames and duration_ms > 0):
            return

        color = color_override
        if color is None:
            color = body_color or TEXT_FG

        if blink and CURSOR_BLINK_DELAY_MS > 0:
            blink_cursor(img, cursor_x, cursor_y, color, duration_ms, frames, durations, missing)
        else:
            frame = img.copy()
            cursor_glyph = get_glyph(CURSOR_CHAR, missing)
            draw_glyph(frame, cursor_glyph, cursor_x, cursor_y, fg_override=color)
            frames.append(frame)
            durations.append(duration_ms)

    # 1. Start Delay (only for the very first line of an event)
    if is_first_line:
        snapshot_with_cursor(START_FRAME_DELAY_MS, blink=True, color_override=PROMPT_FG)

    # 2. Draw Prompt
    for ch in prompt:
        img, cursor_x, cursor_y = draw_one_char(ch, img, cursor_x, cursor_y, PROMPT_FG)

    # 3. Prompt Delay (cursor visible at start of body position)
    snapshot_with_cursor(DELAY_PROMPT_MS, blink=True)

    # 4. Render Body Segments
    for idx, seg in enumerate(segments):
        seg_cursor_color = body_color or TEXT_FG

        if char_delay:
            # Typewriter mode: one frame per character (cursor ON, no blink)
            for ch in seg:
                img, cursor_x, cursor_y = draw_one_char(
                    ch, img, cursor_x, cursor_y, seg_cursor_color
                )
                if not prompt_only:
                    snapshot_with_cursor(char_delay, blink=False, color_override=seg_cursor_color)

            # After finishing this segment, give it a settle pause (blinking)
            if not prompt_only:
                snapshot_with_cursor(SEGMENT_DELAY_MS, blink=True, color_override=seg_cursor_color)
        else:
            # Instant mode: draw whole segment, then a single blinking pause
            for ch in seg:
                img, cursor_x, cursor_y = draw_one_char(
                    ch, img, cursor_x, cursor_y, seg_cursor_color
                )
            if not prompt_only:
                snapshot_with_cursor(SEGMENT_DELAY_MS, blink=True, color_override=seg_cursor_color)

        # Pause between segments
        is_last_segment = (idx == len(segments) - 1)
        if not is_last_segment and not prompt_only:
            snapshot_with_cursor(SEGMENT_DELAY_MS, blink=True, color_override=seg_cursor_color)

    # 5. End of line pause (cursor on next empty line)
    cursor_x = text_left
    cursor_y += line_height
    img, cursor_y = check_and_scroll(img, cursor_y)

    if not prompt_only:
        snapshot_with_cursor(DELAY_NEWLINE_MS, blink=True, color_override=PROMPT_FG)

    return img, cursor_x, cursor_y


def apply_event(img, event, cursor_x, cursor_y,
                text_left, text_top, text_right, baseline_limit,
                frames, durations, record_frames, missing,
                prompt_only=False):
    lines = event['lines']
    for i, line in enumerate(lines):
        img, cursor_x, cursor_y = apply_line(
            img, line, cursor_x, cursor_y,
            text_left, text_right, baseline_limit,
            frames, durations, record_frames, missing,
            prompt_only=prompt_only,
            is_first_line=(i == 0),
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
            record_frames=True,
            missing=missing,
            prompt_only=True,
        )

    # Animated part
    for e in events[start_index:]:
        img, cursor_x, cursor_y = apply_event(
            img, e, cursor_x, cursor_y,
            text_left, text_top, text_right, baseline_limit,
            frames, durations,
            record_frames=True,
            missing=missing,
            prompt_only=False,
        )

    if missing:
        for ch in sorted(missing):
            code = f'U+{ord(ch):04X}'
            print(f'Missing glyph: {repr(ch)} ({code})')

    # Final frame hold
    if frames:
        # Determine continuity from the previous newline blink
        cycle_ms = CURSOR_BLINK_DELAY_MS * 2
        newline_rem = DELAY_NEWLINE_MS % cycle_ms
        start_final_on = True
        if 0 < newline_rem <= CURSOR_BLINK_DELAY_MS:
            start_final_on = False

        blink_cursor(img, cursor_x, cursor_y, PROMPT_FG, DELAY_FINAL_MS, frames, durations, missing, start_on=start_final_on)

    return frames, durations


# ━━━━━━ GIF / WebP saving ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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

    frames[0].save(
        output_path,
        format='WEBP',
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
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
        out_path = output_dir / (txt_path.stem + '.gif')
        render_frames_to_gif(frames, durations, out_path)
        # out_path_webp = output_dir / (txt_path.stem + '.webp')
        # render_frames_to_webp(frames, durations, out_path_webp)
        print(f'wrote {out_path.absolute()}')


def process_script_module(module_name, start_event_id=None, out_name=None, render_all_events=False):
    """
    Load a script from input/<module_name>.py that defines events = [...]
    and render it to one or more GIFs.
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
        frames, durations = render_events_to_frames(events, start_event_id=start_event_id)

        name = out_name or module_name
        if start_event_id is not None:
            name = f'{name}_{start_event_id}'

        out_path = output_dir / (name + '.gif')
        render_frames_to_gif(frames, durations, out_path)
        # out_path_webp = output_dir / (name + '.webp')
        # render_frames_to_webp(frames, durations, out_path_webp)
        print(f'wrote {out_path.absolute()}')
        return

    # render_all_events=True: one GIF per event
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
                frames, durations,
                record_frames=False,
                missing=missing,
                prompt_only=False,
            )

        # Animate only this event
        img, cursor_x, cursor_y = apply_event(
            img, ev, cursor_x, cursor_y,
            text_left, text_top, text_right, baseline_limit,
            frames, durations,
            record_frames=True,
            missing=missing,
            prompt_only=False,
        )

        if missing:
            for ch in sorted(missing):
                code = f'U+{ord(ch):04X}'
                print(f'Missing glyph: {repr(ch)} ({code})')

        # Final blinking cursor hold for this event
        if frames:
            cycle_ms = CURSOR_BLINK_DELAY_MS * 2
            newline_rem = DELAY_NEWLINE_MS % cycle_ms
            start_final_on = True
            if 0 < newline_rem <= CURSOR_BLINK_DELAY_MS:
                start_final_on = False
            
            blink_cursor(img, cursor_x, cursor_y, PROMPT_FG, DELAY_FINAL_MS, frames, durations, missing, start_on=start_final_on)

        name = out_name or module_name
        out_path = output_dir / f'{name}_{ev_id}.gif'
        render_frames_to_gif(frames, durations, out_path)
        # out_path_webp = output_dir / f'{name}_{ev_id}.webp'
        # render_frames_to_webp(frames, durations, out_path_webp)
        print(f'wrote {out_path.absolute()}')


# ━━━━━━ Entrypoint ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == '__main__':
    # process_plain_text_directory()  # Render plaintext in /input

    # process_script_module('black_tangent')  # Render formatted .py in /input
    # process_script_module('black_tangent', start_event_id='boot-final-obi')  # Render whole thing starting from event
    process_script_module('black_tangent', render_all_events=True)  # Render all events discretely

    # process_script_module('dead_channel', render_all_events=True)  # Render all events discretely
