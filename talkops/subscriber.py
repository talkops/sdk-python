from importlib.resources import files
from sseclient import SSEClient
from urllib.parse import quote
import asyncio
import json
import requests
import sys
import time

class Subscriber:
    def __init__(self, use_config):
        self._use_config = use_config
        self._subscribe()

    def _subscribe(self):
        config = self._use_config()
        mercure = config['mercure']
        try:
            messages = SSEClient(
                f"{mercure['url']}?topic={quote(mercure['subscriber']['topic'])}",
                headers={
                    'Authorization': f"Bearer {mercure['subscriber']['token']}",
                }
            )
            for message in messages:
                self._on_event(json.loads(message.data))
        except Exception as e:
            print(e)

    def _on_event(self, event):
        config = self._use_config()
        if event['type'] == 'ping':
            config['publisher'].on_ping()
            return
        if event['type'] == 'function_call':
            for fn in config['functions']:
                if fn.__name__ != event['name']:
                    continue
                arguments_list = [
                    event['args'].get(name) or event['defaultArgs'].get(name)
                    for name in fn.__code__.co_varnames
                ]
                output = fn(*arguments_list)
                if asyncio.iscoroutine(output):
                    output = asyncio.run(output)
                event['output'] = output
                config['publisher'].publish_event(event)
                return
            print(f'Function {fn.__name__} not found.', file=sys.stderr)
            return
        if event['type'] == 'boot':
            for name, value in event['parameters'].items():
                for parameter in config['parameters']:
                    if parameter.name != name:
                        continue
                    parameter.set_value(value)
            ready = True
            for parameter in config['parameters']:
                if parameter.is_optional:
                    continue
                if parameter.has_value:
                    continue
                ready = False
            config['publisher'].publish_state()
            if not ready:
                return
        if event['type'] in config['callbacks']:
            callback = config['callbacks'][event['type']]
            arguments_list = [event['args'].get(name) for name in callback.__code__.co_varnames]
            output = callback(*arguments_list)
            if asyncio.iscoroutine(output):
                output = asyncio.run(output)

    def _get_event_types(self):
        with files('talkops.data').joinpath('event-types.json').open('r', encoding='utf-8') as f:
            return json.load(f)
