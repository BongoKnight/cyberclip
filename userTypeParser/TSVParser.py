"""Implementation of ParserInterface for tsv strings.

Code exemple ::
    a = tsvParser("ccdf ")
    b = tsvParser("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())

"""
import logging
import re
import pandas as pd
from io import StringIO
from userTypeParser.ParserInterface import ParserInterface


class tsvParser(ParserInterface):
    """Parser for tsv."""
    
    def __init__(self, text: str, parsertype="tsv", loglevel = logging.INFO):
        self.text = text
        self.parsertype = "tsv"
        self.objects = pd.DataFrame()
        self.log = logging.Logger("tsv")
        ch = logging.StreamHandler()
        ch.setLevel(loglevel)
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %I:%M:%S')
        # add formatter to ch
        ch.setFormatter(formatter)
        self.log.addHandler(ch)
        
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