from textual.widgets import Static, Label, Input, Select, TextArea
from textual.containers import Horizontal
from textual.app import ComposeResult
from textual.reactive import var
from textual import on, events

class SimpleInput(Static):
    DEFAULT_CSS = """
    SimpleInput {
        margin: 1 1;
        height: 5;
    }
    SimpleInput Label {
        width: 25;
        margin-top: 1;
    }
    """
    value = var(set(""))
    label = var("")
    def __init__(self, label : str ="", value : str ="", **kwargs):
        super().__init__(**kwargs)
        self._value = value
        self.label = label

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Label(self.label, markup=False),
            Input(value=self._value, placeholder="Enter text here...")
            )
    @property
    def value(self):
        return self.query_one(Input).value
    
class SimpleTextArea(Static):
    DEFAULT_CSS = """
    SimpleTextArea {
        margin: 1 1;
        width: auto;
        height: 15;
    }
    SimpleTextArea Label {
        width: 25;
        margin-top: 1;
    }
    SimpleTextArea TextArea {
        width: 1fr;
        height: 15;
        margin: 1;
    }
    """
    value = var(set(""))
    label = var("")
    def __init__(self, label : str ="", value : str ="", choices : list[str] = [], **kwargs):
        super().__init__(**kwargs)
        self._value = value
        self.label = label

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Label(self.label, markup=False),
            TextArea(self._value, language="json")
            )
    
    @property
    def value(self):
        return self.query_one(TextArea).text

class SimpleSelect(Static):
    DEFAULT_CSS = """
    SimpleSelect {
        margin: 1 1;
        height: 5;
    }
    SimpleSelect Label {
        width: 25;
        margin-top: 1;
    }
    """
    value = var(set(""))
    label = var("")
    def __init__(self, label : str ="", value : str ="", choices : list[str] = [], **kwargs):
        super().__init__(**kwargs)
        self._value = value
        self.choices = choices
        self.label = label

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Label(self.label, markup=False),
            Select.from_values(self.choices, value=self._value, prompt=f"Select one...")
            )
    
    @property
    def value(self):
        return self.query_one(Select).value