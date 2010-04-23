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
            self.document = feedparser.parse(self.url(self.topic_id))
        if self.document.get("status", None) == 404:
            raise ResourceNotFound("Topic not found: %s" % self.topic_id)
        return self.document
    
    @staticmethod
    def url(topic_id):
        return Topic.URL % topic_id
    
    @property
    def title(self):
        return self._get().feed.title

    @property
    def content(self):
        return self._get().entries[0].content[0]['value']

    @property
    def reply_count(self):
        return len(self.replies)

    @property
    def replies(self):
        return self._get().entries[1:]
