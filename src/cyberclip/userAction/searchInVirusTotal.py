try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import jq
import re
import json
from pathlib import Path
from yaml.loader import SafeLoader
import requests

"""Search observables in Virus Total."""

DEFAULT_PARAMS = {
                "Relationships":{
                    "type":"fixedlist",
                    "choices":["contacted_urls","contacted_domains","contacted_ips","dropped_files","bundled_files","itw_urls","submissions","execution_parents"],
                    "value":[]
                    },
                }

class searchInVirusTotalAction(actionInterface):
    """Search ip, domain, MD5, SHA1 and SHA256 with the Virus Total API. Results are returned in JSON format. The configuration should be passed in the config file.

A parameter could be passed :

    - `Relationships` a list of relationships to query, be carreful each additionnal relationship consume an API credit. For each observable results will be added under `$.data.<relationship_name>` key and thus specific fields of relationship could be retrievedwith `$.relationships.relationship_name.<path>` thanks to the `Analysis fields` parameter


A configuration is neeeded : 

```yaml
VirusTotal:
- api_key: <VT API Key>
```
    """    
    def __init__(self, parsers ={}, supportedType = {"ip","domain","md5","sha1","sha256"}, complex_param=DEFAULT_PARAMS):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "Virus Total: Search all obsevables."
        self.indicators = "🔑"
        self.lines = []
        self.load_conf("VirusTotal")
        API_KEY = self.conf.get("api-key","")
        self.headers = {"accept": "application/json", "x-apikey": API_KEY}

        
    def execute(self):
        self.observables = self.get_observables()
        self.results = {}
        
        relationships = ",".join(self.get_param_value("Relationships")) if self.get_param_value("Relationships") else ""
        for obs_type in self.supportedType:
            if obs_type=="ip" and (observables:=self.observables.get(obs_type,[])):
                for ip in observables:
                    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}?relationships={relationships}"
                    try:
                        response = requests.get(url, headers=self.headers)
                        self.results[ip] = response.json()
                    except:
                        self.results[ip] = {}
            if obs_type=="domain" and (observables:=self.observables.get(obs_type,[])):
                for domain in observables:
                    url = f"https://www.virustotal.com/api/v3/domains/{domain}?relationships={relationships}"
                    try:
                        response = requests.get(url, headers=self.headers)
                        self.results[domain] = response.json()
                    except:
                        self.results[domain] = {}                   
            if obs_type in ["md5","sha1","sha256"] and (observables:=self.observables.get(obs_type,[])):
                for file_hash in observables:
                    url = f"https://www.virustotal.com/api/v3/files/{file_hash}?relationships={relationships}"
                    try:
                        response = requests.get(url, headers=self.headers)
                        self.results[file_hash] = response.json()
                    except:
                        self.results[file_hash] = {}
                for observable, result in self.results.items():
                    try: 
                        self.results[observable] = result
                    except:
                        self.results[observable] = {}

        return self.results
    
    def __str__(self):
        self.execute()
        return json.dumps(list(self.results.values()), indent=3)

if __name__=='__main__':
    from userTypeParser.MD5Parser import md5Parser

    data = "127.0.0.1, 124.0.12.23, aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, test@domain.com"
    parser = md5Parser(data)
    a = str(searchInVirusTotalAction({"md5":parser},["md5"], complex_param=DEFAULT_PARAMS))