import os
import json
from jinja2 import Environment, FileSystemLoader

class Readme:
    def __init__(self, getter):
        self._getter = getter
        self._generate()

    def _generate(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        env = Environment(
            loader=FileSystemLoader(current_dir),
            autoescape=True
        )
        template = env.get_template('readme.jinja2')
        output = template.render(extension=self._getter())
        with open('/app/README.md', 'w', encoding='utf-8') as f:
            f.write(output)
