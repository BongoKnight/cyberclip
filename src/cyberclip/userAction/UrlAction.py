try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import json
import yaml
import requests
from urllib.parse import urlparse

class baseUrlAction(actionInterface):
    r"""Convert URLs, domains, and IPs to base URL format.

    Extracts the scheme and netloc from URLs, or constructs base URLs from
    domains and IPs with configurable HTTP/HTTPS scheme.

    Supported Types:
        url, domain, ip, ipv6

    Parameters:
        HTTPS (bool): Use HTTPS scheme instead of HTTP.
            Default: True

    Example:
        >>> from userTypeParser.URLParser import URLParser
        >>> parser = URLParser("https://www.example.com/path/of/page?query=1")
        >>> action = baseUrlAction({"url": parser})
        >>> print(action)
        https://www.example.com

        >>> from userTypeParser.domainParser import domainParser
        >>> parser = domainParser("www.example.com")
        >>> action = baseUrlAction({"domain": parser})
        >>> print(action)
        https://www.example.com
    """
    def __init__(self, parsers = {}, supportedType = {"url","domain","ip","ipv6"}, complex_param={"HTTPS":{"type":"bool","value":True}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "To base URL"
        self.results = {}
        
    def execute(self) -> object:
        """Execute base URL extraction on all parsed observables.

        Constructs base URLs from URLs (extracting netloc), domains, and IPs.

        Returns:
            dict[str, str]: Keys are original observables, values are base URLs.
        """
        self.results = {}
        self.observables = self.get_observables()
        https = self.get_param_value("HTTPS")
        if self.observables.get("url"):
            self.results.update({url:f"http{"s"*https}://{urlparse(url).netloc}" for url in self.observables.get("url")})
        if self.observables.get("domain"):
            self.results.update({domain:f"http{"s"*https}://{domain}" for domain in self.observables.get("domain")})
        if self.observables.get("ip"):
            self.results.update({ip:f"http{"s"*https}://{ip}" for ip in self.observables.get("ip")})
        if self.observables.get("ipv6"):
            self.results.update({ip:f"http{"s"*https}://{ip}" for ip in self.observables.get("ipv6")})
        return self.results

    
    def __str__(self):
        """Return human-readable representation of base URLs.

        Calls :meth:`execute` and formats output as one URL per line.

        Returns:
            str: Base URLs, one per line.
        """
        self.execute()
        return  "\n".join([value for key, value in self.results.items() if value!=""])

class QueryUrlAction(actionInterface):
    r"""Query URLs with custom HTTP requests and return responses.

    Sends HTTP requests to URLs with configurable method, headers, data, and
    cookies. Returns page content, HTTP status, response headers, and parsed
    JSON if applicable.

    Supported Types:
        url

    Parameters:
        Method (list): HTTP request method.
            Choices: GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH
            Default: GET
        Headers (longtext): Request headers in YAML format.
            Example: ``{"User-Agent": "MyBot/1.0"}``
            Default: (empty)
        Data (longtext): Request body data in YAML format.
            Example: ``{"key": "value"}``
            Default: (empty)
        Cookies (longtext): Request cookies in YAML format.
            Example: ``{"session": "abc123"}``
            Default: (empty)

    Example:
        >>> from userTypeParser.URLParser import URLParser
        >>> parser = URLParser("https://httpbin.org/get")
        >>> action = QueryUrlAction({"url": parser})
        >>> results = action.execute()
        >>> print(results)
        {'https://httpbin.org/get': {'content': '...', 'status': 200, 'headers': {...}, 'json': {...}}}
    """
    COMPLEX_PARAM = {"Method":{"type":"list","choices":["GET","POST","PUT","DELETE","OPTIONS","HEAD","PATCH"],"value":"GET"},
                    "Headers":{"type":"longtext","value":""},
                    "Data":{"type":"longtext","value":""},
                    "Cookies":{"type":"longtext","value":""}
                    }
    def __init__(self, parsers = {}, supportedType = {"url"}, complex_param=COMPLEX_PARAM):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "Query URL"
        self.indicators = "🚩"
        self.results = {}
        
    def execute(self) -> object:
        """Execute HTTP requests on all parsed URL observables.

        Sends requests with configured method, headers, data, and cookies.

        Returns:
            dict[str, dict]: Keys are URLs, values are response dicts containing
                'content', 'status', 'headers', and optionally 'json' keys.
        """
        self.results = {}
        self.observables = self.get_observables()
        method = self.get_param_value("Method")
        headers, cookies, data = {}, {}, {}
        if _headers := self.get_param_value("Headers"):
            headers = yaml.safe_load(_headers)
        if _data := self.get_param_value("Data"):
            data = yaml.safe_load(_data)
        if _cookies := self.get_param_value("Cookies"):
            cookies = yaml.safe_load(_cookies)
        if urls := self.observables.get("url"):
            for url in urls:
                try:
                    response = requests.request(method, url, headers=headers, data=data, cookies=cookies)
                    self.results.update({url:{"content":response.content.decode("utf-8"),
                                            "status":response.status_code,
                                            "headers":dict(response.headers),
                                            }})
                    try:
                        data = response.json()
                        self.results.get(url).update({"json":data})
                    except:
                        pass
                except Exception as e:
                    self.results.update({url:{"error":str(e)
                        }})
        return self.results

    
    def __str__(self):
        """Return human-readable representation of HTTP responses.

        Calls :meth:`execute` and formats output as TSV with JSON responses.

        Returns:
            str: TSV of URL and response JSON, one per line.
        """
        self.execute()
        text = []
        for k,v in self.results.items():
            text.append(f"{k}\t{json.dumps(v,indent=None)}")
        return "\n".join(text)



class ParseUrlAction(actionInterface):
    r"""Parse URLs into their component parts.

    Extracts and returns all URL components including scheme, netloc, path,
    params, query, and fragment using Python's urlparse.

    Supported Types:
        url

    Example:
        >>> from userTypeParser.URLParser import URLParser
        >>> parser = URLParser("https://user:pass@example.com:8080/path?query=1#frag")
        >>> action = ParseUrlAction({"url": parser})
        >>> print(action)
        https://user:pass@example.com:8080/path?query=1#frag	{"scheme": "https", "netloc": "user:pass@example.com:8080", "path": "/path", "params": "", "query": "query=1", "fragment": "frag"}
    """
    def __init__(self, parsers = {}, supportedType = {"url"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "URL: Parse"
        self.results = {}
        
    def execute(self) -> object:
        """Execute URL parsing on all parsed URL observables.

        Extracts all components from each URL using urlparse.

        Returns:
            dict[str, dict]: Keys are URLs, values are component dicts with keys
                'scheme', 'netloc', 'path', 'params', 'query', 'fragment'.
        """
        self.results = {}
        self.observables = self.get_observables()
        if urls := self.observables.get("url"):
            self.results.update({url:urlparse(url)._asdict() for url in urls})
        return self.results

    
    def __str__(self):
        """Return human-readable representation of parsed URLs.

        Calls :meth:`execute` and formats output as TSV with component JSON.

        Returns:
            str: TSV of URL and component dictionary, one per line.
        """
        self.execute()
        lines = []
        for key, value in self.results.items():
            lines.append(f"{key}\t{json.dumps(value)}")
        return  "\n".join(lines)

if __name__=='__main__':
    from userTypeParser.domainParser import domainParser
    data = "b\nbtoto.com\na"
    text_parser = domainParser(data)
    a = str(baseUrlAction({"domain":text_parser}))
    print(a)