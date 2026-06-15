import os
from pathlib import Path

import yaml


def get_user_data_dir(create: bool = True) -> Path:
    override = os.getenv("CYBERCLIP_DATA_DIR")
    if override:
        data_dir = Path(override).expanduser()
    elif os.name == "nt":
        base_dir = Path(os.getenv("APPDATA") or Path.home() / "AppData/Roaming")
        data_dir = base_dir / "cyberclip"
    else:
        base_dir = Path(os.getenv("XDG_CONFIG_HOME") or Path.home() / ".config")
        data_dir = base_dir / "cyberclip"

    if create:
        data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_package_data_dir() -> Path:
    return Path(__file__).parent / "data"


def get_actions_config_path() -> Path:
    return get_user_data_dir() / "actions.yml"


def get_recipes_path() -> Path:
    return get_user_data_dir() / "recipes.yml"


def load_yaml_list(path: Path, fallback_path: Path | None = None) -> list[dict]:
    for candidate in (path, fallback_path):
        if not candidate or not candidate.exists():
            continue
        with open(candidate, encoding="utf8") as f:
            data = yaml.safe_load(f) or []
        if isinstance(data, list):
            return data
    return []


def save_yaml_list(path: Path, values: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf8") as f:
        yaml.safe_dump(values, f, sort_keys=False, allow_unicode=False)
