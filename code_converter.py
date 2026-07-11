"""
code_converter.py
=================

Final, self-contained Python → high-performance-code converter.

Consolidates everything demonstrated across the project notebooks
(w3test / w4tst / w5_final):

  * Multi-provider LLM access through OpenAI-compatible clients
    (OpenAI, Anthropic, Gemini, Grok, Groq, Ollama, OpenRouter).
  * System-info + Rust-toolchain probing to give the model an accurate
    picture of the target machine (from ``system_info.py``).
  * Two target languages — **C++** (MSVC / cl.exe) and **Rust** (rustc) —
    each with an aggressively optimised compile command.
  * Port Python → target, run the original Python, and compile+run the
    generated code, all from a single Gradio UI.
  * A polished interface driven by ``styles_adv.py``.

Run with::

    python code_converter.py

Requires a ``.env`` with at least ``OPENAI_API_KEY`` (others optional).
"""

from __future__ import annotations

import io
import os
import sys
import platform
import subprocess

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

from system_info import retrieve_system_info, rust_toolchain_info
from styles_adv import ADV_CSS, ADV_THEME, HEADER_HTML, FOOTER_HTML


# --------------------------------------------------------------------------- #
#  API keys & clients                                                          #
# --------------------------------------------------------------------------- #
load_dotenv(override=True)

_API_KEYS = {
    "openai": os.getenv("OPENAI_API_KEY"),
    "anthropic": os.getenv("ANTHROPIC_API_KEY"),
    "google": os.getenv("GOOGLE_API_KEY"),
    "grok": os.getenv("GROK_API_KEY"),
    "groq": os.getenv("GROQ_API_KEY"),
    "openrouter": os.getenv("OPENROUTER_API_KEY"),
}


def _report_keys() -> None:
    """Print a short, non-secret summary of which keys are configured."""
    labels = {
        "openai": ("OpenAI", 8, True),
        "anthropic": ("Anthropic", 7, False),
        "google": ("Google", 2, False),
        "grok": ("Grok", 4, False),
        "groq": ("Groq", 4, False),
        "openrouter": ("OpenRouter", 6, False),
    }
    for key, (name, n, required) in labels.items():
        val = _API_KEYS[key]
        if val:
            print(f"{name} API Key exists and begins {val[:n]}")
        else:
            suffix = "" if required else " (and this is optional)"
            print(f"{name} API Key not set{suffix}")


_report_keys()

# OpenAI-compatible endpoints for every provider.
_BASE_URLS = {
    "anthropic": "https://api.anthropic.com/v1/",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "grok": "https://api.x.ai/v1",
    "groq": "https://api.groq.com/openai/v1",
    "ollama": "http://localhost:11434/v1",
    "openrouter": "https://openrouter.ai/api/v1",
}

openai_client = OpenAI()
anthropic_client = OpenAI(api_key=_API_KEYS["anthropic"], base_url=_BASE_URLS["anthropic"])
gemini_client = OpenAI(api_key=_API_KEYS["google"], base_url=_BASE_URLS["gemini"])
grok_client = OpenAI(api_key=_API_KEYS["grok"], base_url=_BASE_URLS["grok"])
groq_client = OpenAI(api_key=_API_KEYS["groq"], base_url=_BASE_URLS["groq"])
ollama_client = OpenAI(api_key="ollama", base_url=_BASE_URLS["ollama"])
openrouter_client = OpenAI(api_key=_API_KEYS["openrouter"], base_url=_BASE_URLS["openrouter"])

MODELS = [
    "gpt-5",
    "claude-sonnet-4-5-20250929",
    "grok-4",
    "gemini-3-flash-preview",
    "qwen2.5-coder",
    "deepseek-coder-v2",
    "gpt-oss:20b",
    "qwen/qwen3-coder-30b-a3b-instruct",
    "openai/gpt-oss-120b",
]

CLIENTS = {
    "gpt-5": openai_client,
    "claude-sonnet-4-5-20250929": anthropic_client,
    "grok-4": grok_client,
    "gemini-3-flash-preview": gemini_client,
    "openai/gpt-oss-120b": groq_client,
    "qwen2.5-coder": ollama_client,
    "deepseek-coder-v2": ollama_client,
    "gpt-oss:20b": ollama_client,
    "qwen/qwen3-coder-30b-a3b-instruct": openrouter_client,
}


# --------------------------------------------------------------------------- #
#  System info (probed once at import)                                         #
# --------------------------------------------------------------------------- #
SYSTEM_INFO = retrieve_system_info()
RUST_INFO = rust_toolchain_info()

_WORK_DIR = os.path.dirname(os.path.abspath(__file__))
_VSDEVCMD = r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat"


# --------------------------------------------------------------------------- #
#  Language configuration                                                      #
# --------------------------------------------------------------------------- #
class LanguageConfig:
    """Everything that differs between a C++ and a Rust target."""

    def __init__(self, name, extension, editor_lang, compile_command, run_command, shell):
        self.name = name                     # human name, e.g. "C++"
        self.extension = extension           # file extension, e.g. "cpp"
        self.editor_lang = editor_lang       # gr.Code language token
        self.compile_command = compile_command
        self.run_command = run_command
        self.shell = shell                   # whether compile_command needs a shell

    @property
    def source_file(self) -> str:
        return os.path.join(_WORK_DIR, f"main.{self.extension}")


