import pyperclip
from textual import events, work
from textual.reactive import var, reactive
from textual.containers import  Vertical, ScrollableContainer
from textual.widgets import Static,  Button, Input, Switch, Label, Select, TextArea
from textual.app import ComposeResult
from tui.ContentToolbar import ContentToolbar

MARKUP_TYPES = ["actionscript3","apache","applescript","asp","bash","brainfuck","c","c++","cfm","clojure","cmake","coffee","coffee-script","coffeescript","cpp","cs","csharp","css","csv","diff","elixir","erb","go","haml","html","http","java","javascript","jruby","json","jsx","less","lolcode","make","markdown","matlab","nginx","objectivec","pascal","perl","php","profile","python","rb","ruby","rust","salt","saltstate","scss","sh","shell","smalltalk","sql","svg","swift","vhdl","vim","viml","volt","vue","xml","yaml","zsh"]

class ContentView(Static):
    DEFAULT_CSS="""
    ContentView{
        column-span: 3;
        row-span: 5;
        height: 1fr;
    }
    #param-input{
        row-span:1;
        dock: bottom;
    }
    #clip-content{
        width: 100%;
        border: $accent;
    }
    """

    initial_text = "Waiting for Update..."
    text= reactive("Waiting for Update...")
    text_history = var([])

    def compose(self) -> ComposeResult:
        """Create child widgets of a dataLoader.""" 
        yield Vertical(
            ContentToolbar(),
            ScrollableContainer(TextArea(self.initial_text ,name="Content", id="clip-content")),
            Input(placeholder="Add additional parameter for custom action.",id="param-input")
        )

    def filter_action(self):
        from tui.DataTypePannel import DataTypeButton
        from tui.ActionPannel import ActionPannel, ActionButton
        actionView = self.parent.ancestors[-1].query_one(ActionPannel)
        if actionView:
            actions = actionView.query(ActionButton)
            actual_detected_type = set(self.app.parser.detectedType)
            for datatype_button in self.parent.ancestors[-1].query(DataTypeButton):
                # Update actions supported_type and hide action buttons where no type are supported
                if datatype_button.switch and datatype_button.switch.value:
                    for action_button in actions:
                        # Add the supported type if the default action support it.
                        if datatype_button.parser_type in action_button.action_supported_type:
                            action_button.action.supportedType.add(datatype_button.parser_type)
                else:
                    for action_button in actions:
                        if datatype_button.parser_type in action_button.action_supported_type:
                            action_button.action.supportedType.discard(datatype_button.parser_type)
            
            self.app.actions = []
            for action_button in actions:
                if  (len(action_button.action.supportedType.intersection(actual_detected_type)) >=1
                    and len(action_button.action.supportedType.intersection(action_button.action_supported_type)) >= 1
                    ) :
                    action_button.visible = True
                    action_button.remove_class("no-height")
                    self.app.actions.append(action_button)
                else:
                    action_button.visible = False
                    action_button.add_class("no-height")

    def watch_text(self, new_text: str) -> None:
        """Called when the text attribute changes."""
        from tui.DataTypePannel import DataTypeButton, DataLoader
        from tui.ActionPannel import ActionPannel, ActionButton
        textArea = self.query_one(TextArea)
        textArea.clear()
        textArea.insert(str(new_text))
        if new_text not in self.text_history:
            self.text_history.append(new_text)
            self.text_history = self.text_history[-20:]
        
        
        self.app.parser.parseData(new_text)
        parser_types = self.app.parser.detectedType
        # Update detected type buttons
        buttons = self.parent.query(DataTypeButton)
        if buttons:             
            for button in buttons:
                button.remove()
        for type_of_data in parser_types:
            if type_of_data == "text":
                self.parent.query_one(DataLoader).add_dataType(type_of_data, active=False)
            else:
                self.parent.query_one(DataLoader).add_dataType(type_of_data, active=True)
        existing_action = set()
        for action_name, action in self.app.parser.actions.items():
            for action_button in self.parent.query(ActionButton):
                if action_button.action_name == action_name:
                    existing_action.add(action_name)            

        # Add inexisting action buttons
        for action_name, action in self.app.parser.actions.items():
            if  action_name not in existing_action:
                self.parent.query_one(ActionPannel).add_action(action)

        for action in self.parent.query(ActionButton):
            action.action.supportedType = set(action.action_supported_type)
            action.action.parsers = self.app.parser.parsers
           

        # Filter action on existing active datatype
        self.app.call_after_refresh(self.filter_action)
        


        