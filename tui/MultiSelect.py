from textual.widgets import Static, Label, Select
from textual.widgets import _select
from textual.containers import Horizontal
from textual.app import ComposeResult
from textual.reactive import var
from textual import on

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
    def __init__(self, label : str ="", value : set = set(), options : list = [], **kwargs):
        super().__init__(**kwargs)
        self._value = set(value)
        self.label = label
        self.options = []
        if options:
            if isinstance(options[0], str) :
                self.options = [(f"{FALSE_EMOTE} {option}", option) for option in options]
            elif isinstance(options[0], tuple):
                self.options = [(f"{TRUE_EMOTE} {option}", option) if is_active else (f"{FALSE_EMOTE} {option}", option) for option, is_active in options]
        self.options.sort(key=lambda option: option[1])
    
    def compose(self) -> ComposeResult:
        yield Horizontal(
            Label(renderable=self.label, id="title"),
            Select(self.options,prompt="Select options..." ,classes="multiselect")
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
                event.control.set_options(new_options)
                event.control.value = None
                break
    
    @on(_select.SelectOverlay.UpdateSelection)
    def reopen(self, event: _select.SelectOverlay.UpdateSelection):
        self.app.notify("Trying to give focus")
        
    
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
                MultiSelect(options=["Arrakis","Chapterhouse","Caladan"]),
                MultiSelect(options=[("Leto",True),("Jessica", False),("Paul",True)]),
                Log(id="log")
            )
        
        @on(Select.Changed)
        def update(self, event: Select.Changed):
            values = event.select.parent.parent.value
            self.app.query_one(Log).write_line(str(values))
    app = SelectApp()
    app.run()