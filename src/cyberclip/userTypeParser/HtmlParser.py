import re
from bs4 import BeautifulSoup 
from userTypeParser.ParserInterface import ParserInterface


class HtmlParser(ParserInterface):
    """Implementation of ParserInterface for HTML strings.

    Code exemple ::
        a = HtmlParser("dsfsd sdfsdf sdfsdhj j")
        b = HtmlParser("Hello, <b>world</b>")
        print(a.extract(), a.contains())
        print(b.extract(), b.contains())

    Source : https://stackoverflow.com/questions/24856035/how-to-detect-with-python-if-the-string-contains-html-code
    """
    def __init__(self, text: str, parsertype="html"):
        self.text = text
        self.parsertype = "html"
        self.objects = []
        
    def contains(self):
        """Return true if text contains at least one Mitre TTP."""
        if bool(BeautifulSoup(self.text, "html.parser").find()) :
            return True
        else :
            return False
    
    def extract(self):
        """Return the whole text as object."""
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