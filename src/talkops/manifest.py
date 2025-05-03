import os
import json

class Manifest:
    def __init__(self, use_extension):
        self._use_extension = use_extension
        self._generate()

    def _generate(self):
        with open('/app/manifest.json', 'w') as f:
            json.dump(self._use_extension(), f, indent=2)
