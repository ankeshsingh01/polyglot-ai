"""
polyglot-ai: a single terminal chat client for Anthropic, OpenAI, and local
Ollama models — with saved sessions and persona presets.

Usage:
    polyglot-ai                       # start interactive chat with defaults
    polyglot-ai --provider openai     # use a specific provider
    polyglot-ai --persona coder       # start with a persona preset
    polyglot-ai --resume session.json # continue a saved session
    polyglot-ai --list-sessions       # show saved sessions
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import config
from .providers import ProviderError, get_provider

try:
    from rich.console import Console
    from rich.markdown import Markdown
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

console = Console() if HAS_RICH else None


def _print(text: str, markdown: bool = False) -> None:
    if HAS_RICH and markdown:
        console.print(Markdown(text))
    elif HAS_RICH:
        console.print(text)
    else:
        print(text)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="polyglot-ai", description=__doc__.strip())
    p.add_argument("--provider", choices=["anthropic", "openai", "ollama"], help="AI backend to use")
    p.add_argument("--model", help="Override the default model for the chosen provider")
    p.add_argument("--persona", help="Persona preset name (see --list-personas)")
    p.add_argument("--system", help="Raw system prompt (overrides --persona)")
    p.add_argument("--resume", help="Path to a saved session JSON file to continue")
    p.add_argument("--list-sessions", action="store_true", help="List saved sessions and exit")
    p.add_argument("--list-personas", action="store_true", help="List persona presets and exit")
    p.add_argument("--save-as", help="Name to use when saving this session")
    p.add_argument("--no-stream", action="store_true", help="Wait for full reply instead of streaming")
    return p


def resolve_system_prompt(args, cfg: dict) -> str:
    if args.system:
        return args.system
    persona = args.persona or cfg.get("persona", "default")
    return config.DEFAULT_PERSONAS.get(persona, config.DEFAULT_PERSONAS["default"])


def chat_loop(args: argparse.Namespace) -> None:
    cfg = config.load_config()
    provider_name = args.provider or cfg.get("provider", "anthropic")
    model = args.model or cfg.get("model")
    system_prompt = resolve_system_prompt(args, cfg)

    messages: list[dict] = []
    session_path: Path | None = None
    if args.resume:
        session_path = Path(args.resume)
        messages = config.load_session(session_path)
        _print(f"[resumed session: {session_path.name}, {len(messages)} messages]")
    else:
        session_path = config.new_session_path(args.save_as)

    try:
        provider = get_provider(provider_name)
    except ProviderError as e:
        _print(f"Error: {e}")
        sys.exit(1)

    _print(f"polyglot-ai — provider={provider_name} model={model or provider.default_model}")
    _print("Type your message, or /exit to quit, /save to save now, /clear to reset.\n")

    while True:
        try:
            user_input = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue
        if user_input in ("/exit", "/quit"):
            break
        if user_input == "/clear":
            messages = []
            _print("[history cleared]")
            continue
        if user_input == "/save":
            config.save_session(session_path, messages)
            _print(f"[saved to {session_path}]")
            continue

        messages.append({"role": "user", "content": user_input})

        try:
            reply_chunks = []
            print("ai>  ", end="", flush=True)
            for chunk in provider.stream_chat(messages, system_prompt, model):
                reply_chunks.append(chunk)
                print(chunk, end="", flush=True)
            print("\n")
            reply = "".join(reply_chunks)
        except ProviderError as e:
            print()
            _print(f"[error: {e}]")
            messages.pop()
            continue

        messages.append({"role": "assistant", "content": reply})
        config.save_session(session_path, messages)

    if messages:
        config.save_session(session_path, messages)
        _print(f"[session saved: {session_path}]")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.list_personas:
        for name, prompt in config.DEFAULT_PERSONAS.items():
            _print(f"- {name}: {prompt}")
        return

    if args.list_sessions:
        sessions = config.list_sessions()
        if not sessions:
            _print("No saved sessions yet.")
        for s in sessions:
            _print(f"- {s}")
        return

    chat_loop(args)


if __name__ == "__main__":
    main()
