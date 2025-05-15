from urllib.parse import urlencode
import json
import requests
import time
import sys
import threading

class Publisher:
    def __init__(self, use_config, use_state):
        self._use_config = use_config
        self._use_state = use_state
        self._last_event_state = None
        self._last_ping_at = None
        self._original_stdout_write = sys.stdout.write
        self._original_stderr_write = sys.stderr.write
        def stdout_wrapper(chunk):
            self.publish_event({
                'type': 'stdout',
                'data': chunk.strip()
            })
            return self._original_stdout_write(chunk)
        def stderr_wrapper(chunk):
            if b"KeyboardInterrupt" not in chunk:
                self.publish_event({
                    'type': 'stderr',
                    'data': chunk.strip()
                })
            return self._original_stderr_write(chunk)
        sys.stdout.write = stdout_wrapper
        sys.stderr.write = stderr_wrapper
        self._publish_data(json.dumps({'type': 'init'}))
        threading.Timer(0.2, self._publish_state).start()

    def publish_state(self):
        event = {'type': 'state', 'state': self._use_state()}
        self._last_event_state = json.dumps(event)
        self.publish_event(event)

    def on_ping(self):
        self._last_ping_at = time.time() * 1000
        self.publish_event({'type': 'pong'})

    def publish_event(self, event):
        if self._last_ping_at and self._last_ping_at < (time.time() * 1000 - 6000):
            return
        self._publish_data(json.dumps(event))

    def _publish_data(self, data):
        config = self._use_config()
        response = requests.post(
            config['mercure']['url'],
            data=urlencode({
                'topic': config['mercure']['publisher']['topic'],
                'data': data
            }),
            headers={
                'Authorization': f"Bearer {config['mercure']['publisher']['token']}",
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        response.raise_for_status()

    def _publish_state(self):
        event = {'type': 'state', 'state': self._use_state()}
        last_event_state = json.dumps(event)
        if self._last_event_state != last_event_state:
            self.publish_event(event)
            self._last_event_state = last_event_state
        threading.Timer(1.0, self._publish_state).start()

    def __del__(self):
        sys.stdout.write = self._original_stdout_write
        sys.stderr.write = self._original_stderr_write 
