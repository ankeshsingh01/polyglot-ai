"""Config file, persona presets, and session save/load helpers."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

APP_DIR = Path(os.environ.get("POLYGLOT_AI_HOME", Path.home() / ".polyglot-ai"))
SESSIONS_DIR = APP_DIR / "sessions"
CONFIG_FILE = APP_DIR / "config.json"

DEFAULT_PERSONAS = {
    "default": "You are a helpful, concise assistant.",
    "coder": (
        "You are a senior software engineer. Answer with correct, idiomatic code. "
        "Explain trade-offs briefly. Prefer showing code over long prose."
    ),
    "teacher": (
        "You are a patient teacher. Explain concepts step by step with simple "
        "examples, checking understanding as you go."
    ),
    "brutalist": (
        "You are extremely blunt and concise. No pleasantries, no filler, "
        "just the direct answer."
    ),
}


def ensure_dirs() -> None:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    ensure_dirs()
    if not CONFIG_FILE.exists():
        default = {
            "provider": "anthropic",
            "model": None,
            "persona": "default",
        }
        save_config(default)
        return default
    return json.loads(CONFIG_FILE.read_text())


def save_config(cfg: dict) -> None:
    ensure_dirs()
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))


def new_session_path(name: str | None = None) -> Path:
    ensure_dirs()
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    fname = f"{name or 'session'}-{ts}.json"
    return SESSIONS_DIR / fname


def save_session(path: Path, messages: list[dict]) -> None:
    path.write_text(json.dumps(messages, indent=2))


def load_session(path: Path) -> list[dict]:
    return json.loads(path.read_text())


def list_sessions() -> list[Path]:
    ensure_dirs()
    return sorted(SESSIONS_DIR.glob("*.json"), reverse=True)
