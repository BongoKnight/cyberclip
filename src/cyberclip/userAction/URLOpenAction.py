try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
import os

class URLOpenAction(actionInterface):
    """Open all the URL with the default browser."""
    
    def __init__(self, parsers ={}, supportedType = {"url"}):
        super().__init__(parsers = parsers, supportedType = supportedType)       
        self.description = "Open URL in browser."
        
    def execute(self) -> object:
        lines = []
        self.observables = {}
        self.observables = self.get_observables()
        if self.observables.get("url"):
            for url in set(self.observables.get("url")):
                lines.append(f"Openning {url}")
                os.startfile(f"{url}")
        return "\n".join([i for i in lines])
    
    def __str__(self):
        return self.execute()

if __name__=='__main__':
    from userTypeParser.URLParser import URLParser

    data = "127.0.0.1, https://google.com/ user@domain.com aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    url_parser = URLParser(data)
    a = str(URLOpenAction({"url":url_parser},["url"]))