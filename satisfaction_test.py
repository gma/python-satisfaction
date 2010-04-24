import os
import unittest2 as unittest

import satisfaction


class TestHelper(unittest.TestCase):
    
    def setUp(self):
        if hasattr(self, 'withFixtures'):
            self.original_functions = []
            self.withFixtures()
    
    def tearDown(self):
        if hasattr(self, 'original_functions'):
            for cls, func in self.original_functions:
                cls.url = func
    
    def useFixture(self, cls, name=None):
        def stubbed_url(self, topic_id, page=None):
            filename = cls.__name__.lower()
            if name:
                filename += '-%s' % name
            if page:
                filename += '-page-%s' % page
            filename += '.xml'
            return os.path.join(os.getcwd(), 'fixtures', filename)
        self.original_functions.append((cls, cls.url))
        cls.url = stubbed_url

    def topic(self):
        # TODO: topic id is ignored in tests - does it work?
        return satisfaction.Topic('1234')


class MissingProductTest(TestHelper):
    
    def test_product_not_found(self):
        with self.assertRaises(satisfaction.ResourceNotFound):
            satisfaction.Product('bad_product_name').title


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
