"""Implementation of ParserInterface for URL strings.

Code exemple ::
    a = URLParser("dsfsd sdfsdf sdfsdhj j")
    b = URLParser("http://youpi.google.com/test.php?q=3Rte")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())

"""
import logging
import re
from userTypeParser.ParserInterface import ParserInterface


class URLParser(ParserInterface):
    """Parser for URL."""
    
    
    def __init__(self, text: str, parsertype="url", loglevel = logging.INFO):
        self.text = text
        self.parsertype = "url"
        self.objects = []
        self.log = logging.Logger("URL")
        ch = logging.StreamHandler()
        ch.setLevel(loglevel)
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %I:%M:%S')
        # add formatter to ch
        ch.setFormatter(formatter)
        self.log.addHandler(ch)
        
    def contains(self):
        """Return true if text contains at least one URL."""
        if re.search(r"\b(?:(?:https?|ftp|file):\/\/|www\.|ftp\.)(?:([\-a-zA-Z0-9+&@#\/%=~_|$?!:,.]*)|[a-z\-A-Z0-9+&@#\/%=~_|$?!:,.])*(?:([a-z\-A-Z0-9+&@#\/%=~_|$?!:,.]*)|[a-zA-Z0-9\-+&@#\/%=~_|$])",self.text) :
            return True
        else :
            return False
    
    def extract(self):
        """Return all URL contained in text."""
        URLsIter = re.finditer(r"\b(?:(?:https?|ftp|file):\/\/|www\.|ftp\.)(?:([\-a-zA-Z0-9+&@#\/%=~_|$?!:,.]*)|[a-z\-A-Z0-9+&@#\/%=~_|$?!:,.])*(?:([a-z\-A-Z0-9+&@#\/%=~_|$?!:,.]*)|[a-zA-Z0-9\-+&@#\/%=~_|$])", self.text)
        URLs = [URL.group() for URL in URLsIter]
        self.objects = URLs
        self.log.debug(", ".join(self.objects))
        return URLs
        
        
if __name__=="__main__":
    a = URLParser("dsfsd sdfsdf sdfsdhj j")
    b = URLParser("http://youpi.google.com/test.php?q=3Rte")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())