import os
import unittest2 as unittest

import satisfaction


class TestHelper(unittest.TestCase):
    
    def setUp(self):
        if hasattr(self, 'withFixtures'):
            self.original_urls = []
            self.withFixtures()
    
    def tearDown(self):
        if hasattr(self, 'real_atom_url_func'):
            satisfaction.AtomParser.url_for_page = self.real_atom_url_func
        if hasattr(self, 'original_urls'):
            for cls, func in self.original_urls:
                cls.URL = func
    
    def useFixture(self, stubbed_cls, name=None):
        if not hasattr(self, 'real_atom_url_func'):
            def stub_url_func(self, url, page):
                return '%s-page-%s.xml' % (url.rsplit('.', 1)[0], page)
            self.real_atom_url_func = satisfaction.AtomParser.url_for_page
            satisfaction.AtomParser.url_for_page = stub_url_func

        self.original_urls.append((stubbed_cls, stubbed_cls.URL))
        base = stubbed_cls.__name__.lower()
        filename = '%s-%s.xml' % (base, name) if name else '%s.html' % base
        stubbed_cls.URL = os.path.join(os.getcwd(), 'fixtures', filename)

    def product(self):
        return satisfaction.Product('1234')

    def topic(self):
        # TODO: topic id is ignored in tests - does it work?
        return satisfaction.Topic('1234')


class MissingProductTest(TestHelper):
    
    def test_product_not_found(self):
        with self.assertRaises(satisfaction.ResourceNotFound):
            satisfaction.Product('bad_product_name').title


class ProductWithTopicsTest(TestHelper):
    
    def withFixtures(self):
        self.useFixture(satisfaction.Product)
    
    def test_can_retrieve_title(self):
        self.assertEqual('Wordtracker Keywords', self.product().title)
    
    @unittest.skip("pending url refactoring")
    def test_can_retrieve_topics(self):
        self.assertEqual(3, len(list(self.product().topics)))


class MissingTopicTest(TestHelper):

    def test_topic_not_found(self):
        with self.assertRaises(satisfaction.ResourceNotFound):
            self.topic().title
    

class TopicWithoutRepliesTest(TestHelper):
    
    def withFixtures(self):
        self.useFixture(satisfaction.Topic, 'without-replies')

    def test_title_available(self):
        self.assertEqual('Fantastic improvement', self.topic().title)
    
    def test_content_available(self):
        self.assertIn('Well done!', self.topic().content)
    
    def test_no_replies_found(self):
        self.assertEqual(0, self.topic().reply_count)
        self.assertEqual(0, len(list(self.topic().replies)))


class TopicWithRepliesTest(TestHelper):
    
    def withFixtures(self):
        self.useFixture(satisfaction.Topic, 'with-replies')
    
    def test_replies_found(self):
        self.assertEqual(3, self.topic().reply_count)
        self.assertEqual(3, len(list(self.topic().replies)))
    
    def test_topic_not_included_in_replies(self):
        extract_content = lambda reply: reply.content[0]['value']
        reply_messages = map(extract_content, self.topic().replies)
        self.assertNotIn(self.topic().content, reply_messages)


class TopicWithMultiplePagesOfRepliesTest(TestHelper):
    
    def withFixtures(self):
        self.useFixture(satisfaction.Topic, 'with-lots-of-replies')
    
    def test_replies_found(self):
        self.assertEqual(95, self.topic().reply_count)
        self.assertEqual(95, len(list(self.topic().replies)))


if __name__ == '__main__':
    unittest.main()
