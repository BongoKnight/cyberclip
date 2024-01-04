import re
import pandas as pd
from io import StringIO
from userTypeParser.ParserInterface import ParserInterface


class tsvParser(ParserInterface):
    """Implementation of ParserInterface for tsv strings.

    Code exemple ::
        a = tsvParser("ccdf ")
        b = tsvParser("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        print(a.extract(), a.contains())
        print(b.extract(), b.contains())

    """    
    def __init__(self, text: str, parsertype="tsv"):
        self.text = text
        self.parsertype = "tsv"
        self.objects = pd.DataFrame()
        
    def contains(self):
        """Return true if text contains TSV data in at least two columns."""
        try:
            df = pd.read_csv(StringIO(self.text),sep="\t")
            self.objects = df
            if len(df.columns) > 1:
                return True
            else:
                return False
        except :
            return False
    
    def extract(self):
        """Return all tsv contained in text."""
        return [str(self.objects.to_csv(sep="\t"))]
        
        
if __name__=="__main__":
    a = tsvParser("ccdf ")
    b = tsvParser("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())