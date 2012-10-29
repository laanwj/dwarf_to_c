from io import StringIO


class ParseError(Exception):
    pass


class ParseStreamError(ParseError):
    def __init__(self, msg, s):
        ParseError.__init__(self, '%s: %s@%d' % (msg, s.getvalue(), s.pos))


class ParseStream(StringIO):
    def __init__(self, string):
        StringIO.__init__(self, string)
    
    def char(self):
        return self.read(1)
    
    def back(self, n=1):
        self.seek(self.pos - n)
    
    def skip(self, n=1):
        self.seek(self.pos + n)
    
    def peek(self):
        c = self.read(1)
        self.back()
        return c
    
    def next_char(self, rc):
        c = self.read(1)
        if c != rc:
            self.back()
            return False
        return True
    
    def expect_char(self, expected):
        c = self.read(1)
        if c != expected:
            raise ParseStreamError('Expected "%c", got "%c"' % (expected, c), self)
    
    def check_limit(self):
        if self.pos >= self.len:
            raise ParseStreamError('Unexpected end of string', self)
        return True
