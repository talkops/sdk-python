from .link import Link
import re

class Attachment(Link):
    def __init__(self, url, filename):
        super().__init__(url)
        self._filename = None
        self.set_filename(filename)

    def to_json(self):
        data = super().to_json()
        data.update({
            'filename': self._filename,
            'type': 'attachment'
        })
        return data

    def set_filename(self, filename):
        if not isinstance(filename, str) or not filename.strip():
            raise TypeError('Filename must be a non-empty string.')
        illegal_chars = re.compile(r'[\\/:*?"<>|]')
        if illegal_chars.search(filename):
            raise TypeError(f'Filename contains invalid characters: {filename}')
        self._filename = filename
        return self
