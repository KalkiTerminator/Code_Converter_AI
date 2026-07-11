"""
styles_adv.py — Ultimate polished Gradio theme + CSS for the Python → C++/Rust converter.

Exposes:
    ADV_CSS      : a rich CSS string with an animated gradient hero, glassmorphism
                   cards, glow buttons and language-tinted result panels.
    ADV_THEME    : a gr.themes.Soft() instance tuned to match the CSS palette.
    HEADER_HTML  : a ready-to-drop hero banner (call as HEADER_HTML(language)).
    FOOTER_HTML  : a small credits / tips strip for the bottom of the app.

The whole thing is dark-first but degrades gracefully; every color is a CSS
variable so re-skinning is a one-line change.
"""

# --------------------------------------------------------------------------- #
#  Theme                                                                        #
# --------------------------------------------------------------------------- #
import gradio as gr

ADV_THEME = gr.themes.Soft(
    primary_hue=gr.themes.colors.purple,
    secondary_hue=gr.themes.colors.blue,
    neutral_hue=gr.themes.colors.slate,
    radius_size=gr.themes.sizes.radius_lg,
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
    font_mono=[gr.themes.GoogleFont("JetBrains Mono"), "ui-monospace", "monospace"],
).set(
    body_background_fill="#0b0e14",
    body_background_fill_dark="#0b0e14",
    block_background_fill="rgba(22,26,34,0.72)",
    block_border_width="1px",
    block_border_color="rgba(255,255,255,0.08)",
    block_radius="16px",
    block_shadow="0 8px 30px rgba(0,0,0,0.35)",
    input_background_fill="rgba(13,17,23,0.85)",
    button_large_radius="12px",
    button_primary_background_fill="linear-gradient(135deg,#753991,#4d5bd6)",
    button_primary_background_fill_hover="linear-gradient(135deg,#8a45ab,#5a68e6)",
    button_primary_text_color="#ffffff",
)


