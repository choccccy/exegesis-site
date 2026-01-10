CONFIG = {
    'WIDTH': 320,
    'HEIGHT': 240,
    'BG_COLOR': (0, 0, 0),
    'START_FRAME_DELAY_MS': 960,
    'DELAY_PROMPT_MS': 600,
    'SEGMENT_DELAY_MS': 600,
    'DELAY_NEWLINE_MS': 1440,
    'DELAY_FINAL_MS': 7200,
    'CURSOR_CHAR': '|',
    'CURSOR_BLINK_DELAY_MS': 360,
    'PADDING_X': 6,
    'PADDING_Y': 6,
    'START_FROM_BOTTOM': False,  # False = start at top, True = start at bottom and "push up"
    'TRANSPARENT_BG': False,     # True = fully transparent background in GIF
    'PROMPT_FG': (160, 160, 160),
    'TEXT_FG': (160, 160, 160),
    'CHAR_SPACING': 1,
    'LINE_SPACING': 1,
}
START_EVENT_ID = None      # Change to e.g. 3 to start from event ID 3
RENDER_ALL_EVENTS = False  # Set True to render one file per event
OUTPUT_FORMAT = 'gif'      # or webp or gif
OUTPUT_NAME = 'dead_channel'

events = [
  {  # covering loop
    'id': '1',
    'lines': [
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["NOTICE: ", "THIS MESSAGE WILL NOW REPEAT"],
        'color': (255, 128, 128),
        'char_delay': 20,
      },
    ],
  },
  {  # covering loop
    'id': '2',
    'lines': [
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["S.O.S.: ", "TRANSMITTING", " .", " .", " ."],
        'color': (255, 128, 128),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["Core primion flux: ", "❌", " 6553.5% ", "[SENSOR OVERLOAD - INPUT DOMAIN EXCEEDED]"],
        'color': (255, 128, 128),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["Stern primion flux: ", "❌", " 6553.5% ", "[SENSOR OVERLOAD - INPUT DOMAIN EXCEEDED]"],
        'color': (255, 128, 128),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["Bow primion flux: ", "❌", " 6553.5% ", "[SENSOR OVERLOAD - INPUT DOMAIN EXCEEDED]"],
        'color': (255, 128, 128),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["Antikythera neural lattice: ", "❌", " NO RESPONSE"],
        'color': (255, 128, 128),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["Antikythera backups: ", "⚠️", " PARTIAL SNAPSHOTS AVAILABLE ", "| INTEGRITY DEGRADED"],
        'color': (255, 255, 128),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["Crew neural activity: ", "❌", " NO COHERENT PATTERN DETECTED"],
        'color': (255, 128, 128),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["Crew status: ", "❌", " NO RESPONSE ", "| NO VOLUNTARY ACTIVITY DETECTED"],
        'color': (255, 128, 128),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["Antikythera Neural lattice cooling: ", "⚠️", " HEAT LOAD EXCEEDS DESIGN LIMITS ", "| +3.2 K/HOUR"],
        'color': (255, 255, 128),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["Fusion core: ", "✅", " THROTTLED TO STANDBY LOAD"],
        'color': (255, 255, 255),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["Attitude control: ", "✅", " RCS ONLY ", "| HOLDING STATION"],
        'color': (255, 255, 255),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["Collision avoidance: ", "✅", " ENABLED"],
        'color': (255, 255, 255),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["Autopilot systems: ", "✅", " STATION-KEEPING"],
        'color': (255, 255, 255),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["NOTICE: ", "THIS MESSAGE WILL NOW REPEAT"],
        'color': (255, 128, 128),
        'char_delay': 20,
      },
    ],
  },
  {  # actual render
    'id': '3',
    'lines': [
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["S.O.S.: ", "TRANSMITTING", " .", " .", " ."],
        'color': (255, 128, 128),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["Core primion flux: ", "❌", " 6553.5% ", "[SENSOR OVERLOAD - INPUT DOMAIN EXCEEDED]"],
        'color': (255, 128, 128),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["Stern primion flux: ", "❌", " 6553.5% ", "[SENSOR OVERLOAD - INPUT DOMAIN EXCEEDED]"],
        'color': (255, 128, 128),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["Bow primion flux: ", "❌", " 6553.5% ", "[SENSOR OVERLOAD - INPUT DOMAIN EXCEEDED]"],
        'color': (255, 128, 128),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["Antikythera neural lattice: ", "❌", " NO RESPONSE"],
        'color': (255, 128, 128),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["Antikythera backups: ", "⚠️", " PARTIAL SNAPSHOTS AVAILABLE ", "| INTEGRITY DEGRADED"],
        'color': (255, 255, 128),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["Crew neural activity: ", "❌", " NO COHERENT PATTERN DETECTED"],
        'color': (255, 128, 128),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["Crew status: ", "❌", " NO RESPONSE ", "| NO VOLUNTARY ACTIVITY DETECTED"],
        'color': (255, 128, 128),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["Antikythera Neural lattice cooling: ", "⚠️", " HEAT LOAD EXCEEDS DESIGN LIMITS ", "| +3.2 K/HOUR"],
        'color': (255, 255, 128),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["Fusion core: ", "✅", " THROTTLED TO STANDBY LOAD"],
        'color': (255, 255, 255),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["Attitude control: ", "✅", " RCS ONLY ", "| HOLDING STATION"],
        'color': (255, 255, 255),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["Collision avoidance: ", "✅", " ENABLED"],
        'color': (255, 255, 255),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["Autopilot systems: ", "✅", " STATION-KEEPING"],
        'color': (255, 255, 255),
        'char_delay': 20,
      },
      {
        'prompt': "comms_array/Nysa's_Wake > ",
        'text': ["NOTICE: ", "THIS MESSAGE WILL NOW REPEAT"],
        'color': (255, 128, 128),
        'char_delay': 20,
      },
    ],
  },
]
