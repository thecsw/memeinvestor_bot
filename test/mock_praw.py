import time

class Redditor():
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

class Submission(str):
    def __new__(cls, submission_id, *args):
        return super().__new__(cls, submission_id)

    def __init__(self, submission_id, author=Redditor('submitter'), ups=100):
        self.id = submission_id
        self.author = author
        self.ups = ups

    def __str__(self):
        return self.id

class Comment(str):
    def __new__(cls, comment_id, *args):
        return super().__new__(cls, comment_id)

    def __init__(self, comment_id, author_name, body, submission):
        self.id = comment_id
        self.is_root = False
        self.author = Redditor(author_name)
        self.created_utc = time.time()
        self.body = body
        self.replies = []
        self.submission = submission

    def reply_wrap(self, body):
        self.replies.append(body)
