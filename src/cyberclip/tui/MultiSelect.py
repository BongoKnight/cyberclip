from textual.widgets import Static, Label, Select
from textual.widgets import _select
from textual.containers import Horizontal
from textual.app import ComposeResult
from textual.message import Message
from textual.reactive import var
from textual import on
from typing import TYPE_CHECKING, ClassVar

TRUE_EMOTE = "✅"
FALSE_EMOTE = "❌"



if TYPE_CHECKING:
    from typing_extensions import Self

class MultiSelect(Static):
    value = var(set())
    label = var("")
    options = var([])
    DEFAULT_CSS = """
    MultiSelectMinimal{
        height:3;
    }
    #title {
        margin-top: 1;
    }
    """
 
    def __init__(self, label : str ="", value : set = set(), options : list = [], prompt="Select options...", **kwargs):
        super().__init__(**kwargs)
        self._value = set(value)
        self.label = label
        self.options = []
        self.prompt = prompt
        self.select_all = True
        if options:
            if isinstance(options[0], str) :
                self.options = [(f"{FALSE_EMOTE} {option}", option) for option in options]
            elif isinstance(options[0], tuple):
                self.options = [(f"{TRUE_EMOTE} {option}", option) if is_active else (f"{FALSE_EMOTE} {option}", option) for option, is_active in options]
        self.options.sort(key=lambda option: option[1])
    
    def compose(self) -> ComposeResult:
        yield Horizontal(
            Label(renderable=self.label, id="title"),
            Select(self.options, prompt=self.prompt ,classes="multiselect", allow_blank=True)
        )
    
    class Changed(Message):
        def __init__(self, multi_select, **kwargs) -> None:
            super().__init__(**kwargs)
            self._multiselect = multi_select
        
        @property
        def multi_select(self):
            """The MultiSelect that was changed."""
            assert isinstance(self._multiselect, MultiSelect)
            return self._multiselect
        
    def select_or_deselect_all(self):
        self.select_all = not self.select_all
        new_options = self.options
        for index, option in enumerate(self.options):
            if self.select_all:    
                new_options[index] = (f"{TRUE_EMOTE} " + option[1], option[1])
            else:
                new_options[index] = (f"{FALSE_EMOTE} " + option[1], option[1])
        self.options = new_options
        self.select.set_options(new_options)
        self.select.clear()


    @on(Select.Changed)
    def switch_state(self, event: Select.Changed) -> None:
        if event.value == None:
            self.select_or_deselect_all()
        else:
            for index, option in enumerate(self.options):
                if event.value == option[1]:
                    new_options = self.options
                    if option[0].startswith(FALSE_EMOTE):
                        new_options[index] = (f"{TRUE_EMOTE} " + option[1], option[1])
                    else :
                        new_options[index] = (f"{FALSE_EMOTE} " + option[1], option[1])
                    self.options = new_options
                    event.control.set_options(new_options)
        self.post_message(self.Changed(self))


    @property
    def select(self) -> Select:
        return self.query_one(Select)
    
    @property
    def value(self) -> list[str]:
        return [option[1] for option in self.options if option[0].startswith(TRUE_EMOTE)]
    
    @value.setter
    def value(self, value: list):
        self._value = list(set(value))
        if self._value:
            if isinstance(self._value[0], str) :
                self.options = [(f"{FALSE_EMOTE} {option}", option) for option in self._value]
            elif isinstance(self._value[0], tuple):
                    self.options = [(f"{TRUE_EMOTE} {option}", option) if is_active else (f"{FALSE_EMOTE} {option}", option) for option, is_active in self._value]
            self.options.sort(key=lambda option: option[1])
            self.query_one(Select).set_options(self.options)

if __name__ == "__main__":
    from textual.app import App, ComposeResult
    from textual.containers import Vertical
    from textual.widgets import Log
    class SelectApp(App):
        DEFAULT_CSS = """
            #log{
                width: 100%;
                height: 1fr;
                border: blue wide;
                }
        """
        def compose(self) -> ComposeResult:

            yield Vertical(
                MultiSelect(options=["Arrakis","Chapterhouse","Caladan"]),
                MultiSelect(options=[("Leto",True),("Jessica", False),("Paul",True)]),
                Log(id="log")
            )
        
        @on(Select.Changed)
        def update(self, event: Select.Changed):
            values = event.select.parent.parent._value
            self.app.query_one(Log).write_line(str(values))
    app = SelectApp()
    app.run()