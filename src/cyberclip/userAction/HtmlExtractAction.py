try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
from bs4 import BeautifulSoup

class HtmlExtractAction(actionInterface):
    """A action module to extract tags from an HTML document.  
    Extract paragraph and title by default  
    For example :

    - `td > b` : Extract all the bold tags inside a table
    - `#password` : Extract all the Html tags where the id property value is `password` 
    """

    def __init__(self, parsers = {}, supportedType = {"html"}, complex_param={"CSS selectors":{"value":["p"], "type":"tags"}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param= complex_param)
        self.description = "Extract tags from HTML with CSS selector"

    def execute(self) -> object:
        html_texts = self.get_observables().get("html")
        self.results = {}
        if html_texts:
            for html_text in html_texts:
                selected = {}
                soup = BeautifulSoup(html_text, "html.parser")
                filters = self.get_param_value("CSS selectors")
                for css_selector in filters:
                    filtered_dom = soup.select(css_selector)
                    selected.update({css_selector:filtered_dom})
                self.results.update({html_text:selected})
        return self.results
    
    def __str__(self):
        """Visual representation of the action."""
        lines = []
        filtered_dom = self.execute()
        for html_text, html_extract in filtered_dom.items():
            for item in html_extract.values():
                for html_fragment in item:
                    lines.append(str(html_fragment))
        return  "\r\n".join(lines)

class HtmlExtractTextAction(actionInterface):
    """A action module to extract text from an HTML document.  
    Extract paragraph and title by default  
    For example :  

    - `td > b` : Extract all the bold text inside a table
    - `#password` : Extract text from all the Html tags where the id property value is `password`
    """

    def __init__(self, parsers = {}, supportedType = {"html"}, complex_param = {"CSS selectors":{"value":["p"], "type":"tags"}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param = complex_param)
        self.description = "Extract text from HTML with CSS selector"

    def execute(self) -> object:
        self.results = {}
        html_texts = self.get_observables().get("html")
        if html_texts:
            for html_text in html_texts:
                selected = {}
                soup = BeautifulSoup(html_text, "html.parser")
                filters = self.get_param_value("CSS selectors")
                for css_selector in filters:
                    filtered_dom = soup.select(css_selector)
                    selected.update({css_selector:filtered_dom})
                self.results.update({html_text:selected})
        return self.results
    
    def __str__(self):
        lines = []
        filtered_dom = self.execute()
        for html_text, html_extract in filtered_dom.items():
            for item in html_extract.values():
                for html_fragment in item:
                    lines.append(html_fragment.get_text())
        return  "\r\n".join(lines)



if __name__=='__main__':
    from userTypeParser.HtmlParser import HtmlParser
    data = "Hello, <b>world</b>"
    text_parser = HtmlParser(data)
    a = str(HtmlExtractAction({"html":text_parser},["html"], complex_param={"CSS selectors":{"value":["b"], "type":"tags"}}))
    b = str(HtmlExtractTextAction({"html":text_parser},["html"], complex_param={"CSS selectors":{"value":["b"], "type":"tags"}}))

    print(a, b, text_parser.objects)