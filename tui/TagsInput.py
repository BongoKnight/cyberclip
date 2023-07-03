from textual.widgets import Static, Button, Input, Label
from textual.containers import Horizontal, HorizontalScroll
from textual.app import ComposeResult
from textual.reactive import reactive, var
from textual import on, events

class TagsInput(Static):
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
        yield HorizontalScroll(classes="tag-storage")
    
    @on(Input.Submitted)
    def add_tag(self, event : events.Key) -> None:
        input =  self.query_one(Input)
        if input.value and input.value not in self._value:
            new_tag = Tag(value=input.value)
            self.query_one(HorizontalScroll).mount(new_tag)
            self._value.add(input.value)
            input.value = ""
            self.query_one(Input).focus()
    
    @property
    def value(self):
        return list(self._value)
            

        

class Tag(Static):
    DEFAULT_CSS = """
    Tag > Button {
        border: none;
        height: 1;
        min-width: 0;
        background: $primary;
    }
    Tag > Button:hover {
        background: $primary-darken-1;
        color: white;
    }
    Tag {
        margin-top: 1;
        margin-left: 1;
        layout: horizontal;
        height: 4;
        width: auto;
    }
    """
    value = var("")
    def __init__(self, value="", **kwargs):
        super().__init__(**kwargs)
        self.value = value 

    def compose(self) -> ComposeResult:
        yield Button(self.value, id="tag-value")
        yield Button("❌")

    @on(Button.Pressed)
    def edit_tag(self, event : Button.Pressed):
        self.ancestors[1].query_one(Input).focus()
        if event.button.id == "tag-value":
            self.ancestors[1].query_one(Input).value = self.value
            self.ancestors[2].query_one(TagsInput).value.remove(self.value)
            self.remove()
        else:
            self.ancestors[2].query_one(TagsInput).value.remove(self.value)
            self.remove()
        event.stop()


