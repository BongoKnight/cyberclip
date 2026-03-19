import re
from userTypeParser.ParserInterface import ParserInterface


class mailParser(ParserInterface):
    r"""Parse and extract email addresses from text.

    Email addresses in standard user@domain format.

    Regex Pattern:
        ``\b[^\s@=;\)\(\[\]]+@[^\s@,=\)\(\[\]]+\.[^\s@,=\)\(\[\]]+\b``

    Defanging Support:
        No. Email addresses are not typically defanged.

    Example:
        >>> parser = mailParser("No email here")
        >>> parser.contains()
        False
        >>> parser = mailParser("Contact: user@example.com or admin@test.org")
        >>> parser.contains()
        True
        >>> parser.extract()
        ['user@example.com', 'admin@test.org']
    """

    def __init__(self, text: str, parsertype="mail"):
        self.text = text
        self.parsertype = "mail"
        self.objects = []

    def contains(self) -> bool:
        """Check whether the text contains at least one email address.

        Returns:
            bool: True if at least one email address is found in the text.
        """
        if re.search(r"\b[^\s@=;\)\(\[\]]+@[^\s@,=\)\(\[\]]+\.[^\s@,=\)\(\[\]]+\b",self.text) :
            return True
        else :
            return False

    def extract(self) -> list[str]:
        """Extract all email address instances from the text.

        Returns:
            list[str]: A list of extracted email address values.
        """
        mailsIter = re.finditer(r"\b[^\s@=;\)\(\[\])]+@[^\s@,=\)\(\[\]]+\.[^\s@,=\)\(\[\]]+\b", self.text)
        mails = [mail.group() for mail in mailsIter]
        self.objects = mails
        return mails
        
        
if __name__=="__main__":
    a = mailParser("1.3.4.5")
    b = mailParser("toto@domain.com")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())