try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
import base64

class B64DecodeAction(actionInterface):
    """A action module, to decode base 64.  
    For example : 
    
    - `dG90bw==` returns `toto`
    """
    def __init__(self, parsers = {}, supportedType = {"b64"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "Decode Base 64"
        self.decoded_b64 = []
        
    def execute(self) -> object:
        self.base_url = {}
        self.observables = self.get_observables()
        if self.observables.get("b64"):
            self.decoded_b64 = {observable: base64.b64decode(observable) for observable in self.observables.get("b64")}
        return self.decoded_b64

    
    def __str__(self):
        self.execute()
        results = []
        for key, value in self.decoded_b64.items():
            if value!="" :
                try:
                    results.append(f"{key}\n{str(value, encoding='utf-8')}")
                except:
                    results.append(f"{value}")
        return  "\n".join(results)

class B64EncodeAction(actionInterface):
    """A action module, to encode in base 64.  
    For example :
    
    - `toto` returns `dG90bw==`
    """
    def __init__(self, parsers = {}, supportedType = {"text"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "Encode in Base 64"
        self.encoded_b64 = []
        
    def execute(self) -> object:
        self.base_url = {}
        self.observables = self.get_observables()
        if self.observables.get("text"):
            try:
                self.encoded_b64 = {observable: base64.b64encode(observable.encode('utf-8')) for observable in self.observables.get("text")}
            except:
                pass
        return self.encoded_b64

    
    def __str__(self):
        self.execute()
        results = []
        for key, value in self.encoded_b64.items():
            if value!="" :
                results.append(f"{str(value, encoding='utf-8')}")
        return  "\n".join(results)


if __name__=='__main__':
    from userTypeParser.B64Parser import B64Parser
    data = "dG90bw=="
    text_parser = B64Parser(data)
    a = str(B64DecodeAction({"b64":text_parser}))
    print(a)