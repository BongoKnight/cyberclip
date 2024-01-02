from copy import deepcopy

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Button, Input, Checkbox
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import var

try:
    from cyberclip.tui.ActionPannel import ActionButton
    from cyberclip.tui.TagsInput import TagsInput
    from cyberclip.tui.SimpleInput import SimpleInput
    from cyberclip.tui.SelectionInput import SelectionInput
    from cyberclip.tui.MultiSelect import MultiSelect
    from cyberclip.userAction import actionInterface
except:
    from tui.ActionPannel import ActionButton
    from tui.TagsInput import TagsInput
    from tui.SimpleInput import SimpleInput
    from tui.SelectionInput import SelectionInput
    from tui.MultiSelect import MultiSelect
    from userAction import actionInterface

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

    action : actionInterface = var(None)
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
        self.query_one("#dialog").border_title = self.action.description


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
            if isinstance(widget, SimpleInput):
                params.update({key: {"value":value, "type":"text"}})
            if isinstance(widget, TagsInput):
                params.update({key: {"value":value, "type":"tags"}})
            if isinstance(widget, SelectionInput):
                params.update({key: {"value":value, "type":"fixedlist", "choices": widget.choices}})
            if isinstance(widget, MultiSelect):
                params.update({key: {"value":value, "type":"compactlist", "choices": widget.options}})
            if isinstance(widget, Checkbox):
                params.update({key: {"value":value, "type":"bool"}})
        return params

    def get_complex_param_widgets(self):
        if self.action.complex_param:
            widgets = []
            params = deepcopy(self.action.complex_param)
            for key, value in params.items():
                stored_values = self.action.get_value(key)
                if isinstance(value, dict):                
                    default_value = value.get("default", [])
                    options = value.get("choices", [])
                    assert "type" in value.keys()
                    assert "value" in value.keys()
                    real_value = self.action.get_value(key)
                    input_type = value.get("type")
                    self.action.complex_param[key] = real_value
                    if input_type.lower() == "text":
                        widgets.append(SimpleInput(label=key, value=stored_values, classes="complex-input"))
                    elif input_type.lower() == "tags":
                        widgets.append(TagsInput(label=key, value=stored_values, classes="complex-input"))
                    elif input_type.lower() == "fixedlist":
                        widgets.append(SelectionInput(label=key, choices=options, classes="complex-input"))
                    elif input_type.lower() == "compactlist":
                        widgets.append(MultiSelect(label=key, options=options, classes="complex-input"))
                    elif input_type.lower() == "bool":
                        widgets.append(Checkbox(label=key, value=stored_values, classes="complex-input"))
                if isinstance(value, str):
                    widgets.append(SimpleInput(label=key, value=stored_values, classes="complex-input"))
                    self.action.complex_param.update({key:{"type":"text","value":stored_values}})
                if isinstance(value,list):
                    if len(value) == 0:
                        widgets.append(TagsInput(label=key, value=stored_values, classes="complex-input"))
                        self.action.complex_param.update({key:{"type":"tags","value":stored_values}})
                    else:
                        widgets.append(SelectionInput(label=key, choices=stored_values, classes="complex-input"))
                        self.action.complex_param.update({key:{"type":"fixedlist","value":stored_values}})
                if isinstance(value, bool):
                    widgets.append(Checkbox(label=key, value=value))
                    self.action.complex_param.update({key:{"type":"bool","value":stored_values}})
            return widgets