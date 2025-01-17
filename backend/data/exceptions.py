class BadRequest(BaseException):
    def __init__(self, message):
        self.message = message


class Missing(BaseException):
    def __init__(self, message):
        self.message = message
