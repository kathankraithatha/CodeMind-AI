import streamlit as st
def ai_dev_assistant_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');
 
/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }
 
html, body, [data-testid="stAppViewContainer"] {
    background: #080b12 !important;
    color: #e2e8f0 !important;
    font-family: 'Syne', sans-serif;
}
 
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 50% at 20% 0%, rgba(56, 189, 248, 0.06) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 100%, rgba(168, 85, 247, 0.06) 0%, transparent 60%),
        #080b12 !important;
}
 
/* hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
.block-container { padding: 2rem 3rem 4rem !important; max-width: 1400px; }
 
/* ── Typography ── */
h1, h2, h3, h4 { font-family: 'Syne', sans-serif; letter-spacing: -0.02em; }
 
/* ── Hero Header ── */
.hero {
    display: flex;
    align-items: center;
    gap: 1.2rem;
    margin-bottom: 0.25rem;
}
.hero-badge {
    background: linear-gradient(135deg, #38bdf8, #a855f7);
    border-radius: 10px;
    width: 44px; height: 44px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem;
    box-shadow: 0 0 24px rgba(56,189,248,0.35);
    flex-shrink: 0;
}
.hero-title {
    font-size: 2rem; font-weight: 800;
    background: linear-gradient(90deg, #f0f9ff 30%, #a855f7 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0; line-height: 1.1;
}
.hero-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem; font-weight: 300;
    color: #64748b; letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 0.1rem;
}
 
/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(56,189,248,0.3), rgba(168,85,247,0.3), transparent);
    margin: 1.5rem 0 2rem;
}
 
/* ── Control Cards ── */
.control-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
 
/* ── Selectbox / Widgets ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stSelectbox"] > label {
    color: #94a3b8 !important;
}
[data-testid="stSelectbox"] > div > div {
    background: rgba(15, 23, 42, 0.8) !important;
    border: 1px solid rgba(56, 189, 248, 0.15) !important;
    border-radius: 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    color: #e2e8f0 !important;
    transition: border-color 0.2s;
}
[data-testid="stSelectbox"] > div > div:hover {
    border-color: rgba(56, 189, 248, 0.4) !important;
}
[data-testid="stSelectbox"] label {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #475569 !important;
    margin-bottom: 0.3rem !important;
}
 
/* ── Toggle ── */
[data-testid="stToggle"] label {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #475569 !important;
}
[data-testid="stToggle"] > div { gap: 0.5rem; }
 
/* ── Code / Text Areas ── */
[data-testid="stTextArea"] textarea {
    background: rgba(10, 15, 28, 0.9) !important;
    border: 1px solid rgba(56, 189, 248, 0.12) !important;
    border-radius: 12px !important;
    color: #7dd3fc !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    line-height: 1.6 !important;
    resize: vertical !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: rgba(56, 189, 248, 0.45) !important;
    box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.08) !important;
    outline: none !important;
}
[data-testid="stTextArea"] label {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #475569 !important;
}
 
/* ── Output Panel ── */
.output-panel {
    background: rgba(10, 15, 28, 0.7);
    border: 1px solid rgba(168, 85, 247, 0.15);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    min-height: 300px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    line-height: 1.7;
    color: #cbd5e1;
    position: relative;
    overflow: hidden;
}
.output-panel::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #38bdf8, #a855f7, #38bdf8);
    background-size: 200% 100%;
    animation: shimmer 3s linear infinite;
}
@keyframes shimmer { 0% { background-position: 200% 0 } 100% { background-position: -200% 0 } }
 
.output-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.72rem; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: #475569; margin-bottom: 0.75rem;
    display: flex; align-items: center; gap: 0.5rem;
}
.output-label span {
    width: 6px; height: 6px; border-radius: 50%;
    background: #a855f7;
    display: inline-block;
    box-shadow: 0 0 8px #a855f7;
}
 
/* ── Run Button ── */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #0ea5e9, #8b5cf6) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.06em !important;
    padding: 0.6rem 1.8rem !important;
    cursor: pointer !important;
    transition: opacity 0.2s, transform 0.15s, box-shadow 0.2s !important;
    box-shadow: 0 4px 20px rgba(14, 165, 233, 0.25) !important;
}
[data-testid="stButton"] > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 28px rgba(14, 165, 233, 0.35) !important;
}
[data-testid="stButton"] > button:active {
    transform: translateY(0) !important;
}
 
/* ── Chat ── */
.section-label {
    font-size: 0.72rem; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: #475569; margin-bottom: 1rem;
    display: flex; align-items: center; gap: 0.6rem;
}
.section-label::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg, rgba(56,189,248,0.2), transparent);
}
 
[data-testid="stChatMessage"] {
    background: rgba(15, 23, 42, 0.6) !important;
    border: 1px solid rgba(56, 189, 248, 0.08) !important;
    border-radius: 12px !important;
    margin-bottom: 0.75rem !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.83rem !important;
    line-height: 1.65 !important;
}
[data-testid="stChatMessage"][data-testid*="user"] {
    border-color: rgba(168, 85, 247, 0.15) !important;
}
 
[data-testid="stChatInput"] {
    background: rgba(10, 15, 28, 0.9) !important;
    border: 1px solid rgba(56, 189, 248, 0.15) !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"] textarea {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.83rem !important;
    color: #e2e8f0 !important;
    background: transparent !important;
}
 
