import pandas as pd
from io import StringIO
from userTypeParser.ParserInterface import ParserInterface
from utilities import find_delimiter


class csvParser(ParserInterface):
    """Parse and extract CSV/delimiter-separated data from text.

    CSV, TSV, or other delimiter-separated data with automatic delimiter detection.

    Regex Pattern:
        Not regex-based. Uses pandas DataFrame parsing with delimiter auto-detection.

    Defanging Support:
        No. CSV data is not typically defanged.

    Example:
        >>> parser = csvParser("Plain text")
        >>> parser.contains()
        False
        >>> parser = csvParser("col1,col2,col3\\nval1,val2,val3")
        >>> parser.contains()
        True
        >>> parser.extract()
        ['col1,col2,col3\\nval1,val2,val3\\n']
    """
    def __init__(self, text: str, parsertype="csv"):
        self.text = text
        self.parsertype = "csv"
        self.objects = pd.DataFrame()

    def contains(self) -> bool:
        """Check whether the text contains CSV data in at least one column.

        Returns:
            bool: True if the text can be parsed as CSV with at least one column.
        """
        try:
            df = pd.read_csv(StringIO(self.text), sep=find_delimiter(self.text), skip_blank_lines=False)
            self.objects = df
            if len(df.columns) >= 1:
                return True
            else:
                return False
        except :
            return False

    def extract(self) -> list[str]:
        """Extract all CSV data from the text.

        Returns:
            list[str]: A list containing the CSV data as a string.
        """
        return [str(self.objects.to_csv(sep=find_delimiter(self.text)))]
        
        
if __name__=="__main__":
    a = csvParser("ccdf ")
    b = csvParser("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    print(a.extract(), a.contains())
    print(b.extract(), b.contains())