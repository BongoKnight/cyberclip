try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
import requests

class UrlToHtmlAction(actionInterface):
    """
    A action module to recover HTML from an URL.
    Perform a get request on the URL with a desktop-like User-Agent.
    """

    def __init__(self, parsers = {}, supportedType = {"url"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "URL to HTML"
        
    def execute(self) -> object:
        """Execute the action."""
        urls = set(self.parsers.get("url").extract())
        for url in urls:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
                }
                response = requests.get(url, headers=headers)
                self.observables.update({url:response.text})
            except:
                self.observables.update({url:""})
        return self.observables
    
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