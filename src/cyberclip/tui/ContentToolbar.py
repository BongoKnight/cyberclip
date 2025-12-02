from textual.widgets import Static,  Button, Select, TextArea
from textual.containers import Vertical, Horizontal
from textual.app import ComposeResult
from textual import on
from rich.markdown import Markdown


MARKUP_TYPES = ["bash","c","c++","csharp","css","go","html","java","javascript","json","markdown","perl","php","python","ruby","rust","sql","xml","yaml"]

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
            self.app.copy_to_clipboard(self.app.query_one("#clip-content", TextArea).text)
            self.app.notify("Copied to clipboard!")
        if button_id == "clear-button":
            self.app.text = ""

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        from tui.ContentView import ContentView
        content_view = self.app.query_one(ContentView)
        if event.value:
            try:
                content_view.query_one("#clip-content", TextArea).language = event.value
            except:
                content_view.query_one("#clip-content", TextArea).language = None