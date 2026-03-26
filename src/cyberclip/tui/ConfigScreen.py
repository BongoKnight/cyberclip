import yaml
from yaml.loader import SafeLoader
from textual.app import App, ComposeResult, Screen
from textual.containers import Horizontal
from textual.reactive import var, reactive
from textual.widgets import Footer, Static, Input, Button, SelectionList
from pathlib import Path
from rich.markdown import Markdown

try:
    from cyberclip.clipParser import clipParser
except:
    from clipParser import clipParser


class ConfigScreen(Screen):
    DEFAULT_CSS = """ConfigScreen{
        layout: vertical
    }

    ConfigInput {
        height: 3;
    }

    #conf-name{
        width: 20;
    }
    #conf-input{
        min-width: 50%;
        width: auto;
    }"""
    BINDINGS = [
        ("escape", "app.pop_screen", "Escape config screen."),
        ("ctrl+s", "save_conf", "Save config"),
    ]

    def compose(self) -> ComposeResult:
        config_fields = {}
        try:
            with open(Path(__file__).parent / "../data/conf.yml", encoding="utf8") as f:
                config_fields = yaml.load(f, Loader=SafeLoader)
            for config_name, config_elems in config_fields.items():
                yield Static(Markdown(f"# {config_name}"))
                for config in config_elems:
                    if isinstance(config, dict):
                        for key, value in config.items():
                            widget = ConfigInput()
                            widget.input_name = key
                            widget.input_value = value
                            widget.parent_conf = config_name
                            yield widget
        except Exception as e:
            self.app.notify(
                f"The file conf.yaml might not exist. Error : {e}",
                title="Error with conf.",
                timeout=5,
                severity="error",
            )
        yield Footer()

    def action_save_conf(self):
        inputs = self.query(ConfigInput)
        conf = {}
        for input in inputs:
            if conf.get(input.parent_conf):
                conf[input.parent_conf].append({input.input_name: input.input_value})
            else:
                conf[input.parent_conf] = [
                    {input.input_name: input.query_one(Input).value}
                ]
        with open(
            Path(__file__).parent / "../data/conf.yml", "w", encoding="utf8"
        ) as f:
            config_fields = yaml.dump(conf, f)


class ConfigInput(Static):

    parent_conf = var("")
    input_name = var("")
    input_value = reactive("")

    def compose(self) -> ComposeResult:
        """Create child widgets of a dataLoader."""
        yield Horizontal(
            Static(self.input_name, id="conf-name"),
            Input(value=self.input_value, id="conf-input"),
        )


if __name__ == "__main__":

    class ConfigApp(App):
        def compose(self) -> ComposeResult:
            yield ConfigScreen()
            yield Footer()

    app = ConfigApp()
    app.run()


class ActionConfigScreen(Screen):
    DEFAULT_CSS = """ActionConfigScreen {
        layout: vertical;
    }

    #action-config-list {
        height: 1fr;
        border: solid $primary;
        padding: 0 1;
        margin: 0;
    }

    #action-config-help {
        margin: 0 0 1 0;
    }

    #action-config-actions {
        height: auto;
        align-horizontal: right;
    }
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Close action config."),
        ("ctrl+s", "save_conf", "Save action config"),
        ("ctrl+a", "select_all", "Select all actions"),
        ("ctrl+u", "unselect_all", "Unselect all actions"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.action_names = []

    def _load_action_state(self):
        config_path = Path(self.app.parser.actions_config_path)
        config = {}
        if config_path.exists():
            with open(config_path, encoding="utf8") as f:
                config = yaml.safe_load(f) or {}

        enabled = config.get("enabled")
        disabled = config.get("disabled", [])
        enabled_set = (
            {str(name) for name in enabled if str(name).strip()}
            if isinstance(enabled, list)
            else None
        )
        disabled_set = (
            {str(name) for name in disabled if str(name).strip()}
            if isinstance(disabled, list)
            else set()
        )

        all_actions_parser = clipParser(
            actions_config_path=config_path.parent / "__all_actions__.yml"
        )
        all_actions_parser.load_all()
        action_names = sorted(all_actions_parser.actions.keys(), key=str.lower)
        self.action_names = action_names

        state = {}
        for action_name in action_names:
            if enabled_set is not None:
                state[action_name] = action_name in enabled_set
            else:
                state[action_name] = action_name not in disabled_set
        return state

    def compose(self) -> ComposeResult:
        action_state = self._load_action_state()
        yield Static(
            "Use space to toggle the focused action. You can select multiple actions before saving.",
            id="action-config-help",
        )
        yield SelectionList[str](
            *[
                (action_name, action_name, enabled)
                for action_name, enabled in action_state.items()
            ],
            id="action-config-list",
        )
        yield Horizontal(
            Button("Select all", id="select-all"),
            Button("Unselect all", id="unselect-all"),
            Button("Save", id="save", variant="primary"),
            Button("Cancel", id="cancel"),
            id="action-config-actions",
        )
        yield Footer()

    def action_select_all(self):
        action_list = self.query_one(SelectionList)
        for action_name in self.action_names:
            action_list.select(action_name)

    def action_unselect_all(self):
        action_list = self.query_one(SelectionList)
        for action_name in self.action_names:
            action_list.deselect(action_name)

    def action_save_conf(self):
        enabled = sorted(
            [str(value) for value in self.query_one(SelectionList).selected],
            key=str.lower,
        )
        config_path = Path(self.app.parser.actions_config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf8") as f:
            yaml.safe_dump(
                {"enabled": enabled, "disabled": []},
                f,
                sort_keys=False,
                allow_unicode=False,
            )
        self.app.refresh_actions_from_config()
        self.app.notify("Action configuration saved.")
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "select-all":
            self.action_select_all()
        elif event.button.id == "unselect-all":
            self.action_unselect_all()
        elif event.button.id == "save":
            self.action_save_conf()
        elif event.button.id == "cancel":
            self.app.pop_screen()
