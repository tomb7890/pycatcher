class Result:
    def __init__(self, success, err_message, value):
        self._success = success
        self._err_message = err_message
        self._value = value

    @property
    def success(self):
        return self._success

    @staticmethod
    def ok(err_message=None, value=None):
        return Result(True, err_message, value)

    @staticmethod
    def fail(err_message=None, value=None):
        return Result(False, err_message, value)
