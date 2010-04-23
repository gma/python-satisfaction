import os
import unittest2 as unittest

import satisfaction


def fixture(cls, name):
    def wrapper(test):
        def test_with_fixture(*args):
            def stubbed_url(self, topic_id):
                fixture = "%s-%s.xml" % (cls.__name__.lower(), name)
                return os.path.join(os.getcwd(), "fixtures", fixture)

            try:
                original_url = cls.url
                cls.url = stubbed_url
                return test(*args)
            finally:
                cls.url = original_url
        return test_with_fixture
    return wrapper


class TopicTest(unittest.TestCase):
    
    def topic(self, topic_id="409678"):
        return satisfaction.Topic(topic_id)
    
    def test_when_topic_doesnt_exist_then_not_found(self):
        with self.assertRaises(satisfaction.ResourceNotFound):
            self.topic("bad-id").title
    
    @fixture(satisfaction.Topic, "without-replies")
    def test_when_topic_exists_then_title_available(self):
        self.assertEqual("Fantastic improvement", self.topic().title)
    
    @fixture(satisfaction.Topic, "without-replies")
    def test_when_topic_exists_then_content_available(self):
        self.assertIn("Well done!", self.topic().content)
    
    @fixture(satisfaction.Topic, "without-replies")
    def test_when_topic_has_no_replies_then_no_replies_found(self):
        self.assertEqual(0, self.topic().reply_count)
        self.assertEqual(0, len(list(self.topic().replies)))
    
    @fixture(satisfaction.Topic, "with-replies")
    def test_when_topic_has_several_replies_then_replies_found(self):
        self.assertEqual(3, self.topic().reply_count)
        self.assertEqual(3, len(list(self.topic().replies)))
    
    @unittest.skip("pending refactoring to iterator")
    @fixture(satisfaction.Topic, "with-lots-of-replies-page-4")
    @fixture(satisfaction.Topic, "with-lots-of-replies-page-3")
    @fixture(satisfaction.Topic, "with-lots-of-replies-page-2")
    @fixture(satisfaction.Topic, "with-lots-of-replies-page-1")
    def test_when_topic_has_lots_of_replies_then_replies_found(self):
        # self.assertEqual(95, self.topic().reply_count)
        self.assertEqual(95, len(list(self.topic().replies)))
    
    @unittest.skip("can't compare content of topic to reply yet")
    def test_when_topic_has_replies_then_topic_not_included_in_replies(self):
        pass


if __name__ == "__main__":
    unittest.main()
