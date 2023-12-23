"""Implementation of ParserInterface for URL strings.

Code exemple ::
    a = URLParser("dsfsd sdfsdf sdfsdhj j")
    b = URLParser("http://youpi.google.com/test.php?q=3Rte")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())

"""
import re
from userTypeParser.ParserInterface import ParserInterface


class MitreParser(ParserInterface):
    """Parser for Mitre Att&ck TTP."""
    
    
    def __init__(self, text: str, parsertype="mitre"):
        self.text = text
        self.parsertype = "mitre"
        self.objects = []
        
    def contains(self):
        """Return true if text contains at least one Mitre TTP."""
        if re.search(r"\bT\d{4}(\.\d{3})?\b",self.text) :
            return True
        else :
            return False
    
    def extract(self):
        """Return all TTP contained in text."""
        MitreIter = re.finditer(r"\bT\d{4}(\.\d{3})?\b", self.text)
        MitreTTPs = [TTP.group() for TTP in MitreIter]
        self.objects = MitreTTPs
        return MitreTTPs
        
        
if __name__=="__main__":
    a = MitreParser("dsfsd sdfsdf sdfsdhj j")
    b = MitreParser("T1012, T1016, T1027, T1033, T1059, T1059.001, T1059.005, T1082,T1083, T1087, T1095, T1112, T1140, T1547.001, T1547.009, T1560, T1566.001).")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())