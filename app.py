import time
import streamlit as st
from google import genai
from google.genai import types

# PDF Generator Import
try:
    from report import create_pdf
except Exception:
    create_pdf = None


# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="HealthMate AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# SESSION STATE INITIALIZATION
# =========================================================
session_defaults = {
    "page": "Home",
    "chat_history": [],
    "bmi": None,
    "water": None,
    "sleep": None,
    "accent": "Cyan",
}

for key, default_value in session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default_value


# =========================================================
# GEMINI CLIENT (CACHED)
# =========================================================
@st.cache_resource
def get_client():
    try:
        key = st.secrets.get("GEMINI_API_KEY")
        if key:
            return genai.Client(api_key=key)
    except Exception:
        pass
    return None


client = get_client()


def ask_ai(prompt, model="gemini-3.6-flash"):
    """Lightweight, reusable Gemini AI text prompt function."""
    if client is None:
        st.error(
            "Gemini API is not configured. Please add GEMINI_API_KEY "
            "to .streamlit/secrets.toml."
        )
        return None

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        return response.text
    except Exception as exc:
        st.error(f"Gemini request failed: {exc}")
        return None


# =========================================================
# THEME CONFIGURATION (COLOR-ENRICHED PALETTE)
# =========================================================
accent_colors = {
    "Cyan": "#00f2fe",
    "Blue": "#38bdf8",
    "Purple": "#c084fc",
    "Green": "#34d399",
}

accent = accent_colors.get(st.session_state.accent, "#00f2fe")

# Rich Dual-Tone Sapphire/Amethyst/Teal Defaults
background = "#131b38"
sidebar_bg = "#111827"
surface = "rgba(30, 41, 78, 0.72)"
surface2 = "rgba(45, 62, 115, 0.75)"
text = "#ffffff"
muted = "#cbd5e1"
border = "rgba(255, 255, 255, 0.18)"
card_shadow = "0 14px 40px 0 rgba(10, 16, 40, 0.45)"
glass_blur = "blur(20px)"


# =========================================================
# STYLESHEET WITH COLORFUL BACKGROUND ANIMATION
# =========================================================
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

:root {{
    --bg: {background};
    --surface: {surface};
    --surface2: {surface2};
    --text: {text};
    --muted: {muted};
    --border: {border};
    --accent: {accent};
    --shadow: {card_shadow};
    --blur: {glass_blur};
}}

/* Dynamic Aurora Background Animation */
.stApp {{
    background: linear-gradient(135deg, #131b38 0%, #1e1b4b 28%, #0f2c59 55%, #1e1b4b 78%, #142147 100%);
    background-size: 300% 300%;
    animation: auroraWave 14s ease-in-out infinite alternate;
    color: var(--text);
    font-family: 'Plus Jakarta Sans', sans-serif;
}}

@keyframes auroraWave {{
    0% {{ background-position: 0% 20%; }}
    50% {{ background-position: 100% 80%; }}
    100% {{ background-position: 0% 20%; }}
}}

/* Decorative Floating Glowing Mesh Orbs */
.stApp::before {{
    content: '';
    position: fixed;
    top: -150px;
    left: -150px;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(0, 242, 254, 0.35) 0%, rgba(56, 189, 248, 0.15) 45%, transparent 70%);
    filter: blur(50px);
    z-index: 0;
    pointer-events: none;
    animation: floatOrbOne 18s ease-in-out infinite alternate;
}}

.stApp::after {{
    content: '';
    position: fixed;
    bottom: -150px;
    right: -150px;
    width: 650px;
    height: 650px;
    background: radial-gradient(circle, rgba(192, 132, 252, 0.32) 0%, rgba(236, 72, 153, 0.18) 50%, transparent 70%);
    filter: blur(55px);
    z-index: 0;
    pointer-events: none;
    animation: floatOrbTwo 16s ease-in-out infinite alternate;
}}

@keyframes floatOrbOne {{
    0% {{ transform: translate(0, 0) scale(1); }}
    50% {{ transform: translate(120px, 90px) scale(1.15); }}
    100% {{ transform: translate(40px, 140px) scale(0.95); }}
}}

@keyframes floatOrbTwo {{
    0% {{ transform: translate(0, 0) scale(1); }}
    50% {{ transform: translate(-100px, -110px) scale(1.12); }}
    100% {{ transform: translate(-30px, -160px) scale(0.92); }}
}}

/* Modern Sidebar */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, rgba(17, 24, 47, 0.92) 0%, rgba(26, 36, 68, 0.94) 100%) !important;
    backdrop-filter: var(--blur);
    -webkit-backdrop-filter: var(--blur);
    border-right: 1px solid rgba(255, 255, 255, 0.14);
    box-shadow: 6px 0 30px rgba(0, 0, 0, 0.25);
}}

[data-testid="stSidebar"] div[data-testid="stRadio"] label {{
    border-radius: 14px;
    padding: 11px 16px;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    border: 1px solid transparent;
    font-size: 14.5px;
    font-weight: 500;
    color: #e2e8f0;
    margin-bottom: 3px;
}}

[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {{
    background: linear-gradient(90deg, rgba(0, 242, 254, 0.2) 0%, rgba(192, 132, 252, 0.15) 100%);
    border-color: rgba(0, 242, 254, 0.45);
    color: #ffffff;
    transform: translateX(6px);
}}

h1, h2, h3, h4, h5, h6 {{
    font-family: 'Outfit', sans-serif !important;
    color: var(--text) !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
}}

.hero {{
    padding: 38px 44px;
    border: 1px solid rgba(255, 255, 255, 0.22);
    border-radius: 26px;
    background: linear-gradient(135deg, rgba(37, 51, 98, 0.88) 0%, rgba(28, 40, 77, 0.85) 50%, rgba(46, 37, 84, 0.82) 100%);
    backdrop-filter: var(--blur);
    -webkit-backdrop-filter: var(--blur);
    box-shadow: 0 16px 45px rgba(0, 0, 0, 0.35);
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}}

.hero::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 6px;
    height: 100%;
    background: linear-gradient(180deg, #00f2fe 0%, #c084fc 50%, #34d399