/* ── Status pills ── */
.step-badge {
    display: inline-flex; align-items: center; gap: 0.4rem;
    background: rgba(56,189,248,0.08);
    border: 1px solid rgba(56,189,248,0.2);
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem; color: #38bdf8;
    margin-bottom: 0.5rem;
}
.step-badge .dot {
    width: 5px; height: 5px; border-radius: 50%;
    background: #38bdf8;
    animation: pulse 1.2s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.8); }
}
 
/* ── Spinner override ── */
[data-testid="stSpinner"] > div {
    border-top-color: #38bdf8 !important;
}
 
/* ── Info / Warning ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
}
 
/* ════════════════════════════════════════
   ✨ CODE BLOCK STYLING — Full Override
   Targets every selector Streamlit uses
   ════════════════════════════════════════ */
 
/* Inline code — backtick snippets */
.stMarkdown code,
.stMarkdown p code,
.stMarkdown li code,
[data-testid="stMarkdownContainer"] code {
    background: rgba(56, 189, 248, 0.1) !important;
    color: #7dd3fc !important;
    border: 1px solid rgba(56, 189, 248, 0.18) !important;
    border-radius: 5px !important;
    padding: 0.15em 0.45em !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82em !important;
    font-weight: 400 !important;
}
 
/* Fenced code block wrapper — the <pre> */
.stMarkdown pre,
[data-testid="stMarkdownContainer"] pre {
    position: relative !important;
    background: #0d1117 !important;
    border: 1px solid rgba(56, 189, 248, 0.18) !important;
    border-radius: 12px !important;
    padding: 0 !important;
    margin: 1.1rem 0 !important;
    overflow: hidden !important;
    box-shadow:
        0 0 0 1px rgba(56, 189, 248, 0.05),
        0 8px 32px rgba(0, 0, 0, 0.5),
        inset 0 1px 0 rgba(255,255,255,0.03) !important;
}
 
/* Gradient top accent line on every code block */
.stMarkdown pre::before,
[data-testid="stMarkdownContainer"] pre::before {
    content: '' !important;
    display: block !important;
    height: 2px !important;
    background: linear-gradient(90deg, #38bdf8 0%, #a855f7 50%, #38bdf8 100%) !important;
    background-size: 200% 100% !important;
    animation: shimmer 4s linear infinite !important;
    border-radius: 12px 12px 0 0 !important;
}
 
/* Fake window chrome dots */
.stMarkdown pre::after,
[data-testid="stMarkdownContainer"] pre::after {
    content: '● ● ●' !important;
    display: block !important;
    font-size: 0.55rem !important;
    letter-spacing: 0.25em !important;
    color: #334155 !important;
    padding: 0.55rem 1rem 0 !important;
    line-height: 1 !important;
    background: #0d1117 !important;
}
 
/* The actual <code> inside <pre> — highlight.js will color this */
.stMarkdown pre code,
[data-testid="stMarkdownContainer"] pre code {
    display: block !important;
    background: #0d1117 !important;
    color: #abb2bf !important;           /* fallback before hljs fires */
    border: none !important;
    border-radius: 0 !important;
    padding: 1rem 1.25rem 1.25rem !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.83rem !important;
    line-height: 1.7 !important;
    overflow-x: auto !important;
    tab-size: 4 !important;
    white-space: pre !important;
    /* custom scrollbar inside code block */
    scrollbar-width: thin;
    scrollbar-color: rgba(56,189,248,0.2) transparent;
}
.stMarkdown pre code::-webkit-scrollbar { height: 4px; }
.stMarkdown pre code::-webkit-scrollbar-thumb {
    background: rgba(56,189,248,0.2); border-radius: 4px;
}
 
/* ── highlight.js token overrides (Atom One Dark palette) ── */
.hljs { background: #0d1117 !important; color: #abb2bf !important; }
.hljs-keyword, .hljs-selector-tag, .hljs-built_in { color: #c678dd !important; font-style: italic; }
.hljs-string, .hljs-attr                           { color: #98c379 !important; }
.hljs-number, .hljs-literal                        { color: #d19a66 !important; }
.hljs-comment, .hljs-quote                         { color: #5c6370 !important; font-style: italic; }
.hljs-title, .hljs-name, .hljs-section             { color: #61afef !important; }
.hljs-type, .hljs-class .hljs-title                { color: #e5c07b !important; }
.hljs-variable, .hljs-template-variable            { color: #e06c75 !important; }
.hljs-symbol, .hljs-bullet, .hljs-link             { color: #56b6c2 !important; }
.hljs-params                                       { color: #abb2bf !important; }
.hljs-function                                     { color: #61afef !important; }
.hljs-meta                                         { color: #e06c75 !important; }
.hljs-deletion                                     { background: rgba(224, 108, 117, 0.12) !important; }
.hljs-addition                                     { background: rgba(152, 195, 121, 0.12) !important; }
.hljs-emphasis                                     { font-style: italic !important; }
.hljs-strong                                       { font-weight: bold !important; }
 
/* ── Agent Mode card ── */
.agent-card {
    background: rgba(168,85,247,0.06);
    border: 1px solid rgba(168,85,247,0.2);
    border-radius: 10px;
    padding: 0.6rem 1rem;
    display: flex; align-items: center; gap: 0.6rem;
    font-size: 0.75rem; color: #c084fc;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 1rem;
}
 
/* ── Columns gap ── */
[data-testid="stHorizontalBlock"] { gap: 1.5rem !important; }
 
/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(56,189,248,0.25); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)


def codeMindHeader():
    st.markdown("""
<div class="hero">
    <div class="hero-badge">⬡</div>
    <div>
        <div class="hero-title">CodeMind AI</div>
        <div class="hero-sub">Intelligent code analysis · Powered by Gemini</div>
    </div>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)