class InvalidNotificationLevel(ValueError):
    pass


class MessageSizeExceeded(ValueError):
    pass


class APIError(Exception):
    def __init__(self, message, code=0):
        self.code = code
        self.message = message

    def __unicode__(self):
        return str('%s: %s' % (self.message, self.code))


class RateLimited(APIError):
    def __init__(self, message, retry_after=0):
        self.retry_after = retry_after
        super().__init__(message, 429)
