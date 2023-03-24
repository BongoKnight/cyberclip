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

class searchInOpenCTIAction(actionInterface):
    """Parser Interface defines the minimum functions a parser needs to implement."""
    
    def __init__(self, parsers ={}, supportedType = {"ip","domain","mail","url","md5"}, param_data: str =""):
        self.supportedType = supportedType
        self.parsers = parsers
        self.description = "Search all obsevables in OpenCTI."
        self.results = {}
        self.param = param_data
        self.lines = []
        self.config = {}
        with open(Path(__file__).parent / '../data/conf.yml', encoding="utf8") as f:
            self.config = yaml.load(f, Loader=SafeLoader)
            if self.config.get("OpenCTI"):
                conf = {}
                for i in self.config.get("OpenCTI"):
                    if isinstance(i,dict):
                        for key, value in i.items():
                            conf.update({key:value})
                self.conf = dict(conf)
        api_url = self.conf.get("api_url","")
        api_key = self.conf.get("api_key","")
        try:
            self.api = pycti.OpenCTIApiClient(api_url, api_key)
        except:
            print("OpenCTI is not reachable.")
            self.api = None

        
    def execute(self) -> object:
        """Search all type of observables with the openCTI API. The configuration is passed in the config file.
        
        Sample config:

        OpenCTI:
        - api_url: https://opencti.internal/graphql
        - api_key: <UUID API Key>
        """
        self.lines = []
        self.results = {}
        for parser_name, parser in self.parsers.items():
            if parser.parsertype in self.supportedType:
                self.results[parser.parsertype]=parser.extract()
        observables = []
        for obs_type in self.supportedType:
            if self.results.get(obs_type,[]):
                observables+= self.results.get(obs_type,[])
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