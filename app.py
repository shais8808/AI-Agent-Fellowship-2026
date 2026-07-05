"""
Orbit — AI Workspace
A unified chat interface for Gemini, DeepSeek, and Llama.
Run with: streamlit run app.py
"""

import os
import uuid
from datetime import datetime
from typing import Any

import streamlit as st
from dotenv import load_dotenv

from providers import MODEL_CATALOG, get_completion
from templates import BUILTIN_TEMPLATES, TEMPLATE_ICONS
from style import get_css

load_dotenv()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PAGE_TITLE = "Orbit — AI Workspace"
DEFAULT_TITLE = "New chat"
CLEAR_INPUT_FLAG = "_clear_input"

ICON_USER = "🧑"
ICON_ASSISTANT = "🪐"
ICON_ACTIVE_CHAT = "🟣 "
ICON_INACTIVE_CHAT = "💬 "

Session = dict[str, Any]

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

def create_session(title: str = DEFAULT_TITLE) -> str:
    """Create a new chat session and make it the active one. Returns its id."""
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


def init_state() -> None:
    """Set up all session_state defaults. Safe to call on every rerun."""
    if "sessions" not in st.session_state:
        st.session_state.sessions = {}
        create_session()

    st.session_state.setdefault("dark_mode", False)
    st.session_state.setdefault("custom_templates", {})
    st.session_state.setdefault("user_input", "")
    st.session_state.setdefault("session_search", "")

    # Clear the composer *before* the text_area widget is instantiated this run,
    # since Streamlit forbids mutating a widget's session_state key after creation.
    if st.session_state.get(CLEAR_INPUT_FLAG):
        st.session_state.user_input = ""
        st.session_state[CLEAR_INPUT_FLAG] = False


def get_current_session() -> Session:
    return st.session_state.sessions[st.session_state.current_id]


def get_api_keys() -> dict[str, str]:
    return {
        "gemini": os.getenv("GEMINI_API_KEY", ""),
        "github": os.getenv("GITHUB_TOKEN", ""),
    }


# ---------------------------------------------------------------------------
# Sidebar sections
# ---------------------------------------------------------------------------

def _render_new_chat_button() -> None:
    st.markdown('<div class="orbit-primary-btn">', unsafe_allow_html=True)
    if st.button("＋ New chat", use_container_width=True):
        create_session()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def _render_chat_list() -> None:
    st.session_state.session_search = st.text_input(
        "Search", value=st.session_state.session_search,
        placeholder="🔍 Search chats", label_visibility="collapsed",
    )

    st.markdown('<div class="orbit-date-label">Chats</div>', unsafe_allow_html=True)

    sorted_sessions = sorted(
        st.session_state.sessions.items(), key=lambda kv: kv[1]["created"], reverse=True
    )
    query = st.session_state.session_search.lower().strip()

    for sid, sess in sorted_sessions:
        if query and query not in sess["title"].lower():
            continue
        label = sess["title"][:32] + ("…" if len(sess["title"]) > 32 else "")
        prefix = ICON_ACTIVE_CHAT if sid == st.session_state.current_id else ICON_INACTIVE_CHAT
        if st.button(prefix + label, key=f"sess_{sid}", use_container_width=True):
            st.session_state.current_id = sid
            st.rerun()


def _render_model_picker(current: Session) -> None:
    st.markdown('<div class="orbit-date-label">Model</div>', unsafe_allow_html=True)
    models = list(MODEL_CATALOG.keys())
    model_choice = st.selectbox(
        "Model", models, index=models.index(current["model"]), label_visibility="collapsed",
    )
    current["model"] = model_choice


def _render_system_prompt(current: Session) -> None:
    st.markdown('<div class="orbit-date-label">System prompt</div>', unsafe_allow_html=True)
    current["system_prompt"] = st.text_area(
        "System prompt",
        value=current["system_prompt"],
        placeholder='e.g. "You are a professional software engineer."',
        height=90,
        label_visibility="collapsed",
    )


