import pandas as pd
from pathlib import Path
import requests
import os
import json
import time
try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

Mitre_DB = pd.DataFrame()
file_name = Path(__file__).parent / "../data/mittre.json"
if not os.path.exists(file_name) or (time.time() - os.path.getmtime(file_name) ) / 3600 > 24*7:
    try:
        url = "https://github.com/mitre-attack/attack-stix-data/raw/master/enterprise-attack/enterprise-attack.json"
        response = requests.get(url)
        with open(file_name, 'w') as f:
            json.dump(response.json().get("objects"),f)
        del response
    except Exception as e:
        print("Error while retriving database from MITTRE Github", e)

try: 
    Mitre_DB = pd.read_json(file_name)
    Mitre_DB = Mitre_DB[Mitre_DB["type"]=="attack-pattern"]
    Mitre_DB["mitre_id"] = Mitre_DB['external_references'].apply(lambda x:x[0]["external_id"])
    Mitre_DB["mitre_url"] = Mitre_DB['external_references'].apply(lambda x:x[0]["url"])
except Exception as e:
    print("Error while loading Mittre database", e)


class MitreAction(actionInterface):
    """Explain Mitre Att&ck TTP Code.  
    Return the name, and the Mitre URL of a tactic.
    """

    def __init__(self, parsers = {}, supportedType = {"mitre"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "Mitre: Explain tactic"
        
    def execute(self) -> object:
        """
        Returns a pandas dataframe containing the following informations : 

        | mitre_id   | name                              | mitre_url                                 |
        |:-----------|:----------------------------------|:------------------------------------------|
        | T1547      | Boot or Logon Autostart Execution | https://attack.mitre.org/techniques/T1547 |
        """
        lines = []
        self.observables = self.get_observables()
        mitre_techniques = self.observables.get("mitre")
        if mitre_techniques:
            return Mitre_DB[Mitre_DB['mitre_id'].isin(mitre_techniques)]
        else:
            return pd.DataFrame(columns=["mitre_id","name","mitre_url"])
    
    def __str__(self):
        """Returns a TSV representation of the dataframe returned by `execute`"""
        df = self.execute()
        return  df[['mitre_id','name', 'mitre_url']].to_csv(sep="\t", index=None)

if __name__=='__main__':
    from userTypeParser.MitreParser import MitreParser
    data = "ip\tinfo\n154.0.123.1\tT1548"
    text_parser = MitreParser(data)
    a = str(MitreAction({"mitre":text_parser},["mitre"]))
    print(a, text_parser.objects)