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

"""A action module, to open search observables contained in a text in Shodan."""
SHODAN_KEY = ""
SHODAN_CONFIG = {}

with open(Path(__file__).parent / '../data/conf.yml', encoding="utf8") as f:
    config = yaml.load(f, Loader=SafeLoader)
    if config.get("Shodan"):
        conf = {}
        for i in config.get("Shodan"):
            if isinstance(i,dict):
                for key, value in i.items():
                    conf.update({key:value})
        SHODAN_CONFIG = dict(conf)
SHODAN_KEY = SHODAN_CONFIG.get("api-key","")
print(SHODAN_KEY)

class searchInShodanAction(actionInterface):
    """Search all type of observables with the Shodan API. The API Key is passed in the config file. Only IP are handled atm.
    No bulk search on basic plan, wait 1s between each querry.

    A configuration is neeeded : 

    Shodan:
    - api-key: <API Key>
    """    
    def __init__(self, parsers ={}, supportedType = {"ip"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "Search all obsevables in Shodan."
        if SHODAN_KEY:
            self.api = shodan.Shodan(SHODAN_KEY)
        else:
            self.api = None

        
    def execute(self) -> object:
        results = []
        self.observables = self.get_observables()
        if self.api:
            if self.observables.get("ip"):
                for ip in self.observables.get("ip"):
                    try:
                        results.append(self.api.host(ip))
                        time.sleep(1.1)
                    except:
                        pass
        return results
    
    def __str__(self):
        """Visual representation of the action"""
        return json.dumps(self.execute())

if __name__=='__main__':
    from userTypeParser.IPParser import ipv4Parser

    data = "127.0.0.1, 206.168.89.216, aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, test@domain.com"
    parser = ipv4Parser(data)
    a = str(searchInShodanAction({"ip":parser},["ip"]))
    print(a, parser.extract())