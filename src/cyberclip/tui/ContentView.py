import re
from functools import partial

from textual import events, work, on
from textual.reactive import var, reactive
from textual.containers import Vertical, ScrollableContainer
from textual.widgets import Static, Button, Input, Switch, Label, Select, TextArea
from textual.app import ComposeResult

try:
    from cyberclip.tui.ContentToolbar import ContentToolbar
except ImportError:
    from tui.ContentToolbar import ContentToolbar


class ContentView(Static):
    DEFAULT_CSS = """
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
            ScrollableContainer(
                TextArea(
                    self.app.text,
                    name="Content",
                    id="clip-content",
                    show_line_numbers=True,
                )
            ),
        )

    def on_mount(self):
        self.set_interval(2, self.auto_update)

    def auto_update(self):
        text = self.query_one(TextArea).text
        if len(text) < 3000:
            self.app.text = text

    def filter_action(self):
        try:
            from cyberclip.tui.ActionPannel import ActionPannel
        except ImportError:
            from tui.ActionPannel import ActionPannel

        self.app.query_one(ActionPannel).filter_action()

    def update_text(self, new_text: str, force=False) -> None:
        """Called when the text attribute changes."""
        try:
            from cyberclip.tui.DataTypePannel import DataTypeButton, DataLoader
            from cyberclip.tui.ActionPannel import ActionPannel, ActionButton
        except ImportError:
            from tui.DataTypePannel import DataTypeButton, DataLoader
            from tui.ActionPannel import ActionPannel, ActionButton

        textArea = self.query_one(TextArea)
        textArea.replace(
            str(new_text),
            (0, 0),
            (
                textArea.document.line_count,
                len(textArea.document.get_line(textArea.document.line_count - 1)),
            ),
        )
        parser_types = list(self.app.parser.detectedType)
        parser_types.sort()
        # Update detected type buttons
        buttons = self.parent.query(DataTypeButton)
        if buttons:
            for button in buttons:
                button.remove()
        for type_of_data in parser_types:
            self.parent.query_one(DataLoader).add_dataType(type_of_data, active=True)
        existing_action = set()
        valid_action_names = set(self.app.parser.actions.keys())
        for action_name, action in self.app.parser.actions.items():
            for action_button in self.parent.query(ActionButton):
                if action_button.action_name == action_name:
                    existing_action.add(action_name)

        for action_button in list(self.parent.query(ActionButton)):
            if action_button.action_name not in valid_action_names:
                action_button.remove()

        # Add inexisting action buttons
        actions = list(self.app.parser.actions.items())
        # Sort action by name
        actions.sort(key=lambda tup: tup[0])
        for action_name, action in actions:
            if action_name not in existing_action:
                self.parent.query_one(ActionPannel).add_action(action)

        for action in self.parent.query(ActionButton):
            action.actionnable.supportedType = set(action.action_supported_type)
            action.actionnable.parsers = self.app.parser.parsers
        self.parent.query_one(ActionPannel).refresh_recipe_buttons()
        # for action in self.app.parser.actions.values():
        #     action.parsers = self.app.parser.parsers
        # Filter action on existing active datatype
        self.app.call_after_refresh(self.filter_action)
