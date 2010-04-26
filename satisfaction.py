import urllib

import feedparser
import lxml.html


class ResourceNotFound(RuntimeError): pass


class Resource:
    
    def __init__(self, resource_id):
        self.resource_id = resource_id
        self._document = None
    
    @classmethod
    def url(cls, resource_id, page=None):
        url = cls.URL % resource_id
        if page:
            url += '?page=%s' % page
        return url
    
    def resource_not_found(self):
        name = self.__class__.__name__
        raise ResourceNotFound('%s not found: %s' % (name, self.resource_id))
    
    @property
    def document(self):
        if self._document is None:
            self.load_document()
        return self._document
    

class AtomParser:
    
    def load_document(self):
        document = feedparser.parse(self.url(self.resource_id, self._page))
        if document.get('status', None) == 404:
            self.resource_not_found()
        self._document = document
    

class HtmlParser:
    
    def load_document(self):
        response = urllib.urlopen(self.url(self.resource_id))
        if response.headers.getheader('status') == '404':
            self.resource_not_found()
        self._document = lxml.html.document_fromstring(response.read())
    

class Product(Resource, HtmlParser):

    URL = 'http://api.getsatisfaction.com/products/%s'

    @property
    def title(self):
        return self.document.cssselect('a.name')[0].text_content()


class Topic(Resource, AtomParser):
    
    URL = 'http://api.getsatisfaction.com/topics/%s'
    
    def __init__(self, *args):
        Resource.__init__(self, *args)
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
