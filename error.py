class BadUserInputError(BaseException):
    def __init__(self, message):
        self._msg = message

    def msg(self):
        return self._msg
        
    
