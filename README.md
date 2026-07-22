# Code Converter AI

An AI-powered tool that ports **Python** code into high-performance **C++** or **Rust**,
then compiles and runs it — all from a single polished [Gradio](https://www.gradio.app/) UI.

Give it a Python program, pick a model and a target language, and it generates an
aggressively optimised, drop-in equivalent that produces identical output. Run the
original Python and the generated native code side by side to compare correctness and
speed.

---

## Features

- **Multi-provider LLM access** through OpenAI-compatible clients — OpenAI, Anthropic,
  Google Gemini, Grok (xAI), Groq, [Ollama](https://ollama.com/) (local), and
  [OpenRouter](https://openrouter.ai/).
- **Two native targets:**
  - **C++** compiled with MSVC `cl.exe` (`/std:c++20 /O2 /GL /arch:AVX2 /fp:fast /LTCG`).
  - **Rust** compiled with `rustc` (`opt-level=3`, fat LTO, `target-cpu=native`, ...).
- **System-aware prompting** — probes the host machine and Rust toolchain
  (`system_info.py`) so the model tailors code to the actual target hardware.
- **Side-by-side execution** — run the original Python in-process and compile + run the
  generated code, comparing output and timing.
- **Polished dark-first interface** — animated gradient hero, glassmorphism cards, and
  language-tinted result panels (`styles_adv.py`).

---

## Project layout

| File | Purpose |
| --- | --- |
| `code_converter.py` | Main application — LLM porting logic, compilation, and the Gradio UI. |
| `system_info.py` | Probes OS, CPU, and the Rust/C++ toolchains to inform the model. |
| `styles_adv.py` | Advanced Gradio theme, CSS, and header/footer HTML. |
| `styles.py` | Simpler baseline styling. |
| `main.py` | Minimal entry-point stub. |
| `main.cpp` / `main.rs` | Most recently generated target code (overwritten on each conversion). |
| `w3test.ipynb`, `w4tst.ipynb`, `w5_final.ipynb` | Development notebooks the app consolidates. |
| `pyproject.toml` / `uv.lock` | Project metadata and locked dependencies. |

---

## Requirements

- **Python 3.11+**
- A **Windows** host for compilation:
  - **C++** — Visual Studio 2022 Build Tools (MSVC `cl.exe` / `VsDevCmd.bat`).
  - **Rust** — the `rustc` toolchain (`windows-msvc` target).
- At least one LLM API key (see below). Local models via Ollama need no key.

> The porting and UI run on any platform, but the **compile & run** step is currently
> configured for Windows. Adjust the compile commands in `code_converter.py` to target
> other platforms.

---

## Setup

This project uses [`uv`](https://docs.astral.sh/uv/) for dependency management.

```bash
# Install dependencies from the lockfile
uv sync
```

Or with plain `pip`:

```bash
pip install -e .
```

### Configure API keys

Create a `.env` file in the project root with the providers you plan to use
(`OPENAI_API_KEY` is the common default; the rest are optional):

```dotenv
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=...
GOOGLE_API_KEY=...
GROK_API_KEY=...
GROQ_API_KEY=...
OPENROUTER_API_KEY=...
```

---

## Usage

```bash
python code_converter.py
```

This launches the Gradio app in your browser. From there:

1. Paste or edit the **Python** source in the left editor.
2. Choose a **target language** (C++ or Rust) and an **LLM model**.
3. Click **▶ Run Python** to see the reference output.
4. Click **✨ Port** to generate the native code.
5. Click **▶ Run** on the target side to compile and execute the generated code, then
   compare the result and timing.

---

## How it works

For each conversion the app builds a system + user prompt that includes the probed
machine details and the exact compile command, asks the selected model to respond with
**only** target-language code, strips any markdown fences, and writes the result to
`main.cpp` or `main.rs`. Running the target compiles that file with the optimised
toolchain flags and executes the produced binary, capturing its stdout.

---

## Supported models

| Model | Provider |
| --- | --- |
| `gpt-5` | OpenAI |
| `claude-sonnet-4-5-20250929` | Anthropic |
| `grok-4` | Grok (xAI) |
| `gemini-3-flash-preview` | Google Gemini |
| `openai/gpt-oss-120b` | Groq |
| `qwen2.5-coder`, `deepseek-coder-v2`, `gpt-oss:20b` | Ollama (local) |
| `qwen/qwen3-coder-30b-a3b-instruct` | OpenRouter |
