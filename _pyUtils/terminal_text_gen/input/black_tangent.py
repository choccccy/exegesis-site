events = [
  {
    'id': '1',
    'lines': [{'prompt': "onye_Nchọgharị > ", 'text': "boot-up sequence initiated"}]
  },
  {
    'id': '2',
    'lines': [
      {'prompt': "onye_Nchọgharị/POST > ", 'text': "Power-On Self Test initiated"},
      {'prompt': "onye_Nchọgharị/POST > ", 'text': ["Neural Lattice: ", "✅ [Temp: 840K - Pre-heating active]"]},
      {'prompt': "onye_Nchọgharị/POST > ", 'text': ["Somatic Bus: ", "✅"]},
      {'prompt': "onye_Nchọgharị/POST > ", 'text': ["Chronometer Sync: ", "✅ [Stratum-1 Lock]"]}, 
      {'prompt': "onye_Nchọgharị/POST > ", 'text': ["Fusion Core: ", "✅"]},
      {'prompt': "onye_Nchọgharị/POST > ", 'text': ["HV Bus Regulators: ", "✅ [12kV Stable]"]},
      {'prompt': "onye_Nchọgharị/POST > ", 'text': ["Liquid Water Thermal Mass Loop: ", "⚠️ Fluid levels at 28.73%. Refill soon."]},
      {'prompt': "onye_Nchọgharị/POST > ", 'text': ["Skeletal Actuators: ", "❌ Arm 00 node 3 (left elbow): Actuator torque demand +8.3% vs baseline. Hysteresis detected. Seek maintainence or replacement."]},
      {'prompt': "onye_Nchọgharị/POST > ", 'text': ["Joint Encoders: ", "✅"]},
      {'prompt': "onye_Nchọgharị/POST > ", 'text': ["Epidermal Haptics: ", "✅"]},
      {'prompt': "onye_Nchọgharị/POST > ", 'text': ["Reaction Control: ", "✅"]},
      {'prompt': "onye_Nchọgharị/POST > ", 'text': ["Comms Array: ", "❌ Rx-01 (right) automatically adjusted to 300.0% (maximum) gain to maintain parity with receiving antenna 00 (left). Seek maintainence or replacement."]},
      {'prompt': "onye_Nchọgharị/POST > ", 'text': ["Mag-Lock Arrays: ", "✅"]},
    ],
  },
  {
    'id': '3',
    'lines': [{'prompt': "onye_Nchọgharị > ", 'text': "HUD initializing"}]
  },
  {
    'id': '4',
    'lines': [
      {'prompt': "comms_array/local/Mkpụrụobi_mepụta > ", 'text': "U+23F0", 'color': '#99f6ff', 'char_delay': 30},
      {'prompt': "onye_Nchọgharị > ", 'text': "yeah, yeah, i'm up.", 'color': '#c499ff', 'char_delay': 50},
      {'prompt': "comms_array/local/Mkpụrụobi_mepụta > ", 'text': "ETA to Nysa's Wake: 12 MINUTES", 'color': '#99f6ff', 'char_delay': 30},
    ],
  },
  {
    'id': '5',
    'lines': [
      {'prompt': "comms_array/Nysa's_Wake/Antikythera > ", 'text': "Cognitive function measured within variance (101.53% compared to baseline). Good Morning, onye Nchọgharị.", 'color': (255, 255, 255), 'char_delay': 20},
      {'prompt': "onye_Nchọgharị > ", 'text': "gm to you, too.", 'color': '#c499ff', 'char_delay': 50},
    ],
  },
  {
    'id': '6',
    'lines': [
      {'prompt': "onye_Nchọgharị/sensors/radar > ", 'text': "enabled"},
      {'prompt': "onye_Nchọgharị > ", 'text': "...alr, let's get ready for landing.", 'color': '#c499ff', 'char_delay': 50},
      {'prompt': "onye_Nchọgharị/sensors/cameras/IR > ", 'text': "enabled"},
    ],
  },
  {
    'id': '7',
    'lines': [
      {'prompt': "onye_Nchọgharị > ", 'text': "Antikythera, can we get a bay?", 'color': '#c499ff', 'char_delay': 50},
      {'prompt': "comms_array/Nysa's_Wake/Antikythera > ", 'text': "Starboard Bay 9J is available. Dr. Agnès Lemaître will be arriving within the hour to begin loading her lab onto your freighter.", 'color': (255, 255, 255), 'char_delay': 20},
      {'prompt': "onye_Nchọgharị > ", 'text': "eh? why are we running that, wouldn't she prefer somebody from the Research Logistics team?", 'color': '#c499ff', 'char_delay': 50},
      {'prompt': "comms_array/Nysa's_Wake/Antikythera > ", 'text': "Dr. Lemaître preferred your support. No other pilot is assigned.", 'color': (255, 255, 255), 'char_delay': 20},
      {'prompt': "onye_Nchọgharị/sensors/cameras/visible > ", 'text': "enabled"},
      {'prompt': "onye_Nchọgharị > ", 'text': "well, don't argue with the Doc.", 'color': '#c499ff', 'char_delay': 50},
      {'prompt': "comms_array/local/Mkpụrụobi_mepụta > ", 'text': "U+1F469U+200DU+1F52C", 'color': '#99f6ff', 'char_delay': 30},
      {'prompt': "onye_Nchọgharị > ", 'text': "of course you're excited, she's always sweet on you.", 'color': '#c499ff', 'char_delay': 50},
    ],
  },
  {
    'id': '8',
    'lines': [
      {'prompt': "onye_Nchọgharị/tool/vehicle > ", 'text': "connection established with Freighter_17c"},
      {'prompt': "onye_Nchọgharị/tool/Freighter17c > ", 'text': "Synchronizing sensor data with pilot"},
      {'prompt': "onye_Nchọgharị/tool/Freighter17c > ", 'text': "Autopilot enabled, ready for manual handoff"},
      {'prompt': "onye_Nchọgharị > ", 'text': "i've got the ship. all good for landing, Obi?", 'color': '#c499ff', 'char_delay': 50},
      {'prompt': "comms_array/local/Mkpụrụobi_mepụta > ", 'text': "bay lock 5: INTERMITTENT FAULT", 'color': '#99f6ff', 'char_delay': 30},
      {'prompt': "onye_Nchọgharị > ", 'text': "not ideal, but surely the Doc won't have packed us all the way to the brim. we'll manage.", 'color': '#c499ff', 'char_delay': 50},
    ],
  },
]
