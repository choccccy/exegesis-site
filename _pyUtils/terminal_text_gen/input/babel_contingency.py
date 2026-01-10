CONFIG = {
    'WIDTH': 320,
    'HEIGHT': 240,
    'BG_COLOR': (0, 0, 0),
    'START_FRAME_DELAY_MS': 960,
    'DELAY_PROMPT_MS': 600,
    'SEGMENT_DELAY_MS': 480,
    'DELAY_NEWLINE_MS': 960,
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
OUTPUT_FORMAT = 'webp'     # webp or gif
OUTPUT_NAME = 'babel_contingency'

events = [
  {
    'id': '1',
    'lines': [{'prompt': "/ > ", 'text': "boot-up sequence initiated for onye_Nchọgharị"}]
  },
  {
    'id': '2',
    'lines': [
      {'prompt': "/POST > ", 'text': "Power-On Self Test initiated"},
      {'prompt': "/POST > ", 'text': ["Neural Lattice: ", "⚠️ [Temp: 1479.2K - Emergency Cooling Active. Vaporizing and ejecting liquid water as thermal mass]"]},
      {'prompt': "/POST > ", 'text': ["Somatic Bus: ", "⚠️ [Falling back to 48-lane width]"]},
      {'prompt': "/POST > ", 'text': ["Chronometer Sync: ", "⚠️ [Nysa's_Wake Lock lost - Falling back to Delta_Site Lock]"]}, 
      {'prompt': "/POST > ", 'text': ["Fusion Core: ", "✅"]},
      {'prompt': "/POST > ", 'text': ["HV Bus Regulators: ", "✅ [12kV Stable]"]},
      {'prompt': "/POST > ", 'text': ["Liquid Water: ", "❌ Fluid levels at 4.89%. Manuvering thrusters disabled."]},
      {'prompt': "/POST > ", 'text': ["Skeletal Actuators: ", "❌ Arm 00 node 1 (left shoulder) offline - Leg 00 node 3 (left foot) offline"]},
      {'prompt': "/POST > ", 'text': ["Joint Encoders: ", "❌ Arm 00 node 1 (left shoulder) offline - Leg 00 node 3 (left foot) offline"]},
      {'prompt': "/POST > ", 'text': ["Epidermal Haptics: ", "✅"]},
      {'prompt': "/POST > ", 'text': ["Reaction Control: ", "❌ Reaction mass reserved for emergency cooling."]},
      {'prompt': "/POST > ", 'text': ["Magnetic Anchors: ", "✅"]},
      {'prompt': "/POST > ", 'text': ["Magnetic Holsters: ", "✅"]},
      {'prompt': "/POST > ", 'text': ["Comms Array: ", "❌ Rx-01 (right) automatically adjusted to 300.0% (maximum) gain to maintain parity with Rx-00 (left). Seek maintainence or replacement."]},
      {'prompt': "/ > ", 'text': "HUD initializing"},
      {'prompt': "/sensors/radar > ", 'text': "enabled"},
      {'prompt': "/sensors/cameras/IR > ", 'text': "enabled"},
      {'prompt': "/sensors/cameras/visible > ", 'text': "enabled"},
    ],
  },
  {
    'id': '3',
    'lines': [
      {'prompt': "/comms_array/local/Mkpụrụobi_mepụta > ", 'text': "⚠️ EMERGENCY: FREIGHTER_17C CRASHED", 'color': '#99f6ff', 'char_delay': 30},
      {'prompt': "/comms_array/local/Mkpụrụobi_mepụta > ", 'text': "⚠️ EMERGENCY: ONYE_NCHỌGHARỊ LEFT ARM SEVERED", 'color': '#99f6ff', 'char_delay': 30},
      {'prompt': "/comms_array/local/Mkpụrụobi_mepụta > ", 'text': "⚠️ EMERGENCY: ONYE_NCHỌGHARỊ LEFT FOOT DESTROYED", 'color': '#99f6ff', 'char_delay': 30},
      {'prompt': "/comms_array/local/onye_Nchọgharị > ", 'text': "i'm here, i'm here. fuck, my head...", 'color': '#c499ff', 'char_delay': 50},
    ],
  },
  {
    'id': '4',
    'lines':[{'prompt': "/comms_array/local/Mkpụrụobi_mepụta > ", 'text': "DISTRESS BEACON: ACTIVE", 'color': '#99f6ff', 'char_delay': 30}],
  },
  {
    'id': '5',
    'lines': [{'prompt': "/comms_array/Nysa's_Wake/onye_Nchọgharị > ", 'text': "...the Antikythera is offline, isn't it? i still haven't gotten a good morning packet. and the primion excitation that took us down...", 'color': '#c499ff', 'char_delay': 50}],
  },
  {
    'id': '6',
    'lines': [
      {'prompt': "/tool/vehicle > ", 'text': "Connection re-established with Freighter_17c"},
      {'prompt': "/tool/Freighter_17c > ", 'text': "Synchronizing sensor data with pilot"},
      {'prompt': "/tool/Freighter_17c > ", 'text': ["Freighter_17c Disabled: ", "❌ Several critical subsystems offline"]},
      {'prompt': "/tool/Freighter_17c > ", 'text': "Autopilot disabled"},
      {'prompt': "/comms_array/local/onye_Nchọgharị > ", 'text': "'Several subsystems offline', no shit. i don't think we're gonna be able to recover much from this thing. looks like even its core was dumped, glad it failed safe.", 'color': '#c499ff', 'char_delay': 50},
    ],
  },
]
