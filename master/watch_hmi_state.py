import time
import json
import os

json_path = os.path.join(os.path.dirname(__file__), 'hmi_state.json')

last_content = None
print('Watching hmi_state.json for real-time updates. Press Ctrl+C to stop.')
try:
    while True:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if content != last_content:
                os.system('cls' if os.name == 'nt' else 'clear')
                try:
                    parsed = json.loads(content)
                    print(json.dumps(parsed, indent=2))
                except Exception:
                    print(content)
                last_content = content
        except FileNotFoundError:
            print('hmi_state.json not found.')
        time.sleep(0.2)
except KeyboardInterrupt:
    print('\nStopped watching.')
