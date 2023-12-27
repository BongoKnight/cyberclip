from textual.widgets import Static, Label, Input
from textual.containers import Horizontal
from textual.app import ComposeResult
from textual.reactive import var
from textual import on, events

class SimpleInput(Static):
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