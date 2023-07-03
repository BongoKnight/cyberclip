from textual import events
from textual.widgets import Static, Label, SelectionList
from textual.widgets.selection_list import Selection
from textual.containers import Horizontal
from textual.app import ComposeResult
from textual.reactive import var

class SelectionInput(Static):
    value = var(set(""))
    label = var("")
    DEFAULT_CSS = """
    SelectionList {
        padding: 1;
        border: solid $accent;
        max-height: 10;
        margin: 0;
    }
    """
    def __init__(self, label : str ="", choices : str ="", **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.choices = choices
    
    def _on_mount(self) -> None:
        self.query_one(SelectionList).border_title = self.label

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Label(self.label, markup=False),
            SelectionList[str](*[(str(choice), choice, False) for choice in self.choices])
            )

    @property
    def value(self):
        try:
            return list(set(str(value) for value in self.query_one(SelectionList).selected))
        except:
            return []