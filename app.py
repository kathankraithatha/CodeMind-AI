import streamlit as st
import os
import time
from dotenv import load_dotenv
from google import genai
import streamlit_css as sc
import prompt as pr

# Config & Init
load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
gemini_model = "gemini-2.5-flash-lite"

    
st.set_page_config(
    page_title="CodeMind AI",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS — Dark terminal-luxury theme (streamlit_css.py)
sc.ai_dev_assistant_css()

# LLM Core

def call_llm(prompt: str) -> str:
    try:
        response = client.models.generate_content(
            model=gemini_model,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"⚠️ Error: {str(e)}"



# Agent Pipeline
def run_agent(code: str):
    """3-step agentic improvement loop."""
    steps = []

    # Step 1 — analyze & fix
    st.markdown('<div class="step-badge"><span class="dot"></span>Step 1 · Analyzing & fixing issues</div>', unsafe_allow_html=True)
    improved = call_llm(f"""
{pr.run_agent_prompt}
```
{code}
```
""")
    steps.append(improved)
    time.sleep(0.3)

    # Step 2 — optimize
    st.markdown('<div class="step-badge"><span class="dot"></span>Step 2 · Optimizing & applying best practices</div>', unsafe_allow_html=True)
    final_code = call_llm(f"""
{pr.run_agent_prompt}
```
{improved}
```
""")
    steps.append(final_code)
    time.sleep(0.3)

    # Step 3 — explain
    st.markdown('<div class="step-badge"><span class="dot"></span>Step 3 · Generating explanation</div>', unsafe_allow_html=True)
    explanation = call_llm(f"""

{pr.run_agent_improve_code_prompt}

Code:
```
{final_code}
```
""")
    try:
        return final_code, explanation
    except Exception as e:
        st.error("⚠️ Rate limit hit. Please wait a moment and try again.")
    


# Prompt Builder
def build_prompt(code: str, action: str, level: str) -> str:
    action_map = {
        "Explain Code":  "Explain this code comprehensively",
        "Optimize Code": "Optimize and refactor this code for production",
        "Find Bugs":     "Identify all bugs, vulnerabilities, and anti-patterns",
    }
    task = action_map.get(action, "Analyze this code")

    return f"""You are a world-class senior software engineer and technical mentor.

Task: {task}

Audience level: {level} developer


{pr.prompt_builder}
Code to analyze:
```
{code}
```
"""


# Hero Header
sc.codeMindHeader()


# 🔝 Controls Row
col_a, col_b, col_c, col_d = st.columns([2, 1.4, 1.4, 1.2])

with col_a:
    action = st.selectbox("Action", ["Explain Code", "Optimize Code", "Find Bugs"])

with col_b:
    level = st.selectbox("Audience Level", ["Beginner", "Intermediate", "Expert"])

with col_c:
    language = st.selectbox("Language", ["Auto-detect", "Python", "JavaScript", "TypeScript", "Go", "Rust", "Java", "C++"])

with col_d:
    agent_mode = st.toggle("⬡ Agent Mode", value=False)

if agent_mode:
    st.markdown("""
    <div class="agent-card">
        ⬡ &nbsp;<strong>Agent Mode active</strong> — multi-step pipeline: Analyze → Fix → Optimize → Explain
    </div>
    """, unsafe_allow_html=True)


# Editor + Output
col1, col2 = st.columns(2)

with col1:
    code_input = st.text_area(
        "Code Input",
        placeholder="# Paste your code here...\ndef example():\n    pass",
        height=340,
    )

with col2:
    st.markdown('<div class="output-label"><span></span>Analysis Output</div>', unsafe_allow_html=True)
    output_container = st.container()


#  Run Button
btn_col, hint_col = st.columns([1, 5])
with btn_col:
    run_clicked = st.button("▶ Run Analysis", use_container_width=True)
with hint_col:
    st.markdown('<span style="font-family:\'JetBrains Mono\',monospace;font-size:0.72rem;color:#334155;">Press to analyze · Results appear on the right</span>', unsafe_allow_html=True)

if run_clicked:
    if not code_input.strip():
        st.warning("⚠ Paste some code first.")
    else:
        with output_container:
            with st.spinner("Thinking like a senior engineer..."):
                if agent_mode:
                    final_code, explanation = run_agent(code_input)
                    result = f"### 💻 Final Improved Code\n{final_code}\n\n### 🧠 What Changed\n{explanation}"
                else:
                    lang_hint = f"\nLanguage: {language}" if language != "Auto-detect" else ""
                    result = call_llm(build_prompt(code_input + lang_hint, action, level))

                st.session_state["last_result"] = result
                st.session_state["last_code"] = code_input

        with output_container:
            st.markdown(result)

elif "last_result" in st.session_state:
    with output_container:
        st.markdown(st.session_state["last_result"])
else:
    with output_container:
        st.markdown(
            '<div class="output-panel" style="color:#1e293b;font-size:0.78rem;">'
            '// Output will appear here after analysis...'
            '</div>',
            unsafe_allow_html=True
        )


# Chat Section

st.markdown('<div class="divider" style="margin-top:2.5rem"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Context-Aware Chat</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Render history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
if user_input := st.chat_input("Ask anything about your code — debugging, architecture, tradeoffs..."):
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Build context
    context_block = ""
    if "last_code" in st.session_state:
        context_block = f"""
## Context from previous analysis
**Code analyzed:**
```
{st.session_state['last_code']}
```

**Previous analysis:**
{st.session_state.get('last_result', '(none)')}

---
"""

    history_text = "\n".join(
        f"{m['role'].upper()}: {m['content']}"
        for m in st.session_state["messages"]
    )

    chat_prompt = f"""You are CodeMind AI — a senior software engineering assistant. You are precise, opinionated, and deeply technical.

{context_block}

## Conversation
{history_text}

## Instructions
Answer the latest user message directly and concisely, Use code blocks when showing code, Reference the analyzed code above when relevant, Be direct — no filler phrases
"""

    with st.chat_message("assistant"):
        with st.spinner(""):
            reply = call_llm(chat_prompt)
            st.markdown(reply)

    st.session_state["messages"].append({"role": "assistant", "content": reply})


# Footer Controls
st.markdown('<div style="margin-top:1rem"></div>', unsafe_allow_html=True)
footer_col1, footer_col2 = st.columns([1, 8])
with footer_col1:
    if st.button("🗑 Clear Chat"):
        st.session_state["messages"] = []
        st.rerun()