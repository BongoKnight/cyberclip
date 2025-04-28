from textual.widgets import Static, Button, Input, Label
from textual.containers import Horizontal, HorizontalScroll
from textual.app import ComposeResult
from textual.reactive import reactive, var
from textual import on, events
from textual.message import Message

class TagsInput(Static):
    value = var(set())
    label = var("")
    DEFAULT_CSS = """
    TagsInput{
        max-width: 100%;
        width: auto;
        layout: horizontal;
        padding: 1;
    }
    TagsInput > Input {
        width: 25;
    }
    TagsInput > Label{
        margin-top: 1;
        width: 25;
    }
    .tag-storage{
        height:5;
        align-horizontal: left;
    }

    """
    BINDINGS = [("ctrl+r", "delete_all", "Delete all tags")]
    _value = reactive(set[str], recompose=True)
    def __init__(self, label : str ="", value : set = set(), **kwargs):
        super().__init__(**kwargs)
        self._value = set(value)
        self.label = label
    
    def compose(self) -> ComposeResult:
        yield Label(renderable=self.label)
        yield Input(placeholder=f"Enter {self.label.lower()}...",classes="inputag")
        yield HorizontalScroll(*[Tag(value=value, parent_input = self) for value in self._value] ,classes="tag-storage")
    
    @on(Input.Submitted, ".inputag")
    def add_tag(self, event : events.Key) -> None:
        input =  self.query_one(Input)
        if input.value and input.value not in self._value:
            new_tag = Tag(value=input.value)
            new_tag.parent_input = self
            self.query_one(HorizontalScroll).mount(new_tag)
            self._value.add(input.value)
            input.value = ""
            self.query_one(Input).focus()
        
    def action_delete_all(self):
        self._value = set()
        for child in self.query_one(HorizontalScroll).children:
            assert isinstance(child, Tag)
            child.post_message(child.Deleted(child.value))
            child.remove()

    @property
    def value(self):
        return list(self._value)
    


            

        

class Tag(Static):
    DEFAULT_CSS = """
    Tag > Button {
        border: none;
        min-width: 3;
        background: $primary;
        height: 1;
    }

    Tag > Button:hover {
        background: $primary-lighten-1;
        border: none;
        height: 1;
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
    parent_input = var(None)
    def __init__(self, value="", parent_input=None, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.parent_input = parent_input

    def compose(self) -> ComposeResult:
        yield Button(self.value, id="tag-value")
        yield Button("❌", id="delete")

    @on(Button.Pressed)
    def edit_tag(self, event : Button.Pressed):
        if self.parent_input:
            self.parent_input.query_one(Input).focus()
            if event.button.id == "tag-value":
                self.parent_input.query_one(Input).value = self.value
                self.parent_input._value.remove(self.value)
            else:
                self.parent_input._value.remove(self.value)
                self.post_message(self.Deleted(self.value))
            self.remove()
        event.stop()
        
    
    class Deleted(Message):
        """Deleted Value"""
        def __init__(self, value: str) -> None:
            self.value = value
            super().__init__()

if __name__ == "__main__":
    from textual.app import App

    class ClassApp(App):
        def compose(self):
            yield TagsInput("Test",value=["titi","toto"])
    app = ClassApp()
    app.run()