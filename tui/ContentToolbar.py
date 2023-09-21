from textual.widgets import Static,  Button, Select, TextArea
from textual.containers import Vertical
from textual.app import ComposeResult
from textual import on
from rich.markdown import Markdown
import pyperclip


MARKUP_TYPES = ["actionscript3","apache","applescript","asp","bash","brainfuck","c","c++","cfm","clojure","cmake","coffee","coffee-script","coffeescript","cpp","cs","csharp","css","csv","diff","elixir","erb","go","haml","html","http","java","javascript","jruby","json","jsx","less","lolcode","make","markdown","matlab","nginx","objectivec","pascal","perl","php","profile","python","rb","ruby","rust","salt","saltstate","scss","sh","shell","smalltalk","sql","svg","swift","vhdl","vim","viml","volt","vue","xml","yaml","zsh"]

class ContentToolbar(Static):

    DEFAULT_CSS = """

    """
    def compose(self) -> ComposeResult:
            yield Button("Copy", id="copy-button")
            yield Button(u"\u21A9 Undo", id="previous-button", classes="small-button")
            yield Button(u"Redo \u21AA", id="next-button", classes="small-button")
            yield Select([(markup, markup) for markup in MARKUP_TYPES], classes="markup", prompt="Show as...")
        
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        from tui.ContentView import ContentView
        content_view = self.app.query_one(ContentView)
        button_id = event.button.id
        if button_id == "copy-button":
            pyperclip.copy(content_view.text)
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