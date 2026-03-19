import re
try:
    from userTypeParser.ParserInterface import ParserInterface
except:
    from ParserInterface import ParserInterface

import os
from pathlib import Path

class filenameParser(ParserInterface):
    r"""Parse and extract file paths from text.

    Windows-style absolute file paths (e.g., C:/path/to/file.ext).
    Only returns paths that exist in the filesystem.

    Regex Pattern:
        ``\b[A-Z]:(\/|\\).*(\/|\\)[A-Za-z0-9éàèù'_ \.\(\)\$\-\[\]]+\.[A-Za-z0-9]+\b``

    Defanging Support:
        No. File paths are not typically defanged.

    Example:
        >>> parser = filenameParser("No file path here")
        >>> parser.contains()
        False
        >>> parser = filenameParser("C:/Users/user/file.txt")
        >>> parser.contains()
        True
        >>> parser.extract()  # Returns only if file exists
        ['C:/Users/user/file.txt']
    """
    def __init__(self, text: str, parsertype="filename"):
        self.text = text
        self.parsertype = "filename"
        self.objects = []

    def contains(self) -> bool:
        """Check whether the text contains at least one Windows file path.

        Returns:
            bool: True if at least one file path pattern is found in the text.
        """
        if re.search(r"\b[A-Z]:(\/|\\).*(\/|\\)[A-Za-z0-9éàèù'_ \.\(\)\$\-\[\]]+\.[A-Za-z0-9]+\b",self.text) :
            return True
        else :
            return False

    def extract(self) -> list[str]:
        """Extract all file path instances from the text.

        Only returns paths that exist in the filesystem.

        Returns:
            list[str]: A list of extracted file path values that exist on disk.
        """
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