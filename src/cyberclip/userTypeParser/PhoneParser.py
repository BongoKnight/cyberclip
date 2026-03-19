import re
from userTypeParser.ParserInterface import ParserInterface


class phoneParser(ParserInterface):
    r"""Parse and extract phone numbers from text.

    Phone numbers as 10-digit sequences.

    Regex Pattern:
        ``\b[0-9]{10}\b``

    Defanging Support:
        No. Phone numbers are not typically defanged.

    Example:
        >>> parser = phoneParser("No phone here")
        >>> parser.contains()
        False
        >>> parser = phoneParser("Call 5551234567 or 7001122334")
        >>> parser.contains()
        True
        >>> parser.extract()
        ['5551234567', '7001122334']
    """

    def __init__(self, text: str, parsertype="phone"):
        self.text = text
        self.parsertype = "phone"
        self.objects = []

    def contains(self) -> bool:
        """Check whether the text contains at least one phone number.

        Returns:
            bool: True if at least one 10-digit phone number is found in the text.
        """
        if re.search(r"\b[0-9]{10}\b",self.text) :
            return True
        else :
            return False

    def extract(self) -> list[str]:
        """Extract all phone number instances from the text.

        Returns:
            list[str]: A list of extracted 10-digit phone number values.
        """
        phonesIter = re.finditer(r"\b[0-9]{10}\b", self.text)
        phones = [phone.group() for phone in phonesIter]
        self.objects = phones
        return phones
        
        
if __name__=="__main__":
    a = phoneParser("dqdsdqsd")
    b = phoneParser("70011223344")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())