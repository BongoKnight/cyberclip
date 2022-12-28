"""Implementation of ParserInterface for phone strings.

Code exemple ::
    a = phoneParser("dqdsdqsd")
    b = phoneParser("70011223344")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())

"""
import logging
import re
from userTypeParser.ParserInterface import ParserInterface


class phoneParser(ParserInterface):
    """Parser for phone."""
    
    
    def __init__(self, text: str, parsertype="phone", loglevel = logging.INFO):
        self.text = text
        self.parsertype = "phone"
        self.objects = []
        self.log = logging.Logger("phone")
        ch = logging.StreamHandler()
        ch.setLevel(loglevel)
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %I:%M:%S')
        # add formatter to ch
        ch.setFormatter(formatter)
        self.log.addHandler(ch)
        
    def contains(self):
        """Return true if text contains at least one phone."""
        if re.search(r"\b[0-9]{10}\b",self.text) :
            return True
        else :
            return False
    
    def extract(self):
        """Return all phone contained in text."""
        phonesIter = re.finditer(r"\b[0-9]{10}\b", self.text)
        phones = [phone.group() for phone in phonesIter]
        self.objects = phones
        self.log.debug(", ".join(self.objects))
        return phones
        
        
if __name__=="__main__":
    a = phoneParser("dqdsdqsd")
    b = phoneParser("70011223344")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())