import re
from functools import partial

from textual import events, work, on
from textual.reactive import var, reactive
from textual.containers import  Vertical, ScrollableContainer
from textual.widgets import Static,  Button, Input, Switch, Label, Select, TextArea
from textual.app import ComposeResult
try:
    from cyberclip.tui.ContentToolbar import ContentToolbar
except:
    from tui.ContentToolbar import ContentToolbar


class ContentView(Static):
    DEFAULT_CSS="""
    ContentView{
        column-span: 3;
        row-span: 5;
        height: 1fr;
    }
    #clip-content{
        width: 100%;
        border: $primary;
    }
    """

    def compose(self) -> ComposeResult:
        """Create child widgets of a dataLoader.""" 
        yield Vertical(
            ContentToolbar(),
            ScrollableContainer(TextArea(self.app.text, name="Content", id="clip-content", show_line_numbers=True))
            )

    def filter_action(self):
        from tui.DataTypePannel import DataTypeButton
        from tui.ActionPannel import ActionPannel, ActionButton
        actionView = self.app.query_one(ActionPannel)
        if actionView:
            actions = actionView.query(ActionButton)
            actual_detected_type = set(self.app.parser.detectedType)
            for datatype_button in self.app.query(DataTypeButton):
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
            
            filter_text = self.app.query_one(ActionPannel).query_one(Input).value
            for action_button in actions:
                if  (len(action_button.action.supportedType.intersection(actual_detected_type)) >=1
                    and len(action_button.action.supportedType.intersection(action_button.action_supported_type)) >= 1
                    ) :
                    action_button.visible = True
                    action_button.remove_class("no-height")
                    self.app.actions.append(action_button)
                    if filter_text:
                        for word in filter_text.split():
                            if not re.search(f"(?i){word}", action_button.action.description, re.IGNORECASE):
                                if not word in action_button.action.supportedType:
                                    action_button.visible = False
                                    action_button.add_class("no-height")
                else:
                    action_button.visible = False
                    action_button.add_class("no-height")

    def on_mount(self):
        self.set_interval(2, self.auto_update)

    def auto_update(self):
        text = self.query_one(TextArea).text
        if len(text) < 3000:
            self.app.text = text 


    def update_text(self, new_text: str, force=False) -> None:
        """Called when the text attribute changes."""
        from tui.DataTypePannel import DataTypeButton, DataLoader
        from tui.ActionPannel import ActionPannel, ActionButton
        textArea = self.query_one(TextArea)
        textArea.replace(str(new_text), (0,0), (textArea.document.line_count, len(textArea.document.get_line(textArea.document.line_count-1))))
        parser_types = list(self.app.parser.detectedType)
        parser_types.sort()
        # Update detected type buttons
        buttons = self.parent.query(DataTypeButton)
        if buttons:             
            for button in buttons:
                button.remove()
        for type_of_data in parser_types:
            if type_of_data != "text":
                self.parent.query_one(DataLoader).add_dataType(type_of_data, active=True)
            else:
                self.parent.query_one(DataLoader).add_dataType(type_of_data, active=False)
        existing_action = set()
        for action_name, action in self.app.parser.actions.items():
            for action_button in self.parent.query(ActionButton):
                if action_button.action_name == action_name:
                    existing_action.add(action_name)            

        # Add inexisting action buttons
        actions = list(self.app.parser.actions.items())
        # Sort action by name
        actions.sort(key=lambda tup: tup[0])
        for action_name, action in actions:
            if  action_name not in existing_action:
                self.parent.query_one(ActionPannel).add_action(action)

        for action in self.parent.query(ActionButton):
            action.action.supportedType = set(action.action_supported_type)
            action.action.parsers = self.app.parser.parsers
        # for action in self.app.parser.actions.values():
        #     action.parsers = self.app.parser.parsers
        # Filter action on existing active datatype
        self.app.call_after_refresh(self.filter_action)
        


        