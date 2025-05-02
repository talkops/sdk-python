from .media import Media
from urllib.parse import urlparse

class Link(Media):
    def __init__(self, url):
        super().__init__()
        self._url = None
        self.set_url(url)

    def to_json(self):
        return {
            'type': 'link',
            'url': self._url
        }

    def set_url(self, url):
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                raise ValueError
        except ValueError:
            raise TypeError(f'Invalid URL: {url}')
        self._url = url
        return self