def _render_templates() -> None:
    with st.expander("📋 Prompt templates", expanded=False):
        all_templates = {**BUILTIN_TEMPLATES, **st.session_state.custom_templates}
        for name, text in all_templates.items():
            icon = TEMPLATE_ICONS.get(name, "⭐")
            if st.button(f"{icon} {name}", key=f"tmpl_{name}", use_container_width=True):
                st.session_state.user_input = text
                st.rerun()

        st.markdown("**Save a new template**")
        new_name = st.text_input(
            "Template name", key="new_tmpl_name", label_visibility="collapsed",
            placeholder="Template name",
        )
        new_text = st.text_area(
            "Template text", key="new_tmpl_text", label_visibility="collapsed",
            placeholder="Template prompt text…", height=70,
        )
        if st.button("💾 Save template", use_container_width=True):
            if new_name.strip() and new_text.strip():
                st.session_state.custom_templates[new_name.strip()] = new_text
                st.success(f"Saved '{new_name}'")
                st.rerun()
            else:
                st.warning("Give the template a name and some text first.")


def _render_stats_and_actions(current: Session) -> None:
    total_tokens = sum(m.get("tokens") or 0 for m in current["messages"] if m["role"] == "assistant")
    col_a, col_b = st.columns(2)
    col_a.metric("Tokens used", total_tokens)
    col_b.metric("Messages", len(current["messages"]))

    st.session_state.dark_mode = st.toggle("🌙 Dark mode", value=st.session_state.dark_mode)

    if current["messages"]:
        st.download_button(
            "⬇️ Export chat",
            data=build_transcript(current),
            file_name=f"orbit_chat_{current['title'][:20]}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    if st.button("🗑️ Clear this chat", use_container_width=True):
        current["messages"] = []
        st.rerun()


def build_transcript(session: Session) -> str:
    """Render a session's messages as a markdown transcript for export."""
    lines = [f"# {session['title']}\n"]
    for m in session["messages"]:
        who = "**You**" if m["role"] == "user" else f"**Orbit ({session['model']})**"
        lines.append(f"{who}:\n\n{m['content']}\n")
    return "\n---\n\n".join(lines)


def render_sidebar(current: Session) -> None:
    with st.sidebar:
        st.markdown('<div class="orbit-brand">🪐 Orbit</div>', unsafe_allow_html=True)
        _render_new_chat_button()
        _render_chat_list()
        st.divider()
        _render_model_picker(current)
        _render_system_prompt(current)
        _render_templates()
        st.divider()
        _render_stats_and_actions(current)


# ---------------------------------------------------------------------------
# Main chat area
# ---------------------------------------------------------------------------

def render_header(current: Session) -> None:
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center; padding: 4px 0 14px 0;">
            <div style="font-weight:600; font-size:1.1rem;">{current['title']}</div>
            <div style="color:var(--orbit-muted); font-size:0.85rem;">🧠 {current['model']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
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


def render_message_meta(message: dict) -> None:
    bits = []
    if message.get("elapsed") is not None:
        bits.append(f"⏱ {message['elapsed']:.2f}s")
    if message.get("tokens") is not None:
        bits.append(f"🔢 {message['tokens']} tokens")
    if bits:
        st.markdown(f'<div class="orbit-meta">{" · ".join(bits)}</div>', unsafe_allow_html=True)


def render_messages(current: Session) -> None:
    if not current["messages"]:
        render_hero()
        return

    for m in current["messages"]:
        avatar = ICON_USER if m["role"] == "user" else ICON_ASSISTANT
        with st.chat_message(m["role"], avatar=avatar):
            st.markdown(m["content"])
            if m["role"] == "assistant":
                render_message_meta(m)


# ---------------------------------------------------------------------------
# Composer
# ---------------------------------------------------------------------------

def render_composer() -> bool:
    """Draw the message box + send button. Returns True if send was clicked."""
    st.write("")
    input_col, send_col = st.columns([9, 1])

    with input_col:
        st.text_area(
            "Message", key="user_input", placeholder="Ask me anything…",
            height=68, label_visibility="collapsed",
        )

    with send_col:
        st.write("")
        return st.button("➤", use_container_width=True)


def handle_send(current: Session, api_keys: dict[str, str]) -> None:
    """Process the composer text: append user message, call the model, append reply."""
    text = st.session_state.user_input.strip()
    if not text:
        st.warning("Please enter a message before sending.")
        return

    if current["title"] == DEFAULT_TITLE:
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

    st.session_state[CLEAR_INPUT_FLAG] = True
    st.rerun()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    st.set_page_config(
        page_title=PAGE_TITLE, page_icon="🪐", layout="wide", initial_sidebar_state="expanded"
    )

    init_state()
    st.markdown(get_css(st.session_state.dark_mode), unsafe_allow_html=True)

    current = get_current_session()
    api_keys = get_api_keys()

    render_sidebar(current)
    render_header(current)
    render_messages(current)

    if render_composer():
        handle_send(current, api_keys)


if __name__ == "__main__":
    main()