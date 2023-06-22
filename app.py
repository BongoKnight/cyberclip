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
from textual.app import App, ComposeResult
from textual.containers import  Vertical, Horizontal, ScrollableContainer
from textual.reactive import var, reactive
from textual.widgets import Footer, Static,  Button, Input, Switch
from tui.ConfigScreen import ConfigScreen

class ContentView(ScrollableContainer):
    text= reactive("Waiting for Update...")
    parser = var(clipParser())
    initial_text = var(pyperclip.paste())
    text_history = var([])
    
    def compose(self) -> ComposeResult:
        """Create child widgets of a dataLoader.""" 
        yield Vertical(
            Static(self.initial_text ,name="Content", id="clip-content", markup=False),
            Button("Copy", id="copy-button"),
            Button(u"\u21A9 Undo", id="previous-button", classes="small-button"),
            Button(u"Redo \u21AA", id="next-button", classes="small-button"),
            Input(placeholder="Add data for custom action.",id="param-input")
        )

    def filter_action(self):
        actionView = self.parent.ancestors[-1].query_one(ActionPannel)
        if actionView:
            actions = actionView.query(ActionButton)
            actual_detected_type = set(self.parser.detectedType)
            for datatype_button in self.parent.ancestors[-1].query(DataTypeButton):
                # Update actions supported_type and hide action buttons where no type are supported
                if datatype_button.query(Switch):
                    if datatype_button.query(Switch)[0].value:
                        for action_button in actions:
                            # Add the supported type if the default action support it.
                            if datatype_button.parser_type in action_button.action_supported_type:
                                action_button.action.supportedType.add(datatype_button.parser_type)
                    else:
                        for action_button in actions:
                            if datatype_button.parser_type in action_button.action_supported_type:
                                action_button.action.supportedType.discard(datatype_button.parser_type)
                
            for action_button in actions:
                if  (len(action_button.action.supportedType.intersection(actual_detected_type)) >=1
                    and len(action_button.action.supportedType.intersection(action_button.action_supported_type)) >= 1
                    ) :
                    action_button.visible = True
                    action_button.remove_class("no-height")
                else:
                    action_button.visible = False
                    action_button.add_class("no-height")

    def watch_text(self, new_text: str) -> None:
        """Called when the text attribute changes."""   

        if new_text not in self.text_history:
            self.text_history.append(new_text)
            self.text_history = self.text_history[-20:]
        self.query_one("#clip-content").update(str(new_text))
        
        self.parser.parseData(new_text)
        parser_types = self.parser.detectedType
        # Update detected type buttons
        buttons = self.ancestors[-1].query(DataTypeButton)
        if buttons:             
            for button in buttons:
                button.remove()
        for type_of_data in parser_types:
            self.ancestors[-1].query_one(DataLoader).add_dataType(type_of_data)

        existing_action = set()
        for action_name, action in self.parser.actions.items():
            for action_button in self.ancestors[-1].query(ActionButton):
                if action_button.action_name == action_name:
                    existing_action.add(action_name)            

        # Add inexisting action buttons
        for action_name, action in self.parser.actions.items():
            if  action_name not in existing_action:
                self.ancestors[-1].query_one(ActionPannel).add_action(action)

        for action in self.ancestors[-1].query(ActionButton):
            action.action.supportedType = set(action.action_supported_type)
            action.action.parsers = self.parser.parsers

        # Filter action on existing active datatype
        self.filter_action()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "copy-button":
            pyperclip.copy(self.text)
        elif button_id == "previous-button":
            if self.text in self.text_history:
                index = self.text_history.index(self.text)
                self.text = self.text_history[max(0, index - 1)]
        elif button_id == "next-button":
            if self.text in self.text_history:
                index = self.text_history.index(self.text)
                self.text = self.text_history[min(len(self.text_history)-1, index + 1)]


class DataTypeButton(Static):
    """A dataType widget to extract and handle actions on one specific types of data."""
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
            mainApp = self.parent.ancestors[-1].query_one(ContentView)
            if mainApp:
                mainApp.text = "\n".join(mainApp.parser.results["matches"].get(self.parser_type, ""))
                mainApp.filter_action()


    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Event handler called when Switch is pressed."""
        mainApp = self.parent.ancestors[-1].query_one(ContentView)
        mainApp.filter_action()

class DataLoader(Static):
    """A dataLoader widget."""
    select_all_datatype = var(True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "update-button":
            self.data = pyperclip.paste()
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
        yield Vertical(id="data-type-container")
        yield Button("(Un)select all", id="filter-button", variant="primary")


class ActionButton(Static):
    """A action widget for action specific to certain types of data."""
    action = var(None)
    action_name = var("")
    action_supported_type = var({})
    def compose(self) -> ComposeResult:
        yield Button(self.action_name, id="action-button", classes="")
    
    def on_mount(self) -> None:
            self.query_one(Button).tooltip = self.action.__doc__

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

    def add_action(self, action_module: actionInterface) -> ActionButton:
        new_action = ActionButton()
        new_action.action = action_module
        new_action.action_name = action_module.description
        new_action.action_supported_type = set(action_module.supportedType)
        self.query_one("#action-container").mount(new_action)
        new_action.scroll_visible()
        return new_action

    def on_input_changed(self, event: Input.Changed) -> None:
        actions = self.query(ActionButton)
        mainApp = self.parent.ancestors[-1].query_one(ContentView).filter_action()
        for action in actions:
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
    SCREENS = {"conf": ConfigScreen()}
    CSS_PATH = "app.css"
    BINDINGS = [
        ("ctrl+s", "save", "Save actual view."),
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+f", "filter", "Filter"),
        ("ctrl+b", "copy", "Copy actual content to clipboard."),
        ("ctrl+r", "reset", "Reset content view to clipboard content."),
        ("ctrl+e", "push_screen('conf')", "Edit config")
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

    def action_filter(self):
        self.query_one("#action-filter").focus()
        

if __name__ == "__main__":
    ClipBrowser().run()
