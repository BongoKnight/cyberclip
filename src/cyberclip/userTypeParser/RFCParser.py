import re
try:
    from userTypeParser.ParserInterface import ParserInterface
except:
    from ParserInterface import ParserInterface

RFC_REGEX = r"\bRFC\s?\d+\b"

class RFCParser(ParserInterface):
    r"""Parse and extract RFC (Request for Comments) document numbers from text.

    RFC identifiers in format "RFC ####" or "RFC####" (case-insensitive).

    Regex Pattern:
        ``\bRFC\s?\d+\b`` (case-insensitive)

    Defanging Support:
        No. RFC identifiers are not typically defanged.

    Example:
        >>> parser = RFCParser("No RFC here")
        >>> parser.contains()
        False
        >>> parser = RFCParser("See RFC 2646 and rfc9110 for details")
        >>> parser.contains()
        True
        >>> parser.extract()
        ['RFC 2646', 'rfc9110']
    """

    def __init__(self, text: str, parsertype="rfc"):
        self.text = text
        self.parsertype = "rfc"
        self.objects = []

    def contains(self) -> bool:
        """Check whether the text contains at least one RFC identifier.

        Returns:
            bool: True if at least one RFC identifier is found in the text.
        """
        if re.search(RFC_REGEX, self.text, re.IGNORECASE) :
            return True
        else :
            return False

    def extract(self) -> list[str]:
        """Extract all RFC identifier instances from the text.

        Returns:
            list[str]: A list of extracted RFC identifier values.
        """
        rfcIter = re.finditer(RFC_REGEX, self.text, re.IGNORECASE)
        rfcs = [rfc.group() for rfc in rfcIter]
        self.objects = rfcs
        return rfcs
        
        
if __name__=="__main__":
    a = RFCParser("dsfsd sdfsdf sdfsdhj j")
    b = RFCParser("RFC 2646")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())