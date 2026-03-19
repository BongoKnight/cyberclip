import re
from userTypeParser.ParserInterface import ParserInterface


class asnumParser(ParserInterface):
    r"""Parse and extract Autonomous System Numbers from text.

    AS Numbers in format AS#### (e.g., AS15169 for Google).

    Regex Pattern:
        ``\bAS\d+\b`` (case-insensitive)

    Defanging Support:
        No. AS numbers are not typically defanged.

    Example:
        >>> parser = asnumParser("No AS number here")
        >>> parser.contains()
        False
        >>> parser = asnumParser("Networks: AS15169 and as13335")
        >>> parser.contains()
        True
        >>> parser.extract()
        ['AS15169', 'as13335']
    """

    def __init__(self, text: str, parsertype="asnum"):
        self.text = text
        self.parsertype = "asnum"
        self.objects = []

    def contains(self) -> bool:
        """Check whether the text contains at least one AS number.

        Returns:
            bool: True if at least one AS number is found in the text.
        """
        if re.search(r"\bAS\d+\b", self.text, re.IGNORECASE) :
            return True
        else :
            return False

    def extract(self) -> list[str]:
        """Extract all AS number instances from the text.

        Returns:
            list[str]: A list of extracted AS number values (format: AS#### or as####).
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