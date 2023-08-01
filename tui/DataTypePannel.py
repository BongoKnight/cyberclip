import pyperclip
from textual.reactive import var
from textual.containers import  VerticalScroll, Horizontal
from textual.widgets import Static,  Button, Switch
from textual.app import ComposeResult
from clipboardHandler import get_clipboard_data

class DataTypeButton(Static):
    """A dataType widget to extract and handle actions on one specific types of data."""
    DEFAULT_CSS = """#left-pannel{
        row-span:5;
        column-span: 1;
        height:100%;
        row-span:5;

    }

    #filter-button{
        width: 100%;
    }

    #data-type-container{
        row-span: 5;
        column-span: 1;    
    }

    #datatype-button{
        width: 80%;
        height: 3;
    }

    .datatype{
        width: 100%;
        height: 3;
    }

    #update-button{
        width: 100%;
        height:3;
    }"""
    parser_type = var("text")

    def compose(self) -> ComposeResult:
        """Create child widgets of a dataType.""" 
        yield Horizontal(
             Button(self.parser_type, id="datatype-button", classes=""),
             Switch(value=True, id="datatype-active")
             )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a  button is pressed."""
        if event.button.id == "datatype-button":
            from tui.ContentView import ContentView
            mainApp = self.parent.ancestors[-1].query_one(ContentView)
            if mainApp:
                mainApp.text = "\n".join(mainApp.parser.results["matches"].get(self.parser_type, ""))
                mainApp.filter_action()


    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Event handler called when Switch is pressed."""
        from tui.ContentView import ContentView
        mainApp = self.parent.ancestors[-1].query_one(ContentView)
        mainApp.filter_action()

class DataLoader(Static):
    """A dataLoader widget."""
    select_all_datatype = var(True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        from tui.ContentView import ContentView
        if event.button.id == "update-button":
            data = get_clipboard_data()
            text_data = data.get(1,"") # 1 is textual data in Windows clipboard
            utf8_data = data.get(13,"") # 13 is UTF8 data in Windows clipboard
            filepath_data = "\r\n".join(data.get(15, [])) # 15 is file data in textual Clipboard
            if utf8_data:
                self.data = '\r\n'.join(list(set([filepath_data, utf8_data])))
            elif text_data:
                self.data ='\r\n'.join(list(set([filepath_data, text_data])))
            else :
                self.data ='\r\n'.join(list(set([filepath_data])))
            mainApp = self.ancestors[-1].query_one(ContentView)
            if mainApp: 
                mainApp.text = self.data
        if event.button.id == "filter-button":
            self.select_all_datatype = not  self.select_all_datatype 
            for switch in self.query(Switch):
                switch.value = self.select_all_datatype

    def add_dataType(self, type_of_data: str) -> DataTypeButton:
        """An action to add a timer."""
        new_datatype = DataTypeButton(classes="datatype")
        self.query_one("#data-type-container").mount(new_datatype)
        new_datatype.scroll_visible()
        new_datatype.parser_type = type_of_data 

    def compose(self) -> ComposeResult:
        """Create child widgets of a dataLoader."""
        yield Button("Reset", id="update-button", variant="success")
        yield VerticalScroll(id="data-type-container")
        yield Button("(Un)select all", id="filter-button", variant="primary")