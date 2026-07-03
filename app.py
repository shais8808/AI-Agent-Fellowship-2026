"""
Orbit — AI Workspace
A unified chat interface for Gemini, DeepSeek, and Llama.
Run with: streamlit run app.py
"""

import uuid
from datetime import date, datetime

import streamlit as st
from dotenv import load_dotenv
import os

from providers import MODEL_CATALOG, get_completion
from templates import BUILTIN_TEMPLATES, TEMPLATE_ICONS
from style import get_css

load_dotenv()

st.set_page_config(page_title="Orbit — AI Workspace", page_icon="🪐", layout="wide", initial_sidebar_state="expanded")

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

def new_session(title="New chat"):
    sid = str(uuid.uuid4())
    st.session_state.sessions[sid] = {
        "title": title,
        "messages": [],
        "system_prompt": "",
        "model": list(MODEL_CATALOG.keys())[0],
        "created": datetime.now(),
    }
    st.session_state.current_id = sid
    return sid


if "sessions" not in st.session_state:
    st.session_state.sessions = {}
    new_session()

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if "custom_templates" not in st.session_state:
    st.session_state.custom_templates = {}

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

if "session_search" not in st.session_state:
    st.session_state.session_search = ""

# Clear the composer *before* the text_area widget is instantiated this run,
# since Streamlit forbids mutating a widget's session_state key after creation.
if st.session_state.get("_clear_input"):
    st.session_state.user_input = ""
    st.session_state["_clear_input"] = False

st.markdown(get_css(st.session_state.dark_mode), unsafe_allow_html=True)

current = st.session_state.sessions[st.session_state.current_id]

api_keys = {
    "gemini": os.getenv("GEMINI_API_KEY", ""),
    "github": os.getenv("GITHUB_TOKEN", ""),
}

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown('<div class="orbit-brand">🪐 Orbit</div>', unsafe_allow_html=True)

    st.markdown('<div class="orbit-primary-btn">', unsafe_allow_html=True)
    if st.button("＋ New chat", use_container_width=True):
        new_session()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.session_state.session_search = st.text_input(
        "Search", value=st.session_state.session_search, placeholder="🔍 Search chats", label_visibility="collapsed"
    )

    st.markdown('<div class="orbit-date-label">Chats</div>', unsafe_allow_html=True)

    sorted_sessions = sorted(st.session_state.sessions.items(), key=lambda kv: kv[1]["created"], reverse=True)
    query = st.session_state.session_search.lower().strip()

    for sid, sess in sorted_sessions:
        if query and query not in sess["title"].lower():
            continue
        label = sess["title"][:32] + ("…" if len(sess["title"]) > 32 else "")
        is_active = sid == st.session_state.current_id
        prefix = "🟣 " if is_active else "💬 "
        if st.button(prefix + label, key=f"sess_{sid}", use_container_width=True):
            st.session_state.current_id = sid
            st.rerun()

    st.divider()

    st.markdown('<div class="orbit-date-label">Model</div>', unsafe_allow_html=True)
    model_choice = st.selectbox(
        "Model", list(MODEL_CATALOG.keys()),
        index=list(MODEL_CATALOG.keys()).index(current["model"]),
        label_visibility="collapsed",
    )
    if model_choice != current["model"]:
        current["model"] = model_choice

    st.markdown('<div class="orbit-date-label">System prompt</div>', unsafe_allow_html=True)
    sys_prompt = st.text_area(
        "System prompt",
        value=current["system_prompt"],
        placeholder='e.g. "You are a professional software engineer."',
        height=90,
        label_visibility="collapsed",
    )
    current["system_prompt"] = sys_prompt

    with st.expander("📋 Prompt templates", expanded=False):
        all_templates = {**BUILTIN_TEMPLATES, **st.session_state.custom_templates}
        for name, text in all_templates.items():
            icon = TEMPLATE_ICONS.get(name, "⭐")
            if st.button(f"{icon} {name}", key=f"tmpl_{name}", use_container_width=True):
                st.session_state.user_input = text
                st.rerun()

        st.markdown("**Save a new template**")
        new_tmpl_name = st.text_input("Template name", key="new_tmpl_name", label_visibility="collapsed",
                                       placeholder="Template name")
        new_tmpl_text = st.text_area("Template text", key="new_tmpl_text", label_visibility="collapsed",
                                      placeholder="Template prompt text…", height=70)
        if st.button("💾 Save template", use_container_width=True):
            if new_tmpl_name.strip() and new_tmpl_text.strip():
                st.session_state.custom_templates[new_tmpl_name.strip()] = new_tmpl_text
                st.success(f"Saved '{new_tmpl_name}'")
                st.rerun()
            else:
                st.warning("Give the template a name and some text first.")

    st.divider()

    total_tokens = sum(m.get("tokens") or 0 for m in current["messages"] if m["role"] == "assistant")
    col_a, col_b = st.columns(2)
    col_a.metric("Tokens used", total_tokens)
    col_b.metric("Messages", len(current["messages"]))

    st.session_state.dark_mode = st.toggle("🌙 Dark mode", value=st.session_state.dark_mode)

    if current["messages"]:
        transcript_lines = [f"# {current['title']}\n"]
        for m in current["messages"]:
            who = "**You**" if m["role"] == "user" else f"**Orbit ({current['model']})**"
            transcript_lines.append(f"{who}:\n\n{m['content']}\n")
        transcript = "\n---\n\n".join(transcript_lines)
        st.download_button(
            "⬇️ Export chat", data=transcript, file_name=f"orbit_chat_{current['title'][:20]}.md",
            mime="text/markdown", use_container_width=True,
        )

    if st.button("🗑️ Clear this chat", use_container_width=True):
        current["messages"] = []
        st.rerun()

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------

