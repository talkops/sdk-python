from urllib.parse import urlencode
import aiofiles.os
import aiohttp
import asyncio
import json
import time

class Publisher:
    def __init__(self, use_config, use_state):
        self._use_config = use_config
        self._use_state = use_state
        self._last_event_state = None
        self._last_ping_at = None
        asyncio.create_task(self._publish_data({'type': 'init'}))
        asyncio.create_task(self._publish_state_periodically())

    async def _generate_event_state(self):
        state = self._use_state()
        try:
            stat_result = await aiofiles.os.stat("error.log")
            state["hasErrors"] = stat_result.st_size > 0
        except FileNotFoundError:
            state["hasErrors"] = False
        return {"type": "state", "state": state}

    async def publish_state(self):
        event = await self._generate_event_state()
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

    async def _publish_state_periodically(self):
        while True:
            await asyncio.sleep(0.5)
            event = await self._generate_event_state()
            last_event_state = json.dumps(event)
            if self._last_event_state != last_event_state:
                self._last_event_state = last_event_state
                asyncio.create_task(self.publish_event(event))
