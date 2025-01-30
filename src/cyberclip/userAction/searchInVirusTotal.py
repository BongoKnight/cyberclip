try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

from jsonpath import jsonpath
import json
from pathlib import Path
from yaml.loader import SafeLoader
import requests

"""A action module, to open search observables contained in a text in Virus Total."""

DEFAULT_PARAMS = {
                "Analysis fields":{
                    "type":"tags",
                    "value":["$.data.attributes.last_analysis_stats.malicious","$.data.attributes.tags","$.data.attributes.first_submission_date","$.data.attributes.creation_date","$.data.attributes.reputation","$.data.attributes.meaningful_name","$.data.attributes.magic","$.data.attributes.size","$.data.attributes.jarm","$.data.attributes.asn"]
                    }
                }

class searchInVirusTotalAction(actionInterface):
    """Search all type of observables with the Virus Total API. The configuration is passed in the config file.
    
    A configuration is neeeded : 

    VirusTotal:
    - api_key: <VT API Key>
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
        for obs_type in self.supportedType:
            if obs_type=="ip" and (observables:=self.observables.get(obs_type,[])):
                for ip in observables:
                    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
                    try:
                        self.results[ip] = response.json()
                    except:
                        self.results[ip] = {}
            if obs_type=="domain" and (observables:=self.observables.get(obs_type,[])):
                for domain in observables:
                    url = f"https://www.virustotal.com/api/v3/domains/{domain}"
                    try:
                        response = requests.get(url, headers=self.headers)
                        self.results[domain] = response.json()
                    except:
                        self.results[domain] = {}                   
            if obs_type in ["md5","sha1","sha256"] and (observables:=self.observables.get(obs_type,[])):
                for file_hash in observables:
                    url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
                    try:
                        response = requests.get(url, headers=self.headers)
                        self.results[file_hash] = response.json()
                    except:
                        self.results[file_hash] = {}

        for observable, result in self.results.items():
            data = {}
            for selector in self.get_param_value("Analysis fields"):
                cleaned_selector = selector 
                if cleaned_selector.startswith("$.data.attributes."):
                    cleaned_selector = cleaned_selector.replace("$.data.attributes.", "")
                if seen := jsonpath(result, selector):
                    data[cleaned_selector] = seen
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