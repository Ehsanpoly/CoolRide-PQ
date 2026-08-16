from __future__ import annotations

import json
from pathlib import Path

from .models import SiteConfig


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_config_path() -> Path:
    return repository_root() / "configs" / "reference-50mw-ai-campus.json"


def load_site_config(path: str | Path | None = None) -> SiteConfig:
    config_path = Path(path) if path else default_config_path()
    with config_path.open("r", encoding="utf-8") as stream:
        return SiteConfig.from_dict(json.load(stream))
