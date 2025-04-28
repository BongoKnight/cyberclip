try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import shodan
from pathlib import Path
import yaml
from yaml.loader import SafeLoader
import json
import time
import jsonpath

"""A action module, to open search observables contained in a text in Shodan."""

class searchInShodanAction(actionInterface):
    """Search all type of observables with the Shodan API. The API Key is passed in the config file. Only IP are handled atm.
    No bulk search on basic plan, wait 1s between each querry.

A configuration is neeeded : 

```yaml
Shodan:
- api-key: <API Key>
```
    """    
    def __init__(self, parsers ={}, supportedType = {"ip"}, complex_param={ "IP Analysis fields":{"type":"tags","value":["$.ports","$.domains","$.data[:].http.server","$.data[:].http.html_hash","$.data[:].http.title","$.data[:].http.port","$.data[:].http.headers_hash"]}, "Allow bulk search":{"type":"boolean","value":False}, "Free account":{"type":"boolean","value":False}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "Shodan: Search IP"
        self.indicators = "🔑"
        self.load_conf("Shodan")
        if self.conf.get("api-key",""):
            self.api = shodan.Shodan(self.conf.get("api-key",""))
        else:
            self.api = None

        
    def execute(self) -> object:
        self.results = {}
        self.observables = self.get_observables()
        if self.api:
            if self.observables.get("ip"):
                if not self.get_param_value("Allow bulk search"):
                    for ip in self.observables.get("ip"):
                        try:
                            self.results[ip] = self.api.host(ip)
                            if self.get_param_value("Free account"):
                                time.sleep(1.1)
                        except:
                            pass
                else:
                    data = self.api.host(self.observables.get("ip"))
                    for info in data:
                        self.results[info["ip_str"]] = info
        for observable, result in self.results.items():
            fields = self.get_param_value("IP Analysis fields")
            if fields:
                clean_results = {i:dict() for i in self.results.keys()}

                for path in fields:
                    unitary_paths, value = jsonpath.jsonpath(result, path, result_type="PATH"), jsonpath.jsonpath(result, path)
                    if isinstance(value, str):
                        clean_results[observable].update({path:value})
                    # lots of nested list fields in shodan API
                    elif type(value) == list and value and value!=[[]]:
                        if isinstance(value[0], list):
                            clean_results[observable].update({path:value[0]})
                        else:
                            clean_results[observable].update({path:value})
                    else:
                        clean_results[observable].update({path:str(value)})

                self.results = clean_results
        return self.results
    
    def __str__(self):
        self.execute()
        return "\n".join(f"{json.dumps(v)}" for k,v in self.results.items())

if __name__=='__main__':
    from userTypeParser.IPParser import ipv4Parser

    data = "127.0.0.1, 206.168.89.216, aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, test@domain.com"
    parser = ipv4Parser(data)
    a = str(searchInShodanAction({"ip":parser},["ip"]))
    print(a, parser.extract())