# --------------------------------------------------------------------------- #
#  CSS                                                                          #
# --------------------------------------------------------------------------- #
ADV_CSS = """
/* ------------------------------- palette ------------------------------- */
:root {
  --py-color:   #4dabf7;   /* python blue   */
  --py-glow:    rgba(77,171,247,.55);
  --cpp-color:  #f0a500;   /* c++ amber     */
  --cpp-glow:   rgba(240,165,0,.55);
  --rust-color: #ff7043;   /* rust orange   */
  --rust-glow:  rgba(255,112,67,.55);
  --accent:     #a06bff;   /* violet accent */
  --accent-2:   #4d5bd6;   /* indigo accent */
  --card:       rgba(22,26,34,.72);
  --card-solid: #12161e;
  --text:       #e9eef5;
  --muted:      #9aa7b8;
  --stroke:     rgba(255,255,255,.08);
}

/* --------------------------- global container -------------------------- */
.gradio-container {
  max-width: 100% !important;
  padding: 0 clamp(16px, 4vw, 56px) 40px !important;
  background:
    radial-gradient(1200px 600px at 15% -10%, rgba(160,107,255,.18), transparent 60%),
    radial-gradient(1000px 500px at 100% 0%, rgba(77,91,214,.16), transparent 55%),
    #0b0e14 !important;
  color: var(--text);
}

/* ------------------------------- hero ---------------------------------- */
.hero {
  position: relative;
  margin: 22px 0 8px;
  padding: 30px 34px;
  border-radius: 22px;
  overflow: hidden;
  border: 1px solid var(--stroke);
  background: linear-gradient(120deg, #1a1030, #101a34, #10222b);
  background-size: 240% 240%;
  animation: heroShift 16s ease infinite;
  box-shadow: 0 12px 40px rgba(0,0,0,.45);
}
@keyframes heroShift {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
.hero::after {
  content: "";
  position: absolute; inset: 0;
  background: radial-gradient(600px 200px at 90% 120%, rgba(255,112,67,.20), transparent 70%);
  pointer-events: none;
}
.hero h1 {
  margin: 0;
  font-size: clamp(1.6rem, 3vw, 2.4rem);
  font-weight: 800;
  letter-spacing: -.02em;
  background: linear-gradient(90deg, #fff, #c9b6ff 40%, #7fd7ff 80%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hero p {
  margin: 8px 0 0;
  color: var(--muted);
  font-size: .98rem;
  max-width: 720px;
}
.hero .badges { margin-top: 16px; display: flex; gap: 10px; flex-wrap: wrap; }
.hero .badge {
  font-size: .78rem; font-weight: 600;
  padding: 5px 12px; border-radius: 999px;
  border: 1px solid var(--stroke);
  background: rgba(255,255,255,.05);
  color: var(--text);
  backdrop-filter: blur(6px);
}
.hero .badge.py   { color: var(--py-color);   border-color: var(--py-glow); }
.hero .badge.cpp  { color: var(--cpp-color);  border-color: var(--cpp-glow); }
.hero .badge.rust { color: var(--rust-color); border-color: var(--rust-glow); }

/* ------------------------------- cards --------------------------------- */
.card, .gr-group {
  background: var(--card) !important;
  border: 1px solid var(--stroke) !important;
  border-radius: 16px !important;
  backdrop-filter: blur(10px);
}

/* code editors get a subtle top accent line */
.code-py  { box-shadow: inset 0 3px 0 0 var(--py-color);  border-radius: 14px; }
.code-out { box-shadow: inset 0 3px 0 0 var(--accent);    border-radius: 14px; }

/* labels */
label span, .gr-box label { color: var(--muted) !important; font-weight: 600; }

/* ------------------------------ controls ------------------------------- */
.controls {
  margin: 14px 0 6px !important;
  padding: 12px 14px;
  border-radius: 16px;
  border: 1px solid var(--stroke);
  background: linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.01));
}
.controls .wrap { gap: 12px; justify-content: center; align-items: center; }

/* buttons — shared */
button.lg, .controls button {
  font-weight: 700 !important;
  letter-spacing: .01em;
  transition: transform .12s ease, box-shadow .18s ease, filter .18s ease !important;
}
button.lg:hover, .controls button:hover { transform: translateY(-1px); }
button.lg:active, .controls button:active { transform: translateY(0); }

/* convert button — the star of the show */
.convert-btn button {
  background: linear-gradient(135deg, var(--accent), var(--accent-2)) !important;
  color: #fff !important;
  border: none !important;
  box-shadow: 0 8px 24px rgba(160,107,255,.35);
}
.convert-btn button:hover {
  box-shadow: 0 10px 30px rgba(160,107,255,.55);
  filter: brightness(1.06);
}

/* run buttons — ghost style with language-tinted hover glow */
.run-btn button {
  background: rgba(255,255,255,.04) !important;
  color: var(--text) !important;
  border: 1px solid var(--stroke) !important;
}
.run-btn.py button:hover {
  border-color: var(--py-color) !important;
  box-shadow: 0 0 0 2px var(--py-glow) inset, 0 6px 20px var(--py-glow);
}
.run-btn.target button:hover {
  border-color: var(--cpp-color) !important;
  box-shadow: 0 0 0 2px var(--cpp-glow) inset, 0 6px 20px var(--cpp-glow);
}

/* dropdown */
.controls .gr-dropdown, .controls .wrap-inner { min-width: 220px; }

/* ------------------------------ results -------------------------------- */
.py-out textarea {
  background: linear-gradient(180deg, rgba(77,171,247,.16), rgba(77,171,247,.06)) !important;
  border: 1px solid var(--py-glow) !important;
  color: #d6ecff !important;
  font-family: "JetBrains Mono", ui-monospace, monospace !important;
  font-weight: 600;
}
.target-out textarea {
  background: linear-gradient(180deg, rgba(240,165,0,.18), rgba(240,165,0,.07)) !important;
  border: 1px solid var(--cpp-glow) !important;
  color: #ffe9b8 !important;
  font-family: "JetBrains Mono", ui-monospace, monospace !important;
  font-weight: 600;
}

/* small stat / speedup pill */
.speedup {
  display: inline-flex; align-items: center; gap: 8px;
  margin-top: 10px; padding: 8px 14px;
  border-radius: 999px;
  font-weight: 700; font-size: .9rem;
  color: #baffc9;
  background: rgba(46,204,113,.10);
  border: 1px solid rgba(46,204,113,.35);
}

/* ------------------------------- footer -------------------------------- */
.footer {
  margin-top: 26px; padding-top: 16px;
  border-top: 1px solid var(--stroke);
  color: var(--muted); font-size: .84rem;
  display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px;
}
.footer a { color: var(--accent); text-decoration: none; }
.footer a:hover { text-decoration: underline; }

/* hide gradio footer branding for a cleaner look */
footer { display: none !important; }

/* scrollbars */
*::-webkit-scrollbar { width: 10px; height: 10px; }
*::-webkit-scrollbar-thumb { background: rgba(255,255,255,.12); border-radius: 8px; }
*::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,.22); }
"""


# --------------------------------------------------------------------------- #
#  HTML fragments                                                              #
# --------------------------------------------------------------------------- #
def HEADER_HTML(language: str = "C++") -> str:
    """Hero banner. `language` is the currently selected target language."""
    lang_class = "rust" if language.lower() == "rust" else "cpp"
    return f"""
    <div class="hero">
      <h1>⚡ Python → {language} Performance Porter</h1>
      <p>
        Paste Python, pick a model, and get a hand-tuned, compilable
        {language} port that produces <b>identical output</b> at native speed —
        then benchmark both side by side, right here.
      </p>
      <div class="badges">
        <span class="badge py">🐍 Python source</span>
        <span class="badge {lang_class}">🦀 {language} target</span>
        <span class="badge">🤖 Multi-model</span>
        <span class="badge">🏎️ Native benchmarks</span>
      </div>
    </div>
    """


FOOTER_HTML = """
<div class="footer">
  <span>Built with Gradio · OpenAI-compatible clients · MSVC / rustc back-ends</span>
  <span>Tip: use <b>Run Python</b> then <b>Run target</b> to compare wall-clock times.</span>
</div>
"""
