"""
Code browser example.

Run with:

    python app.py
"""

import sys
import pyperclip
from textual.app import App, ComposeResult
from textual.widgets import Footer

from tui.ConfigScreen import ConfigScreen
from tui.DataTypePannel import DataLoader
from tui.ContentView import ContentView
from tui.ActionPannel import ActionPannel


class ClipBrowser(App):
    """Textual clipboard browser app."""
    SCREENS = {"conf": ConfigScreen()}
    CSS_PATH = "app.scss"
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
