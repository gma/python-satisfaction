import datetime
import time
import urllib

import feedparser
import lxml.html


class ResourceNotFound(RuntimeError):
    
    pass


class Parser(object):
    
    def __init__(self, url, child_cls=None):
        self.url = url
        self.child_cls = child_cls
        self._document = None
    
    @property
    def document(self):
        if self._document is None:
            self.load_document()
        return self._document


class HtmlParser(Parser):
    
    def load_document(self):
        response = urllib.urlopen(self.url)
        if response.headers.getheader('status') == '404':
            raise ResourceNotFound(self.url)
        self._document = lxml.html.document_fromstring(response.read())
    
    def tags(self, selector):
        return self.document.cssselect(selector)
    
    def title(self):
        return self.document.cssselect('title')[0].text_content()
    
    def __iter__(self):
        while True:
            for tag in self.document.cssselect('div.hproduct a.name'):
                resource_id = tag.get('href').rsplit('/')[-1]
                yield self.child_cls(resource_id)
            raise StopIteration


class AtomParser(Parser):
    
    def __init__(self, url, child_cls, first_child_entry=0):
        Parser.__init__(self, url, child_cls)
        self.first_child_entry = first_child_entry
        self.page = 1
    
    def __iter__(self):
        while True:
            for entry in self.document.entries[self.first_child_entry:]:
                yield self.child_cls.from_entry(entry)
            if self.more_pages_to_load():
                self.load_next_page()
            else:
                raise StopIteration
    
    def page_number(self, page_type):
        def link_tag_for_type(link):
            return link ['rel'] == page_type
        url = filter(link_tag_for_type, self.document.feed.links)[0]['href']
        return int(url.split('=')[-1])
    
    def more_pages_to_load(self):
        return self.page_number('self') < self.page_number('last')
    
    def load_next_page(self):
        self._document = None
        self.page += 1
    
    def url_for_page(self):
        return self.url + '?page=%s' % self.page
    
    def load_document(self):
        document = feedparser.parse(self.url_for_page())
        if document.get('status', None) == 404:
            raise ResourceNotFound(self.url_for_page())
        self._document = document
    
    def first_entry(self):
        return self.document.entries[0]


class Resource(object):
    
    def __init__(self, resource_id):
        self.resource_id = resource_id
    
    def url(self):
        return self.URL % {'id': self.resource_id}
    
    def child_url(self, resource):
        return '%s/%s' % (self.url(), resource)


class HtmlResource(Resource):
    
    @property
    def title(self):
        return self.parser.title()


class AtomResource(Resource):
    
    def __init__(self, resource_id):
        Resource.__init__(self, resource_id)
        self._entry = None
    
    @classmethod
    def from_entry(cls, entry):
        resource = cls(entry.id.split('/')[-1])
        resource._entry = entry
        return resource
    
    @property
    def entry(self):
        if self._entry is None:
            self._entry = self.parser.first_entry()
        return self._entry


class Company(HtmlResource):
    
    URL = 'http://api.getsatisfaction.com/companies/%(id)s'
    
    def __init__(self, name):
        self.name = name
        self.parser = HtmlParser(self.url())
    
    def url(self):
        return self.URL % {'id': self.name}

    @property
    def resource_id(self):
        return self.parser.tags('span.id')[0].text_content()
    
    @property
    def products(self):
        return iter(HtmlParser(self.child_url('products'), Product))


class Product(HtmlResource):
    
    URL = 'http://api.getsatisfaction.com/products/%(id)s'
    
    def __init__(self, resource_id):
        HtmlResource.__init__(self, resource_id)
        self.parser = HtmlParser(self.url())
        self._topic_parser = None
    
    @property
    def topic_parser(self):
        if self._topic_parser is None:
            self._topic_parser = AtomParser(self.child_url('topics'), Topic)
        return self._topic_parser
    
    @property
    def topic_count(self):
        return int(self.topic_parser.document.feed['totalresults'])
    
    @property
    def topics(self):
        return iter(self.topic_parser)


class Message(object):
    
    @property
    def title(self):
        return self.entry.title
    
    @property
    def content(self):
        return self.entry.content[0]['value']

    def parse_time(self, isodate):
        timetuple = time.strptime(isodate, '%Y-%m-%dT%H:%M:%SZ')
        return datetime.datetime(*timetuple[0:6])
    
    @property
    def updated_at(self):
        return self.parse_time(self.entry.updated)
    
    @property
    def published_at(self):
        return self.parse_time(self.entry.published)


class Topic(AtomResource, Message):
    
    URL = 'http://api.getsatisfaction.com/topics/%(id)s'
    
    def __init__(self, resource_id):
        AtomResource.__init__(self, resource_id)
        self.parser = AtomParser(self.url(), Reply, first_child_entry=1)
    
    @property
    def reply_count(self):
        return int(self.entry['reply_count'])
    
    @property
    def replies(self):
        return iter(self.parser)


class Reply(AtomResource, Message):
    
    pass
