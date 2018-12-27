import time

class Redditor():
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

class Submission(str):
    def __new__(cls, id, *args):
        return super().__new__(cls, id)

    def __init__(self, id, author=Redditor('submitter'), ups=100):
        self.id = id
        self.author = author
        self.ups = ups

    def __str__(self):
        return self.id

class Comment(str):
    def __new__(cls, id, *args):
        return super().__new__(cls, id)

    def __init__(self, id, author_name, body, submission):
        self.id = id
        self.is_root = False
        self.author = Redditor(author_name)
        self.created_utc = time.time()
        self.body = body
        self.replies = []
        self.submission = submission

    def reply_wrap(self, body):
        self.replies.append(body)
