"""Implementation of ParserInterface for md5 strings.

Code exemple ::
    a = md5Parser("1.3.4.5")
    b = md5Parser("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())

"""
import logging
import re
from userTypeParser.ParserInterface import ParserInterface


class md5Parser(ParserInterface):
    """Parser for md5."""
    
    
    def __init__(self, text: str, parsertype="md5", loglevel = logging.INFO):
        self.text = text
        self.parsertype = "md5"
        self.objects = []
        self.log = logging.Logger("md5")
        ch = logging.StreamHandler()
        ch.setLevel(loglevel)
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %I:%M:%S')
        # add formatter to ch
        ch.setFormatter(formatter)
        self.log.addHandler(ch)
        
    def contains(self):
        """Return true if text contains at least one md5."""
        if re.search(r"\b[0-9a-f]{32}\b",self.text) :
            return True
        else :
            return False
    
    def extract(self):
        """Return all md5 contained in text."""
        md5sIter = re.finditer(r"\b[0-9a-f]{32}\b", self.text)
        md5s = [md5.group() for md5 in md5sIter]
        self.objects = md5s
        self.log.debug(", ".join(self.objects))
        return md5s
        
        
if __name__=="__main__":
    a = md5Parser("1.3.4.5")
    b = md5Parser("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())
