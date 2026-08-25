import json
import os
import tempfile
from pathlib import Path

import pytest

os.environ.setdefault("POLYGLOT_AI_HOME", tempfile.mkdtemp())

from polyglot_ai import config
from polyglot_ai.providers import ProviderError, get_provider, PROVIDERS


def test_default_personas_exist():
    assert "default" in config.DEFAULT_PERSONAS
    assert "coder" in config.DEFAULT_PERSONAS


def test_config_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "APP_DIR", tmp_path)
    monkeypatch.setattr(config, "SESSIONS_DIR", tmp_path / "sessions")
    monkeypatch.setattr(config, "CONFIG_FILE", tmp_path / "config.json")

    cfg = config.load_config()
    assert cfg["provider"] == "anthropic"

    cfg["provider"] = "openai"
    config.save_config(cfg)
    reloaded = config.load_config()
    assert reloaded["provider"] == "openai"


def test_session_save_and_load(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "SESSIONS_DIR", tmp_path)
    path = tmp_path / "test-session.json"
    messages = [{"role": "user", "content": "hi"}]
    config.save_session(path, messages)
    loaded = config.load_session(path)
    assert loaded == messages


def test_get_provider_known():
    for name in PROVIDERS:
        provider = get_provider(name)
        assert provider.name == name


def test_get_provider_unknown_raises():
    with pytest.raises(ProviderError):
        get_provider("not-a-real-provider")


def test_anthropic_provider_missing_key_raises(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    provider = get_provider("anthropic")
    with pytest.raises(ProviderError):
        list(provider.stream_chat([{"role": "user", "content": "hi"}], "system", None))