st.markdown(
    f"""
    <div style="display:flex; justify-content:space-between; align-items:center; padding: 4px 0 14px 0;">
        <div style="font-weight:600; font-size:1.1rem;">{current['title']}</div>
        <div style="color:var(--orbit-muted); font-size:0.85rem;">🧠 {current['model']}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not current["messages"]:
    st.markdown(
        """
        <div class="orbit-hero">
            <div class="orbit-hero-orb"></div>
            <div class="orbit-hero-title">Hello there</div>
            <div class="orbit-hero-sub">How can Orbit assist you today?</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    for m in current["messages"]:
        avatar = "🧑" if m["role"] == "user" else "🪐"
        with st.chat_message(m["role"], avatar=avatar):
            st.markdown(m["content"])
            if m["role"] == "assistant" and (m.get("tokens") or m.get("elapsed")):
                meta_bits = []
                if m.get("elapsed") is not None:
                    meta_bits.append(f"⏱ {m['elapsed']:.2f}s")
                if m.get("tokens") is not None:
                    meta_bits.append(f"🔢 {m['tokens']} tokens")
                st.markdown(f'<div class="orbit-meta">{" · ".join(meta_bits)}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Composer
# ---------------------------------------------------------------------------

st.write("")
input_col, send_col = st.columns([9, 1])

with input_col:
    user_text = st.text_area(
        "Message", key="user_input", placeholder="Ask me anything…", height=68, label_visibility="collapsed"
    )

with send_col:
    st.write("")
    send_clicked = st.button("➤", use_container_width=True)

if send_clicked:
    text = st.session_state.user_input.strip()
    if not text:
        st.warning("Please enter a message before sending.")
    else:
        if current["title"] == "New chat":
            current["title"] = text[:40] + ("…" if len(text) > 40 else "")

        current["messages"].append({"role": "user", "content": text})

        history = [{"role": m["role"], "content": m["content"]} for m in current["messages"]]

        with st.spinner("Orbit is thinking…"):
            result = get_completion(current["model"], history, current["system_prompt"], api_keys)

        if result["ok"]:
            current["messages"].append({
                "role": "assistant",
                "content": result["content"],
                "tokens": result["tokens"],
                "elapsed": result["elapsed"],
            })
        else:
            current["messages"].append({
                "role": "assistant",
                "content": f"⚠️ **Error:** {result['error']}",
                "tokens": None,
                "elapsed": result.get("elapsed"),
            })

        st.session_state["_clear_input"] = True
        st.rerun()
