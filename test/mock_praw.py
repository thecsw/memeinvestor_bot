import time

class Redditor():
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

class Submission():
    def __init__(self, id, author=Redditor('submitter'), ups=100):
        self.id = id
        self.author = author
        self.ups = ups

    def __str__(self):
        return self.id

class Comment():
    def __init__(self, author_name, body, submission=None):
        self.is_root = False
        self.author = Redditor(author_name)
        self.created_utc = time.time()
        self.body = body
        self.replies = []
        self.submission = submission

    def __str__(self):
        return '123'

    def reply_wrap(self, body):
        self.replies.append(body)
