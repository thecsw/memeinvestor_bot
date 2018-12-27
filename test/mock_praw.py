import time

class Redditor():
    def __init__(self, name):
        self.name = name

class Comment():
    def __init__(self, author_name, body):
        self.is_root = False
        self.author = Redditor(author_name)
        self.created_utc = time.time()
        self.body = body
        self.replies = []

    def reply_wrap(self, body):
        self.replies.append(body)
