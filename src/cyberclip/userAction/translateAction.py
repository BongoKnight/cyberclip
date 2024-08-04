try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import json
import requests

DEFAULT_PARAMS = {
                "Source":{
                    "type":"list",
                    "choices":["AR","BG","CS","DA","DE","EL","EN","ES","ET","FI","FR","HU","ID","IT","JA","KO","LT","LV","NB","NL","PL","PT","RO","RU","SK","SL","SV","TR","UK","ZH"],
                    "value": "EN"
                    },
                "Target":{
                    "type":"list",
                    "choices":["AR","BG","CS","DA","DE","EL","EN","EN-GB","EN-US","ES","ET","FI","FR","HU","ID","IT","JA","KO","LT","LV","NB","NL","PL","PT","PT-BR","PT-PT","RO","RU","SK","SL","SV","TR","UK","ZH","ZH-HANS","ZH-HANT"],
                    "value": "FR"
                    },
                "Free API":{
                    "type": "bool",
                    "value": True
                    }
                }


class translateWithDeeplAction(actionInterface):
    """Translate a text through the DeepL API.
    
    A configuration and an API key are neeeded : 

    Deepl:
    - api_key: <Deepl API Key>
    """    
    def __init__(self, parsers ={}, supportedType = {"text"}, complex_param=DEFAULT_PARAMS):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "Tanslate text"
        self.lines = []
        self.load_conf("Deepl")
        API_KEY = self.conf.get("api-key","")
        freeAPI = self.get_param_value("Free API")
        if freeAPI:
            self.base_url = "https://api-free.deepl.com/v2"
        else:
            self.base_url = "https://api.deepl.com/v2"
        self.headers = {"Content-Type": "application/json", "Authorization": f"DeepL-Auth-Key {API_KEY}"}

    def execute(self) -> object:
            self.results = ""
            text = self.get_observables().get("text", [])
            url = f"{self.base_url}/translate"
            try:
                data = {"source_lang": self.get_param_value("Source"),
                        "target_lang": self.get_param_value("Target"),
                        "text": text
                        }
                response = requests.post(url, headers=self.headers, data=json.dumps(data))
                print(response.text)
                self.results = "\r\n".join(result.get("text") for result in response.json().get("translations", [{}]))
                try:
                    quota = requests.get(f"{self.base_url}/usage", headers=self.headers).json()
                    self.results+= f"\r\n\r\n[Quota:{quota.get('character_count')}/{quota.get('character_limit')}]"
                except:
                    pass
            except Exception as e:
                self.results = str(e)
            return self.results

    def __str__(self):
        return self.execute()
    
if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "Hello, World!"
    text_parser = TextParser(data)
    a = str(translateWithDeeplAction({"text":text_parser},["text"],complex_param=DEFAULT_PARAMS))
    print(a)