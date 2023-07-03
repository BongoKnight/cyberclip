try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
from pathlib import Path
import yaml
from datetime import datetime, timedelta
from yaml.loader import SafeLoader
import requests

class searchYetiAction(actionInterface):
    """A action module, to add observables contained in the keyboard to Yeti via the API.
A config is needed :

Yeti:
- url: http://127.0.0.1:5000
- api-key: <api-key>
    """
    
    def __init__(self, parsers ={}, supportedType = {"ip","domain","mail","url"}, complex_param = {"Source":"", "Threat":[], "Campaign":[], "Tags":[]}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param = complex_param)
        self.description = "Add observables in YETI."
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
        self.get_observables()
        for obs_type in self.supportedType:
            observables = self.observables.get(obs_type,[])
            tags = self.complex_param.get("Tags", "")
            source = self.complex_param.get("Source", "")
            campaigns = self.complex_param.get("Campaign", "")
            threats = self.complex_param.get("Threat", "")
            if threats:
                for threat in threats:
                    tags.append(f"threat{threat}")
            if campaigns:
                for campaign in campaigns:
                    tags.append(f"campaign{campaign}")
            if len(observables)>0:
                try:
                    headers = {'Accept': 'application/json'}
                    headers.update({"X-Api-Key": self.conf.get("api-key"), "Content-Type":"application/json"})
                    params = {"observables": [{"tags": tags, "value": o, "source": source} for o in observables]}
                    resp = requests.post(self.conf.get("url") + "/api/observable/bulk", headers=headers,
                            verify=False, json=params)
                    if resp.json():
                        for item in resp.json():
                            if datetime.fromisoformat(item.get("created")) < datetime.now() - timedelta(hours=1,minutes=2):
                                self.lines.append(f'{item.get("value")} is already known. \r\n{set([i.get("name","") for i in item.get("tags")])}')
                except ConnectionError:
                    self.lines.append("Error while connecting Yeti.")
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