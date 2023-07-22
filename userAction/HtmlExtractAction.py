try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
from bs4 import BeautifulSoup
import pyhtml2md

class HtmlExtractAction(actionInterface):
    """
    A action module to extract tags from an HTML document.
    Extract paragraph and title by default
    For example :
        `td > b` : Extract all the bold tags inside a table
        `#password` : Extract all the Html tags with the #password id 
    """

    def __init__(self, parsers = {}, supportedType = {"html"}, param_data="h1, h2, h3, h4, h5, p"):
        super().__init__(parsers = parsers, supportedType = supportedType, param_data = param_data)
        self.description = "Extract tags from HTML with CSS selector"

    def execute(self) -> object:
        """Execute the action."""
        self.observables = {}
        html_texts = self.parsers.get("html").extract()
        if html_texts:
            for html_text in html_texts:
                soup = BeautifulSoup(html_text, "html.parser")
                filtered_dom = soup.select(self.param)
                self.observables.update({html_text:filtered_dom})
        return self.observables
    
    def __str__(self):
        """Visual representation of the action"""
        lines = []
        filtered_dom = self.execute()
        for html_text, html_extract in filtered_dom.items():
            for item in html_extract:
                lines.append(str(item))
        return  "\r\n".join(lines)

class HtmlExtractTextAction(actionInterface):
    """
    A action module to extract text from an HTML document.
    Extract paragraph and title by default
    For example :
        `td > b` : Extract all the bold text inside a table
        `#password` : Extract text from all the Html tags with the #password id 
    """

    def __init__(self, parsers = {}, supportedType = {"html"}, param_data="h1, h2, h3, h4, h5, p"):
        super().__init__(parsers = parsers, supportedType = supportedType, param_data = param_data)
        self.description = "Extract text from HTML with CSS selector"

    def execute(self) -> object:
        """Execute the action."""
        self.observables = {}
        html_texts = self.parsers.get("html").extract()
        if html_texts:
            for html_text in html_texts:
                soup = BeautifulSoup(html_text, "html.parser")
                filtered_dom = soup.select(self.param)
                self.observables.update({html_text:filtered_dom})
        return self.observables
    
    def __str__(self):
        """Visual representation of the action"""
        lines = []
        filtered_dom = self.execute()
        for html_text, html_extract in filtered_dom.items():
            for item in html_extract:
                lines.append(str(item.string))
        return  "\r\n".join(lines)

class HtmlToMarkdownAction(actionInterface):
    """
A action module to convert HTML to Markdown.
For example :
    <h1>Dune</h1><p>Fear is the mind-killer.</p><p>Fear is the little-death that brings total obliteration.</p>
    
    Returns :
    # Dune
    Fear is the mind-killer.
    Fear is the little-death that brings total obliteration.
    """

    def __init__(self, parsers = {}, supportedType = {"html"}, param_data="h1, h2, h3, h4, h5, p"):
        super().__init__(parsers = parsers, supportedType = supportedType, param_data = param_data)
        self.description = "Convert HTML to Markdown."

    def execute(self) -> object:
        """Execute the action."""
        self.observables = {}
        html_texts = self.parsers.get("html").extract()
        if html_texts:
            for html_text in html_texts:
                soup = BeautifulSoup(html_text, "html.parser")
                filtered_dom = soup.select(self.param)
                self.observables.update({html_text:filtered_dom})
        return self.observables
    
    def __str__(self):
        """Visual representation of the action"""
        lines = []
        filtered_dom = self.execute()
        for html_text, html_extract in filtered_dom.items():
            for item in html_extract:
                lines.append(str(item))
        return   pyhtml2md.convert("\r\n".join(lines))


if __name__=='__main__':
    from userTypeParser.HtmlParser import HtmlParser
    data = "Hello, <b>world</b>"
    text_parser = HtmlParser(data)
    a = str(HtmlExtractAction({"html":text_parser},["html"], param_data="b"))
    print(a, text_parser.objects)