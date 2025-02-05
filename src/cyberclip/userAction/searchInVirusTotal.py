try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import jq
import json
from pathlib import Path
from yaml.loader import SafeLoader
import requests

"""A action module, to open search observables contained in a text in Virus Total."""

DEFAULT_PARAMS = {
                "Relationships":{
                    "type":"tags",
                    "value":["contacted_urls","contacted_domains","contacted_ips","dropped_files","bundled_files","itw_urls","submissions"]
                    },
                "Analysis fields":{
                    "type":"tags",
                    "value":[".data.attributes.last_analysis_stats.malicious",
                             ".data.attributes.tags",
                             ".data.attributes.first_submission_date",
                             ".data.attributes.creation_date",
                             ".data.attributes.reputation",
                             ".data.attributes.meaningful_name",
                             ".data.attributes.magic",
                             ".data.attributes.size",
                             ".data.attributes.jarm",
                             ".data.attributes.asn",
                             ".data.relationships.bundled_files.data[].id",
                             ".data.relationships.contacted_domains.data[].id",
                             ".data.relationships.contacted_ips.data[].id",
                             ".data.relationships.contacted_urls.data[].context_attributes.url",
                             ".data.relationships.dropped_files.data[].id",
                             ".data.relationships.submissions.data.attributes.country",
                             ".data.relationships.submissions.data.attributes.date"]
                    },
                }

class searchInVirusTotalAction(actionInterface):
    """Search ip, domain, MD5, SHA1 and SHA256 with the Virus Total API. The configuration should be passed in the config file.

Two parameters could be passed :

- `Analysis fields` a list of objects to be returned depending of the type of observable searched. JSON scheme is described on [VT](https://docs.virustotal.com/reference/files), you can unset this parameter to retrieve the whole JSON,
- `Relationships` a list of relationships to query. For each observable results will be added under `$.data.<relationship_name>` key and thus specific fields of relationship could be retrievedwith `$.relationships.relationship_name.<path>` thanks to the `Analysis fields` parameter


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

        
    def execute(self) -> object:
        self.observables = self.get_observables()
        self.results = {}
        
        relationships = ",".join(self.get_param_value("Relationships")) if self.get_param_value("Relationships") else ""
        for obs_type in self.supportedType:
            if obs_type=="ip" and (observables:=self.observables.get(obs_type,[])):
                for ip in observables:
                    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}?relationships={relationships}"
                    try:
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
            data = result
            if self.get_param_value("Analysis fields"):
                data = {}
                for selector in self.get_param_value("Analysis fields"):
                    cleaned_selector = selector 
                    if cleaned_selector.startswith(".data.attributes."):
                        cleaned_selector = cleaned_selector.replace(".data.attributes.", "")
                    if cleaned_selector.startswith(".data.relationships."):
                        cleaned_selector = cleaned_selector.replace(".data.relationships.", "")
                    if seen := jq.compile(selector).input_value(result):
                        data[cleaned_selector] = seen.text()
                    else:
                        data[cleaned_selector] = ""
            self.results[observable] = data
        return self.results
    
    def __str__(self):
        self.execute()
        text = []
        for k,v in self.results.items():
            text.append(f"{k}\t{json.dumps(v,indent=None)}")
        return "\n".join(text)

if __name__=='__main__':
    from userTypeParser.MD5Parser import md5Parser

    data = "127.0.0.1, 124.0.12.23, aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, test@domain.com"
    parser = md5Parser(data)
    a = str(searchInVirusTotalAction({"md5":parser},["md5"], complex_param=DEFAULT_PARAMS))