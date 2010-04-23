import feedparser


class ResourceNotFound(RuntimeError): pass


class Resource:
    
    @classmethod
    def url(cls, resource_id):
        return cls.URL % resource_id
    

class Reply(Resource):

    def __init__(self, parent):
        self.parent = parent
        
    def __iter__(self):
        for entry in self.parent._get().entries[1:]:
            yield entry
    

class Topic(Resource):
    
    URL = "http://api.getsatisfaction.com/topics/%s"
    
    def __init__(self, resource_id):
        self.resource_id = resource_id
        self.document = None
    
    def _get(self):
        if self.document is None:
            self.document = feedparser.parse(self.url(self.resource_id))
        if self.document.get("status", None) == 404:
            name = self.__class__.__name__
            raise ResourceNotFound("%s not found: %s" % (name, self.resource_id))
        return self.document
    
    @property
    def title(self):
        return self._get().feed.title

    @property
    def content(self):
        return self._get().entries[0].content[0]['value']

    @property
    def reply_count(self):
        # TODO: read the number straight out of the atom feed
        return len(list(self.replies))

    @property
    def replies(self):
        return iter(Reply(self))
