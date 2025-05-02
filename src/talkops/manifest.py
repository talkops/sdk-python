import os
import json

class Manifest:
    def __init__(self, get_config):
        self._get_config = get_config
        time.sleep(0.5)
        self._generate()

    def _generate(self):
        with open('/app/manifest.json', 'w') as f:
            json.dump(self._get_config(), f, indent=2)
