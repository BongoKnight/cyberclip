try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
from bs4 import BeautifulSoup

class HtmlExtractAction(actionInterface):
    """
    A action module to extract data from an HTML document.
    For example :
        `td > b` : Extract all the bold text inside a table
        `#password` : Extract all the HtmlTags with the #password id 
    """

    def __init__(self, parsers = {}, supportedType = {"html"}, param_data="html"):
        self.supportedType = supportedType
        self.parsers = parsers
        self.description = "Extract from HTML with CSS selector"
        self.results = {}
        self.param = param_data

        
    def execute(self) -> object:
        """Execute the action."""
        self.results = {}
        html_texts = self.parsers.get("html").extract()
        if html_texts:
            for html_text in html_texts:
                soup = BeautifulSoup(html_text, "html.parser")
                filtered_dom = soup.select(self.param)
                self.results.update({html_text:filtered_dom})
        return self.results
    
    def __str__(self):
        """Visual representation of the action"""
        lines = []
        filtered_dom = self.execute()
        for html_text, html_extract in filtered_dom.items():
            for item in html_extract:
                lines.append(str(item))
        return  "\r\n".join(lines)

if __name__=='__main__':
    from userTypeParser.HtmlParser import HtmlParser
    data = "Hello, <b>world</b>"
    text_parser = HtmlParser(data)
    a = str(HtmlExtractAction({"html":text_parser},["html"], param_data="b"))
    print(a, text_parser.objects)