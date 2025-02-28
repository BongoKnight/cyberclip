try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
import requests
from urllib.parse import urlparse
import ssl
import socket
import json

class UrlToHtmlAction(actionInterface):
    """A action module to recover HTML from an URL.  
    Perform a get request on the URL with a desktop-like User-Agent.
    """

    def __init__(self, parsers = {}, supportedType = {"url"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "URL: Get HTML content"
        self.indicators = "🚩"

        
    def execute(self) -> object:
        self.results = {}
        for url in self.get_observables().get("url", []):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
                }
                response = requests.get(url, headers=headers)
                self.results.update({url:response.text})
            except Exception as e:
                self.results.update({url:str(e)})
        return self.results


    def __str__(self):
        self.execute()
        return "\n".join([html for html in self.results.values()])

class GetCertificatesAction(actionInterface):
    """A action module to recover certificate from Domain or IP. Request the domain to do so."""
    CONF = {"Port":{"type":"text", "value":"443"}}
    def __init__(self, parsers = {}, supportedType = {"domain","ip"}, complex_param = CONF):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "Get certificate"
        self.indicators = "🚩"

    def verify_ssl_certificate(self, hostname, port=443):
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=0.7) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                ssock.do_handshake()
                cert = ssock.getpeercert()
                return cert

    def execute(self) -> object:
        self.results = {}
        observables = set(self.get_observables().get("ip",[]) +  self.get_observables().get("domain",[]))
        for observable in observables:
            port = int(self.get_param_value("Port"))
            try:
                self.results[observable] = json.dumps(self.verify_ssl_certificate(observable, port=port))
            except Exception as e:
                self.results[observable] = f"Error while getting the certificate : {e}, {port}"
        return self.results
    
    def __str__(self):
        self.execute()
        return "\r\n".join(f"{observable}\t{str(certif)}" for observable, certif in self.results.items())

class UrlToFaviconHashAction(actionInterface):
    """A action module to recover mmh3 hash of a favicon for a domain or Url.  
    Perform a get request on the URL with a desktop-like User-Agent.
    """

    def __init__(self, parsers = {}, supportedType = {"url","domain"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "Favicon hash (mmh3)"
        self.indicators = "🚩"
        
    def execute(self) -> object:
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
            except Exception as e:
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
        lines = []
        hashes = self.execute()
        for observable, hash in hashes.items():
            lines.append(f"{observable}\t{hash}")
        return  "\r\n".join(lines)

if __name__=='__main__':
    from userTypeParser.HtmlParser import HtmlParser
    data = "Hello, <b>world</b>"
    text_parser = HtmlParser(data)
    a = str(UrlToHtmlAction({"html":text_parser},["html"]))
    print(a, text_parser.objects)