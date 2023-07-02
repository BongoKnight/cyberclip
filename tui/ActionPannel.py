import re
from textual.reactive import var
from textual.containers import  VerticalScroll
from textual.widgets import Static,  Button, Input
from textual.app import ComposeResult
from userAction import actionInterface

class ActionButton(Static):
    """A action widget for action specific to certain types of data."""
    DEFAULT_CSS="""#action-container{
        column-span: 1;
        row-span: 5;
        height: 100%;
    }
    #action-pannel{
        column-span: 1;
        row-span: 5;
        height: 100%;
    }


    #action-filter{
        height: 3;
    }

    #action-button{
        width: 100%;
        height: 3;
    }
    
    .no-height{
        height: 0;
    }"""


    action : actionInterface = var(None)
    action_name = var("")
    action_supported_type = var({})
    def compose(self) -> ComposeResult:
        yield Button(self.action_name, id="action-button", classes="")
    
    def on_mount(self) -> None:
            self.query_one(Button).tooltip = self.action.__doc__

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a  button is pressed."""
        from tui.ModalParamScreen import ParamScreen
        from tui.ContentView import ContentView
        if event.button.id == "action-button":
            if not self.action.complex_param :
                self.update_text()
            else :
                param_screen = ParamScreen()
                param_screen.action_button = self
                self.app.push_screen(param_screen, self.handle_param)

    def update_text(self):
        from tui.ContentView import ContentView
        mainApp = self.app.query_one(ContentView)
        if mainApp:
            if self.parent.ancestors[-1].query_one("#param-input").value:
                self.action.param = self.parent.ancestors[-1].query_one("#param-input").value
            self.parent.ancestors[-1].query_one("#param-input").value = ""
            mainApp.text = str(self.action)

    def handle_param(self, complex_param : dict):
        if complex_param :
            self.action.complex_param = complex_param
            self.update_text()


class ActionPannel(Static):
    BINDINGS = [("escape", "clean_filter", "Clear the filter value."),]

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Filter actions", id="action-filter")
        yield VerticalScroll(id="action-container")   

    def add_action(self, action_module: actionInterface) -> ActionButton:
        new_action = ActionButton()
        new_action.action = action_module
        new_action.action_name = action_module.description
        new_action.action_supported_type = set(action_module.supportedType)
        self.query_one("#action-container").mount(new_action)
        new_action.scroll_visible()
        return new_action

    def on_input_changed(self, event: Input.Changed) -> None:
        from tui.ContentView import ContentView
        actions = self.query(ActionButton)
        self.app.query_one(ContentView).filter_action()
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
        
    def clean_filter(self):
        self.query_one(Input).value = ""