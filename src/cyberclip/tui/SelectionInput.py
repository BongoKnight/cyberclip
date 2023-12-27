from textual import events
from textual.widgets import Static, Label, SelectionList
from textual.containers import Horizontal
from textual.app import ComposeResult
from textual.reactive import var
from textual import on


class SelectionInput(Static):
    value = var(set(""))
    label = var("")
    DEFAULT_CSS = """
    SelectionInput{
        height: 1fr;
        max-height: 10;
    }
    SelectionList {
        padding: 1;
        border: solid $accent;
        max-height: 10;
        margin: 0;
    }
    """
    def __init__(self, label : str ="", choices : list[str] ="", **kwargs):
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
                SelectionInput(choices=["Arrakis","Chapterhouse","Caladan"]),
                Log(id="log")
            )
        
        @on(SelectionList.SelectedChanged)
        def update(self, event: SelectionList.SelectedChanged):
            values = event.selection_list.parent.parent.value
            self.app.query_one(Log).write_line(str(values))
    app = SelectApp()
    app.run()