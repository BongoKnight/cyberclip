import importlib

from cyberclip.userAction.actionInterface import actionInterface
from cyberclip.utilities import find_delimiter


def test_load_conf_normalizes_key_separators(monkeypatch):
    def fake_dotenv_values(path):
        return {
            "DATALAKE_BASE_URL": "https://datalake.example/api",
            "DATALAKE_EMAIL": "user@example.com",
            "DATALAKE_PASSWORD": "password",
            "MODAT_API-KEY": "hyphen-token",
            "URLSCAN_API_KEY": "underscore-token",
            "URLQUERY_API_KEY": "urlquery-token",
            "SHODAN_API-KEY": "shodan-token",
        }

    action_interface_module = importlib.import_module(
        "cyberclip.userAction.actionInterface"
    )
    monkeypatch.setattr(action_interface_module, "dotenv_values", fake_dotenv_values)

    action = actionInterface()

    assert action.load_conf("Datalake") == {
        "base_url": "https://datalake.example/api",
        "email": "user@example.com",
        "password": "password",
    }
    assert action.load_conf("Modat") == {"api_key": "hyphen-token"}
    assert action.load_conf("UrlScan") == {"api_key": "underscore-token"}
    assert action.load_conf("UrlQuery") == {"api_key": "urlquery-token"}
    assert action.load_conf("Shodan") == {"api_key": "shodan-token"}


class TestFindDelimiter:
    """Test suite for find_delimiter function"""

    def test_find_delimiter_comma(self):
        text = "a,b,c\n1,2,3\n4,5,6"
        assert find_delimiter(text) == ","

    def test_find_delimiter_semicolon(self):
        text = "a;b;c\n1;2;3\n4;5;6"
        assert find_delimiter(text) == ";"

    def test_find_delimiter_tab(self):
        text = "a\tb\tc\n1\t2\t3\n4\t5\t6"
        assert find_delimiter(text) == "\t"

    def test_find_delimiter_pipe(self):
        text = "a|b|c\n1|2|3\n4|5|6"
        assert find_delimiter(text) == "|"

    def test_find_delimiter_quoted_lines(self):
        text = '"a,4"\n"d,3"\n"d,d"'
        assert find_delimiter(text) == ","

    def test_find_delimiter_whole_line_quoted_csv(self):
        text = '"name,age,city"\n"alice,22,paris"\n"bob,35,lyon"'
        assert find_delimiter(text) == ","

    def test_find_delimiter_quoted_fields_csv(self):
        text = '"name","age","city"\n"alice","22","paris"\n"bob","35","lyon"'
        assert find_delimiter(text) == ","

    def test_find_delimiter_with_spaces_around_lines(self):
        text = "   a,b,c   \n   1,2,3   \n   4,5,6   "
        assert find_delimiter(text) == ","

    def test_find_delimiter_plain_text_returns_default(self):
        text = "this is normal text\nwith no actual table\njust words"
        assert find_delimiter(text) == ","

    def test_find_delimiter_single_line_returns_default(self):
        text = "a,b,c"
        assert find_delimiter(text) == ","

    def test_find_delimiter_typographic_quotes(self):
        text = "“name,age,city”\n“alice,22,paris”\n“bob,35,lyon”"
        assert find_delimiter(text) == ","

    def test_find_delimiter_empty_returns_default(self):
        assert find_delimiter("") == ","
