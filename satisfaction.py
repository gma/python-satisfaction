import feedparser


class ResourceNotFound(RuntimeError):
    
    pass


class Topic(object):
    
    URL = "http://api.getsatisfaction.com/topics/%s"
    
    def __init__(self, topic_id):
        self.topic_id = topic_id
        self.document = None
    
    def _get(self):
        if self.document is None:
            self.document = feedparser.parse(self.url())
        if self.document.status == 404:
            raise ResourceNotFound("Topic not found: %s" % self.topic_id)
        return self.document
    
    def url(self):
        return Topic.URL % self.topic_id
    
    @property
    def title(self):
        return self._get().feed.title

    @property
    def content(self):
        return self._get().entries[0].content[0]['value']

    @property
    def reply_count(self):
        return len(self._get().entries) - 1