
class NoteNotFound(Exception):
    def __init__(self, msg, *args, **kwargs):
        self.msg = msg
        super(*args, **kwargs)
    

