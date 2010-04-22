import unittest2 as unittest

import satisfaction


class TopicTest(unittest.TestCase):
    
    def topic(self, topic_id="409678"):
        return satisfaction.Topic(topic_id)
        
    def test_when_topic_doesnt_exist_then_not_found(self):
        with self.assertRaises(satisfaction.ResourceNotFound):
            self.topic("bad-id").title
    
    def test_when_topic_exists_then_title_available(self):
        self.assertEqual(self.topic().title, "Fantastic improvement")
    
    def test_when_topic_exists_then_content_available(self):
        self.assertIn("Well done!", self.topic().content)
    
    def test_when_topic_has_no_replies_then_no_replies_returned(self):
        self.assertEqual(0, self.topic().reply_count)


if __name__ == '__main__':
    unittest.main()
