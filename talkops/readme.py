from importlib.resources import files
from jinja2 import BaseLoader, Environment
import os
import json

class Readme:
    def __init__(self, getter):
        self._getter = getter
        self._generate()

    def _generate(self):
        template_text = files('talkops.data').joinpath('readme.jinja2').read_text(encoding='utf-8')

        current_dir = os.path.dirname(os.path.abspath(__file__))
        env = Environment(
            loader=BaseLoader(),
            autoescape=True
        )
        template = env.from_string(template_text)
        output = template.render(extension=self._getter())
        with open('/app/README.md', 'w', encoding='utf-8') as f:
            f.write(output)
