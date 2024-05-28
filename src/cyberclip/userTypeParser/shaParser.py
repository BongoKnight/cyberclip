import re
try:
    from userTypeParser.ParserInterface import ParserInterface
except:
    from ParserInterface import ParserInterface

class SHA1Parser(ParserInterface):
    """Implementation of ParserInterface for SHA1 strings.

    Code exemple ::
        a = SHA1Parser("ccdf ")
        b = SHA1Parser("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        print(a.extract(), a.contains())
        print(b.extract(), b.contains())

    """
    
    
    def __init__(self, text: str, parsertype="sha1"):
        self.text = text
        self.parsertype = "sha1"
        self.objects = []
        
    def contains(self):
        """Return true if text contains at least one SHA1."""
        if re.search(r"\b([0-9a-f]{40}|[0-9A-F]{40})\b",self.text) :
            return True
        else :
            return False
    
    def extract(self):
        """Return all SHA1 contained in text."""
        SHA1sIter = re.finditer(r"\b([0-9a-f]{40}|[0-9A-F]{40})\b", self.text)
        SHA1s = [SHA1.group() for SHA1 in SHA1sIter]
        self.objects = SHA1s
        return SHA1s

class SHA256Parser(ParserInterface):
    """Implementation of ParserInterface for SHA256 strings.

    Code exemple ::
        a = SHA1Parser("ccdf ")
        b = SHA1Parser("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        print(a.extract(), a.contains())
        print(b.extract(), b.contains())

    """
    
    
    def __init__(self, text: str, parsertype="sha256"):
        self.text = text
        self.parsertype = "sha256"
        self.objects = []
        
    def contains(self):
        """Return true if text contains at least one SHA1."""
        if re.search(r"\b([0-9a-f]{64}|[0-9A-F]{64})\b",self.text) :
            return True
        else :
            return False
    
    def extract(self):
        """Return all SHA1 contained in text."""
        SHA256sIter = re.finditer(r"\b([0-9a-f]{64}|[0-9A-F]{64})\b", self.text)
        SHA256s = [SHA256.group() for SHA256 in SHA256sIter]
        self.objects = SHA256s
        return SHA256s
        
if __name__=="__main__":
    a = SHA1Parser("ccdf ")
    b = SHA1Parser("AAAAAAAAAAAAAAAAAAAAAAAAAAA1AAAAAAAAAAAA ")
    c = SHA1Parser("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    d = SHA1Parser("aaaaaaaaaaaaaAaaaaaaaaaaaaaaaaaaaaaaaaaa")

    print(a.extract(), a.contains())
    print(b.extract(), b.contains())
    print(c.extract(), c.contains())
    print(d.extract(), d.contains())