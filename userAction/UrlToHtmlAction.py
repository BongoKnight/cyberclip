try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
import requests

class UrlToHtmlAction(actionInterface):
    """
    A action module to recover HTML from an URL.
    """
    def __init__(self, parsers = {}, supportedType = {"url"}, param_data=""):
        self.supportedType = supportedType
        self.parsers = parsers
        self.description = "URL to HTML"
        self.results = {}
        self.param = param_data

        
    def execute(self) -> object:
        """Execute the action."""
        self.results = {}
        urls = set(self.parsers.get("url").extract())
        for url in urls:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
                }
                response = requests.get(url, headers=headers)
                self.results.update({url:response.text})
            except:
                self.results.update({url:""})
        return self.results
    
    def __str__(self):
        """Visual representation of the action"""
        lines = []
        htmls = self.execute()
        for url, html in htmls.items():
            lines.append(f"#{url}\r\n{str(html)}")
        return  "\r\n".join(lines)

if __name__=='__main__':
    from userTypeParser.HtmlParser import HtmlParser
    data = "Hello, <b>world</b>"
    text_parser = HtmlParser(data)
    a = str(UrlToHtmlAction({"html":text_parser},["html"], param_data="b"))
    print(a, text_parser.objects)