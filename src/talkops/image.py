from .link import Link

class Image(Link):
    def to_json(self):
        data = super().to_json()
        data['type'] = 'image'
        return data
