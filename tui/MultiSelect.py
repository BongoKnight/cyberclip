from textual.widgets import Static, Button, Input, Label, Select
from textual.containers import Horizontal, HorizontalScroll
from textual.app import ComposeResult
from textual.reactive import reactive, var
from textual import on, events

TRUE_EMOTE = "✅"
FALSE_EMOTE = "❌"

class MultiSelect(Static):
    value = var(set())
    label = var("")
    options = var([])
    DEFAULT_CSS = """
    MultiSelect{
        height:3;
    }
    #title {
        margin-top: 1;
    }
    """
    def __init__(self, label : str ="Select options", value : set = set(), options : list = [], **kwargs):
        super().__init__(**kwargs)
        self._value = set(value)
        self.label = label
        self.options = [(f"{FALSE_EMOTE} {option}", option) for option in options]
    
    def compose(self) -> ComposeResult:
        yield Horizontal(
            Label(renderable=self.label, id="title"),
            Select(self.options,prompt=self.label ,classes="multiselect")
        )
    

    @on(Select.Changed)
    def switch_state(self, event: Select.Changed) -> None:
        for index, option in enumerate(self.options):
            if event.value == option[1]:
                new_options = self.options
                if option[0].startswith(FALSE_EMOTE):
                    new_options[index] = (f"{TRUE_EMOTE} " + option[1], option[1])
                else :
                    new_options[index] = (f"{FALSE_EMOTE} " + option[1], option[1])
                self.options = new_options
                event.select.set_options(new_options)
                event.select.value = None
                break

    @property
    def value(self) -> list[str]:
        return [option[1] for option in self.options if option[0].startswith(TRUE_EMOTE)]

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
                MultiSelect(options=["Leto","Jessica","Paul"]),
                Log(id="log")
            )
        
        @on(Select.Changed)
        def update(self, event: Select.Changed):
            values = self.query_one(MultiSelect).value
            self.app.query_one(Log).write_line(str(values))
    app = SelectApp()
    app.run()