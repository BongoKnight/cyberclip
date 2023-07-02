import pyperclip
from textual.reactive import var, reactive
from textual.containers import  Vertical, ScrollableContainer
from textual.widgets import Static,  Button, Input, Switch, Label
from textual.app import ComposeResult

from clipParser import clipParser


class ContentView(Static):
    DEFAULT_CSS="""#content-view{
        border: $accent;
        column-span: 3;
        row-span: 5;
        height: 100%;

    }

    .small-button{
        border: none;
        height: auto;
        width: auto;
        min-width: 0;
    }

    #copy-button{
        layer: above;
        dock: right;
        align-vertical: top;
        background: $accent 10%;
        min-width: 18;
    }
    #next-button{
        layer: above;
        dock: right;
        align-vertical: top;
        margin-top: 3;
        background: $accent 10%;
    }
    #previous-button{
        layer: above;
        dock: right;
        align-vertical: top;
        margin-top: 3;
        margin-right: 10;
        background: $accent 10%;
    }

    #copy-button:hover, #previous-button:hover, #next-button:hover {
        background: $accent;
    }

    #param-input{
        row-span:1;
        dock: bottom;
    }
    """


    text= reactive("Waiting for Update...")
    parser = var(clipParser())
    initial_text = var(pyperclip.paste())
    text_history = var([])
    
    def compose(self) -> ComposeResult:
        """Create child widgets of a dataLoader.""" 
        yield Vertical(
            ScrollableContainer(Label(self.initial_text ,name="Content", id="clip-content", markup=False)),
            Button("Copy", id="copy-button"),
            Button(u"\u21A9 Undo", id="previous-button", classes="small-button"),
            Button(u"Redo \u21AA", id="next-button", classes="small-button"),
            Input(placeholder="Add additional parameter for custom action.",id="param-input")
        )

    def filter_action(self):
        from tui.DataTypePannel import DataTypeButton
        from tui.ActionPannel import ActionPannel, ActionButton
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
        from tui.DataTypePannel import DataTypeButton, DataLoader
        from tui.ActionPannel import ActionPannel, ActionButton
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