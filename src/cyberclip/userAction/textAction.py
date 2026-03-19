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
    r"""Append text to the end of each line.

    Adds specified text to the end of every line in the input text.

    Supported Types:
        text

    Parameters:
        Text to add (text): String to append to each line. Supports \t for tabs.
            Default: "" (empty string)

    Example:
        >>> from userTypeParser.TextParser import TextParser
        >>> parser = TextParser("line1\nline2\nline3")
        >>> action = appendEachLineAction({"text": parser})
        >>> action.complex_param["Text to add"]["value"] = " END"
        >>> print(action)
        line1 END
        line2 END
        line3 END
    """ 
    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param: dict = {"Text to add":{"type":"text","value":""}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param= complex_param)
        self.description = "Append text on each line."

    def execute(self) -> object:
        """Execute text appending on all lines.

        Returns:
            str: Text with specified string appended to each line.
        """
        self.observables = self.get_observables()
        if self.observables.get("text"):
            text = self.observables.get("text")[0].splitlines()
            return "\r\n".join([line + self.get_param_value("Text to add").replace("\\t","\t") for line in text])
        return ""

    def __str__(self):
        """Return human-readable representation of results.

        Returns:
            str: Formatted text with appended content.
        """
        return  self.execute()

class prependAction(actionInterface):
    r"""Prepend text to the beginning of input.

    Adds specified text before the entire input. Useful for adding headers to data.

    Supported Types:
        text

    Parameters:
        Text to add (text): String to prepend. Supports \t for tabs.
            Default: "" (empty string)

    Example:
        >>> from userTypeParser.TextParser import TextParser
        >>> parser = TextParser("data\ndata")
        >>> action = prependAction({"text": parser})
        >>> action.complex_param["Text to add"]["value"] = "HEADER\n"
        >>> print(action)
        HEADER
        data
        data
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
    r"""Prepend text to the beginning of each line.

    Adds specified text to the start of every line in the input text.

    Supported Types:
        text

    Parameters:
        Text to prepend (text): String to prepend to each line. Supports \t for tabs.
            Default: "" (empty string)

    Example:
        >>> from userTypeParser.TextParser import TextParser
        >>> parser = TextParser("line1\nline2")
        >>> action = prependEachLineAction({"text": parser})
        >>> action.complex_param["Text to prepend"]["value"] = "> "
        >>> print(action)
        > line1
        > line2
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
    r"""Convert text to lowercase.

    Transforms all characters in the input text to lowercase.

    Supported Types:
        text

    Example:
        >>> from userTypeParser.TextParser import TextParser
        >>> parser = TextParser("Hello WORLD")
        >>> action = toLowerCaseAction({"text": parser})
        >>> print(action)
        hello world
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
    r"""Convert text to UPPERCASE.

    Transforms all characters in the input text to uppercase.

    Supported Types:
        text

    Example:
        >>> from userTypeParser.TextParser import TextParser
        >>> parser = TextParser("Hello world")
        >>> action = toUperCaseAction({"text": parser})
        >>> print(action)
        HELLO WORLD
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
    r"""Count occurrences of each unique line.

    Analyzes text and counts how many times each unique line appears.

    Supported Types:
        text

    Example:
        >>> from userTypeParser.TextParser import TextParser
        >>> parser = TextParser("apple\nbanana\napple\napple\nbanana")
        >>> action = countAction({"text": parser})
        >>> print(action)
        3	apple
        2	banana
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
    r"""Find and replace text using regular expressions.

    Performs regex-based search and replace operations on text using Python's re.sub().

    Supported Types:
        text

    Parameters:
        Search (text): Regular expression pattern to find.
            Default: "" (empty string)
        Replace (text): Replacement string (supports regex groups like \1, \2).
            Default: "" (empty string)

    Example:
        >>> from userTypeParser.TextParser import TextParser
        >>> parser = TextParser("Hello 123 World 456")
        >>> action = findReplaceAction({"text": parser})
        >>> action.complex_param = {"Search": r"\d+", "Replace": "###"}
        >>> print(action)
        Hello ### World ###
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

