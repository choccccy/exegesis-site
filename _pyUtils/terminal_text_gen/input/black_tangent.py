CONFIG = {
    # 'WIDTH': 320,  # full height log
    'WIDTH': 256,  # HUD log
    # 'HEIGHT': 240,
    'HEIGHT': 24,  # HUD log
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
OUTPUT_NAME = 'black_tangent'

events = [
  {
    'id': '1',
    'lines': [{'prompt': "/ > ", 'text': "boot-up sequence initiated for onye_Nchọgharị"}]
  },
  {
    'id': '2',
    'lines': [
      {'prompt': "/POST > ", 'text': "Power-On Self Test initiated"},
      {'prompt': "/POST > ", 'text': ["Neural Lattice: ", "✅ [Temp: 901.2K - Pre-heating active]"]},
      {'prompt': "/POST > ", 'text': ["Somatic Bus: ", "✅"]},
      {'prompt': "/POST > ", 'text': ["Chronometer Sync: ", "✅ [Delay-adjusted Lock with Nysa's_Wake]"]}, 
      {'prompt': "/POST > ", 'text': ["Fusion Core: ", "✅"]},
      {'prompt': "/POST > ", 'text': ["HV Bus Regulators: ", "✅ [12kV Stable]"]},
      {'prompt': "/POST > ", 'text': ["Liquid Water: ", "⚠️ Fluid levels at 28.73%. Refill soon."]},
      {'prompt': "/POST > ", 'text': ["Skeletal Actuators: ", "❌ Arm 00 node 3 (left elbow): Actuator torque demand +8.3% vs baseline. Hysteresis detected. Seek maintainence or replacement."]},
      {'prompt': "/POST > ", 'text': ["Joint Encoders: ", "✅"]},
      {'prompt': "/POST > ", 'text': ["Epidermal Haptics: ", "✅"]},
      {'prompt': "/POST > ", 'text': ["Reaction Control: ", "✅"]},
      {'prompt': "/POST > ", 'text': ["Magnetic Anchors: ", "✅"]},
      {'prompt': "/POST > ", 'text': ["Magnetic Holsters: ", "✅"]},
      {'prompt': "/POST > ", 'text': ["Comms Array: ", "❌ Rx-01 (right) automatically adjusted to 300.0% (maximum) gain to maintain parity with Rx-00 (left). Seek maintainence or replacement."]},
    ],
  },
  {
    'id': '3',
    'lines': [{'prompt': "/ > ", 'text': "HUD initializing"}]
  },
  {
    'id': '4',
    'lines': [
      {'prompt': "/comms_array/local/Mkpụrụobi_mepụta > ", 'text': "U+23F0", 'color': '#99f6ff', 'char_delay': 30},
      {'prompt': "/comms_array/local/onye_Nchọgharị > ", 'text': "yeah, yeah, i'm up.", 'color': '#c499ff', 'char_delay': 50},
      {'prompt': "/comms_array/local/Mkpụrụobi_mepụta > ", 'text': "ETA to Nysa's Wake: 12 MINUTES", 'color': '#99f6ff', 'char_delay': 30},
    ],
  },
  {
    'id': '5',
    'lines': [
      {'prompt': "/comms_array/Nysa's_Wake/Antikythera > ", 'text': "Cognitive function measured within variance (101.53% compared to baseline).", 'color': (255, 255, 255), 'char_delay': 20},
      {'prompt': "/comms_array/Nysa's_Wake/Antikythera > ", 'text': "Good Morning, onye Nchọgharị.", 'color': (255, 255, 255), 'char_delay': 20},
      {'prompt': "/comms_array/Nysa's_Wake/onye_Nchọgharị > ", 'text': "gm to you, too.", 'color': '#c499ff', 'char_delay': 50},
    ],
  },
  {
    'id': '6',
    'lines': [
      {'prompt': "/sensors/radar > ", 'text': "enabled"},
      {'prompt': "/comms_array/local/onye_Nchọgharị > ", 'text': "...alr, let's get ready for landing.", 'color': '#c499ff', 'char_delay': 50},
      {'prompt': "/sensors/cameras/IR > ", 'text': "enabled"},
    ],
  },
  {
    'id': '7',
    'lines': [
      {'prompt': "/comms_array/Nysa's_Wake/onye_Nchọgharị > ", 'text': "Antikythera, can we get a bay?", 'color': '#c499ff', 'char_delay': 50},
      {'prompt': "/comms_array/Nysa's_Wake/Antikythera > ", 'text': "Starboard Bay 9J is available. Dr. Agnès Lemaître will be arriving within the hour to begin loading her lab onto your freighter.", 'color': (255, 255, 255), 'char_delay': 20},
      {'prompt': "/comms_array/Nysa's_Wake/onye_Nchọgharị > ", 'text': "eh? why are we running that, wouldn't she prefer somebody from the Research Logistics team?", 'color': '#c499ff', 'char_delay': 50},
      {'prompt': "/comms_array/Nysa's_Wake/Antikythera > ", 'text': "Dr. Lemaître preferred your support. No other pilot is assigned.", 'color': (255, 255, 255), 'char_delay': 20},
      {'prompt': "/sensors/cameras/visible > ", 'text': "enabled"},
      {'prompt': "/comms_array/local/onye_Nchọgharị > ", 'text': "well, don't argue with the Doc.", 'color': '#c499ff', 'char_delay': 50},
      {'prompt': "/comms_array/local/Mkpụrụobi_mepụta > ", 'text': "U+1F469U+200DU+1F52C", 'color': '#99f6ff', 'char_delay': 30},
      {'prompt': "/comms_array/local/onye_Nchọgharị > ", 'text': "of course you're excited, she's always sweet on you.", 'color': '#c499ff', 'char_delay': 50},
    ],
  },
  {
    'id': '8',
    'lines': [
      {'prompt': "/tool/vehicle > ", 'text': "Connection established with Freighter_17c"},
      {'prompt': "/tool/Freighter_17c > ", 'text': "Synchronizing sensor data with pilot"},
      {'prompt': "/tool/Freighter_17c > ", 'text': "Autopilot enabled, ready for manual handoff"},
      {'prompt': "/comms_array/local/onye_Nchọgharị > ", 'text': "i've got the ship. all good for landing, Obi?", 'color': '#c499ff', 'char_delay': 50},
      {'prompt': "/comms_array/local/Mkpụrụobi_mepụta > ", 'text': "bay lock 5: ⚠️ INTERMITTENT FAULT", 'color': '#99f6ff', 'char_delay': 30},
      {'prompt': "/comms_array/local/onye_Nchọgharị > ", 'text': "tsk. not ideal, but surely the Doc won't have packed us all the way to the brim. we'll manage.", 'color': '#c499ff', 'char_delay': 50},
    ],
  },
]
