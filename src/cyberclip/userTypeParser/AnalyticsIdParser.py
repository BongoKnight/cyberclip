import re
try:
    from userTypeParser.ParserInterface import ParserInterface
except:
    from ParserInterface import ParserInterface

BASE_REGEX = r"(\b|^)((GT|GTM|G|AW)-[A-Z0-9]{7,15}|UA-\d+-\d+|hjid:\d+|s_gi\([\"'][^\"']+[\"']\))(\b|$)"

class AnalyticsIdParser(ParserInterface):
    r"""Parse and extract analytics tracking IDs from text.

    Supports Google Analytics (UA, GA4, GTM), Adobe Analytics, and Hotjar identifiers.

    Regex Pattern:
        ``(\b|^)((GT|GTM|G|AW)-[A-Z0-9]{7,15}|UA-\d+-\d+|hjid:\d+|s_gi\([\"'][^\"']+[\"']\))(\b|$)``
        (case-insensitive)

    Defanging Support:
        No. Analytics IDs are not typically defanged.

    Example:
        >>> parser = AnalyticsIdParser("No analytics here")
        >>> parser.contains()
        False
        >>> parser = AnalyticsIdParser("Trackers: UA-12345678-1 and G-XXXXXXXXX")
        >>> parser.contains()
        True
        >>> parser.extract()
        ['UA-12345678-1', 'G-XXXXXXXXX']
    """

    def __init__(self, text: str, parsertype="analytics"):
        self.text = text
        self.parsertype = "analytics"
        self.objects = []

    def contains(self) -> bool:
        """Check whether the text contains at least one analytics ID.

        Returns:
            bool: True if at least one analytics ID is found in the text.
        """
        if re.search(BASE_REGEX, self.text, re.IGNORECASE) :
            return True
        else :
            return False

    def extract(self) -> list[str]:
        """Extract all analytics ID instances from the text.

        Returns:
            list[str]: A list of extracted analytics ID values.
        """
        analyticsIter = re.finditer(BASE_REGEX, self.text, re.IGNORECASE)
        analyticsIds = [analytic.group(0) for analytic in analyticsIter]
        self.objects = analyticsIds
        return analyticsIds
        
        
if __name__=="__main__":
    a = AnalyticsIdParser("dsfsd sdfsdf sdfsdhj j")
    b = AnalyticsIdParser("G-XXXXXXXX s_gi('adobeid')")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())