"""Implementation of ParserInterface for SHA1 strings.

Code exemple ::
    a = SHA1Parser("ccdf ")
    b = SHA1Parser("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())

"""
import logging
import re
from userTypeParser.ParserInterface import ParserInterface


class SHA1Parser(ParserInterface):
    """Parser for SHA1."""
    
    
    def __init__(self, text: str, parsertype="sha1", loglevel = logging.INFO):
        self.text = text
        self.parsertype = "sha1"
        self.objects = []
        self.log = logging.Logger("SHA1")
        ch = logging.StreamHandler()
        ch.setLevel(loglevel)
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %I:%M:%S')
        # add formatter to ch
        ch.setFormatter(formatter)
        self.log.addHandler(ch)
        
    def contains(self):
        """Return true if text contains at least one SHA1."""
        if re.search(r"\b[0-9a-f]{40}\b",self.text) :
            return True
        else :
            return False
    
    def extract(self):
        """Return all SHA1 contained in text."""
        SHA1sIter = re.finditer(r"\b[0-9a-f]{40}\b", self.text)
        SHA1s = [SHA1.group() for SHA1 in SHA1sIter]
        self.objects = SHA1s
        self.log.debug(", ".join(self.objects))
        return SHA1s
        
        
if __name__=="__main__":
    a = SHA1Parser("ccdf ")
    b = SHA1Parser("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())