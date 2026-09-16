import re
from userTypeParser.ParserInterface import ParserInterface


class telegramTokenParser(ParserInterface):
    r"""Parse and extract Telegram Token from text.

    Regex Pattern:
        ``\b([0-9]{8,10}):[A-za-z0-9]{35}\b`` (case-insensitive)

    Example:
        >>> parser = telegramTokenParser("No token here")
        >>> parser.contains()
        False
        >>> parser = telegramTokenParser("8775192674:AAFEL4hignTrdW38vtTfdkTeXXtpsaqE9Dw")
        >>> parser.contains()
        True
    """

    def __init__(self, text: str, parsertype="telegram"):
        self.text = text
        self.parsertype = "telegram"
        self.objects = []

    def contains(self) -> bool:
        """Check whether the text contains at least one telegram token.

        Returns:
            bool: True if at least one telegram token is found in the text.
        """
        if re.search(r"\b([0-9]{8,10}):[A-za-z0-9]{35}\b", self.text, re.IGNORECASE):
            return True
        else:
            return False

    def extract(self) -> list[str]:
        """Extract all Telegram token instances from the text.

        Returns:
            list[str]: A list of extracted Telegram token values.
        """
        asnumsIter = re.finditer(r"\b([0-9]{8,10}):[A-za-z0-9]{35}\b", self.text, re.IGNORECASE)
        asnums = [asnum.group().replace("[.]", ".") for asnum in asnumsIter]
        self.objects = asnums
        return asnums


if __name__ == "__main__":
    a = telegramTokenParser("dqsdq. fdsf")
    b = telegramTokenParser("8775192674:AAFEL4hignTrdW38vtTfdkTeXXtpsaqE9Dw")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())
