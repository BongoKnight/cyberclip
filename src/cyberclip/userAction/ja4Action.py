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

JA4_DB = None
JA3_DB = None


def get_JAX_data():
    global JA4_DB, JA3_DB
    JA4_DB = pd.DataFrame()
    file_name = os.path.join(Path(__file__).parent / "../data/ja4.json")
    if not os.path.exists(file_name) or (time.time() - os.path.getmtime(file_name) ) / 3600 > 24*7:
        try:
            url = "https://ja4db.com/api/download/"
            response = requests.get(url)
            with open(file_name, 'w') as f:
                json.dump(response.json(),f)
            del response
        except Exception as e:
            print("Error while retriving JA4+ database from ja4db.com", e)

    try: 
        JA4_DB = pd.read_json(file_name)
    except Exception as e:
        print("Error while loading JA4 database", e)


    JA3_DB = pd.DataFrame()
    file_name = os.path.join(Path(__file__).parent / "../data/ja3.json")
    if not os.path.exists(file_name) or (time.time() - os.path.getmtime(file_name) ) / 3600 > 24*7:
        try:
            url = "https://ja3.me/download/ja3me.json"
            response = requests.get(url)
            with open(file_name, 'w') as f:
                json.dump(response.json(),f)
            del response
        except Exception as e:
            print("Error while retriving JA3 database from ja3.me", e)

    try: 
        JA3_DB = pd.read_json(file_name)
    except Exception as e:
        print("Error while loading JA3 database", e)


class JA4Action(actionInterface):
    """A action module, to search for JA4+.  
    Return the software or librairy associated to a JA4 fingerprint.
    """

    def __init__(self, parsers = {}, supportedType = {"ja4"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "JA4: Search"
        self.indicators = "📑"
        
    def execute(self) -> object:
        """
        Return JA4+ data. Data returned include: Matching_Values, application, library, device, os, user_agent_string, certificate_authority, verified, notes.
        """
        get_JAX_data()
        self.observables = self.get_observables()
        ja4s = self.observables.get("ja4")
        if ja4s:
            mask = JA4_DB.isin(ja4s)
            matching_df = JA4_DB
            matching_df['Matching_Values'] = matching_df.where(mask).bfill(axis=1).iloc[:, 0]
            filtered_df = matching_df[matching_df['Matching_Values'].notna()]
            return filtered_df
        else:
            return pd.DataFrame(columns=["Matching_Values","application", "library", "device", "os", "user_agent_string", "certificate_authority", "verified", "notes"])
    
    def __str__(self):
        """Returns a TSV representation of the dataframe returned by `execute`"""
        df = self.execute()
        return  df[["Matching_Values","application", "library", "device", "os", "user_agent_string", "certificate_authority", "verified", "notes"]].to_csv(sep="\t", index=None)

class JA3Action(actionInterface):
    """A action module, to search for JA3.  
    Return the software or librairy associated to a JA3 fingerprint.
    """

    def __init__(self, parsers = {}, supportedType = {"md5"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "JA3: Search"
        self.indicators = "📑"
        
    def execute(self) -> object:
        """
        Return JA3 data. Data returned include: digest, first_seen, last_seen, user_agent, ja3, source.
        """
        get_JAX_data()
        self.observables = self.get_observables()
        ja3s = self.observables.get("md5")
        if ja3s:
            return JA3_DB[JA3_DB['digest'].isin(ja3s)]
        else:
            return pd.DataFrame(columns=["digest","first_seen","last_seen","user_agent","ja3","source"])
    
    def __str__(self):
        """Returns a TSV representation of the dataframe returned by `execute`"""
        df = self.execute()
        return  df[["digest","first_seen","last_seen","user_agent","ja3","source"]].to_csv(sep="\t", index=None)


if __name__=='__main__':
    from userTypeParser.JA4Parser import ja4Parser
    from userTypeParser.MD5Parser import md5Parser
    data = "ip\tt13d301200_1d37bd780c83_d339722ba4af info\n154.0.123.1\tT1548 0b2012eb6e9a1f76ba56587d4a391211"
    ja4_parser = ja4Parser(data)
    ja3_parser = md5Parser(data)
    a = str(JA4Action({"ja4":ja4_parser},["ja4"]))
    print(a, ja4_parser.objects)
    print(str(JA3Action({"md5":ja3_parser},["md5"])), ja3_parser.objects)