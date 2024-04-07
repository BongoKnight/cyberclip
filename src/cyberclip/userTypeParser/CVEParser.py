import re
try:
    from userTypeParser.ParserInterface import ParserInterface
except:
    from ParserInterface import ParserInterface


class CVEParser(ParserInterface):
    """Implementation of ParserInterface for CVE strings.

    Code exemple ::
        a = CVEParser("dsfsd sdfsdf sdfsdhj j")
        b = CVEParser("CVE-2024-22252")
        print(a.extract(), a.contains())
        print(b.extract(), b.contains())

    """
        
    
    def __init__(self, text: str, parsertype="cve"):
        self.text = text
        self.parsertype = "cve"
        self.objects = []
        
    def contains(self):
        """Return true if text contains at least one CVE."""
        if re.search(r"\bCVE-\d{4}-\d{3,5}\b",self.text, re.IGNORECASE) :
            return True
        else :
            return False
    
    def extract(self):
        """Return all CVE contained in text."""
        cveIter = re.finditer(r"\bCVE-\d{4}-\d{3,5}\b",self.text, re.IGNORECASE)
        cves = [cve.group() for cve in cveIter]
        self.objects = cves
        return cves
        
        
if __name__=="__main__":
    a = CVEParser("dsfsd sdfsdf sdfsdhj j")
    b = CVEParser("CVE-2024-22252")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())