try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
import requests
from urllib.parse import urlparse

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
        results = {}
        for url in urls:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
                }
                response = requests.get(url, headers=headers)
                results.update({url:response.text})
            except:
                results.update({url:""})
        return results

class UrlToFaviconHashAction(actionInterface):
    """
    A action module to recover mmh3 hash of a favicon for a domain or Url.
    Perform a get request on the URL with a desktop-like User-Agent.
    """

    def __init__(self, parsers = {}, supportedType = {"url","domain"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "Favicon hash (mmh3)"
        
    def execute(self) -> object:
        """Execute the action."""
        results = {}
        self.observables = self.get_observables()
        for url in self.observables.get("url", []):
            try:
                parsed_url = urlparse(url)
                hash = self.get_favicon_hash(parsed_url.netloc, parsed_url.scheme)
                results.update({url:hash})
            except Exception as e:
                results.update({url:f"Error : {str(e)}"})
        for domain in self.observables.get("domain", []):
            try:
                hash = self.get_favicon_hash(domain)
                results.update({domain:hash})
            except:
                results.update({domain:f"Error : {str(e)}"})
        return results

    def get_favicon_hash(self, netloc, scheme : str = "http") -> str:
        import mmh3
        import codecs
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
        }
        response = requests.get(f"{scheme}://{netloc}/favicon.ico", headers=headers)
        favicon = codecs.encode(response.content, 'base64')
        hash = mmh3.hash(favicon)
        return hash


    def __str__(self):
        """Visual representation of the action"""
        lines = []
        hashes = self.execute()
        for observable, hash in hashes.items():
            lines.append(f"{observable}\t{hash}")
        return  "\r\n".join(lines)

if __name__=='__main__':
    from userTypeParser.HtmlParser import HtmlParser
    data = "Hello, <b>world</b>"
    text_parser = HtmlParser(data)
    a = str(UrlToHtmlAction({"html":text_parser},["html"], param_data="b"))
    print(a, text_parser.objects)