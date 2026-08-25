# polyglot-ai 🤖

**One terminal chat client for Claude, GPT, and local Ollama models.**
Switch providers with a flag, save/resume sessions, and use persona presets — all from your terminal.

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-brightgreen)

---

## Why

Most AI CLI tools lock you into one provider. `polyglot-ai` doesn't care whether
you're using Anthropic's Claude, OpenAI's GPT, or a fully local model through
Ollama — same interface, same saved sessions, same personas.

## Features

- 🔀 **Multi-provider** — Anthropic, OpenAI, or local Ollama, switch with `--provider`
- 💾 **Auto-saved sessions** — every conversation is saved as JSON and resumable with `--resume`
- 🎭 **Persona presets** — `coder`, `teacher`, `brutalist`, or write your own system prompt
- ⚡ **Streaming output** — tokens appear as they're generated
- 🖥️ **Zero-lock-in** — plain JSON sessions, no vendor database

## Install

```bash
git clone https://github.com/yourusername/polyglot-ai.git
cd polyglot-ai
pip install -e ".[all]"
```

Or just the provider you need:

```bash
pip install -e ".[anthropic]"   # Claude only
pip install -e ".[openai]"      # GPT only
pip install -e ".[ollama]"      # local models only
```

## Setup

Set the API key for whichever provider you plan to use:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
# or
export OPENAI_API_KEY=sk-...
```

For Ollama, just have it running locally — no key needed:

```bash
ollama serve
```

## Usage

```bash
# Start chatting with the default provider (anthropic)
polyglot-ai

# Use a specific provider and model
polyglot-ai --provider openai --model gpt-4o

# Start with a persona
polyglot-ai --persona coder

# Resume a previous session
polyglot-ai --resume ~/.polyglot-ai/sessions/session-20260825-101500.json

# List saved sessions / personas
polyglot-ai --list-sessions
polyglot-ai --list-personas
```

Inside the chat:

| Command  | Action                      |
|----------|------------------------------|
| `/save`  | Save the session immediately |
| `/clear` | Clear conversation history   |
| `/exit`  | Quit (auto-saves)             |

## Project layout

```
polyglot-ai/
├── polyglot_ai/
│   ├── main.py         # CLI entrypoint + REPL loop
│   ├── providers.py    # Anthropic / OpenAI / Ollama adapters
│   └── config.py        # config + session persistence
├── tests/
│   └── test_basic.py
├── pyproject.toml
└── requirements.txt
```

## Adding a new provider

Subclass `BaseProvider` in `providers.py` and implement `stream_chat()`,
then register it in the `PROVIDERS` dict. That's it — the CLI and session
logic don't need any changes.

## Running tests

```bash
pip install -e ".[dev]"
pytest
```

## Roadmap

- [ ] Multi-turn tool/function calling support
- [ ] `--export markdown` to turn a session into a shareable doc
- [ ] Web UI wrapper (Flask/FastAPI) reusing the same provider layer
- [ ] Token/cost tracking per session

## Contributing

PRs welcome. Please open an issue first for larger changes.

## License

MIT — see [LICENSE](LICENSE).
