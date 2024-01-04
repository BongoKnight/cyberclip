try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface

import hashlib
import json

"""FileAction.

Classes:
    ExtractTextAction: try to extract text from file thanks to `textract`
    CalculateHashAction: return hash of file

"""

class ExtractTextAction(actionInterface):
    """
    A action module to extract text from files contained in the clipboard.  
    Make use of textract lib.
    """
    def __init__(self, parsers = {}, supportedType = {"filename"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "Extract text from files."
        self.results = {}
        
    def execute(self) -> object:
        """Execute the action."""
        import textract
        self.results = {}
        self.observables = self.get_observables()
        if filenames := self.observables.get("filename", []):
            for filename in filenames:
                try:
                    self.results.update({filename: textract.process(filename)})
                except Exception as e:
                    self.results.update({filename: f"Error while processing file : {str(e)}"})
    
    def __str__(self):
        """Visual representation of the action"""
        self.execute()
        results = []
        for filename, text in self.results.items():
            if isinstance(text, bytes):
                results.append(str(text, "utf-8"))
            if isinstance(text, str):
                results.append(text)
        return  "\n\n".join(results)

class CalculateHashAction(actionInterface):
    """
    A action module to calculate hashes from files contained in the clipboard.  
    Default : MD5 and SHA1
    """
    CONF =  {"Hashes":{"type":"tags","value":["MD5","SHA1"]}}
    def __init__(self, parsers = {}, supportedType = {"filename"}, complex_param = CONF):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "Calculate hash from files."
        self.results = {}
        
    def execute(self) -> object:
        """Execute the action."""
        self.results = {}
        self.observables = self.get_observables()
        if filenames := self.observables.get("filename", []):
            for filename in filenames:
                with open(filename, 'rb') as file:
                    filecontent = file.read()
                    hashes = {}
                    for hash in self.get_param_value("Hashes"):
                        try:
                            if hash.lower() == "sha1":
                                hash_str = hashlib.sha1(filecontent).hexdigest()
                                hashes['SHA1'] = hash_str 
                            if hash.lower() == "md5":
                                hash_str = hashlib.md5(filecontent).hexdigest()
                                hashes['MD5'] = hash_str 
                            if hash.lower() == "sha256":
                                hash_str = hashlib.sha256(filecontent).hexdigest()
                                hashes['SHA256'] = hash_str
                            if hash.lower() == "sha224":
                                hash_str = hashlib.sha224(filecontent).hexdigest()
                                hashes['SHA224'] = hash_str
                        except Exception as e:
                            self.results.update({filename: f"Error while processing file : {str(e)}"})

                self.results.update({filename:hashes})
    
    
    def __str__(self):
        """Visual representation of the action"""
        self.execute()
        lines = []
        for filename, hashes in self.results.items():
            lines.append(f"{filename}\t{json.dumps(hashes)}")
        return  "\r\n".join(lines)


if __name__=='__main__':
    from userTypeParser.filenameParser import filenameParser
    data = r'file'
    filename_parser = filenameParser(data)
    a = str(ExtractTextAction({"filename":filename_parser}))
    print(a)