import os
import json
import base64
from urllib.parse import urlparse
from .publisher import Publisher
from .subscriber import Subscriber
from .parameter import Parameter
from .readme import Readme
from .manifest import Manifest
import pkg_resources

class Extension:
    def __init__(self, token=None):
        token = token or os.environ.get('TALKOPS_TOKEN')
        if token:
            mercure = json.loads(base64.b64decode(token).decode())
            self._publisher = Publisher(
                lambda: {'mercure': mercure},
                lambda: {
                    'category': self._category,
                    'demo': self._demo,
                    'icon': self._icon,
                    'installationSteps': self._installation_steps,
                    'instructions': self._instructions,
                    'name': self._name,
                    'parameters': self._parameters,
                    'sdk': {
                        'name': 'python',
                        'version': pkg_resources.get_distribution('talkops').version,
                    },
                    'softwareVersion': self._software_version,
                    'functionSchemas': self._function_schemas,
                }
            )
            Subscriber(
                lambda: {
                    'callbacks': self._callbacks,
                    'extension': self,
                    'functions': self._functions,
                    'mercure': mercure,
                    'parameters': self._parameters,
                    'publisher': self._publisher,
                }
            )

        if os.environ.get('NODE_ENV') == 'development':
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
                        'version': '2.14.1',
                    },
                    'softwareVersion': self._software_version,
                    'website': self._website,
                }
            )

        self._callbacks = {}
        self._category = None
        self._demo = False
        self._features = []
        self._functions = []
        self._function_schemas = []
        self._icon = None
        self._installation_steps = []
        self._instructions = None
        self._name = None
        self._parameters = []
        self._software_version = None
        self._website = None

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

    def set_software_version(self, software_version):
        self._software_version = software_version
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
        if not isinstance(function_schemas, list):
            raise ValueError('function_schemas must be an array.')
        self._function_schemas = function_schemas
        return self

    def set_functions(self, functions):
        if not isinstance(functions, list):
            raise ValueError('functions must be an array.')
        self._functions = functions
        return self

    def enable_alarm(self):
        self._publisher.enable_alarm()
        return self

    def send_medias(self, medias):
        self._publisher.send_medias(medias)
        return self

    def send_message(self, text):
        self._publisher.send_message(text)
        return self

    def send_notification(self, text):
        self._publisher.send_notification(text)
        return self

    def _get_event_types(self):
        with open(os.path.join(os.path.dirname(__file__), 'event_types.json'), 'r') as f:
            return json.load(f)

    def _get_categories(self):
        with open(os.path.join(os.path.dirname(__file__), 'categories.json'), 'r') as f:
            return json.load(f)
