import asyncio
import json
import os
import signal
import socket

class EventBus:
    def __init__(self, use_state, use_config, set_enabled):
        self._use_state = use_state
        self._use_config = use_config
        self._set_enabled = set_enabled
        self._last_event_state: str | None = None
        self._client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._client.setblocking(False)

    async def start(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        self._loop = asyncio.get_running_loop()
        await self._loop.sock_connect(self._client, os.environ['TALKOPS_SOCKET'])
        asyncio.create_task(self.publish_event({"type": "init"}))
        asyncio.create_task(self._publish_state_periodically())
        while True:
            data = await self._loop.sock_recv(self._client, 4096)
            if not data:
                break
            event = json.loads(data.decode())
            asyncio.create_task(self._on_event(event))

    def _generate_event_state(self):
        return {"type": "state", "state": self._use_state()}

    async def publish_event(self, event):
        data = json.dumps(event, separators=(',', ':')).encode() + b'\n'
        await asyncio.to_thread(self._client.sendall, data)

    async def _publish_state(self):
        event = self._generate_event_state()
        self._last_event_state = json.dumps(event)
        await self.publish_event(event)

    async def _publish_state_periodically(self):
        while True:
            await asyncio.sleep(0.5)
            event = self._generate_event_state()
            last_event_state = json.dumps(event)
            if self._last_event_state != last_event_state:
                self._last_event_state = last_event_state
                asyncio.create_task(self.publish_event(event))

    async def _on_event(self, event):
        config = self._use_config()
        if event['type'] == 'boot':
            self._set_enabled(event['enabled'])
            for name, value in event['parameters'].items():
                for parameter in config['parameters']:
                    if parameter.name != name:
                        continue
                    if isinstance(value, str):
                        parameter.set_value(value)
                    else:
                        parameter.set_value("")
            asyncio.create_task(self._publish_state())
        if event['type'] == 'enable':
            self._set_enabled(True)
        if event['type'] == 'disable':
            self._set_enabled(False)
        ready = True
        for parameter in config['parameters']:
            if parameter.is_optional:
                continue
            if parameter.has_value:
                continue
            ready = False
        if not ready:
            return
        if event['type'] == 'function_call':
            for function in config['functions']:
                if function.__name__ != event['name']:
                    continue
                arguments_list = [
                    event['args'].get(name) or event['defaultArgs'].get(name)
                    for name in function.__code__.co_varnames
                ]
                output = function(*arguments_list)
                if asyncio.iscoroutine(output):
                    output = await asyncio.create_task(output)
                event['output'] = output
                asyncio.create_task(self.publish_event(event))
                return
            print(f'Function {function.__name__} not found.', file=sys.stderr)
            return
        if event['type'] in config['callbacks']:
            callback = config['callbacks'][event['type']]
            arguments_list = [event['args'].get(name) for name in callback.__code__.co_varnames]
            output = callback(*arguments_list)
            if asyncio.iscoroutine(output):
                asyncio.create_task(output)
