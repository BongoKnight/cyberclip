import re
try:
    from userTypeParser.ParserInterface import ParserInterface
except:
    from ParserInterface import ParserInterface

import os
from pathlib import Path

class filenameParser(ParserInterface):
    """Implementation of ParserInterface for FileName strings.

    Code exemple ::
        a = filenameParser("dsfsd sdfsdf sdfsdhj j")
        b = filenameParser('C:/Users/svernin/AppData/Local/Temp/Sans titre.jpg')
        print(a.extract(), a.contains())
        print(b.extract(), b.contains())

    """
    def __init__(self, text: str, parsertype="filename"):
        self.text = text
        self.parsertype = "filename"
        self.objects = []
        
    def contains(self):
        """Return true if text contains at least one filename."""
        if re.search(r"\b[A-Z]:(\/|\\).*(\/|\\)[A-Za-z0-9éàèù'_ \.\(\)\$\-\[\]]+\.[A-Za-z0-9]+\b",self.text) :
            return True
        else :
            return False
    
    def extract(self):
        """Return all filenames contained in text and existing in the filesystem."""
        filenamesIter = re.finditer(r"\b[A-Z]:(\/|\\).*(\/|\\)[A-Za-z0-9éàèù'_ \.\(\)\$\-\[\]]+\.[A-Za-z0-9]+\b", self.text)
        filepaths_clean = [filename.group().replace('\\','/')[0:] for filename in filenamesIter]
        filenames = [filename for filename in filepaths_clean if os.path.isfile(filename)]
        self.objects = filenames
        return filenames
        
        
if __name__=="__main__":
    a = filenameParser("dsfsd sdfsdf sdfsdhj j")
    b = filenameParser('C:/Users/svernin/AppData/Local/Temp/Sans titre.jpg')
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())