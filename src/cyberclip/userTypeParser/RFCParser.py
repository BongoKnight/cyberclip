import re
try:
    from userTypeParser.ParserInterface import ParserInterface
except:
    from ParserInterface import ParserInterface

RFC_REGEX = r"\bRFC\s?\d+\b"

class RFCParser(ParserInterface):
    """Implementation of ParserInterface to detect mention of RFC (Request for comment).

    Code exemple ::
        a = RFCParser("dsfsd sdfsdf sdfsdhj j")
        b = RFCParser("RFC 2646")
        print(a.extract(), a.contains())
        print(b.extract(), b.contains())

    """
        
    
    def __init__(self, text: str, parsertype="rfc"):
        self.text = text
        self.parsertype = "rfc"
        self.objects = []
        
    def contains(self):
        """Return true if text contains at least one RFC."""
        if re.search(RFC_REGEX, self.text, re.IGNORECASE) :
            return True
        else :
            return False
    
    def extract(self):
        """Return all RFC contained in text."""
        rfcIter = re.finditer(RFC_REGEX, self.text, re.IGNORECASE)
        rfcs = [rfc.group() for rfc in rfcIter]
        self.objects = rfcs
        return rfcs
        
        
if __name__=="__main__":
    a = RFCParser("dsfsd sdfsdf sdfsdhj j")
    b = RFCParser("RFC 2646")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())