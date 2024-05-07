import re
from userTypeParser.ParserInterface import ParserInterface


class md5Parser(ParserInterface):
    """Implementation of ParserInterface for md5 strings.

    Code exemple ::
        a = md5Parser("1.3.4.5")
        b = md5Parser("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        print(a.extract(), a.contains())
        print(b.extract(), b.contains())

    """
    
    def __init__(self, text: str, parsertype="md5"):
        self.text = text
        self.parsertype = "md5"
        self.objects = []
        
    def contains(self):
        """Return true if text contains at least one md5."""
        if re.search(r"\b([0-9a-f]{32}|[0-9A-F]{32})\b",self.text) :
            return True
        else :
            return False
    
    def extract(self):
        """Return all md5 contained in text."""
        md5sIter = re.finditer(r"\b([0-9a-f]{32}|[0-9A-F]{32})\b", self.text)
        md5s = [md5.group(1) for md5 in md5sIter]
        self.objects = md5s
        return md5s
        
        
if __name__=="__main__":
    a = md5Parser("1.3.4.5")
    b = md5Parser("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())
