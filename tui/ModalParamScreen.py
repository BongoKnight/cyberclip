from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Button, Input, Checkbox
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import var

from tui.ActionPannel import ActionButton
from tui.TagsInput import TagsInput
from tui.SimpleInput import SimpleInput
from tui.SelectionInput import SelectionInput
from tui.MultiSelect import MultiSelect

class ParamScreen(Screen):
    """Modal screen for entering parameters"""
    DEFAULT_CSS = """
    ParamScreen {
        align: center middle;
        background: black 30%;
        layout: vertical;

    }
    #dialog {
        padding: 3 3;
        width: 80%;
        height: 80%;
        border: $accent;
        }
    
    #submit {
        height: 3;
        align-horizontal: right;
    }

    SimpleInput > Label{
        width: 25;
    }
    SimpleInput, TagsInput {
        margin: 1 1;
        height: 5;
    }
    """

    action_button : ActionButton = var(None)
    BINDINGS = [("escape", "app.pop_screen", "Escape config screen.")]

    def compose(self) -> ComposeResult:
        yield Vertical(
            VerticalScroll(*self.get_complex_param_widgets()),
            Horizontal(
                Button("Cancel", variant="error", id="cancel"),
                Button("Save params", variant="primary", id="save"), id="submit"
            ),
            id="dialog"
        )

    def on_mount(self) -> None:
        self.query_one("#dialog").border_title = self.action_button.action.description


    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss({})
        else:
            self.dismiss(self.return_parameters())
            
    def return_parameters(self):
        params = {}
        for widget in self.query(".complex-input"):
            key = widget.label
            value = widget.value
            params.update({key: value})
        return params

    def get_complex_param_widgets(self):
        if self.action_button.action.complex_param_scheme:
            widgets = []
            stored_values = self.action_button.action.complex_param
            for key, value in self.action_button.action.complex_param_scheme.items():
                if isinstance(value, dict):
                    assert "type" in value.keys()
                    assert "value" in value.keys()
                    real_value = value.get("value")
                    input_type = value.get("type")
                    self.action_button.action.complex_param[key] = real_value
                    stored_values = self.action_button.action.complex_param
                    if input_type.lower() == "text":
                        widgets.append(SimpleInput(label=key, value=stored_values.get(key,""), classes="complex-input"))
                    elif input_type.lower() == "tags":
                        widgets.append(TagsInput(label=key, value=stored_values.get(key,[]), classes="complex-input"))
                    elif input_type.lower() == "fixedlist":
                        widgets.append(SelectionInput(label=key, choices=real_value, classes="complex-input"))
                    elif input_type.lower() == "compactlist":
                        widgets.append(MultiSelect(label=key, choices=real_value, classes="complex-input"))
                    elif input_type.lower() == "bool":
                        widgets.append(Checkbox(label=key, value=real_value, classes="complex-input"))
                if isinstance(value, str):
                    widgets.append(SimpleInput(label=key, value=stored_values.get(key,""), classes="complex-input"))
                if isinstance(value,list):
                    if len(value) == 0:
                        widgets.append(TagsInput(label=key, value=stored_values.get(key,[]), classes="complex-input"))
                    else:
                        widgets.append(SelectionInput(label=key, choices=value, classes="complex-input"))
                if isinstance(value, bool):
                    widgets.append(Checkbox(label=key, value=value))
            return widgets