try:
    from userAction.actionInterface import actionInterface
except:
    from actionInterface import actionInterface
from collections import Counter
import re
from datetime import datetime
from urllib.parse import unquote, quote
import html



class appendEachLineAction(actionInterface):   
    """Append text to the end of each line of a given text.  
    """ 
    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param: dict = {"Text to add":{"type":"text","value":""}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param= complex_param)
        self.description = "Append text on each line."

    def execute(self) -> object:
        """Add a line of text at the beginning of each line of a text.
        
        Return:
            text (str): Text with prepended data
        """
        self.observables = self.get_observables()
        if self.observables.get("text"):
            text = self.observables.get("text")[0].splitlines()
            return "\r\n".join([line + self.get_param_value("Text to add").replace("\\t","\t") for line in text])
        return ""
    
    def __str__(self):
        """Add a line of text at the beginning of a text."""
        return  self.execute()

class prependAction(actionInterface):   
    """Prepend text to a given text.
    
    Usefull for adding a header to data.
    """

    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param = {"Text to add":{"type":"text","value":""}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param= complex_param)
        self.description = "Prepend text."

        
    def execute(self) -> object:
        """Add a line of text at the beginning of a text.
        
        Return:
            text (str): Text with prepended data
        """
        self.observables = self.get_observables()
        if self.observables.get("text"):
            return self.get_param_value("Text to add").replace("\\t","\t")+"\r\n"+self.observables.get("text")[0]
        return ""

    
    def __str__(self):
        """Add a line of text at the beginning of a text."""
        return  self.execute()


class prependEachLineAction(actionInterface):   
    """Add text at the beginning of each line of a given text.
    Enter the text to preprend as a param.
    """ 

    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param: dict={"Text to prepend":{"type":"text","value":""}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param = complex_param)
        self.description = "Prepend text on each line."
        
    def execute(self) -> object:
        """Add a line of text at the end of each line of a text.
        
        Return:
            text (str): Text with prepended data
        """
        self.observables = self.get_observables()
        text = self.observables.get("text","")[0].splitlines()
        return "\r\n".join([self.get_param_value("Text to prepend").replace("\\t","\t") + line for line in text])


    def __str__(self):
        return  self.execute()

