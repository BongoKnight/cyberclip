import re
try:
    from userTypeParser.ParserInterface import ParserInterface
except:
    from ParserInterface import ParserInterface

BASE_REGEX = r"(\b|^)((GT|GTM|G|AW)-[A-Z0-9]{7,15}|UA-\d+-\d+|hjid:\d+|s_gi\([\"'][^\"']+[\"']\))(\b|$)"

class AnalyticsIdParser(ParserInterface):
    """Implementation of ParserInterface for various strings related to analytics.
    Supports Google Analytics, Adobe Analytics and Hotjar.

    Code exemple ::
        a = AnalyticsIdParser("dsfsd sdfsdf sdfsdhj j")
        b = AnalyticsIdParser("G-XXXXXXX")
        print(a.extract(), a.contains())
        print(b.extract(), b.contains())

    """
        
    
    def __init__(self, text: str, parsertype="analytics"):
        self.text = text
        self.parsertype = "analytics"
        self.objects = []
        
    def contains(self):
        """Return true if text contains at least one analytics id."""
        if re.search(BASE_REGEX, self.text, re.IGNORECASE) :
            return True
        else :
            return False


    def extract(self):
        """Return all analytics id contained in text."""
        analyticsIter = re.finditer(BASE_REGEX, self.text, re.IGNORECASE)
        analyticsIds = [analytic.group(0) for analytic in analyticsIter]
        self.objects = analyticsIds
        return analyticsIds
        
        
if __name__=="__main__":
    a = AnalyticsIdParser("dsfsd sdfsdf sdfsdhj j")
    b = AnalyticsIdParser("G-XXXXXXXX s_gi('adobeid')")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())