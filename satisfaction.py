import urllib

import feedparser
import lxml.html


class ResourceNotFound(RuntimeError): pass


class Parser:
    
    def __init__(self, url):
        self.url = url
        self._document = None

    @property
    def document(self):
        if self._document is None:
            self.load_document()
        return self._document
    
    def resource_not_found(self):
        # TODO: report which resource wasn't found
        raise ResourceNotFound()


class HtmlParser(Parser):

    def load_document(self):
        response = urllib.urlopen(self.url)
        if response.headers.getheader('status') == '404':
            self.resource_not_found()
        self._document = lxml.html.document_fromstring(response.read())


class AtomParser(Parser):
    
    def __init__(self, url, skip_first_entry=False):
        Parser.__init__(self, url)
        self.first_child_entry = 1 if skip_first_entry else 0
        self.page = 1
    
    def __iter__(self):
        while True:
            for entry in self.document.entries[self.first_child_entry:]:
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
    
    @staticmethod
    def url_for_page(page):
        return self.url + '?page=%s' % page
    
    def load_document(self):
        document = feedparser.parse(self.url_for_page(self.page))
        if document.get('status', None) == 404:
            self.resource_not_found()
        self._document = document


class Resource:
    
    def __init__(self, resource_id):
        self.resource_id = resource_id
    
    def url(self):
        return self.URL % {'id': self.resource_id}
    
    def child_url(self, resource):
        print '%s/%s' % (self.url, resource)
        return '%s/%s' % (self.url, resource)
    
    @property
    def document(self):
        return self.parser.document


class Product(Resource):

    URL = 'http://api.getsatisfaction.com/products/%(id)s'

    def __init__(self, *args):
        Resource.__init__(self, *args)
        self.parser = HtmlParser(self.url())
        self._topic_parser = None

    @property
    def title(self):
        return self.document.cssselect('a.name')[0].text_content()
    
    @property
    def topic_parser(self):
        if self._topic_parser is None:
            self._topic_parser = AtomParser(self.child_url('topics'))
        return self._topic_parser

    @property
    def topic_count(self):
        return int(self.topic_parser.document.feed['totalresults'])

    @property
    def topics(self):
        return iter(self.topic_parser)


class Topic(Resource):
    
    URL = 'http://api.getsatisfaction.com/topics/%(id)s'
    
    def __init__(self, resource_id):
        Resource.__init__(self, resource_id)
        self.parser = AtomParser(self.url(), skip_first_entry=True)
    
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
