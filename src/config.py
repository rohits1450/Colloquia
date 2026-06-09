"""Load and expose project configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "settings.yaml"


def load_config(path: Path | None = None) -> dict[str, Any]:
    config_path = path or CONFIG_PATH
    with open(config_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    for key, rel in cfg.get("paths", {}).items():
        cfg["paths"][key] = str((ROOT / rel).resolve())

    return cfg
