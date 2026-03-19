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
    r"""Fetch HTML content from URLs via HTTP GET requests.

    Performs HTTP GET requests with a desktop Firefox user-agent to retrieve
    HTML content from URLs.

    Supported Types:
        url

    Network Activity:
        Makes GET requests to provided URLs.

    Example:
        >>> from userTypeParser.URLParser import URLParser
        >>> parser = URLParser("https://example.com")
        >>> action = UrlToHtmlAction({"url": parser})
        >>> results = action.execute()
        >>> print(results["https://example.com"][:50])
        <!doctype html>
        <html>
        <head>
            <title>Example...
    """

    def __init__(self, parsers = {}, supportedType = {"url"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "URL: Get HTML content"
        self.indicators = "🚩"

        
    def execute(self) -> object:
        """Execute HTTP GET requests on all parsed URL observables.

        Fetches HTML content from each URL with desktop user-agent.

        Returns:
            dict[str, str]: Keys are URLs, values are HTML response text or
                error messages.
        """
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
        """Return human-readable representation of HTML content.

        Calls :meth:`execute` and formats output as concatenated HTML.

        Returns:
            str: HTML content from all URLs, one per line.
        """
        self.execute()
        return "\n".join([html for html in self.results.values()])

class GetCertificatesAction(actionInterface):
    r"""Retrieve SSL/TLS certificates from domains and IP addresses.

    Connects to domains or IPs via SSL/TLS and retrieves certificate details
    including issuer, subject, validity dates, and SANs.

    Supported Types:
        domain, ip

    Network Activity:
        Makes SSL/TLS connections to provided hosts.

    Parameters:
        Port (text): TCP port number for SSL/TLS connection.
            Default: 443

    Example:
        >>> from userTypeParser.domainParser import domainParser
        >>> parser = domainParser("example.com")
        >>> action = GetCertificatesAction({"domain": parser})
        >>> results = action.execute()
        >>> print(results["example.com"][:100])
        {"subject": ((("commonName", "example.com"),),), "issuer": ...
    """
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
        """Execute SSL certificate retrieval on all parsed observables.

        Connects to each domain/IP and retrieves SSL certificate via handshake.

        Returns:
            dict[str, str]: Keys are domains/IPs, values are JSON-formatted
                certificate details or error messages.
        """
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
        """Return human-readable representation of certificates.

        Calls :meth:`execute` and formats output as TSV with JSON certificates.

        Returns:
            str: TSV of domain/IP and certificate JSON, one per line.
        """
        self.execute()
        return "\r\n".join(f"{observable}\t{str(certif)}" for observable, certif in self.results.items())

class UrlToFaviconHashAction(actionInterface):
    r"""Compute MurmurHash3 (mmh3) of favicon for URLs and domains.

    Fetches favicon.ico from URLs or domains and computes its mmh3 hash.
    Useful for Shodan searches with ``http.favicon.hash`` filter.

    Supported Types:
        url, domain

    Network Activity:
        Makes GET requests to /favicon.ico on provided hosts.

    Example:
        >>> from userTypeParser.domainParser import domainParser
        >>> parser = domainParser("example.com")
        >>> action = UrlToFaviconHashAction({"domain": parser})
        >>> results = action.execute()
        >>> print(results)
        {'example.com': -1234567890}

    Note:
        Requires mmh3 library. Use hash with Shodan:
        ``http.favicon.hash:-1234567890``
    """

    def __init__(self, parsers = {}, supportedType = {"url","domain"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "Favicon hash (mmh3)"
        self.indicators = "🚩"
        
    def execute(self) -> object:
        """Execute favicon hash computation on all parsed observables.

        Fetches favicon.ico and computes mmh3 hash for URLs and domains.

        Returns:
            dict[str, int | str]: Keys are URLs/domains, values are mmh3 hash
                integers or error messages.
        """
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
        """Return human-readable representation of favicon hashes.

        Calls :meth:`execute` and formats output as TSV with hash values.

        Returns:
            str: TSV of URL/domain and mmh3 hash, one per line.
        """
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