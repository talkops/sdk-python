from urllib.parse import urlencode
import aiohttp
import asyncio
import json
import sys
import time

class Publisher:
    def __init__(self, use_config, use_state):
        self._use_config = use_config
        self._use_state = use_state
        self._last_event_state = None
        self._last_ping_at = None

    async def start(self):
        self._original_stdout_write = sys.stdout.write
        self._original_stderr_write = sys.stderr.write
        def stdout_wrapper(chunk):
            data = chunk.strip()
            if(data != ""):
                asyncio.create_task(self.publish_event({
                    'type': 'stdout',
                    'data': data,
                    'time': time.time()
                }))
            return self._original_stdout_write(chunk)
        def stderr_wrapper(chunk):
            if "KeyboardInterrupt" not in chunk:
                data = chunk.strip()
                if(data != ""):
                    asyncio.create_task(self.publish_event({
                        'type': 'stderr',
                        'data': data,
                        'time': time.time()
                    }))
            return self._original_stderr_write(chunk)
        sys.stdout.write = stdout_wrapper
        sys.stderr.write = stderr_wrapper

        asyncio.create_task(self._publish_data({'type': 'init'}))
        await asyncio.sleep(0.5)
        asyncio.create_task(self._periodic_publish_state())

    async def publish_state(self):
        event = {'type': 'state', 'state': self._use_state()}
        self._last_event_state = json.dumps(event)
        await self.publish_event(event)

    async def on_ping(self):
        self._last_ping_at = time.time()
        await self.publish_event({'type': 'pong'})

    async def publish_event(self, event):
        if self._last_ping_at and self._last_ping_at < (time.time() - 6):
            return
        asyncio.create_task(self._publish_data(event))

    async def _publish_data(self, data):
        if isinstance(data, dict):
            data = json.dumps(data)

        config = self._use_config()
        async with aiohttp.ClientSession() as session:
            async with session.post(
                config['mercure']['url'],
                data=urlencode({
                    'topic': config['mercure']['publisher']['topic'],
                    'data': data
                }),
                headers={
                    'Authorization': f"Bearer {config['mercure']['publisher']['token']}",
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            ) as response:
                if response.status >= 400:
                    raise Exception(f"Failed to publish event: {response.status}")
                return await response.text()

    async def _periodic_publish_state(self):
        while True:
            event = {'type': 'state', 'state': self._use_state()}
            last_event_state = json.dumps(event)
            if self._last_event_state != last_event_state:
                await self.publish_event(event)
                self._last_event_state = last_event_state
            await asyncio.sleep(1.0)
