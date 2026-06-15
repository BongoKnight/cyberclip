import io
from pathlib import Path

from cyberclip import data_paths


class _WritableMemoryFile(io.StringIO):
    def __init__(self, key: str, files: dict[str, str]):
        super().__init__()
        self._key = key
        self._files = files

    def close(self):
        self._files[self._key] = self.getvalue()
        super().close()


def _patch_memory_files(monkeypatch, files: dict[str, str]):
    def fake_exists(self):
        return str(self) in files

    def fake_open(path, mode="r", encoding=None):
        key = str(path)
        if "r" in mode:
            if key not in files:
                raise FileNotFoundError(key)
            return io.StringIO(files[key])
        if "w" in mode:
            return _WritableMemoryFile(key, files)
        raise ValueError(f"Unsupported mode: {mode}")

    monkeypatch.setattr(Path, "exists", fake_exists)
    monkeypatch.setattr(Path, "mkdir", lambda self, parents=False, exist_ok=False: None)
    monkeypatch.setattr("builtins.open", fake_open)


def test_data_paths_use_override_directory(monkeypatch):
    override_dir = Path("C:/tmp/cyberclip-data")
    monkeypatch.setenv("CYBERCLIP_DATA_DIR", str(override_dir))
    monkeypatch.setattr(
        data_paths, "get_user_data_dir", lambda create=True: override_dir
    )

    assert data_paths.get_user_data_dir(create=False) == override_dir
    assert data_paths.get_recipes_path() == override_dir / "recipes.yml"
    assert data_paths.get_actions_config_path() == override_dir / "actions.yml"


def test_load_yaml_list_uses_fallback_when_primary_is_missing(monkeypatch):
    primary_path = Path("primary.yml")
    fallback_path = Path("fallback.yml")
    files = {str(fallback_path): "- name: bundled\n  description: sample\n"}
    _patch_memory_files(monkeypatch, files)

    assert data_paths.load_yaml_list(primary_path, fallback_path) == [
        {"name": "bundled", "description": "sample"}
    ]


def test_save_yaml_list_round_trips_values(monkeypatch):
    recipes_path = Path("nested/recipes.yml")
    recipes = [
        {
            "name": "Normalize URLs",
            "description": "Example recipe",
            "steps": [{"actionnableName": "To base URL", "usePreset": True}],
        }
    ]
    files: dict[str, str] = {}
    _patch_memory_files(monkeypatch, files)

    data_paths.save_yaml_list(recipes_path, recipes)

    assert data_paths.load_yaml_list(recipes_path) == recipes
