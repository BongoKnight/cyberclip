from textual.widgets import Static,  Button, Select, TextArea
from textual.containers import Vertical, Horizontal
from textual.app import ComposeResult
from textual import on
from rich.markdown import Markdown
import pyperclip


MARKUP_TYPES = ["actionscript3","apache","applescript","asp","bash","brainfuck","c","c++","cfm","clojure","cmake","coffee","coffee-script","coffeescript","cpp","cs","csharp","css","csv","diff","elixir","erb","go","haml","html","http","java","javascript","jruby","json","jsx","less","lolcode","make","markdown","matlab","nginx","objectivec","pascal","perl","php","profile","python","rb","ruby","rust","salt","saltstate","scss","sh","shell","smalltalk","sql","svg","swift","vhdl","vim","viml","volt","vue","xml","yaml","zsh"]

class ContentToolbar(Static):

    DEFAULT_CSS = """
        #copy-button, #clear-button {
            margin-top: 1;
        }

    """
    def compose(self) -> ComposeResult:
            yield Horizontal(
                Button("📋", id="copy-button", classes="small-button"),
                Button("❌", id="clear-button", classes="small-button"),
                Select([(markup, markup) for markup in MARKUP_TYPES], classes="markup", prompt="Show as...")
            )

    def on_mount(self) -> None:
        self.query_one("#copy-button").tooltip = "Copy text to clipboard"
        self.query_one("#clear-button").tooltip = "Delete the whole text"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        from tui.ContentView import ContentView
        button_id = event.button.id
        if button_id == "copy-button":
            pyperclip.copy(self.app.text)
            self.app.notify("Copied to clipboard!")
        if button_id == "clear-button":
            self.app.text = ""

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        from tui.ContentView import ContentView
        content_view = self.app.query_one(ContentView)
        if event.value:
            content_view.query_one("#clip-content").langage = event.value