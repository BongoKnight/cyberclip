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
        max-width: 100%;
        width: auto;
        layout: horizontal;
    }
    TagsInput > Input, Label {
        width: 25;
    }
    TagsInput > Label {
        margin-top: 1;
    }
    .tag-storage{
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
        yield Input(placeholder=f"Enter {self.label}...",classes="inputag")
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
            self.remove()
        event.stop()


if __name__ == "__main__":
    from textual.app import App

    class ClassApp(App):
        def compose(self):
            yield TagsInput("Test",value=["titi","toto"])
    app = ClassApp()
    app.run()