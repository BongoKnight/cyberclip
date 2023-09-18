from textual.widgets import Static, Button, Input, Label
from textual.containers import Horizontal, HorizontalScroll
from textual.app import ComposeResult
from textual.reactive import reactive, var
from textual import on, events

class MultiSelect(Static):
    value = var(set())
    label = var("")
    DEFAULT_CSS = """
    TagsInput{
        layout: horizontal;
    }
    TagsInput > Input, Label {
        width: 25;
    }

    HorizontalScroll{
        height:4;
        align-horizontal: left;
        }

    """
    def __init__(self, label : str ="", value : set = set(), **kwargs):
        super().__init__(**kwargs)
        self._value = set(value)
        self.label = label
    
    def compose(self) -> ComposeResult:
        yield Label(renderable=self.label)
        yield Input(placeholder=f"Enter {self.label}...")
        yield HorizontalScroll(*[Tag(value=value, parent_input = self) for value in self._value] ,classes="tag-storage")
    
    @on(Input.Submitted)
    def filter_entries(self, event : events.Key) -> None:
        return
    
    @property
    def value(self):
        return list(self._value)

if __name__ == "__main__":
    from textual.app import App, ComposeResult 
    MultiSelect().run()