class toLowerCaseAction(actionInterface):   
    """Return the given text in lower case.

    `Hello` returns `hello`
    """ 

    def __init__(self, parsers = {}, supportedType = {"text"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "To lower case"
        
    def execute(self) -> object:
        """Add a line of text at the end of each line of a text.
        
        Return:
            text (str): Text lower cased
        """
        self.observables = self.get_observables()
        text = self.observables.get("text","")[0].lower()
        return text

class toUperCaseAction(actionInterface):   
    """Return the given text in UPPER case.

    `Hello` returns `HELLO`
    """ 

    def __init__(self, parsers = {}, supportedType = {"text"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "To UPPER case"
        
    def execute(self) -> object:
        """Add a line of text at the end of each line of a text.
        
        Return:
            text (str): Text upper cased
        """
        self.observables = self.get_observables()
        text = self.observables.get("text","")[0].upper()
        return text

    def __str__(self):
        return  self.execute()

class countAction(actionInterface):    
    """Count the number of time each unique line is contained in a text.

    Return :
        <number_of_occurences>\t<occurence>
    """
    def __init__(self, parsers = {}, supportedType = {"text"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "Count lines occurences."
        
    def execute(self) -> object:
        """Count the number of occurence of each line."""
        lines = []
        self.observables = self.get_observables()
        if self.observables.get("text"):
            lines = self.observables.get("text")[0].splitlines()
            counts = Counter(lines)
            return counts
        return {}

    
    def __str__(self):
        counts = self.execute()
        return  "\n".join([f"{count}\t{line}" for line, count in counts.items()])

class findReplaceAction(actionInterface):    
    """Search and replace using regex.sub().  
    Enter the regex as a param.
    """

    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param={"Search":"","Replace":""}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "Regex: Find and replace"
        
    def execute(self) -> object:
        """Find a regex pattern and replace it.
        """
        self.observables = self.get_observables()
        if self.observables.get("text"):
            text = self.observables.get("text")[0]
            search_regex = self.get_param_value('Search')
            replace_regex = self.get_param_value('Replace')
            return re.sub(search_regex, replace_regex, text, flags= re.MULTILINE)
        return ""

    
    def __str__(self):
        return  self.execute()

class regexFilterAction(actionInterface):    
    """Filter lines matching a regex.  
    Enter the regex as a param.
    """

    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param= {"Regex":{"type":"text","value":""}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param = complex_param)
        self.description = "Regex: Filter"
        
    def execute(self) -> object:
        lines = []
        self.observables = self.get_observables()
        if self.observables.get("text"):
            lines = self.observables.get("text")[0].splitlines()
        return "\n".join([i for i in lines if re.search(self.get_param_value("Regex"), i)])

    
    def __str__(self):
        return  self.execute()

class reverseRegexFilterAction(actionInterface):    
    """Filter lines not matching a regex.  
    Enter the regex as a param.
    """

    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param= {"Regex":{"type":"text","value":""}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param = complex_param)
        self.description = "Regex: Reverse filter"
        
    def execute(self) -> object:
        lines = []
        self.observables = self.get_observables()
        if self.observables.get("text"):
            lines = self.observables.get("text")[0].splitlines()
        return "\n".join([i for i in lines if not re.search(self.get_param_value("Regex"), i)])

    def __str__(self):
        return  self.execute()

class extractRegexGroupAction(actionInterface):    
    """Extract group matching a regex.  
    Enter the regex as a param.
    """

    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param= {"Regex":{"type":"text","value":""}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param = complex_param)
        self.description = "Regex: Extract group"
        
    def execute(self) -> object:
        text = ""
        self.observables = self.get_observables()
        if self.observables.get("text"):
            text = self.observables.get("text")[0]
            matches = re.finditer(self.get_param_value("Regex"), text, re.MULTILINE)
            results = []
            for matchNum, match in enumerate(matches, start=1):
                results.append("\t".join(match.groups()))
            return "\n".join(results)
        else:
            return ""
        
    def __str__(self):
        return  self.execute()

class timestampToDateAction(actionInterface):
    """Convert a Unix timestamp to a readable date"""
    
    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param={}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param= complex_param)
        self.description = "Timestamp: To date"
        
    def execute(self) -> object:
        """Convert a text which is a timestamp to a date.
        
        Returns:
            datetime.datetime(timestamp)
        """
        if self.get_observables().get("text"):
            text = self.observables.get("text")[0]
            if re.search(r"\d+", text):
                try: 
                    timestamps_regex = re.findall(r"(^|\b)(\d{10})(\b|$)", text)
                    dates = []
                    for timestamp in timestamps_regex:
                        dates.append(str(datetime.fromtimestamp(int(timestamp[1]))))
                    return "\r\n".join(dates)
                except Exception as e:
                    return str(e)
        return "Invalid timestamp."
    
    def __str__(self):
        return  self.execute()

class fromHexAction(actionInterface):
    """Convert a hexadecimal string to the corresponding UTF-8 string. String should not be prefixed by 0x"""
    
    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param={}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param= complex_param)
        self.description = "Hex: To UTF-8"
        
    def execute(self) -> object:
        """Convert a hexadecimal string to the corresponding UTF-8 string. String should not be prefixed by 0x.
        
        Returns:
            bytes.fromhex(text).decode('utf-8')
        """
        if self.get_observables().get("text"):
            text = self.observables.get("text")[0]
            try: 
                return bytes.fromhex(text).decode('utf-8')
            except Exception as e:
                return "Invalid hexadecimal: " + str(e)
        return "No text found."
    
    def __str__(self):
        return  self.execute()
    
class UrlUnquoteAction(actionInterface):
    """Unquote a URL encoded text. `%22Hello!%22` returns `"Hello!"`
    """
    
    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param={}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param= complex_param)
        self.description = "URL decode"
        
    def execute(self) -> object:
        """Unquote a URL encoded text.
        
        Returns:
            urllib.parse.unquote(text)
        """
        if self.get_observables().get("text"):
            text = self.observables.get("text")[0]
            try: 
                return unquote(text)
            except Exception as e:
                return "Invalid URL encoding: " + str(e)
        return "No text found."
    
    def __str__(self):
        return  self.execute()
    
class UrlQuoteAction(actionInterface):
    """Encode a text in an URL safe way. `Yeah !` returns `Yeah%20%21`"""
    
    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param={}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param= complex_param)
        self.description = "URL encode"
        
    def execute(self) -> object:
        """Encode a text in an URL safe way.
        
        Returns:
            urllib.parse.quote(text)
        """
        if self.get_observables().get("text"):
            text = self.observables.get("text")[0]
            try: 
                return quote(text)
            except Exception as e:
                return "Invalid URL encoding: " + str(e)
        return "No text found."
    
    def __str__(self):
        return  self.execute()
    
class HtmlUnquoteAction(actionInterface):
    """Unescape HTML encoded text. `&gt;` is replaced by `>`."""
    
    def __init__(self, parsers = {}, supportedType = {"text"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "HTML entity decode"
        
    def execute(self) -> object:
        """Unescape a HTML encoded text.
        
        Returns:
            html.unescape(text)
        """
        if self.get_observables().get("text"):
            text = self.observables.get("text")[0]
            try: 
                return html.unescape(text)
            except Exception as e:
                return "Invalid HTML encoding: " + str(e)
        return "No text found."
    
    def __str__(self):
        return  self.execute()
    
class HtmlQuoteAction(actionInterface):
    """Escape special character in a text with HTML entity. `>` is replaced by `&gt;`."""
    
    def __init__(self, parsers = {}, supportedType = {"text"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "HTML entity encode"
        
    def execute(self) -> object:
        """Escape a text with HTML entity.
        
        Returns:
            html.escape(text)
        """
        if self.get_observables().get("text"):
            text = self.observables.get("text")[0]
            try: 
                return html.escape(text)
            except Exception as e:
                return "Invalid HTML encoding: " + str(e)
        return "No text found."
    
    def __str__(self):
        return  self.execute()
    

class toHexAction(actionInterface):
    """Convert a UTF-8 string to the coressponding one in hexadecimal. """
    
    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param={}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param= complex_param)
        self.description = "Hex: From UTF-8"
        
    def execute(self) -> object:
        """Convert a UTF-8 string to the coressponding one in hexadecimal.
        
        Returns:
            text.encode().hex()
        """
        if self.get_observables().get("text"):
            text = self.observables.get("text")[0]
            try: 
                return text.encode().hex()
            except Exception as e:
                return str(e)
        return "No text found."
    
    def __str__(self):
        return  self.execute()

class toplLinesAction(actionInterface):
    """A action module to crop data to only the N first lines. Default 10 lines."""
    
    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param={"Number of lines":{"type":"text","value":"10"}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param= complex_param)
        self.description = "Top N lines."
        
    def execute(self) -> object:
        """Return the N first lines of a text.
        
        Returns:
            lines[0:n] (list(str)): The n first lines
        """
        nb = self.get_param_value("Number of lines")
        lines = []
        self.observables = self.get_observables()
        if self.observables.get("text"):
            lines = self.observables.get("text")[0].splitlines()
            return "\n".join([i for i in lines[:min(int(nb), len(lines))]])
        return ""

    
    def __str__(self):
        return  self.execute()
    
class saveInFileAction(actionInterface):
    """Save the actual data in a file"""
    
    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param={"Save as":{"type":"save","value":"./tmp.txt"}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param= complex_param)
        self.description = "Save as"
        
    def execute(self) -> object:
        """Save text in a file.
        
        Returns:
            lines[0:n] (list(str)): The n first lines
        """
        filename = self.get_param_value("Save as")
        self.observables = self.get_observables()
        if self.observables.get("text"):
            text = self.observables.get("text")[0]
            with open(filename,"w", encoding="utf-8") as file:
                file.write(text)
            return text
        return ""

    
    def __str__(self):
        return  self.execute()

if __name__=='__main__':
    from userTypeParser.TextParser import TextParser
    data = "b\nb\na"
    data2 = """aaa baba aa cba aba
    aaaa
    """
    text_parser = TextParser(data)
    text_parser2 = TextParser(data2)
    a = str(regexFilterAction({"text":text_parser},["text"],complex_param={"Regex":{"type":"text","value":"^a"}}))
    b = str(reverseRegexFilterAction({"text":text_parser},["text"],complex_param={"Regex":{"type":"text","value":"^a"}}))
    c = str(extractRegexGroupAction({"text":text_parser2},["text"],complex_param={"Regex":{"type":"text","value":"a{2,}"}}))
    d = str(extractRegexGroupAction({"text":text_parser2},["text"],complex_param={"Regex":{"type":"text","value":r"([a\s]ba)"}}))
    e = str(prependAction({"text":text_parser},["text"], complex_param={"Text to add":{"type":"text","value":"c"}}))

    print(f"Match :\n{a}")
    print(f"Don't match :\n{b}")
    print(f"Extract :\n{c}")
    print(f"Extract multi group:\n{d}")
    print(f"Prepend:\n{e}")