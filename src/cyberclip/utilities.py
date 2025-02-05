import re

def clean_tsv(new_text: str, text:str):
    """If new_text is a TSV value that starts with text as a first field, returns everythings except this field

    Code exemple ::
    clean_tsv("a\tbaba", "a")
    >>> "baba"
    clean_tsv("b\tbaba", "a")
    >>> "b\tbaba"
    """
    result = new_text
    if new_text.startswith(f"{text}\t"):
        result = re.sub("^"+re.escape(text)+"\t", "", new_text)
    return result
