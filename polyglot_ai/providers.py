"""
Provider abstraction layer.

Each provider implements a simple `stream_chat(messages, system, model)`
generator that yields text chunks, so the CLI layer never needs to know
which backend it's talking to.

Supported out of the box:
  - anthropic  (Claude models)
  - openai     (GPT models)
  - ollama     (local models, no API key needed)
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Iterator


class ProviderError(RuntimeError):
    pass


class BaseProvider(ABC):
    name: str = "base"
    default_model: str = ""

    @abstractmethod
    def stream_chat(self, messages: list[dict], system: str, model: str | None) -> Iterator[str]:
        """Yield response text chunks."""
        raise NotImplementedError

    def require_env(self, key: str) -> str:
        value = os.environ.get(key)
        if not value:
            raise ProviderError(
                f"Missing environment variable '{key}'. "
                f"Set it with: export {key}=your_key_here"
            )
        return value


class AnthropicProvider(BaseProvider):
    name = "anthropic"
    default_model = "claude-sonnet-4-6"

    def stream_chat(self, messages, system, model=None):
        try:
            import anthropic
        except ImportError as e:
            raise ProviderError(
                "The 'anthropic' package isn't installed. Run: pip install anthropic"
            ) from e

        api_key = self.require_env("ANTHROPIC_API_KEY")
        client = anthropic.Anthropic(api_key=api_key)

        with client.messages.stream(
            model=model or self.default_model,
            max_tokens=2048,
            system=system,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                yield text


class OpenAIProvider(BaseProvider):
    name = "openai"
    default_model = "gpt-4o-mini"

    def stream_chat(self, messages, system, model=None):
        try:
            from openai import OpenAI
        except ImportError as e:
            raise ProviderError(
                "The 'openai' package isn't installed. Run: pip install openai"
            ) from e

        api_key = self.require_env("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)

        full_messages = [{"role": "system", "content": system}] + messages
        stream = client.chat.completions.create(
            model=model or self.default_model,
            messages=full_messages,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta


class OllamaProvider(BaseProvider):
    """Talks to a locally running Ollama server. No API key required."""

    name = "ollama"
    default_model = "llama3"

    def stream_chat(self, messages, system, model=None):
        try:
            import requests
        except ImportError as e:
            raise ProviderError(
                "The 'requests' package isn't installed. Run: pip install requests"
            ) from e

        host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        full_messages = [{"role": "system", "content": system}] + messages

        try:
            resp = requests.post(
                f"{host}/api/chat",
                json={"model": model or self.default_model, "messages": full_messages, "stream": True},
                stream=True,
                timeout=60,
            )
            resp.raise_for_status()
        except Exception as e:
            raise ProviderError(
                f"Couldn't reach Ollama at {host}. Is it running? ('ollama serve')"
            ) from e

        import json as _json
        for line in resp.iter_lines():
            if not line:
                continue
            data = _json.loads(line)
            content = data.get("message", {}).get("content", "")
            if content:
                yield content


PROVIDERS: dict[str, type[BaseProvider]] = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "ollama": OllamaProvider,
}


def get_provider(name: str) -> BaseProvider:
    cls = PROVIDERS.get(name)
    if cls is None:
        raise ProviderError(
            f"Unknown provider '{name}'. Choose from: {', '.join(PROVIDERS)}"
        )
    return cls()
