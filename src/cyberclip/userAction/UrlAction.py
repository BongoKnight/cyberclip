try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import json
import requests
from urllib.parse import urlparse

class baseUrlAction(actionInterface):
    """Return a link from a domain or an URL to the base dir.  
For example : 

- `https://www.example.com/path/of/page` returns `https://www.example.com/`
- `www.example.com` returns `https://www.example.com/`
    """
    def __init__(self, parsers = {}, supportedType = {"url","domain","ip","ipv6"}, complex_param={"HTTPS":{"type":"bool","value":True}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "To base URL"
        self.results = {}
        
    def execute(self) -> object:
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
        self.execute()
        return  "\n".join([value for key, value in self.results.items() if value!=""])

class QueryUrlAction(actionInterface):
    """Query URL with specified parameters and method. Return page content, response status and response headers. If returned data are in json format return them as well. 
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
        self.results = {}
        self.observables = self.get_observables()
        method = self.get_param_value("Method")
        headers, cookies, data = {}, {}, {}
        if _headers := self.get_param_value("Headers"):
            headers = json.loads(_headers)
        if _data := self.get_param_value("Data"):
            data = json.loads(_data)
        if _cookies := self.get_param_value("Cookies"):
            cookies = json.loads(_cookies)
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
        self.execute()
        text = []
        for k,v in self.results.items():
            text.append(f"{k}\t{json.dumps(v,indent=None)}")
        return "\n".join(text)



class ParseUrlAction(actionInterface):
    """Return a dictionary of URL components (ie. proto, fragment, netloc...)
    """
    def __init__(self, parsers = {}, supportedType = {"url"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "URL: Parse"
        self.results = {}
        
    def execute(self) -> object:
        self.results = {}
        self.observables = self.get_observables()
        if urls := self.observables.get("url"):
            self.results.update({url:urlparse(url)._asdict() for url in urls})
        return self.results

    
    def __str__(self):
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