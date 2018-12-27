import sys
sys.path.append('src')

import unittest
from comment_worker import CommentWorker
from mock_comment import Comment

class TestUserInit(unittest.TestCase):
    def setUp(self):
        sm = lambda: []
        self.worker = CommentWorker(sm)

    def test_create(self):
        comment = Comment()
        self.worker(123)

if __name__ == '__main__':
    unittest.main()
