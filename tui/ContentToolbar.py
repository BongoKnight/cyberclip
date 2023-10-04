from textual.widgets import Static,  Button, Select, TextArea
from textual.containers import Vertical, Horizontal
from textual.app import ComposeResult
from textual import on
from rich.markdown import Markdown
import pyperclip


MARKUP_TYPES = ["actionscript3","apache","applescript","asp","bash","brainfuck","c","c++","cfm","clojure","cmake","coffee","coffee-script","coffeescript","cpp","cs","csharp","css","csv","diff","elixir","erb","go","haml","html","http","java","javascript","jruby","json","jsx","less","lolcode","make","markdown","matlab","nginx","objectivec","pascal","perl","php","profile","python","rb","ruby","rust","salt","saltstate","scss","sh","shell","smalltalk","sql","svg","swift","vhdl","vim","viml","volt","vue","xml","yaml","zsh"]

class ContentToolbar(Static):

    DEFAULT_CSS = """

    """
    def compose(self) -> ComposeResult:
            yield Horizontal(
                Button("📋", id="copy-button", classes="small-button"),
                Button("❌", id="clear-button", classes="small-button"),
                Button(u"\u21A9", id="previous-button", classes="small-button"),
                Button(u"\u21AA", id="next-button", classes="small-button"),
                #Select([(markup, markup) for markup in MARKUP_TYPES], classes="markup", prompt="Show as...")
            )

    def on_mount(self) -> None:
        self.query_one("#copy-button").tooltip = "Copy text to clipboard"
        self.query_one("#clear-button").tooltip = "Delete the whole text"
        self.query_one("#previous-button").tooltip = "Undo"
        self.query_one("#next-button").tooltip = "Redo"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        from tui.ContentView import ContentView
        content_view = self.app.query_one(ContentView)
        button_id = event.button.id
        if button_id == "copy-button":
            pyperclip.copy(content_view.text)
        if button_id == "clear-button":
            content_view.text = ""
        elif button_id == "previous-button":
            if content_view.text in content_view.text_history:
                index = content_view.text_history.index(content_view.text)
                content_view.text = content_view.text_history[max(0, index - 1)]
        elif button_id == "next-button":
            if content_view.text in content_view.text_history:
                index = content_view.text_history.index(content_view.text)
                content_view.text = content_view.text_history[min(len(content_view.text_history)-1, index + 1)]
    
    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        from tui.ContentView import ContentView
        content_view = self.app.query_one(ContentView)
        if event.value:
            content_view.query_one("#clip-content").langage = event.value
        else :
            textArea = content_view.query_one(TextArea)
            textArea.clear()
            textArea.insert(str(content_view.text))