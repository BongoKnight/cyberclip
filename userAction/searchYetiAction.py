try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
from pathlib import Path
import yaml
from yaml.loader import SafeLoader
import requests

class searchYetiAction(actionInterface):
    """A action module, to search observables contained in the keyboard to Yeti API.
A config is needed :

Yeti:
- url: http://127.0.0.1:5000
- api-key: <api-key>
    """
    
    def __init__(self, parsers ={}, supportedType = {"ip","ipv6","domain","mail","url"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "Search observables in YETI."
        self.config = {}
        with open(Path(__file__).parent / '../data/conf.yml', encoding="utf8") as f:
            self.config = yaml.load(f, Loader=SafeLoader)
            if self.config.get("Yeti"):
                conf = {}
                for i in self.config.get("Yeti"):
                    if isinstance(i,dict):
                        for key, value in i.items():
                            conf.update({key:value})
                self.conf = dict(conf)


    def execute(self) -> object:
        """Execute the action."""
        self.lines = []
        self.observables = self.get_observables()
        for obs_type in self.supportedType:
            obs = self.observables.get(obs_type,[])
            if len(obs)>0:
                headers = {'Accept': 'application/json'}
                headers.update({"X-Api-Key": self.conf.get("api-key"), "Content-Type":"application/json"})
                for value in obs:
                    # For some reason the Yeti API don't handle well when the value filter is a list.
                    params = {'params':{'range':200},'filter':{'value':[value]}}
                    resp = requests.post(self.conf.get("url") + "/api/observablesearch", headers=headers,
                        verify=False, json=params)
                    if resp.json():
                        self.lines.append(f"Found in Yeti: {value}")

        return
    
    def __str__(self):
        """Visual representation of the action"""
        self.execute()
        return "\n".join(self.lines)

if __name__=='__main__':
    from userTypeParser.mailParser import mailParser

    data = "127.0.0.1, 124.0.12.23 test@example.com aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    VRGNI_parser = mailParser(data)
    a = str(searchYetiAction({"mail":VRGNI_parser},["mail"]))