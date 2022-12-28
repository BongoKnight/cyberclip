"""Implementation of ParserInterface for text. If the text is not the blank string return True. Allow to make transforms on a text.

Code exemple ::
    a = TextParser("1.3.4.5")
    b = TextParser("toto")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())

"""
import re
from userTypeParser.ParserInterface import ParserInterface

class TextParser(ParserInterface):
    """Parser for text."""
    
    def __init__(self, text, parsertype="text"):
        self.text = text
        self.parsertype = "text"
        self.objects = []

        
    def contains(self):
        """Return true if text is not blank."""
        return bool(self.text)

    
    def extract(self):
        """Return the whole text as object."""
        self.objects = [self.text]
        return self.objects
        
        
if __name__=="__main__":
    a = TextParser("1.3.4.5")
    b = TextParser("toto")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())