class ReplaceDelimiterAction(actionInterface):
    r"""Replace delimiters in text using regex substitution.

    Searches for delimiter patterns and replaces them with different delimiters.
    Useful for converting between CSV, TSV, newline-separated formats.

    Supported Types:
        text

    Parameters:
        Search (list): Delimiter to search for.
            Choices: Comma, Line return (CRLF), Line return (LF), Colon, Tab
            Default: Line return (CRLF)
        Replace (list): Delimiter to replace with.
            Choices: Comma, Line return (CRLF), Line return (LF), Colon, Tab
            Default: Line return (CRLF)

    Example:
        >>> from userTypeParser.TextParser import TextParser
        >>> parser = TextParser("apple,banana,cherry")
        >>> action = ReplaceDelimiterAction({"text": parser})
        >>> action.complex_param["Search"]["value"] = "Comma"
        >>> action.complex_param["Replace"]["value"] = "Line return (LF)"
        >>> print(action)
        apple
        banana
        cherry
    """

    DELIMITER_MAP = {
        "Comma": ",",
        "Line return (CRLF)": "\r\n",
        "Line return (LF)": "\n",
        "Colon": ":",
        "Tab": "\t"
    }

    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param={"Search":{"type":"list", "value":"Line return (CRLF)","choices":["Comma","Line return (CRLF)","Line return (LF)","Colon","Tab"]},"Replace":{"type":"list","value":"Line return (CRLF)","choices":["Comma","Line return (CRLF)","Line return (LF)","Colon","Tab"]}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param=complex_param)
        self.description = "Regex: Find and replace delimiter"

    def execute(self) -> object:
        """Execute delimiter replacement on parsed text.

        Returns:
            str: Text with delimiters replaced.
        """
        self.observables = self.get_observables()
        if self.observables.get("text"):
            text = self.observables.get("text")[0]
            search_label = self.get_param_value('Search')
            replace_label = self.get_param_value('Replace')
            search_regex = self.DELIMITER_MAP.get(search_label, search_label)
            replace_regex = self.DELIMITER_MAP.get(replace_label, replace_label)
            return re.sub(search_regex, replace_regex, text, flags= re.MULTILINE)
        return ""

    def __str__(self):
        """Return human-readable representation of delimiter replacement.

        Calls :meth:`execute` and returns the modified text.

        Returns:
            str: Text with replaced delimiters.
        """
        return  self.execute()


class regexFilterAction(actionInterface):
    r"""Filter lines that match a regular expression.

    Keeps only lines that match the specified regex pattern.

    Supported Types:
        text

    Parameters:
        Regex (text): Regular expression pattern to match.
            Default: "" (empty string)

    Example:
        >>> from userTypeParser.TextParser import TextParser
        >>> parser = TextParser("error: failed\ninfo: success\nerror: timeout")
        >>> action = regexFilterAction({"text": parser})
        >>> action.complex_param["Regex"]["value"] = r"^error:"
        >>> print(action)
        error: failed
        error: timeout
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
    r"""Filter lines that do NOT match a regular expression.

    Removes lines that match the specified regex pattern, keeping only non-matching lines.

    Supported Types:
        text

    Parameters:
        Regex (text): Regular expression pattern to exclude.
            Default: "" (empty string)

    Example:
        >>> from userTypeParser.TextParser import TextParser
        >>> parser = TextParser("error: failed\ninfo: success\nerror: timeout")
        >>> action = reverseRegexFilterAction({"text": parser})
        >>> action.complex_param["Regex"]["value"] = r"^error:"
        >>> print(action)
        info: success
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
    r"""Extract captured groups from regex matches.

    Applies a regex with capturing groups to text and extracts all matched
    groups. Results are tab-separated if multiple groups exist.

    Supported Types:
        text

    Parameters:
        Regex (text): Regular expression with capturing groups.
            Example: r"(\w+)@(\w+\.\w+)" extracts username and domain
            Default: "" (empty string)

    Example:
        >>> from userTypeParser.TextParser import TextParser
        >>> parser = TextParser("user@example.com admin@test.org")
        >>> action = extractRegexGroupAction({"text": parser})
        >>> action.complex_param["Regex"]["value"] = r"(\w+)@(\w+\.\w+)"
        >>> print(action)
        user	example.com
        admin	test.org
    """

    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param= {"Regex":{"type":"text","value":""}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param = complex_param)
        self.description = "Regex: Extract group"
        
    def execute(self) -> object:
        """Execute regex group extraction on parsed text.

        Returns:
            str: Tab-separated groups, one match per line.
        """
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
        """Return human-readable representation of extracted groups.

        Calls :meth:`execute` and returns the extracted groups.

        Returns:
            str: Extracted regex groups.
        """
        return  self.execute()

