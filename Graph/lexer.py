# Implements a lexer to support a recursive descent
# parser of AGDL.

class State:
    START = 1
    NAME = 2
    NUMBER = 3
    FILE = 4

class Type:
    NAME = 1
    NUMBER = 2
    FILE = 3 

class Lexer(object):

    def __init__(self, filepath):
        with open(filepath, 'r') as file:
            self.lines = file.read().replace('\n', '')
            print len(self.lines)
        self.token = ""
        self.index = 0
        self.state = State.START;
        self.token_type = None
        
        self.advance()

    def advance(self):
        # Do nothing if we've consumed the entire file.
        self.token = ''
        self.token_type = None
        self.state = State.START
        while (self.index < len(self.lines)):
            char = self.lines[self.index]
            self.index = self.index + 1

            # Multiplex based on whether we're at a start of a token
            # or in the middle of constructing a token
            if self.state == State.START:
                if char.isspace():
                    continue
                if char.isalpha():
                    self.state = State.NAME
                    self.token_type = Type.NAME
                elif char.isdigit():
                    self.state = State.NUMBER
                    self.token_type = Type.NUMBER
                elif self.isBracket(char):
                    self.token = char
                    break
                elif char == '"':
                    self.state = State.FILE
                    self.token_type = Type.FILE
                else:
                    raise ValueError("Invalid character " + char + " found.")
            elif self.state == State.NAME:
                if (not char.isalpha()) and (char != '_'):
                    self.index = self.index - 1
                    break
            elif self.state == State.NUMBER:
                if not char.isdigit():
                    self.index = self.index - 1
                    break
            elif self.state == State.FILE:
                if char == '"':
                    self.token = self.token + char
                    break
            
            # Add the character to the token being constructed
            self.token = self.token + char            

    def isBracket(self, char):
        return char == '<' or char == '>' or char == '{' or char == '}'

    def inspect(self, str):
        return self.token == str

    def inspectName(self):
        return self.token_type == Type.NAME

    def inspectNumber(self):
        return self.token_type == Type.NUMBER

    def inspectEOF(self):
        return self.index >= len(self.lines)
    
    def consume(self, str):
        if (self.token == str):
            self.advance()
            return str
        else:
            raise ValueError("Expected token: " + str + " but got token: " + self.token) 

    def consumeTag(self):
        if self.token_type != Type.NAME:
            raise ValueError("Expected an ID name but received token: " + self.token + " instead")
        
        if not self.token.isupper():
            raise ValueError("Expected tag with all capitals but received token: " + self.token)

        token = self.token
        self.advance()
        return token
        
    def consumeName(self):
        if self.token_type != Type.NAME:
            raise ValueError("Expected an ID name but received token: " + self.token + " instead")

        token = self.token
        self.advance()
        return token

    def consumeNumber(self):
        if self.token_type != Type.NUMBER:
            raise ValueError("Expected a number but received token: " + self.token + " instead")
        
        number = self.token
        self.advance()
        return number

    def consumeFile(self):
        if self.token_type != Type.FILE:
            raise ValueError("Expected a filepath but received token: " + self.token + " instead")
        
        file = self.token
        self.advance()
        return file

    def getToken(self):
        return self.token