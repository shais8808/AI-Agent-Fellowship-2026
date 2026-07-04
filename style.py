"""
style.py
Injects Orbit's visual theme into Streamlit.

Design language: "mission control for AI models." Orbit sits between three
models the way a satellite sits between bodies it's tracking — the palette
leans into deep space (ink/indigo) with a violet "signal" accent and a warm
amber "beacon" accent used sparingly for the primary action (sending a
message = launching it). Every widget Streamlit renders — including the
ones that live outside the normal DOM tree, like selectbox dropdowns — is
explicitly themed so dark mode never produces invisible or low-contrast text.
"""


def get_css(dark: bool) -> str:
    if dark:
        bg = "#0d0b14"
        bg_secondary = "#15121f"
        sidebar_bg = "#0a0810"
        card_bg = "#1c1828"
        card_hover = "#241f34"
        text = "#f6f4fb"
        text_muted = "#b6adc9"
        text_faint = "#847a99"
        border = "#2c2740"
        border_soft = "#221e33"
        input_bg = "#171320"
        shadow = "0 12px 32px rgba(0, 0, 0, 0.45)"
    else:
        bg = "#faf9fd"
        bg_secondary = "#ffffff"
        sidebar_bg = "#ffffff"
        card_bg = "#f5f2fb"
        card_hover = "#eee7fb"
        text = "#1c1830"
        text_muted = "#655d78"
        text_faint = "#8a8299"
        border = "#e7e1f3"
        border_soft = "#efeaf9"
        input_bg = "#ffffff"
        shadow = "0 10px 28px rgba(90, 70, 140, 0.10)"

    accent = "#8b5cf6"
    accent_light = "#b39dfb" if dark else "#9061f9"
    accent_dark = "#6d28d9" if dark else "#5b21b6"
    beacon = "#f2a93b"        # warm secondary accent — the "star" Orbit's models circle
    beacon_light = "#ffcf7d"
    danger = "#f87171" if dark else "#dc2626"
    success = "#4ade80" if dark else "#16a34a"

    return f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {{
        --orbit-bg: {bg};
        --orbit-bg-secondary: {bg_secondary};
        --orbit-sidebar: {sidebar_bg};
        --orbit-card: {card_bg};
        --orbit-card-hover: {card_hover};
        --orbit-text: {text};
        --orbit-muted: {text_muted};
        --orbit-faint: {text_faint};
        --orbit-border: {border};
        --orbit-border-soft: {border_soft};
        --orbit-input: {input_bg};
        --orbit-accent: {accent};
        --orbit-accent-light: {accent_light};
        --orbit-accent-dark: {accent_dark};
        --orbit-beacon: {beacon};
        --orbit-beacon-light: {beacon_light};
        --orbit-danger: {danger};
        --orbit-success: {success};
        --orbit-shadow: {shadow};
        --orbit-font-display: 'Space Grotesk', 'Inter', sans-serif;
        --orbit-font-body: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        --orbit-font-mono: 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace;
    }}

    /* ------------------------------------------------------------------ */
    /* Base                                                                */
    /* ------------------------------------------------------------------ */

    .stApp {{
        background: var(--orbit-bg);
        color: var(--orbit-text);
        font-family: var(--orbit-font-body);
    }}

    body, p, span, div, li, label {{
        color: var(--orbit-text);
    }}

    h1, h2, h3, h4, h5, h6 {{
        font-family: var(--orbit-font-display) !important;
        color: var(--orbit-text) !important;
        letter-spacing: -0.01em;
    }}

    a {{ color: var(--orbit-accent-light); }}
    a:hover {{ color: var(--orbit-beacon); }}

    ::selection {{ background: var(--orbit-accent); color: #ffffff; }}

    /* Scrollbars */
    ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{
        background: var(--orbit-border);
        border-radius: 10px;
        border: 2px solid var(--orbit-bg);
    }}
    ::-webkit-scrollbar-thumb:hover {{ background: var(--orbit-accent-dark); }}

    /* Visible keyboard focus everywhere */
    button:focus-visible, input:focus-visible, textarea:focus-visible,
    [data-baseweb="select"]:focus-within, a:focus-visible {{
        outline: 2px solid var(--orbit-accent-light) !important;
        outline-offset: 2px;
    }}

    #MainMenu, footer, header[data-testid="stHeader"] {{ background: transparent; }}

    .block-container {{ padding-top: 1.6rem; }}

    /* ------------------------------------------------------------------ */
    /* Sidebar shell                                                       */
    /* ------------------------------------------------------------------ */

    [data-testid="stSidebar"] {{
        background: var(--orbit-sidebar);
        border-right: 1px solid var(--orbit-border);
    }}

    [data-testid="stSidebar"] * {{
        color: var(--orbit-text);
    }}

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
        color: var(--orbit-text);
    }}

    .orbit-brand {{
        display: flex;
        align-items: center;
        gap: 10px;
        font-family: var(--orbit-font-display);
        font-size: 1.5rem;
        font-weight: 700;
        padding: 2px 0 20px 0;
        background: linear-gradient(135deg, {accent_light}, {beacon});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    /* ------------------------------------------------------------------ */
    /* Chat / session list                                                 */
    /* ------------------------------------------------------------------ */

    .orbit-date-label {{
        font-family: var(--orbit-font-mono);
        font-size: 0.68rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--orbit-faint) !important;
        margin: 18px 0 6px 4px;
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

    /* Session buttons in the sidebar list get a quiet left rail; the
       active one lights up violet so it reads as "in orbit" right now. */
    [data-testid="stSidebar"] .stButton > button {{
        text-align: left;
        justify-content: flex-start;
        border-left: 2px solid transparent;
        font-weight: 400;
    }}

    /* ------------------------------------------------------------------ */
    /* Hero                                                                 */
    /* ------------------------------------------------------------------ */

    .orbit-hero {{
        text-align: center;
        padding: 64px 20px 24px 20px;
    }}

    .orbit-hero-orb {{
        position: relative;
        width: 84px;
        height: 84px;
        margin: 0 auto 26px auto;
        border-radius: 50%;
        background: radial-gradient(circle at 35% 30%, {accent_light}, {accent_dark} 70%);
        box-shadow: 0 0 60px {accent}55;
    }}

    .orbit-hero-orb::before {{
        content: "";
        position: absolute;
        inset: -18px;
        border-radius: 50%;
        border: 1.5px solid {accent}55;
    }}

    .orbit-hero-orb::after {{
        content: "";
        position: absolute;
        top: 50%;
        left: 50%;
        width: 8px;
        height: 8px;
        margin: -4px 0 0 -4px;
        border-radius: 50%;
        background: {beacon};
        box-shadow: 0 0 12px {beacon};
        animation: orbit-spin 6s linear infinite;
        transform-origin: 4px 60px;
    }}

    @media (prefers-reduced-motion: no-preference) {{
        @keyframes orbit-spin {{
            from {{ transform: rotate(0deg) translateY(-60px) rotate(0deg); }}
            to   {{ transform: rotate(360deg) translateY(-60px) rotate(-360deg); }}
        }}
    }}
    @media (prefers-reduced-motion: reduce) {{
        .orbit-hero-orb::after {{ animation: none; top: -14px; left: 50%; }}
    }}

    .orbit-hero-title {{
        font-family: var(--orbit-font-display);
        font-size: 1.9rem;
        font-weight: 700;
        color: var(--orbit-accent-light);
    }}

    .orbit-hero-sub {{
        font-size: 1.25rem;
        font-weight: 500;
        color: var(--orbit-muted);
        margin-top: 4px;
    }}

    /* ------------------------------------------------------------------ */
    /* Chat messages                                                       */
    /* ------------------------------------------------------------------ */

    div[data-testid="stChatMessage"] {{
        background: var(--orbit-card);
        border: 1px solid var(--orbit-border);
        border-radius: 16px;
        padding: 6px 10px;
        margin-bottom: 4px;
        box-shadow: var(--orbit-shadow);
    }}

    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {{
        color: var(--orbit-text);
        line-height: 1.55;
    }}

    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] code {{
        font-family: var(--orbit-font-mono);
        background: var(--orbit-input);
        border: 1px solid var(--orbit-border);
        color: var(--orbit-beacon-light);
        padding: 1px 6px;
        border-radius: 5px;
        font-size: 0.85em;
    }}

    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] pre {{
        background: var(--orbit-input) !important;
        border: 1px solid var(--orbit-border);
        border-radius: 10px;
    }}

    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] pre code {{
        background: transparent;
        border: none;
        color: var(--orbit-text);
    }}

    /* User bubble gets a faint violet wash to separate it from Orbit's replies */
    div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
        background: linear-gradient(180deg, {accent}14, var(--orbit-card));
        border-color: {accent}44;
    }}

    .orbit-meta {{
        font-family: var(--orbit-font-mono);
        font-size: 0.7rem;
        color: var(--orbit-faint);
        margin: 2px 4px 4px 4px;
    }}

    /* ------------------------------------------------------------------ */
    /* Buttons                                                              */
    /* ------------------------------------------------------------------ */

    .stButton > button {{
        border-radius: 10px;
        border: 1px solid var(--orbit-border);
        background: var(--orbit-card);
        color: var(--orbit-text) !important;
        font-family: var(--orbit-font-body);
        transition: border-color 0.15s ease, color 0.15s ease, background 0.15s ease;
    }}

    .stButton > button p {{ color: var(--orbit-text) !important; }}

    .stButton > button:hover {{
        border-color: var(--orbit-accent);
        color: var(--orbit-accent-light) !important;
        background: var(--orbit-card-hover);
    }}

    .stButton > button:hover p {{ color: var(--orbit-accent-light) !important; }}

    .orbit-primary-btn button {{
        background: linear-gradient(135deg, {accent}, {accent_dark});
        color: #ffffff !important;
        border: none;
        font-weight: 600;
    }}

    .orbit-primary-btn button p {{ color: #ffffff !important; }}

    .orbit-primary-btn button:hover {{
        opacity: 0.92;
        color: #ffffff !important;
    }}

    /* Send button — the "launch" action, gets the beacon accent */
    div[data-testid="column"]:has(button[kind="secondary"]) button[aria-label]:not([aria-label]) {{ }}
    .stApp [data-testid="stHorizontalBlock"] div[data-testid="column"]:last-child .stButton > button {{
        background: linear-gradient(135deg, {beacon}, {beacon_light});
        border: none;
        color: #1c1830 !important;
        font-weight: 700;
        font-size: 1.1rem;
        height: 100%;
        box-shadow: 0 4px 16px {beacon}55;
    }}
    .stApp [data-testid="stHorizontalBlock"] div[data-testid="column"]:last-child .stButton > button p {{
        color: #1c1830 !important;
    }}
    .stApp [data-testid="stHorizontalBlock"] div[data-testid="column"]:last-child .stButton > button:hover {{
        opacity: 0.9;
        transform: translateY(-1px);
    }}

    [data-testid="stDownloadButton"] button {{
        background: var(--orbit-card);
        color: var(--orbit-text) !important;
        border: 1px solid var(--orbit-border);
    }}
    [data-testid="stDownloadButton"] button p {{ color: var(--orbit-text) !important; }}
    [data-testid="stDownloadButton"] button:hover {{
        border-color: var(--orbit-accent);
        color: var(--orbit-accent-light) !important;
    }}
    [data-testid="stDownloadButton"] button:hover p {{ color: var(--orbit-accent-light) !important; }}

    /* ------------------------------------------------------------------ */
    /* Text inputs / text areas                                            */
    /* ------------------------------------------------------------------ */

    textarea, .stTextInput input, [data-testid="stTextAreaRootElement"] {{
        background: var(--orbit-input) !important;
        color: var(--orbit-text) !important;
        border-radius: 12px !important;
        border: 1px solid var(--orbit-border) !important;
        font-family: var(--orbit-font-body) !important;
    }}

    textarea::placeholder, .stTextInput input::placeholder {{
        color: var(--orbit-faint) !important;
        opacity: 1;
    }}

    textarea:focus, .stTextInput input:focus {{
        border-color: var(--orbit-accent) !important;
        box-shadow: 0 0 0 3px {accent}2a !important;
    }}

    /* Composer text area gets slightly larger, rounder treatment */
    .stApp [data-testid="stHorizontalBlock"] [data-testid="stTextArea"] textarea {{
        border-radius: 16px !important;
        padding: 14px 16px !important;
    }}

    /* ------------------------------------------------------------------ */
    /* Labels (widget labels use their own testid, independent of color:)  */
    /* ------------------------------------------------------------------ */

    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label {{
        color: var(--orbit-muted) !important;
        font-size: 0.85rem;
    }}

    /* ------------------------------------------------------------------ */
    /* Selectbox — including the dropdown, which renders in a portal       */
    /* ------------------------------------------------------------------ */

    [data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        background: var(--orbit-input) !important;
        color: var(--orbit-text) !important;
        border-color: var(--orbit-border) !important;
        border-radius: 12px !important;
    }}

    [data-testid="stSelectbox"] div[data-baseweb="select"] * {{
        color: var(--orbit-text) !important;
    }}

    /* The dropdown menu is portaled to <body>, outside the sidebar, so it
       needs its own explicit theme or it silently inherits Streamlit's
       default light popover — the classic "black text on black" bug. */
    div[data-baseweb="popover"] ul[role="listbox"],
    div[data-baseweb="popover"] div[data-baseweb="menu"] {{
        background: var(--orbit-card) !important;
        border: 1px solid var(--orbit-border) !important;
        border-radius: 12px !important;
        box-shadow: var(--orbit-shadow) !important;
    }}

    div[data-baseweb="popover"] li[role="option"] {{
        color: var(--orbit-text) !important;
        font-family: var(--orbit-font-body);
    }}

    div[data-baseweb="popover"] li[role="option"]:hover,
    div[data-baseweb="popover"] li[aria-selected="true"] {{
        background: var(--orbit-card-hover) !important;
        color: var(--orbit-accent-light) !important;
    }}

    /* ------------------------------------------------------------------ */
    /* Expander                                                             */
    /* ------------------------------------------------------------------ */

    [data-testid="stExpander"] {{
        background: var(--orbit-card);
        border: 1px solid var(--orbit-border) !important;
        border-radius: 12px !important;
        overflow: hidden;
    }}

    [data-testid="stExpander"] summary {{
        color: var(--orbit-text) !important;
        font-weight: 500;
    }}

    [data-testid="stExpander"] summary:hover {{
        color: var(--orbit-accent-light) !important;
    }}

    [data-testid="stExpander"] svg {{
        fill: var(--orbit-muted) !important;
    }}

    [data-testid="stExpanderDetails"] {{
        border-top: 1px solid var(--orbit-border-soft);
    }}

    /* ------------------------------------------------------------------ */
    /* Toggle                                                               */
    /* ------------------------------------------------------------------ */

    [data-testid="stToggle"] label p {{
        color: var(--orbit-text) !important;
    }}

    [data-testid="stToggle"] [role="switch"][aria-checked="true"] {{
        background: var(--orbit-accent) !important;
    }}

    /* ------------------------------------------------------------------ */
    /* Metrics                                                              */
    /* ------------------------------------------------------------------ */

    [data-testid="stMetric"] {{
        background: var(--orbit-card);
        border: 1px solid var(--orbit-border);
        border-radius: 12px;
        padding: 10px 14px;
    }}

    [data-testid="stMetricLabel"] p {{
        color: var(--orbit-faint) !important;
        font-family: var(--orbit-font-mono);
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }}

    [data-testid="stMetricValue"] {{
        color: var(--orbit-accent-light) !important;
        font-family: var(--orbit-font-display);
    }}

    /* ------------------------------------------------------------------ */
    /* Alerts (warning / success / error)                                   */
    /* ------------------------------------------------------------------ */

    [data-testid="stAlert"] {{
        border-radius: 12px;
        font-family: var(--orbit-font-body);
    }}

    [data-testid="stAlert"] p {{
        color: inherit !important;
    }}

    /* ------------------------------------------------------------------ */
    /* Spinner                                                              */
    /* ------------------------------------------------------------------ */

    [data-testid="stSpinner"] p {{
        color: var(--orbit-muted) !important;
        font-family: var(--orbit-font-body);
    }}

    /* ------------------------------------------------------------------ */
    /* Misc                                                                 */
    /* ------------------------------------------------------------------ */

    hr {{ border-color: var(--orbit-border); }}

    [data-testid="stCaptionContainer"] {{ color: var(--orbit-faint) !important; }}
</style>
"""
