try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
import base64
import random

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


class Base64PermutateAction(actionInterface):
    """A action module, to return permutation encode of a string in base 64.  Allowing to create YARA rule or search Malware or Phishing sample using specific functions.
    For example :
    - `document.location` returns `Y3VtZW50LmxvY2F0,b2N1bWVudC5sb2Nh,dW1lbnQubG9jYXRp`
    """
    def __init__(self, parsers = {}, supportedType = {"text"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "Calculate Base64 permutation"
        self.encoded_b64 = []
        
    def execute(self) -> object:
        results = set()
        self.observables = self.get_observables()
        text = self.observables.get("text")[0]
        printable_glyphs = [x for x in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"]
        for i in range(10):
            for nb in range(10):
                prefix = str("".join([printable_glyphs[random.randint(0, len(printable_glyphs))-1] for j in range(nb)]))
                sufix = str("".join([printable_glyphs[random.randint(0, len(printable_glyphs))-1] for j in range(nb)]))
                complete_text = prefix + text + sufix
                results.add(base64.b64encode(complete_text.encode("utf-8")).decode("ascii")[4*((nb)//3+1):4*((nb)//3+1)+4*(len(bytes(text,"utf-8"))//3-1)])
        return list(results)

    def __str__(self):
        results = self.execute()
        return  "\n".join(results)

if __name__=='__main__':
    from userTypeParser.B64Parser import B64Parser
    data = "dG90bw=="
    text_parser = B64Parser(data)
    a = str(B64DecodeAction({"b64":text_parser}))
    print(a)