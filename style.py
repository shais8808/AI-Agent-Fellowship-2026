"""
style.py
Injects Orbit's visual theme (purple accent, dark/light variants) into Streamlit.
"""

def get_css(dark: bool) -> str:
    if dark:
        bg = "#131117"
        bg_secondary = "#1a1720"
        sidebar_bg = "#0f0d13"
        card_bg = "#1e1b26"
        text = "#f1eef7"
        text_muted = "#a29bb5"
        border = "#2c2836"
        input_bg = "#211d2b"
    else:
        bg = "#faf9fc"
        bg_secondary = "#ffffff"
        sidebar_bg = "#ffffff"
        card_bg = "#f4f2fa"
        text = "#211d2b"
        text_muted = "#6b6478"
        border = "#e6e2ef"
        input_bg = "#ffffff"

    accent = "#8b5cf6"
    accent_light = "#a78bfa"
    accent_dark = "#7c3aed"

    return f"""
<style>
    :root {{
        --orbit-bg: {bg};
        --orbit-bg-secondary: {bg_secondary};
        --orbit-sidebar: {sidebar_bg};
        --orbit-card: {card_bg};
        --orbit-text: {text};
        --orbit-muted: {text_muted};
        --orbit-border: {border};
        --orbit-input: {input_bg};
        --orbit-accent: {accent};
        --orbit-accent-light: {accent_light};
        --orbit-accent-dark: {accent_dark};
    }}

    .stApp {{
        background: var(--orbit-bg);
        color: var(--orbit-text);
    }}

    [data-testid="stSidebar"] {{
        background: var(--orbit-sidebar);
        border-right: 1px solid var(--orbit-border);
    }}

    [data-testid="stSidebar"] * {{
        color: var(--orbit-text);
    }}

    .orbit-brand {{
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.4rem;
        font-weight: 700;
        padding: 4px 0 18px 0;
        background: linear-gradient(135deg, {accent_light}, {accent_dark});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    .orbit-session-item {{
        padding: 8px 10px;
        border-radius: 8px;
        font-size: 0.85rem;
        color: var(--orbit-muted);
        cursor: pointer;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .orbit-session-item.active {{
        background: var(--orbit-card);
        color: var(--orbit-text);
        font-weight: 600;
    }}

    .orbit-date-label {{
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--orbit-muted);
        margin: 14px 0 4px 4px;
    }}

    .orbit-hero {{
        text-align: center;
        padding: 60px 20px 20px 20px;
    }}

    .orbit-hero-orb {{
        width: 90px;
        height: 90px;
        margin: 0 auto 18px auto;
        border-radius: 50%;
        background: radial-gradient(circle at 35% 30%, {accent_light}, {accent_dark} 70%);
        box-shadow: 0 0 50px {accent}66;
    }}

    .orbit-hero-title {{
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--orbit-accent-light);
    }}

    .orbit-hero-sub {{
        font-size: 1.4rem;
        font-weight: 600;
        color: var(--orbit-text);
        margin-top: 2px;
    }}

    div[data-testid="stChatMessage"] {{
        background: var(--orbit-card);
        border: 1px solid var(--orbit-border);
        border-radius: 14px;
        padding: 4px 6px;
    }}

    .orbit-meta {{
        font-size: 0.72rem;
        color: var(--orbit-muted);
        margin-top: 4px;
    }}

    .stButton > button {{
        border-radius: 10px;
        border: 1px solid var(--orbit-border);
        background: var(--orbit-card);
        color: var(--orbit-text);
    }}

    .stButton > button:hover {{
        border-color: var(--orbit-accent);
        color: var(--orbit-accent-light);
    }}

    .orbit-primary-btn button {{
        background: linear-gradient(135deg, {accent}, {accent_dark});
        color: white !important;
        border: none;
        font-weight: 600;
    }}

    .orbit-primary-btn button:hover {{
        opacity: 0.9;
        color: white !important;
    }}

    textarea, .stTextInput input {{
        background: var(--orbit-input) !important;
        color: var(--orbit-text) !important;
        border-radius: 12px !important;
        border: 1px solid var(--orbit-border) !important;
    }}

    [data-testid="stMetricValue"] {{
        color: var(--orbit-accent-light);
    }}

    hr {{
        border-color: var(--orbit-border);
    }}
</style>
"""
