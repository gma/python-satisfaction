import urllib

import feedparser
import lxml.html


class ResourceNotFound(RuntimeError): pass


class Parser:
    
    def __init__(self, resource):
        self._document = None
        self.resource = resource

    @property
    def document(self):
        if self._document is None:
            self.load_document()
        return self._document
    
    def resource_not_found(self):
        # TODO: report which resource wasn't found
        raise ResourceNotFound()


class AtomParser(Parser):
    
    def __init__(self, *args):
        Parser.__init__(self, *args)
        self.page = 1
    
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
        self.page += 1
    
    def load_document(self):
        url = self.resource.url(self.resource.resource_id, self.page)
        document = feedparser.parse(url)
        if document.get('status', None) == 404:
            self.resource_not_found()
        self._document = document


class HtmlParser(Parser):
    
    def load_document(self):
        response = urllib.urlopen(self.resource.url(self.resource.resource_id))
        if response.headers.getheader('status') == '404':
            self.resource_not_found()
        self._document = lxml.html.document_fromstring(response.read())
    

class Resource:
    
    def __init__(self, resource_id):
        self.resource_id = resource_id
    
    @classmethod
    def url(cls, resource_id, page=None):
        url = cls.URL % resource_id
        if page:
            url += '?page=%s' % page
        return url
    
    @property
    def document(self):
        return self.parser.document


class Product(Resource):

    URL = 'http://api.getsatisfaction.com/products/%s'

    def __init__(self, *args):
        Resource.__init__(self, *args)
        self.parser = HtmlParser(self)

    @property
    def title(self):
        return self.document.cssselect('a.name')[0].text_content()


class Topic(Resource):
    
    URL = 'http://api.getsatisfaction.com/topics/%s'
    
    def __init__(self, *args):
        Resource.__init__(self, *args)
        self.parser = AtomParser(self)
    
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
        return iter(self.parser)
