try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
import json
import requests

from dataclasses import dataclass

class RFCExplainerAction(actionInterface):
    """A action module, to get info on a RFC (Request For Comments).
    """
    def __init__(self, parsers = {}, supportedType = {"rfc"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "Get RFC"
        self.decoded_b64 = []
        
    def execute(self) -> object:
        self.base_url = {}
        self.observables = self.get_observables()
        self.results = {}
        if rfcs:= self.observables.get("rfc",[]):
            for rfc in rfcs:
                clean_rfc : str = rfc.lower().replace(" ","")
                url = "https://www.rfc-editor.org/rfc/" + clean_rfc + ".txt"
                html_url = "https://datatracker.ietf.org/doc/html/" + clean_rfc 
                info = requests.get(url)
                if info.status_code == 200:
                    self.results[rfc]= f"# {clean_rfc.upper()}\r\n\r\nHTML version: {html_url}\r\n\r\n{info.text}"
                else:
                    self.results[rfc]="RFC not found."
        return self.results

    
    def __str__(self):
        self.execute()
        results = []
        for rfc, text in self.results.items():
            results.append(text)
        return  "\r\n\r\n".join(results)

