import sys
from typing import Type
import pyperclip
from io import StringIO
import pandas as pd


from textual import on
from textual.reactive import var, reactive
from textual._path import CSSPathType
from textual.app import App, CSSPathType, ComposeResult
from textual.containers import Grid
from textual.driver import Driver
from textual.widgets import Footer, TabbedContent, TabPane, Label

from tui.ConfigScreen import ConfigScreen
from tui.DataTypePannel import DataLoader
from tui.ContentView import ContentView
from tui.ActionPannel import ActionPannel, ActionCommands

from tui.TableView import FiltrableDataFrame
from userTypeParser import TSVParser
from clipParser import clipParser


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

    parser = var(clipParser())
    text= reactive("Waiting for Update...")

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
            with TabPane('TableView', id="table-view"):
                yield FiltrableDataFrame(pd.DataFrame(), id="main-table")
            with TabPane('Recipes'):
                yield Label("Recipes")
        yield Footer()

    def action_quit(self):
        sys.exit()

    def action_save(self):      
        with open("clipboard.txt", "w") as f:
            f.write(self.text)

    def action_copy(self):
        pyperclip.copy(self.text)

    def action_select_action_filter(self):
        filter = self.app.query_one("#action-filter").focus()
        filter.value = ""

    @on(TabbedContent.TabActivated)
    def check_TSV(self, event: TabbedContent.TabActivated):
        if event.tab.label_text == "TableView":
            df = pd.DataFrame()
            parser = TSVParser.tsvParser(pyperclip.paste())
            if parser.extract():            
                try:
                    df = pd.read_clipboard(sep="\t",header=None)
                    df.columns = [str(i) for i in df.columns]
                    self.app.call_after_refresh(self.update_dataframe, df)
                except Exception as e:
                    self.app.notify(f"Error : {str(e)}",title="Error while loading data...",timeout=5, severity="error")
    
    def update_dataframe(self, df):
        tab = self.query("#table-view")[1]
        tab.remove_children()
        tab.mount(FiltrableDataFrame(pd.DataFrame(df), id="main-table"))

    def watch_text(self, new_text: str) -> None:
        self.query_one(ContentView).update_text(new_text)

if __name__ == "__main__":
    ClipBrowser().run()
