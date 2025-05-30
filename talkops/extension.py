from .event_bus import EventBus
from .parameter import Parameter
from .readme import Readme
from .manifest import Manifest
from .media import Media
from importlib.metadata import version
from importlib.resources import files
from urllib.parse import urlparse
import asyncio
import json
import nest_asyncio

class Extension:
    def __init__(self):
        self._callbacks = {}
        self._category = None
        self._demo = False
        self._enabled = False
        self._event_bus = None
        self._features = []
        self._functions = []
        self._function_schemas = []
        self._icon = None
        self._installation_steps = []
        self._instructions = None
        self._name = None
        self._parameters = []
        self._started = False
        self._website = None

    async def _setup(self):
        await asyncio.sleep(0.5)
        Readme(
            lambda: {
                'features': self._features,
                'name': self._name,
            }
        )
        Manifest(
            lambda: {
                'category': self._category,
                'demo': self._demo,
                'features': self._features,
                'icon': self._icon,
                'name': self._name,
                'sdk': {
                    'name': 'python',
                    'version': version('talkops'),
                },
                'website': self._website,
            }
        )
        self._event_bus = EventBus(
            lambda: {
                'category': self._category,
                'demo': self._demo,
                'icon': self._icon,
                'installationSteps': self._installation_steps,
                'instructions': self._instructions,
                'name': self._name,
                'parameters': [p.to_json() for p in self._parameters],
                'sdk': {
                    'name': 'python',
                    'version': version('talkops'),
                },
                'functionSchemas': self._function_schemas,
            },
            lambda: {
                'callbacks': self._callbacks,
                'functions': self._functions,
                'parameters': self._parameters,
            },
            self._set_enabled
        )
        await asyncio.gather(self._event_bus.start())

    def _set_enabled(self, enabled):
        self._enabled = enabled

    def start(self):
        if self._started:
            return
        self._started = True
        nest_asyncio.apply()
        asyncio.run(self._setup())
        return self

    def on(self, event_type, callback):
        if event_type not in self._get_event_types():
            raise ValueError(f'event_type must be one of the following strings: {", ".join(self._get_event_types())}')
        if not callable(callback):
            raise ValueError('callback must be a function.')
        self._callbacks[event_type] = callback
        return self

    def set_demo(self, demo):
        if not isinstance(demo, bool):
            raise ValueError('demo must be a boolean.')
        self._demo = demo
        return self

    def set_name(self, name):
        if not isinstance(name, str) or not name.strip():
            raise ValueError('name must be a non-empty string.')
        self._name = name
        return self

    def set_icon(self, icon):
        if not isinstance(icon, str) or not icon.strip():
            raise ValueError('icon must be a non-empty string.')
        try:
            urlparse(icon)
        except ValueError:
            raise ValueError('icon must be a valid URL.')
        self._icon = icon
        return self

    def set_website(self, website):
        if not isinstance(website, str) or not website.strip():
            raise ValueError('website must be a non-empty string.')
        try:
            urlparse(website)
        except ValueError:
            raise ValueError('website must be a valid URL.')
        self._website = website
        return self

    def set_category(self, category):
        if category not in self._get_categories():
            raise ValueError(f'category must be one of the following strings: {", ".join(self._get_categories())}')
        self._category = category
        return self

    def set_features(self, features):
        if not isinstance(features, list) or not all(isinstance(f, str) and f.strip() for f in features):
            raise ValueError('features must be an array of non-empty strings.')
        self._features = features
        return self

    def set_installation_steps(self, installation_steps):
        if not isinstance(installation_steps, list) or not all(isinstance(step, str) and step.strip() for step in installation_steps):
            raise ValueError('installation_steps must be an array of non-empty strings.')
        self._installation_steps = installation_steps
        return self

    def set_parameters(self, parameters):
        if not isinstance(parameters, list) or not all(isinstance(p, Parameter) for p in parameters):
            raise ValueError('parameters must be an array of Parameter instances.')
        self._parameters = parameters
        return self

    def set_instructions(self, instructions):
        if not isinstance(instructions, str) or not instructions.strip():
            raise ValueError('instructions must be a non-empty string.')
        self._instructions = instructions
        return self

    def set_function_schemas(self, function_schemas):
        if (
            not isinstance(function_schemas, list) or
            not all(
                isinstance(schema, dict) and
                schema is not None for schema in function_schemas
            )
        ):
            raise ValueError('functionSchemas must be an array of non-null objects.')
        self._function_schemas = function_schemas
        return self

    def set_functions(self, functions):
        if (
            not isinstance(functions, list) or
            not all(callable(fn) for fn in functions) or
            not all(hasattr(fn, '__name__') and fn.__name__.strip() for fn in functions)
        ):
            raise ValueError('functions must be an array of named functions.')
        self._functions = functions
        return self

    def enable_alarm(self):
        nest_asyncio.apply()
        asyncio.run(self._event_bus.publish_event({
            'type': 'alarm'
        }))
        return self

    def send_medias(self, medias):
        if not isinstance(medias, list):
            medias = [medias]
        if not all(isinstance(media, Media) for media in medias):
            raise ValueError("medias must be a list of Media instances.")
        nest_asyncio.apply()
        asyncio.run(self._event_bus.publish_event({
            'type': 'medias',
            'medias': [media.to_json() for media in medias]
        }))
        return self

    def send_message(self, text):
        if not isinstance(text, str) or not text.strip():
            raise ValueError('text must be a non-empty string.')
        nest_asyncio.apply()
        asyncio.run(self._event_bus.publish_event({
            'type': 'message',
            'text': text
        }))
        return self

    def send_notification(self, text):
        if not isinstance(text, str) or not text.strip():
            raise ValueError('text must be a non-empty string.')
        nest_asyncio.apply()
        asyncio.run(self._event_bus.publish_event({
            'type': 'notification',
            'text': text
        }))
        return self

    def _get_categories(self):
        with files('talkops.data').joinpath('categories.json').open('r', encoding='utf-8') as f:
            return json.load(f)

    def _get_event_types(self):
        with files('talkops.data').joinpath('event-types.json').open('r', encoding='utf-8') as f:
            return json.load(f)
