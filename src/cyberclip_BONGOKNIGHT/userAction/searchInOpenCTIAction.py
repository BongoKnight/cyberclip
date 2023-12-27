try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import os
import urllib.parse
from pathlib import Path
import yaml
from yaml.loader import SafeLoader
import urllib.parse
import pycti

"""A action module, to open search observables contained in a text in an OpenCTI instance."""
OPENCTI_CONFIG = {}
OPENCTI_CLIENT = None
OPENCTI_URL = ""
OPENCTI_KEY = ""

with open(Path(__file__).parent / '../data/conf.yml', encoding="utf8") as f:
    config = yaml.load(f, Loader=SafeLoader)
    if config.get("OpenCTI"):
        conf = {}
        for i in config.get("OpenCTI"):
            if isinstance(i,dict):
                for key, value in i.items():
                    conf.update({key:value})
        OPENCTI_CONFIG = dict(conf)
OPENCTI_URL = OPENCTI_CONFIG.get("api_url","")
OPENCTI_KEY = OPENCTI_CONFIG.get("api_key","")
try:
    if OPENCTI_KEY and OPENCTI_URL:
        OPENCTI_CLIENT = pycti.OpenCTIApiClient(OPENCTI_URL, OPENCTI_KEY)
except:
    print("OpenCTI is not reachable.")
    OPENCTI_CLIENT = None


class searchInOpenCTIAction(actionInterface):
    """Search all type of observables with the openCTI API. The configuration is passed in the config file.
    
    A configuration is neeeded : 

    OpenCTI:
    - api_url: https://opencti.internal/graphql
    - api_key: <UUID API Key>
    """    
    def __init__(self, parsers ={}, supportedType = {"ip","ipv6","domain","mail","url","md5"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "Search all obsevables in OpenCTI."
        self.lines = []
        self.config = {}
        if OPENCTI_CLIENT:
            self.api = OPENCTI_CLIENT
        else:
            self.api = None

        
    def execute(self) -> object:
        self.lines = []
        self.observables = self.get_observables()
        observables = []
        for obs_type in self.supportedType:
            if self.observables.get(obs_type,[]):
                observables+= self.observables.get(obs_type,[])
        results = self.api.stix_cyber_observable.list(filters=[{"values":observables, "key":"value"}])
        indexed_result = {result.get("value"):result for result in results}
        return indexed_result
    
    def __str__(self):
        """Visual representation of the action"""
        out = self.execute()
        return "\r\n".join([f"{i} found in OpenCTI." for i in out.keys()])

if __name__=='__main__':
    from userTypeParser.mailParser import mailParser

    data = "127.0.0.1, 124.0.12.23, aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, test@domain.com"
    parser = mailParser(data)
    a = str(searchInOpenCTIAction({"mail":parser},["mail"]))