'''

Library errors

'''

class LoxError(Exception):
    def __init__(self,reason):
        self.value = reason
    def __str__(self):
        return self.value

class LoxFatal(Exception):
    def __init__(self,reason):
        self.value = reason
    def __str__(self):
        return self.value





