import re
from userTypeParser.ParserInterface import ParserInterface


class phoneParser(ParserInterface):
    """Implementation of ParserInterface for phone strings.

    Code exemple ::
        a = phoneParser("dqdsdqsd")
        b = phoneParser("70011223344")
        print(a.extract(), a.contains())
        print(b.extract(), b.contains())

    """
    
    
    def __init__(self, text: str, parsertype="phone"):
        self.text = text
        self.parsertype = "phone"
        self.objects = []
        
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
        return phones
        
        
if __name__=="__main__":
    a = phoneParser("dqdsdqsd")
    b = phoneParser("70011223344")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())