# ---- C++ : MSVC cl.exe inside a VS Developer environment ------------------- #
_CPP_COMPILE = (
    f'"{_VSDEVCMD}" -arch=x64 && '
    f'cd /d "{_WORK_DIR}" && '
    "cl /nologo /std:c++20 /O2 /GL /arch:AVX2 /fp:fast /EHsc /DNDEBUG "
    "main.cpp /Fe:main.exe /link /LTCG"
)

# ---- Rust : rustc with maximum runtime-performance flags ------------------- #
_RUST_COMPILE = [
    "rustc", "main.rs",
    "-C", "opt-level=3",
    "-C", "lto=fat",
    "-C", "codegen-units=1",
    "-C", "target-cpu=native",
    "-C", "panic=abort",
    "-C", "strip=symbols",
    "-C", "link-arg=/OPT:REF",
    "-C", "link-arg=/OPT:ICF",
]

LANGUAGES = {
    "C++": LanguageConfig(
        name="C++",
        extension="cpp",
        editor_lang="cpp",
        compile_command=_CPP_COMPILE,
        run_command=os.path.join(_WORK_DIR, "main.exe"),
        shell=True,
    ),
    "Rust": LanguageConfig(
        name="Rust",
        extension="rs",
        # gr.Code has no 'rust' token in Gradio 5.x; 'cpp' gives the closest
        # C-style syntax highlighting for Rust source.
        editor_lang="cpp",
        compile_command=_RUST_COMPILE,
        run_command=[os.path.join(_WORK_DIR, "main.exe")],
        shell=False,
    ),
}


# --------------------------------------------------------------------------- #
#  Prompt construction                                                         #
# --------------------------------------------------------------------------- #
def system_prompt_for(cfg: LanguageConfig) -> str:
    return (
        f"Your task is to convert Python code into high performance {cfg.name} code.\n"
        f"Respond only with {cfg.name} code. Do not provide any explanation other than "
        f"occasional comments.\n"
        f"The {cfg.name} response needs to produce an identical output in the fastest "
        f"possible time.\n"
    )


def user_prompt_for(python: str, cfg: LanguageConfig) -> str:
    return f"""
Port this Python code to {cfg.name} with the fastest possible implementation that produces identical output in the least time.
The system information is:
{SYSTEM_INFO}
Your response will be written to a file called main.{cfg.extension} and then compiled and executed; the compilation command is:
{cfg.compile_command}
Respond only with {cfg.name} code.
Python code to port:

```python
{python}
```
"""


def messages_for(python: str, cfg: LanguageConfig):
    return [
        {"role": "system", "content": system_prompt_for(cfg)},
        {"role": "user", "content": user_prompt_for(python, cfg)},
    ]


def _clean_reply(reply: str) -> str:
    """Strip markdown code fences the model may have added."""
    for fence in ("```cpp", "```rust", "```rs", "```c++", "```"):
        reply = reply.replace(fence, "")
    return reply.strip() + "\n"


# --------------------------------------------------------------------------- #
#  Core actions                                                                #
# --------------------------------------------------------------------------- #
def port(model: str, python: str, language: str) -> str:
    """Ask the selected model to port the Python code to `language`."""
    cfg = LANGUAGES[language]
    client = CLIENTS.get(model)
    if client is None:
        return f"// No client configured for model '{model}'."

    # OpenAI reasoning models accept a reasoning_effort hint.
    reasoning_effort = "high" if "gpt" in model else None
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages_for(python, cfg),
            reasoning_effort=reasoning_effort,
        )
    except Exception as exc:  # network / quota / provider errors
        return f"// Conversion failed for model '{model}':\n// {exc}"

    return _clean_reply(response.choices[0].message.content or "")


def write_output(code: str, language: str) -> str:
    """Persist generated code to main.<ext> and return the path."""
    cfg = LANGUAGES[language]
    with open(cfg.source_file, "w", encoding="utf-8") as f:
        f.write(code)
    return cfg.source_file


def run_python(code: str) -> str:
    """Execute the Python source in-process, capturing stdout."""
    globals_dict = {"__builtins__": __builtins__}
    buffer = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buffer
    try:
        exec(code, globals_dict)  # noqa: S102 — intentional user-code sandbox
        output = buffer.getvalue()
    except Exception as exc:
        output = f"Error: {exc}"
    finally:
        sys.stdout = old_stdout
    return output


