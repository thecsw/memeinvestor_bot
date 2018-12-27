import praw

class Comment(praw.models.Comment):
    def __init__(self):
        print(123)
