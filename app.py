import sys
import pyperclip
from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.widgets import Footer

from tui.ConfigScreen import ConfigScreen
from tui.DataTypePannel import DataLoader
from tui.ContentView import ContentView
from tui.ActionPannel import ActionPannel



class ClipBrowser(App):
    """Textual clipboard browser app."""
    CSS_PATH = "app.scss"

    SCREENS = {"conf": ConfigScreen}
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
        yield Grid(
            DataLoader(id="left-pannel"),
            ContentView(id="content-view"),
            ActionPannel(id="action-pannel"),
            id="maingrid"
        )
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
        filter = self.app.query_one("#action-filter").focus()
        filter.value = ""

if __name__ == "__main__":
    ClipBrowser().run()
