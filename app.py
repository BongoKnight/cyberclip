"""
Code browser example.

Run with:

    python app.py
"""

import sys
import pyperclip
import re

from clipParser import clipParser
from userAction.actionInterface import actionInterface
from rich.syntax import Syntax
from rich.traceback import Traceback

from textual import events
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.reactive import var, reactive
from textual.widgets import Footer, Header, Static, Placeholder, Button, Input
from textual.widget import Widget

class ContentView(Static):
    text= reactive("Waiting for Update...")
    parser = var(clipParser())
    initial_text = var(pyperclip.paste())
    
    def compose(self) -> ComposeResult:
        """Create child widgets of a dataLoader.""" 
        yield Vertical(
            Static(self.initial_text ,name="Content", id="clip-content"),
            Input(placeholder="Add data for custom action.",id="param-input")
        )



    def watch_text(self, old_text: str, new_text) -> None:
        """Called when the text attribute changes."""   
        self.query_one(Static).update(new_text)
        buttons = self.ancestors[-1].query(DataTypeButton)
        if buttons:             
            for button in buttons:
                button.remove()
        buttons = self.ancestors[-1].query(ActionButton)
        if buttons:
            for button in buttons:
                button.remove() 
        parser_types = self.parser.parseData(new_text).get("detectedType")
        parser_types.sort()
        for type_of_data in parser_types:
            self.ancestors[-1].query_one(DataLoader).add_dataType(type_of_data)

        for action_name, action in self.parser.actions.items():
            for type_of_data in parser_types:
                if type_of_data in action.supportedType:
                    self.ancestors[-1].query_one(ActionPannel).add_action(action)
                    break



class DataTypeButton(Static):
    """A dataType widget for action specific to certain types of data."""
    parser_type = var("text")
    def compose(self) -> ComposeResult:
        """Create child widgets of a dataType.""" 
        yield Button(self.parser_type, id="datatype-button", classes="")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a  button is pressed."""
        if event.button.id == "datatype-button":
            mainApp = self.parent.ancestors[-1].query_one(ContentView)
            if mainApp:
                mainApp.text = "\n".join(mainApp.parser.results["matches"].get(self.parser_type, ""))

class DataLoader(Static):
    """A dataLoader widget."""
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "update-button":
            self.data = pyperclip.paste()
            mainApp = self.ancestors[-1].query_one(ContentView)
            if mainApp: 
                mainApp.text = self.data    

    def add_dataType(self, type_of_data: str) -> None:
        """An action to add a timer."""
        new_datatype = DataTypeButton()
        self.query_one("#data-type-container").mount(new_datatype)
        new_datatype.scroll_visible()
        new_datatype.parser_type = type_of_data 

    def compose(self) -> ComposeResult:
        """Create child widgets of a dataLoader.""" 
        yield Button("Reset", id="update-button", variant="success")
        yield Vertical(id="data-type-container")


class ActionButton(Static):
    """A action widget for action specific to certain types of data."""
    action = var(None)
    action_name = var("")
    def compose(self) -> ComposeResult:
        yield Button(self.action_name, id="action-button", classes="")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a  button is pressed."""
        if event.button.id == "action-button":
            mainApp = self.parent.ancestors[-1].query_one(ContentView)
            if mainApp:
                if self.parent.ancestors[-1].query_one("#param-input").value:
                    self.action.param = self.parent.ancestors[-1].query_one("#param-input").value
                self.parent.ancestors[-1].query_one("#param-input").value = ""
                mainApp.text = str(self.action)

class ActionPannel(Static):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Filter actions", id="action-filter")
        yield Vertical(id="action-container")   

    def add_action(self, action_module: actionInterface) -> None:
        """An action to add a timer."""
        existing_action = False
        new_action = ActionButton()
        new_action.action = action_module
        new_action.action_name = action_module.description
        self.query_one("#action-container").mount(new_action)
        new_action.scroll_visible() 

    def on_input_changed(self, event: Input.Changed) -> None:
        actions = self.query(ActionButton)
        for action in actions:
            action.visible = True
            action.remove_class("no-height")
            for word in event.value.split():
                if not re.search(f"(?i){word}", action.action.description, re.IGNORECASE):
                    if not word in action.action.supportedType:
                        action.visible = False
                        action.add_class("no-height")

    def action_match(action, value):
        if re.search(f"(?i){value}", action.action.description, re.IGNORECASE):
            return True
        elif value in action.action.supportedType:
            return True
        else:
            return



class ClipBrowser(App):
    """Textual clipboard browser app."""

    CSS_PATH = "app.css"
    BINDINGS = [
        ("ctrl+s", "save", "Save actual view."),
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+b", "copy", "Copy actual content to clipboard."),
        ("ctrl+r", "reset", "Reset content view to clipboard content."),


    ]

    def compose(self) -> ComposeResult:
        """Compose our UI."""
        yield DataLoader(id="left-pannel")
        yield ContentView(id="content-view")    
        yield ActionPannel(id="action-pannel")
        yield Footer()

    def action_quit(self):
        sys.exit()

    def action_save(self):      
        with open("clipboard.txt", "w") as f:
            f.write(self.query_one(ContentView).text)

    def action_copy(self):
        pyperclip.copy(self.query_one(ContentView).text)

    def action_reset(self):
        self.query_one(ContentView).text = pyperclip.paste()
        

if __name__ == "__main__":
    ClipBrowser().run()
