from pathlib import Path

from textual.widgets import Static, Label, Button
from textual.containers import Horizontal
from textual.app import ComposeResult
from textual.reactive import var
from textual import on, events
from textual_fspicker import FileOpen, FileSave, SelectDirectory

class FileInput(Static):
    DEFAULT_CSS = """
    FileInput {
        margin: 1 1;
        height: 5;
    }
    FileInput Label {
        width: 25;
        margin-top: 1;
    }
    FileInput .selected {
        border: $primary;
        width: 1fr;
        margin-left: 2;
        margin-bottom: 2;
    }
    """
    value = var(set(""))
    label = var("")

    def __init__(self, label : str ="", value : str ="~/", type="open",  **kwargs):
        super().__init__(**kwargs)
        self._value = value
        self.label = label
        self.type = type

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Label(self.label, markup=False),
            Button(label="Select file..."),
            Label(self._value, markup=False, classes="selected")
            )
        
    @property
    def value(self):
        return str(self.query_one(".selected", Label).renderable)
    
    def show_selected(self, to_show: Path | None) -> None:
        """Show the file that was selected by the user.

        Args:
            to_show: The file to show.
        """
        self.query_one(".selected", Label).update("" if to_show is None else str(to_show))
    
    @on(Button.Pressed)
    def open_file(self) -> None:
        """Show the `FileOpen` dialog when the button is pushed."""
        if self.type == "filesave" or self.type == "save":
            self.app.push_screen(
                FileSave("."),
                callback=self.show_selected
            )
        elif self.type == "dir":
            self.app.push_screen(
                SelectDirectory("."),
                callback=self.show_selected
            )
        else:
            self.app.push_screen(
                FileOpen("."),
                callback=self.show_selected
            )
        self.app.notify("Diplayed!")


