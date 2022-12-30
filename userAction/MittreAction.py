import pandas as pd
import requests
import os
import json
import time
try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

Mitre_DB = pd.DataFrame()
file_name = os.path.join("mittre.json")
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
    """
    A action module, to crop data to only the N first lines.
    """
    def __init__(self, parsers = {}, supportedType = {"mitre"}, param_data=""):
        self.supportedType = supportedType
        self.parsers = parsers
        self.description = "Mitre tactic to Mittre description."
        self.results = {}
        self.param = param_data

        
    def execute(self) -> object:
        """Execute the action."""
        lines = []
        mitre_techniques = self.parsers.get("mitre").extract()
        if mitre_techniques:
            return Mitre_DB[Mitre_DB['mitre_id'].isin(mitre_techniques)]
        else:
            return pd.DataFrame(columns=["mitre_id","name","mitre_url"])




    
    def __str__(self):
        """Visual representation of the action"""
        df = self.execute()
        return  df[['mitre_id','name', 'mitre_url']].to_csv(sep="\t", index=None)

if __name__=='__main__':
    from userTypeParser.MitreParser import MitreParser
    data = "ip\tinfo\n154.0.123.1\T1548"
    text_parser = MitreParser(data)
    a = str(MitreAction({"mitre":text_parser},["mitre"]))
    print(a, text_parser.objects)