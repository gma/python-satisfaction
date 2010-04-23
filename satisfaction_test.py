import os
import unittest2 as unittest

import satisfaction


class TestHelper:

    def stub_resource_url(self, cls, fixture):
        def stubbed_url(self, topic_id, page):
            fname = "%s-%s-page-%s.xml" % (cls.__name__.lower(), fixture, page)
            return os.path.join(os.getcwd(), "fixtures", fname)
        self.original_url = cls.url
        cls.url = stubbed_url

    def replace_url_stub(self, cls):
        cls.url = self.original_url

    def topic(self):
        # TODO: topic id is ignored in tests - does it work?
        return satisfaction.Topic("1234")
    

class MissingTopicTest(unittest.TestCase, TestHelper):

    def test_when_topic_doesnt_exist_then_not_found(self):
        with self.assertRaises(satisfaction.ResourceNotFound):
            self.topic().title
    

class TopicWithNoRepliesTest(unittest.TestCase, TestHelper):
    
    def setUp(self):
        self.stub_resource_url(satisfaction.Topic, "without-replies")
        
    def tearDown(self):
        self.replace_url_stub(satisfaction.Topic)
    
    def test_when_topic_exists_then_title_available(self):
        self.assertEqual("Fantastic improvement", self.topic().title)
    
    def test_when_topic_exists_then_content_available(self):
        self.assertIn("Well done!", self.topic().content)
    
    def test_when_topic_has_no_replies_then_no_replies_found(self):
        self.assertEqual(0, self.topic().reply_count)
        self.assertEqual(0, len(list(self.topic().replies)))


class TopicWithRepliesTest(unittest.TestCase, TestHelper):
    
    def setUp(self):
        self.stub_resource_url(satisfaction.Topic, "with-replies")
    
    def tearDown(self):
        self.replace_url_stub(satisfaction.Topic)
    
    def test_when_topic_has_several_replies_then_replies_found(self):
        self.assertEqual(3, self.topic().reply_count)
        self.assertEqual(3, len(list(self.topic().replies)))
    
    def test_when_topic_has_replies_then_topic_not_included_in_replies(self):
        extract_content = lambda reply: reply.content[0]['value']
        reply_messages = map(extract_content, self.topic().replies)
        self.assertNotIn(self.topic().content, reply_messages)


class TopicWithMultiplePagesOfRepliesTest(unittest.TestCase, TestHelper):
    
    def setUp(self):
        self.stub_resource_url(satisfaction.Topic, "with-lots-of-replies")
    
    def tearDown(self):
        self.replace_url_stub(satisfaction.Topic)
    
    def test_when_topic_replies_span_multiple_pages_then_replies_found(self):
        self.assertEqual(95, self.topic().reply_count)
        self.assertEqual(95, len(list(self.topic().replies)))


if __name__ == "__main__":
    unittest.main()