def compile_and_run(code: str, language: str) -> str:
    """Write, compile and execute the generated code; return its stdout."""
    if platform.system() != "Windows":
        return (
            "Compilation is configured for Windows (MSVC / rustc on windows-msvc).\n"
            "Adjust the compile commands in code_converter.py for this platform."
        )

    cfg = LANGUAGES[language]
    write_output(code, language)
    try:
        subprocess.run(
            cfg.compile_command,
            check=True,
            text=True,
            capture_output=True,
            shell=cfg.shell,
        )
        run_result = subprocess.run(
            cfg.run_command,
            check=True,
            text=True,
            capture_output=True,
        )
        return run_result.stdout
    except subprocess.CalledProcessError as exc:
        return f"An error occurred:\n{exc.stderr or exc.stdout or exc}"
    except FileNotFoundError as exc:
        return f"Toolchain not found:\n{exc}"


# --------------------------------------------------------------------------- #
#  Sample Python payload                                                        #
# --------------------------------------------------------------------------- #
PYTHON_HARD = '''# Be careful to support large numbers

def lcg(seed, a=1664525, c=1013904223, m=2**32):
    value = seed
    while True:
        value = (a * value + c) % m
        yield value

def max_subarray_sum(n, seed, min_val, max_val):
    lcg_gen = lcg(seed)
    random_numbers = [next(lcg_gen) % (max_val - min_val + 1) + min_val for _ in range(n)]
    max_sum = float('-inf')
    for i in range(n):
        current_sum = 0
        for j in range(i, n):
            current_sum += random_numbers[j]
            if current_sum > max_sum:
                max_sum = current_sum
    return max_sum

def total_max_subarray_sum(n, initial_seed, min_val, max_val):
    total_sum = 0
    lcg_gen = lcg(initial_seed)
    for _ in range(20):
        seed = next(lcg_gen)
        total_sum += max_subarray_sum(n, seed, min_val, max_val)
    return total_sum

# Parameters
n = 10000         # Number of random numbers
initial_seed = 42 # Initial seed for the LCG
min_val = -10     # Minimum value of random numbers
max_val = 10      # Maximum value of random numbers

# Timing the function
import time
start_time = time.time()
result = total_max_subarray_sum(n, initial_seed, min_val, max_val)
end_time = time.time()

print("Total Maximum Subarray Sum (20 runs):", result)
print("Execution Time: {:.6f} seconds".format(end_time - start_time))
'''


# --------------------------------------------------------------------------- #
#  Gradio UI                                                                    #
# --------------------------------------------------------------------------- #
def build_ui() -> gr.Blocks:
    default_language = "C++"

    with gr.Blocks(
        css=ADV_CSS,
        theme=ADV_THEME,
        title="Python → C++/Rust Performance Porter",
        analytics_enabled=False,
    ) as ui:
        header = gr.HTML(HEADER_HTML(default_language))

        with gr.Row(equal_height=True):
            with gr.Column(scale=6):
                python = gr.Code(
                    label="Python (original)",
                    value=PYTHON_HARD,
                    language="python",
                    lines=26,
                    elem_classes=["card", "code-py"],
                )
            with gr.Column(scale=6):
                target = gr.Code(
                    label=f"{default_language} (generated)",
                    value="",
                    language=LANGUAGES[default_language].editor_lang,
                    lines=26,
                    elem_classes=["card", "code-out"],
                )

        with gr.Row(elem_classes=["controls"]):
            language = gr.Dropdown(
                list(LANGUAGES.keys()),
                value=default_language,
                show_label=False,
                scale=1,
            )
            python_run = gr.Button("▶ Run Python", elem_classes=["run-btn", "py"], scale=1)
            model = gr.Dropdown(MODELS, value=MODELS[0], show_label=False, scale=2)
            convert = gr.Button(
                f"✨ Port to {default_language}",
                variant="primary",
                elem_classes=["convert-btn"],
                scale=2,
            )
            target_run = gr.Button(
                f"▶ Run {default_language}",
                elem_classes=["run-btn", "target"],
                scale=1,
            )

        with gr.Row(equal_height=True):
            with gr.Column(scale=6):
                python_out = gr.TextArea(
                    label="Python result",
                    lines=8,
                    elem_classes=["card", "py-out"],
                )
            with gr.Column(scale=6):
                target_out = gr.TextArea(
                    label=f"{default_language} result",
                    lines=8,
                    elem_classes=["card", "target-out"],
                )

        gr.HTML(FOOTER_HTML)

        # ---- interactions ------------------------------------------------- #
        def on_language_change(lang: str):
            cfg = LANGUAGES[lang]
            return (
                HEADER_HTML(lang),                                 # header
                gr.update(label=f"{lang} (generated)",
                          language=cfg.editor_lang, value=""),     # target editor
                gr.update(value=f"✨ Port to {lang}"),              # convert btn
                gr.update(value=f"▶ Run {lang}"),                  # run btn
                gr.update(label=f"{lang} result", value=""),       # result box
            )

        language.change(
            fn=on_language_change,
            inputs=[language],
            outputs=[header, target, convert, target_run, target_out],
        )

        convert.click(fn=port, inputs=[model, python, language], outputs=[target])
        python_run.click(fn=run_python, inputs=[python], outputs=[python_out])
        target_run.click(fn=compile_and_run, inputs=[target, language], outputs=[target_out])

    return ui


# --------------------------------------------------------------------------- #
#  Entry point                                                                  #
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    build_ui().launch(inbrowser=True)
