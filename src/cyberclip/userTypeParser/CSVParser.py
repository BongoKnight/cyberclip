import pandas as pd
from io import StringIO
from userTypeParser.ParserInterface import ParserInterface
from utilities import find_delimiter


class csvParser(ParserInterface):
    """Implementation of ParserInterface for tsv strings.

    Code exemple ::
        a = csvParser("ccdf ")
        b = csvParser("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        print(a.extract(), a.contains())
        print(b.extract(), b.contains())

    """    
    def __init__(self, text: str, parsertype="csv"):
        self.text = text
        self.parsertype = "csv"
        self.objects = pd.DataFrame()
        
    def contains(self):
        """Return true if text contains CSV data in at least two columns."""


        try:
            df = pd.read_csv(StringIO(self.text), sep=find_delimiter(self.text), skip_blank_lines=False)
            self.objects = df
            if len(df.columns) >= 1:
                return True
            else:
                return False
        except :
            return False
    
    def extract(self):
        """Return all tsv contained in text."""
        return [str(self.objects.to_csv(sep=find_delimiter(self.text)))]
        
        
if __name__=="__main__":
    a = csvParser("ccdf ")
    b = csvParser("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())