import pyperclip
from rich.console import RenderableType
from textual.reactive import var
from textual.containers import  VerticalScroll, Horizontal, Vertical
from textual.widgets import Static,  Button, Switch, TextArea
from textual.app import ComposeResult
from clipboardHandler import get_clipboard_text

class DataTypeButton(Static):
    """A dataType widget to extract and handle actions on one specific types of data."""
    DEFAULT_CSS = """
"""
    parser_type = var("text")

    def __init__(self, active: bool = True, renderable: RenderableType = "", *, expand: bool = False, shrink: bool = False, markup: bool = True, name: str | None = None, id: str | None = None, classes: str | None = None, disabled: bool = False) -> None:
        super().__init__(renderable, expand=expand, shrink=shrink, markup=markup, name=name, id=id, classes=classes, disabled=disabled)
        self._active = active

    def compose(self) -> ComposeResult:
        """Create child widgets of a dataType.""" 
        yield Horizontal(
             Button(self.parser_type, id="datatype-button", classes=""),
             Switch(value=self._active, id="datatype-active"), classes="datatype"
             )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a  button is pressed."""
        if event.button.id == "datatype-button":
            from tui.ContentView import ContentView
            contentView = self.parent.ancestors[-1].query_one(ContentView)
            if contentView:
                contentView.text = "\n".join(self.app.parser.results["matches"].get(self.parser_type, ""))
                contentView.filter_action()
    
    @property
    def switch(self) -> Switch:
        try:
            return self.query_one(Switch)
        except:
            return


    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Event handler called when Switch is pressed."""
        from tui.ContentView import ContentView
        contentView = self.parent.ancestors[-1].query_one(ContentView)
        contentView.filter_action()

class DataLoader(Static):
    """A dataLoader widget."""
    select_all_datatype = var(True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        from tui.ContentView import ContentView
        if event.button.id == "update-button":
            self.data = get_clipboard_text()
            mainApp = self.ancestors[-1].query_one(ContentView)
            if mainApp: 
                mainApp.text = self.data
        if event.button.id == "text-update-button":
            mainApp = self.ancestors[-1].query_one(ContentView)
            self.data = mainApp.query_one(TextArea).text
            if mainApp: 
                mainApp.text = self.data
        if event.button.id == "filter-button":
            self.select_all_datatype = not  self.select_all_datatype 
            for switch in self.query(Switch):
                switch.value = self.select_all_datatype

    def add_dataType(self, type_of_data: str, active : bool = True) -> DataTypeButton:
        """An action to add a timer."""
        new_datatype = DataTypeButton(classes="datatype", active=active)
        self.query_one("#data-type-container").mount(new_datatype)
        new_datatype.scroll_visible()
        new_datatype.parser_type = type_of_data 
        return new_datatype

    def compose(self) -> ComposeResult:
        """Create child widgets of a dataLoader."""
        yield Vertical(
            Button("Parse clip", id="update-button", variant="success"),
            Button("Parse text", id="text-update-button", variant="primary"), classes='update'
        )
        yield VerticalScroll(id="data-type-container")
        yield Button("(Un)select all", id="filter-button", variant="primary")