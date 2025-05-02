from .link import Link

class Video(Link):
    def to_json(self):
        data = super().to_json()
        data['type'] = 'video'
        return data
