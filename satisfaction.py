import feedparser


class ResourceNotFound(RuntimeError): pass


class Resource:
    
    @classmethod
    def url(cls, resource_id, page):
        url = cls.URL % resource_id
        if page:
            url += '?page=%s' % page
        return url
    

class Topic(Resource):
    
    URL = 'http://api.getsatisfaction.com/topics/%s'
    
    def __init__(self, resource_id):
        self.resource_id = resource_id
        self._document = None
        self._page = 1
    
    def __iter__(self):
        while True:
            for entry in self.document.entries[1:]:
                yield entry
            if self.more_pages_to_load():
                self.load_next_page()
            else:
                raise StopIteration
    
    def page_number(self, page_type):
        link_tag_for_type = lambda link: link['rel'] == page_type
        url = filter(link_tag_for_type, self.document.feed.links)[0]['href']
        return int(url.split('=')[-1])
    
    def more_pages_to_load(self):
        return self.page_number('self') < self.page_number('last')
    
    def load_next_page(self):
        self._document = None
        self._page += 1
    
    @property
    def document(self):
        if self._document is None:
            url = self.url(self.resource_id, self._page)
            self._document = feedparser.parse(url)
        if self._document.get('status', None) == 404:
            name = self.__class__.__name__
            raise ResourceNotFound('%s not found: %s' % (name, self.resource_id))
        return self._document
    
    @property
    def title(self):
        return self.document.feed.title

    @property
    def content(self):
        return self.document.entries[0].content[0]['value']

    @property
    def reply_count(self):
        return int(self.document.entries[0]['reply_count'])

    @property
    def replies(self):
        return iter(self)