class timestampToDateAction(actionInterface):
    r"""Convert Unix timestamps to human-readable dates.

    Searches for 10-digit Unix timestamps in text and converts them to
    datetime strings.

    Supported Types:
        text

    Example:
        >>> from userTypeParser.TextParser import TextParser
        >>> parser = TextParser("Event at 1609459200 and 1640995200")
        >>> action = timestampToDateAction({"text": parser})
        >>> print(action)
        2021-01-01 00:00:00
        2022-01-01 00:00:00
    """
    
    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param={}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param= complex_param)
        self.description = "Timestamp: To date"
        
    def execute(self) -> object:
        """Execute timestamp conversion on parsed text.

        Finds all 10-digit timestamps and converts to datetime strings.

        Returns:
            str: Converted dates, one per line, or error message.
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
        """Return human-readable representation of converted timestamps.

        Calls :meth:`execute` and returns the date strings.

        Returns:
            str: Converted datetime strings.
        """
        return  self.execute()

class fromHexAction(actionInterface):
    r"""Decode hexadecimal string to UTF-8 text.

    Converts hexadecimal-encoded text back to UTF-8. Input should NOT include
    0x prefix (use "48656c6c6f" not "0x48656c6c6f").

    Supported Types:
        text

    Example:
        >>> from userTypeParser.TextParser import TextParser
        >>> parser = TextParser("48656c6c6f")
        >>> action = fromHexAction({"text": parser})
        >>> print(action)
        Hello
    """
    
    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param={}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param= complex_param)
        self.description = "Hex: To UTF-8"
        
    def execute(self) -> object:
        """Execute hex decoding on parsed text.

        Returns:
            str: Decoded UTF-8 string or error message.
        """
        if self.get_observables().get("text"):
            text = self.observables.get("text")[0]
            try:
                return bytes.fromhex(text).decode('utf-8')
            except Exception as e:
                return "Invalid hexadecimal: " + str(e)
        return "No text found."

    def __str__(self):
        """Return human-readable representation of decoded hex.

        Calls :meth:`execute` and returns the decoded text.

        Returns:
            str: UTF-8 decoded text.
        """
        return  self.execute()
    
class UrlUnquoteAction(actionInterface):
    r"""Decode URL-encoded (percent-encoded) text.

    Converts percent-encoded characters back to their original form.

    Supported Types:
        text

    Example:
        >>> from userTypeParser.TextParser import TextParser
        >>> parser = TextParser("%22Hello%20World%21%22")
        >>> action = UrlUnquoteAction({"text": parser})
        >>> print(action)
        "Hello World!"
    """
    
    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param={}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param= complex_param)
        self.description = "URL decode"
        
    def execute(self) -> object:
        """Execute URL decoding on parsed text.

        Returns:
            str: URL-decoded text or error message.
        """
        if self.get_observables().get("text"):
            text = self.observables.get("text")[0]
            try:
                return unquote(text)
            except Exception as e:
                return "Invalid URL encoding: " + str(e)
        return "No text found."

    def __str__(self):
        """Return human-readable representation of decoded URL text.

        Calls :meth:`execute` and returns the decoded text.

        Returns:
            str: URL-decoded text.
        """
        return  self.execute()
    
class UrlQuoteAction(actionInterface):
    r"""Encode text to URL-safe percent-encoded format.

    Converts special characters to percent-encoded equivalents for safe use
    in URLs.

    Supported Types:
        text

    Example:
        >>> from userTypeParser.TextParser import TextParser
        >>> parser = TextParser("Hello World!")
        >>> action = UrlQuoteAction({"text": parser})
        >>> print(action)
        Hello%20World%21
    """
    
    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param={}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param= complex_param)
        self.description = "URL encode"
        
    def execute(self) -> object:
        """Execute URL encoding on parsed text.

        Returns:
            str: URL-encoded text or error message.
        """
        if self.get_observables().get("text"):
            text = self.observables.get("text")[0]
            try:
                return quote(text)
            except Exception as e:
                return "Invalid URL encoding: " + str(e)
        return "No text found."

    def __str__(self):
        """Return human-readable representation of encoded URL text.

        Calls :meth:`execute` and returns the encoded text.

        Returns:
            str: URL-encoded text.
        """
        return  self.execute()
    
class HtmlUnquoteAction(actionInterface):
    r"""Decode HTML entities to plain text.

    Converts HTML character entities back to their original characters.

    Supported Types:
        text

    Example:
        >>> from userTypeParser.TextParser import TextParser
        >>> parser = TextParser("&lt;div&gt;Hello &amp; Goodbye&lt;/div&gt;")
        >>> action = HtmlUnquoteAction({"text": parser})
        >>> print(action)
        <div>Hello & Goodbye</div>
    """
    
    def __init__(self, parsers = {}, supportedType = {"text"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "HTML entity decode"
        
    def execute(self) -> object:
        """Execute HTML entity decoding on parsed text.

        Returns:
            str: Decoded text or error message.
        """
        if self.get_observables().get("text"):
            text = self.observables.get("text")[0]
            try:
                return html.unescape(text)
            except Exception as e:
                return "Invalid HTML encoding: " + str(e)
        return "No text found."

    def __str__(self):
        """Return human-readable representation of decoded HTML.

        Calls :meth:`execute` and returns the decoded text.

        Returns:
            str: HTML entity decoded text.
        """
        return  self.execute()
    
class HtmlQuoteAction(actionInterface):
    r"""Encode special characters as HTML entities.

    Converts characters like <, >, & to their HTML entity equivalents.

    Supported Types:
        text

    Example:
        >>> from userTypeParser.TextParser import TextParser
        >>> parser = TextParser("<div>Hello & Goodbye</div>")
        >>> action = HtmlQuoteAction({"text": parser})
        >>> print(action)
        &lt;div&gt;Hello &amp; Goodbye&lt;/div&gt;
    """
    
    def __init__(self, parsers = {}, supportedType = {"text"}):
        super().__init__(parsers = parsers, supportedType = supportedType)
        self.description = "HTML entity encode"
        
    def execute(self) -> object:
        """Execute HTML entity encoding on parsed text.

        Returns:
            str: HTML-encoded text or error message.
        """
        if self.get_observables().get("text"):
            text = self.observables.get("text")[0]
            try:
                return html.escape(text)
            except Exception as e:
                return "Invalid HTML encoding: " + str(e)
        return "No text found."

    def __str__(self):
        """Return human-readable representation of encoded HTML.

        Calls :meth:`execute` and returns the encoded text.

        Returns:
            str: HTML entity encoded text.
        """
        return  self.execute()
    

class toHexAction(actionInterface):
    r"""Encode UTF-8 text as hexadecimal string.

    Converts text to its hexadecimal byte representation.

    Supported Types:
        text

    Example:
        >>> from userTypeParser.TextParser import TextParser
        >>> parser = TextParser("Hello")
        >>> action = toHexAction({"text": parser})
        >>> print(action)
        48656c6c6f
    """
    
    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param={}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param= complex_param)
        self.description = "Hex: From UTF-8"
        
    def execute(self) -> object:
        """Execute hex encoding on parsed text.

        Returns:
            str: Hexadecimal representation or error message.
        """
        if self.get_observables().get("text"):
            text = self.observables.get("text")[0]
            try:
                return text.encode().hex()
            except Exception as e:
                return str(e)
        return "No text found."

    def __str__(self):
        """Return human-readable representation of hex-encoded text.

        Calls :meth:`execute` and returns the hex string.

        Returns:
            str: Hexadecimal encoded text.
        """
        return  self.execute()

class toplLinesAction(actionInterface):
    r"""Extract the first N lines from text.

    Truncates text to only the specified number of leading lines. Useful for
    previewing large outputs or limiting results.

    Supported Types:
        text

    Parameters:
        Number of lines (text): Maximum number of lines to keep.
            Default: 10

    Example:
        >>> from userTypeParser.TextParser import TextParser
        >>> parser = TextParser("line1\nline2\nline3\nline4\nline5")
        >>> action = toplLinesAction({"text": parser})
        >>> action.complex_param["Number of lines"]["value"] = "3"
        >>> print(action)
        line1
        line2
        line3
    """
    
    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param={"Number of lines":{"type":"text","value":"10"}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param= complex_param)
        self.description = "Top N lines."
        
    def execute(self) -> object:
        """Execute line truncation on parsed text.

        Returns:
            str: First N lines joined with newlines.
        """
        nb = self.get_param_value("Number of lines")
        lines = []
        self.observables = self.get_observables()
        if self.observables.get("text"):
            lines = self.observables.get("text")[0].splitlines()
            return "\n".join([i for i in lines[:min(int(nb), len(lines))]])
        return ""

    def __str__(self):
        """Return human-readable representation of truncated text.

        Calls :meth:`execute` and returns the first N lines.

        Returns:
            str: Truncated text.
        """
        return  self.execute()
    
class saveInFileAction(actionInterface):
    r"""Save text data to a file.

    Writes the current text to a file at the specified path. Creates or
    overwrites the file with UTF-8 encoding.

    Supported Types:
        text

    Parameters:
        Save as (save): File path where text will be saved.
            Default: ./tmp.txt

    Example:
        >>> from userTypeParser.TextParser import TextParser
        >>> parser = TextParser("Hello, World!")
        >>> action = saveInFileAction({"text": parser})
        >>> action.complex_param["Save as"]["value"] = "/tmp/output.txt"
        >>> result = action.execute()
        >>> print(result)
        Hello, World!

    Note:
        Returns the text content after saving (file contents are not read back).
    """
    
    def __init__(self, parsers = {}, supportedType = {"text"}, complex_param={"Save as":{"type":"save","value":"./tmp.txt"}}):
        super().__init__(parsers = parsers, supportedType = supportedType, complex_param= complex_param)
        self.description = "Save as"
        
    def execute(self) -> object:
        """Execute file save operation on parsed text.

        Writes text to configured file path.

        Returns:
            str: The saved text content.
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
        """Return human-readable representation of saved text.

        Calls :meth:`execute` and returns the text that was saved.

        Returns:
            str: Saved text content.
        """
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