import re
from userTypeParser.ParserInterface import ParserInterface


class asnumParser(ParserInterface):
    """Implementation of ParserInterface for asnum strings.

    Code exemple ::
        a = asnumParser("dqsdq. fdsf")
        b = asnumParser("AS2456")
        print(a.extract(), a.contains())
        print(b.extract(), b.contains())
    """
    
    
    def __init__(self, text: str, parsertype="asnum"):
        self.text = text
        self.parsertype = "asnum"
        self.objects = []
        
    def contains(self):
        """
        Return True if text contains at least one asnum.
        """
        if re.search(r"\bAS\d+\b", self.text, re.IGNORECASE) :
            return True
        else :
            return False
    
    def extract(self):
        """
        Return all asnum contained in text.
        
        Return:
            asmums (list(str)): A list of as number with the following format : AS<Num> or as<num>
        """
        asnumsIter = re.finditer(r"\bAS\d+\b", self.text, re.IGNORECASE)
        asnums = [asnum.group().replace("[.]",".") for asnum in asnumsIter]
        self.objects = asnums
        return asnums
        
        
if __name__=="__main__":
    a = asnumParser("dqsdq. fdsf")
    b = asnumParser("AS2589")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())