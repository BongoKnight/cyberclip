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
    """A action module, to add observables contained in a text to Yeti via the API.

    Note:
        A config is needed :

        ```yaml
        Yeti:
        - url: http://127.0.0.1:5000
        - api-key: <api-key>
        ```

    Attributes:
        Source (str): From where the data come from
        Threat (`list` of `str`, optional): List of associated threats
        Campaigns (`list` of `str`, optional): List of associated campaigns
        Tags (`list` of `str`, optional): List of associated tags

    Warning: 
        These attributes are the description of the `complex_param` attribute of the action.
    """
    
    def __init__(self, parsers ={}, supportedType = {"ip","ipv6","domain","mail","url"}, complex_param = {"Source":"", "Threat":[], "Campaign":[], "Tags":[]}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param = complex_param)
        self.description = "Add observables in YETI."
        self.config = self.load_conf("Yeti")
        self.indicators = "🔑"


    def execute(self) -> object:
        self.lines = []
        self.get_observables()
        for obs_type in self.supportedType:
            observables = self.observables.get(obs_type,[])
            tags = self.get_param_value("Tags")
            source = self.get_param_value("Source")
            campaigns = self.get_param_value("Campaign")
            threats = self.get_param_value("Threat")
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
    
    def __str__(self):
        self.execute()
        return "\n".join(self.lines)

if __name__=='__main__':
    from userTypeParser.mailParser import mailParser

    data = "127.0.0.1, 124.0.12.23 test@example.com aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    VRGNI_parser = mailParser(data)
    a = str(searchYetiAction({"mail":VRGNI_parser},["mail"]))