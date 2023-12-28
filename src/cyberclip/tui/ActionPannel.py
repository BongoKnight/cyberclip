import re
from textual import on
from textual.reactive import var
from textual.containers import  VerticalScroll
from textual.widgets import Static,  Button, Input
from textual.app import ComposeResult
from textual.command import Hit, Hits, Provider
from functools import partial

try:
    from cyberclip.userAction import actionInterface
except:
    from userAction import actionInterface


class ActionButton(Static):
    """A action widget for action specific to certain types of data."""
    DEFAULT_CSS="""
"""


    action : actionInterface = var(None)
    action_name = var("")
    action_supported_type = var({})
    def compose(self) -> ComposeResult:
        yield Button(self.action_name, id="action-button", classes="")
    
    def on_mount(self) -> None:
        self.query_one(Button).tooltip = self.action.__doc__

    @on(Button.Pressed, "#action-button")
    def execute_option_action(self, event: Button.Pressed) -> None:
        """Event handler called when a  button is pressed."""
        from tui.ModalParamScreen import ParamScreen
        from tui.ContentView import ContentView
        if not self.action.complex_param :
            self.update_text()
        else :
            param_screen = ParamScreen()
            param_screen.border_title = f"Parameters for '{self.action.description}' action."
            param_screen.action = self.action
            self.app.push_screen(param_screen, self.handle_param)

    def update_text(self):
        from tui.ContentView import ContentView
        contentView = self.app.query_one(ContentView)
        if contentView:
            if self.parent.ancestors[-1].query_one("#param-input").value:
                self.action.param = self.parent.ancestors[-1].query_one("#param-input").value
            self.parent.ancestors[-1].query_one("#param-input").value = ""
            try:
                self.app.text = str(self.action)
            except Exception as e:
                self.app.notify(f"Error : {e}", severity="error",timeout=5)

    def handle_param(self, complex_param : dict):
        if complex_param :
            self.action.complex_param = complex_param
            self.update_text()

class ActionCommands(Provider):
    """A command provider to return all actions for the current text."""

    def recover_actions(self) -> list[actionInterface.actionInterface]:
        """Get a list of all actions."""
        return self.app.parser.actions.values()
    
    def execute_action(self, action: actionInterface) -> None:
        """Event handler called when a  button is pressed."""
        from tui.ModalParamScreen import ParamScreen
        from tui.ContentView import ContentView
        if not action.complex_param :
            self.app.text = str(action)
        else :
            param_screen = ParamScreen()
            param_screen.border_title = f"Parameters for '{action.description}' action."
            param_screen.action = action
            self.app.push_screen(param_screen, partial(self.app.handle_param, action))

    async def startup(self) -> None:  
        """Called once when the command palette is opened, prior to searching."""
        worker = self.app.run_worker(self.recover_actions, thread=True)
        self.actions = await worker.wait()

    async def search(self, query: str) -> Hits:  
        """Search for action."""
        matcher = self.matcher(query)  

        for action in self.actions :
            action_desc = action.description
            action_doc = action.__doc__
            scoreDesc = matcher.match(action_desc) 
            scoreDoc = matcher.match(action_doc) 

            if scoreDesc > 0 or scoreDoc > 0:
                yield Hit(
                    max(scoreDesc, scoreDoc),
                    matcher.highlight(action_desc),
                    partial(self.execute_action, action),
                    help=action_doc,
                )

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
        self.app.actions = self.app.query_one(ContentView).filter_action()
        for action in actions:
            for word in event.value.split():
                if not re.search(f"(?i){word}", action.action.description, re.IGNORECASE):
                    if not word in action.action.supportedType:
                        action.visible = False
                        action.add_class("no-height")

    def clean_filter(self):
        self.query_one(Input).value = ""