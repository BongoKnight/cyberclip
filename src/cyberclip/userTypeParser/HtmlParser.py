import re
from bs4 import BeautifulSoup 
from userTypeParser.ParserInterface import ParserInterface


class HtmlParser(ParserInterface):
    """Parse and extract HTML content from text.

    HTML content detected using BeautifulSoup parsing.

    Regex Pattern:
        Not regex-based. Uses BeautifulSoup HTML parser.

    Defanging Support:
        No. HTML content is not typically defanged.

    Example:
        >>> parser = HtmlParser("No HTML here")
        >>> parser.contains()
        False
        >>> parser = HtmlParser("Hello, <b>world</b>")
        >>> parser.contains()
        True
        >>> parser.extract()
        ['Hello, <b>world</b>']

    Source:
        https://stackoverflow.com/questions/24856035/how-to-detect-with-python-if-the-string-contains-html-code
    """
    def __init__(self, text: str, parsertype="html"):
        self.text = text
        self.parsertype = "html"
        self.objects = []

    def contains(self) -> bool:
        """Check whether the text contains at least one HTML element.

        Returns:
            bool: True if at least one HTML element is found in the text.
        """
        if bool(BeautifulSoup(self.text, "html.parser").find()) :
            return True
        else :
            return False

    def extract(self) -> list[str]:
        """Extract all HTML content from the text.

        Returns the entire text as HTML if it contains HTML elements.

        Returns:
            list[str]: A list containing the extracted HTML content.
        """
        html_entries = BeautifulSoup(self.text, "html.parser").select("html")
        if len(html_entries)>1:
            self.objects = [str(html_entry) for html_entry in html_entries]
        else:
            self.objects = [self.text]
        return self.objects
        
        
if __name__=="__main__":
    a = HtmlParser("dsfsd sdfsdf sdfsdhj j")
    b = HtmlParser("Hello, <b>world</b>")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())