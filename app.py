import sys
from typing import Type
import pyperclip
from textual._path import CSSPathType
from textual.app import App, CSSPathType, ComposeResult
from textual.containers import Grid
from textual.driver import Driver
from textual.widgets import Footer, TabbedContent, TabPane, Label

from tui.ConfigScreen import ConfigScreen
from tui.DataTypePannel import DataLoader
from tui.ContentView import ContentView
from tui.ActionPannel import ActionPannel, ActionCommands



class ClipBrowser(App):
    """Textual clipboard browser app."""
    CSS_PATH = "app.scss"
    COMMANDS = {ActionCommands}
    SCREENS = {"conf": ConfigScreen}
    BINDINGS = [
        ("ctrl+p", "command_palette","Command palette"),
        ("ctrl+s", "save", "Save actual view."),
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+f", "select_action_filter", "Filter"),
        ("ctrl+b", "copy", "Copy actual content to clipboard."),
        ("ctrl+r", "reset", "Reset content view to clipboard content."),
        ("ctrl+e", "push_screen('conf')", "Edit config")
    ]

    def __init__(self, driver_class: type[Driver] | None = None, css_path: CSSPathType | None = None, watch_css: bool = False):
        super().__init__(driver_class, css_path, watch_css)
        self.actions = []

    def compose(self) -> ComposeResult:
        """Compose our UI."""
        self.console.set_window_title("📝CyberClip👩‍💻")
        with TabbedContent():
            with TabPane("📝CyberClip👩‍💻"):
                yield Grid(
                    DataLoader(id="left-pannel"),
                    ContentView(id="content-view"),
                    ActionPannel(id="action-pannel"),
                    id="maingrid"
                )
            with TabPane('TableView'):
                yield Label("TableView")
            with TabPane('Recipes'):
                yield Label("Recipes")
        yield Footer()

    def action_quit(self):
        sys.exit()

    def action_save(self):      
        with open("clipboard.txt", "w") as f:
            f.write(self.query_one(ContentView).text)

    def action_copy(self):
        pyperclip.copy(self.query_one(ContentView).text)

    def select_action_filter(self):
        filter = self.app.query_one("#action-filter").focus()
        filter.value = ""

if __name__ == "__main__":
    ClipBrowser().run()
