import json
import os
import re
import time
from pathlib import Path

import streamlit as st
from google import genai
from google.genai import types

# PDF Generator Import
try:
    from report import create_pdf
except Exception:
    create_pdf = None


# =========================================================
# PAGE CONFIGURATION (must be the first Streamlit call)
# =========================================================
st.set_page_config(
    page_title="HealthMate AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# SESSION STATE & SAVED PREFERENCES
# =========================================================
DEFAULT_SETTINGS = {
    "model": "Auto (recommended)",
    "language": "English",
    "detail": "Standard",
    "tone": "Friendly",
    "name": "",
    "theme": "Dark",
    "font_size": "Medium",
    "animations": True,
    "start_page": "Home",
}

# Settings are saved next to app.py (fine for local use; on a shared server
# every visitor would share this one file).
PREFS_FILE = Path(__file__).with_name("healthmate_settings.json")


def load_prefs():
    try:
        data = json.loads(PREFS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_prefs():
    try:
        PREFS_FILE.write_text(
            json.dumps(
                {"accent": st.session_state.accent, "settings": st.session_state.settings},
                indent=2,
            ),
            encoding="utf-8",
        )
        return True
    except Exception:
        return False


def has_api_key():
    try:
        if st.secrets.get("GEMINI_API_KEY"):
            return True
    except Exception:
        pass
    return bool(os.environ.get("GEMINI_API_KEY"))


session_defaults = {
    "page": "Home",
    "chat_history": [],
    "bmi": None,
    "water": None,
    "sleep": None,
    "accent": "Teal",
    "results": {},  # saved AI results so they survive reruns (e.g. after a download click)
    "settings": dict(DEFAULT_SETTINGS),
}

for key, default_value in session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

if "prefs_loaded" not in st.session_state:
    st.session_state.prefs_loaded = True
    saved_prefs = load_prefs()
    if isinstance(saved_prefs.get("settings"), dict):
        st.session_state.settings = {
            **DEFAULT_SETTINGS,
            **{k: v for k, v in saved_prefs["settings"].items() if k in DEFAULT_SETTINGS},
        }
    if isinstance(saved_prefs.get("accent"), str):
        st.session_state.accent = saved_prefs["accent"]

# make sure every settings key exists (older sessions may miss new ones)
st.session_state.settings = {**DEFAULT_SETTINGS, **st.session_state.settings}


# =========================================================
# GEMINI CLIENT & MULTI-MODEL FAILOVER RETRY HANDLER
# =========================================================
# Edit this list if Google renames/retires a model. Order = priority.
MODELS_TO_TRY = ["gemini-3.5-flash-lite", "gemini-3.5-flash"]

RETRYABLE_ERRORS = ["429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE", "500", "INTERNAL", "DEADLINE_EXCEEDED"]
SKIP_MODEL_ERRORS = ["404", "NOT_FOUND"]
FATAL_ERRORS = ["API_KEY_INVALID", "API key not valid", "PERMISSION_DENIED", "UNAUTHENTICATED"]


def get_client():
    """Fetches a client using the API key from Streamlit secrets or environment."""
    key = None
    try:
        key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        key = None
    if not key:
        key = os.environ.get("GEMINI_API_KEY")
    if key:
        try:
            return genai.Client(api_key=key)
        except Exception:
            return None
    return None


LANGUAGE_RULES = {
    "English": "Respond in English.",
    "Hindi": "Respond in Hindi (Devanagari script).",
    "Hinglish": "Respond in Hinglish (Hindi written using English letters).",
}
DETAIL_RULES = {
    "Brief": "Keep the answer short and to the point (under about 150 words).",
    "Standard": "Give a balanced answer with clear sections.",
    "Detailed": "Give a thorough, well-structured answer with explanations.",
}
TONE_RULES = {
    "Friendly": "Use a warm, friendly, easy-to-understand tone.",
    "Professional": "Use a formal, professional tone. Explain medical terms simply.",
    "Simple": "Use very simple words suitable for a school student.",
}
AUTO_MODEL = "Auto (recommended)"


def apply_style(contents):
    """Adds the user's chosen language, detail level and tone to the request."""
    cfg = st.session_state.settings
    style = (
        "\n\nResponse style rules: "
        f"{LANGUAGE_RULES.get(cfg.get('language'), LANGUAGE_RULES['English'])} "
        f"{DETAIL_RULES.get(cfg.get('detail'), DETAIL_RULES['Standard'])} "
        f"{TONE_RULES.get(cfg.get('tone'), TONE_RULES['Friendly'])}"
    )
    if isinstance(contents, str):
        return contents + style
    if isinstance(contents, list):
        return list(contents) + [style]
    return contents


def model_order():
    """Preferred model first (if chosen), then the normal fallback list."""
    preferred = st.session_state.settings.get("model", AUTO_MODEL)
    if preferred in MODELS_TO_TRY:
        return [preferred] + [m for m in MODELS_TO_TRY if m != preferred]
    return list(MODELS_TO_TRY)


def ask_ai(contents, max_retries=3):
    """Reusable Gemini call (text or multimodal) with multi-model fallback and backoff."""
    client = get_client()
    if client is None:
        st.error(
            "Gemini API key is missing or invalid. Please set GEMINI_API_KEY "
            "in .streamlit/secrets.toml."
        )
        return None

    last_error = "No response received."
    styled_contents = apply_style(contents)

    for model in model_order():
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=styled_contents,
                )
                if response and response.text:
                    return response.text
                last_error = f"{model}: empty response"
                break  # empty answer (e.g. blocked) -> try next model
            except Exception as exc:
                err_msg = str(exc)
                last_error = f"{model}: {err_msg[:300]}"

                if any(code in err_msg for code in FATAL_ERRORS):
                    st.error("Gemini rejected the API key. Please check GEMINI_API_KEY.")
                    return None

                if any(code in err_msg for code in SKIP_MODEL_ERRORS):
                    break  # model doesn't exist -> next model immediately

                if any(code in err_msg for code in RETRYABLE_ERRORS):
                    if attempt < max_retries - 1:
                        time.sleep(2 * (attempt + 1))
                        continue
                    break  # retries used up -> next model

                break

    st.warning("⏳ Could not get a response from Gemini. Last error:")
    st.code(last_error)
    return None


# =========================================================
# THEME CONFIGURATION
# =========================================================
accent_colors = {
    "Teal": "#0d9488",
    "Blue": "#2563eb",
    "Indigo": "#4f46e5",
    "Emerald": "#059669",
}

THEMES = {
    "Dark": {
        "bg": "#0b1220",
        "sidebar": "#0f172a",
        "surface": "#111b2e",
        "surface2": "#17233b",
        "text": "#e6edf7",
        "muted": "#94a3b8",
        "border": "rgba(148, 163, 184, 0.20)",
        "shadow": "0 1px 2px rgba(0, 0, 0, 0.35), 0 8px 24px rgba(0, 0, 0, 0.22)",
    },
    "Light": {
        "bg": "#f4f7fb",
        "sidebar": "#ffffff",
        "surface": "#ffffff",
        "surface2": "#f1f5f9",
        "text": "#0f172a",
        "muted": "#64748b",
        "border": "rgba(15, 23, 42, 0.12)",
        "shadow": "0 1px 2px rgba(15, 23, 42, 0.06), 0 8px 24px rgba(15, 23, 42, 0.06)",
    },
}

FONT_SIZES = {"Small": 14, "Medium": 16, "Large": 18}


def hex_to_rgba(hex_color, alpha):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


_cfg = st.session_state.settings
accent = accent_colors.get(st.session_state.accent, accent_colors["Teal"])
accent_soft = hex_to_rgba(accent, 0.16)
palette = THEMES.get(_cfg.get("theme"), THEMES["Dark"])
base_px = FONT_SIZES.get(_cfg.get("font_size"), 16)
motion_css = (
    ""
    if _cfg.get("animations", True)
    else "*, *::before, *::after { transition: none !important; animation: none !important; }"
)


# =========================================================
# STYLESHEET (CLEAN, PROFESSIONAL)
# =========================================================
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {{
    --bg: {palette["bg"]};
    --sidebar: {palette["sidebar"]};
    --surface: {palette["surface"]};
    --surface2: {palette["surface2"]};
    --text: {palette["text"]};
    --muted: {palette["muted"]};
    --border: {palette["border"]};
    --shadow: {palette["shadow"]};
    --accent: {accent};
    --accent-soft: {accent_soft};
}}

.stApp {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Inter', sans-serif;
}}

[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 2rem; max-width: 1200px; }}

.stMarkdown, .stMarkdown p, .stMarkdown li,
[data-testid="stWidgetLabel"] p, label, [data-testid="stCaptionContainer"] {{
    color: var(--text);
}}
.stMarkdown p, .stMarkdown li {{ font-size: {base_px}px; line-height: 1.65; }}

h1, h2, h3, h4, h5, h6 {{
    font-family: 'Inter', sans-serif !important;
    color: var(--text) !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {{
    background: var(--sidebar) !important;
    border-right: 1px solid var(--border);
}}
[data-testid="stSidebar"] div[data-testid="stRadio"] label {{
    border-radius: 10px;
    padding: 9px 12px;
    margin-bottom: 2px;
    border: 1px solid transparent;
    transition: background 0.2s ease, border-color 0.2s ease;
    cursor: pointer;
}}
[data-testid="stSidebar"] div[data-testid="stRadio"] label p {{
    color: var(--text);
    font-size: 14.5px;
    font-weight: 500;
}}
[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {{
    background: var(--surface2);
}}
[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {{
    background: var(--accent-soft);
    border-color: var(--accent);
}}

.brand {{ display: flex; align-items: center; gap: 12px; padding: 6px 4px 14px; }}
.brand-badge {{
    width: 42px; height: 42px; border-radius: 12px;
    background: var(--accent); color: #fff;
    display: flex; align-items: center; justify-content: center; font-size: 22px;
}}
.brand-title {{ font-weight: 800; font-size: 18px; color: var(--text); line-height: 1.1; }}
.brand-sub {{ font-size: 11px; color: var(--muted); letter-spacing: 1.2px; font-weight: 600; margin-top: 3px; }}

.status {{
    display: inline-flex; gap: 8px; align-items: center;
    background: var(--surface2); border: 1px solid var(--border);
    color: var(--text); padding: 5px 12px; border-radius: 999px;
    font-size: 11.5px; font-weight: 600;
}}
.dot {{ width: 8px; height: 8px; border-radius: 50%; background: var(--pill, var(--accent)); }}

/* ---------- Hero ---------- */
.hero {{
    padding: 28px 32px;
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
    border-radius: 16px;
    background: var(--surface);
    box-shadow: var(--shadow);
    margin-bottom: 24px;
}}
.hero small {{
    color: var(--accent); font-weight: 700; letter-spacing: 1.6px;
    text-transform: uppercase; font-size: 11px;
}}
.hero h1 {{ margin: 8px 0 6px 0; font-size: clamp(26px, 3vw, 36px); line-height: 1.15; }}
div.hero p {{ color: var(--muted); margin: 0; font-size: 15.5px; line-height: 1.6; max-width: 760px; }}

/* ---------- Cards ---------- */
.card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 22px;
    min-height: 140px;
    box-shadow: var(--shadow);
    display: flex; flex-direction: column; align-items: flex-start; justify-content: center;
    transition: border-color 0.2s ease, transform 0.2s ease;
}}
.card:hover {{ border-color: var(--accent); transform: translateY(-2px); }}

.card .icon, .tool-icon {{
    width: 46px; height: 46px; border-radius: 12px;
    background: var(--accent-soft);
    display: flex; align-items: center; justify-content: center;
    font-size: 24px !important; line-height: 1;
}}
.card .label {{
    color: var(--muted); font-size: 11.5px; margin-top: 14px;
    text-transform: uppercase; font-weight: 700; letter-spacing: 1.2px;
}}
.card .value {{ color: var(--text); font-size: 26px; font-weight: 800; margin-top: 4px; letter-spacing: -0.5px; }}
.card .desc {{ color: var(--muted); font-size: 13px; margin-top: 4px; }}

.tool {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px 14px 0 0;
    padding: 22px;
    min-height: 140px;
    box-shadow: var(--shadow);
    transition: border-color 0.2s ease;
}}
.tool:hover {{ border-color: var(--accent); }}
.tool-static {{ border-radius: 14px !important; }}
.tool b {{ color: var(--text); font-size: 17px; display: block; margin-top: 12px; font-weight: 700; }}
div.tool p {{ color: var(--muted); font-size: 13.5px; line-height: 1.5; margin: 6px 0 0 0; }}

/* ---------- AI result box ---------- */
div[class*="st-key-result_box"] {{
    background: var(--surface);
    border: 1px solid var(--border) !important;
    border-left: 4px solid var(--accent) !important;
    border-radius: 14px !important;
    padding: 12px 18px;
    box-shadow: var(--shadow);
}}

/* ---------- Buttons ---------- */
.stButton > button, div[data-testid="stDownloadButton"] > button,
[data-testid="stFormSubmitButton"] > button {{
    border-radius: 10px;
    border: 1px solid var(--accent);
    background: var(--accent);
    color: #ffffff;
    font-weight: 600;
    padding: 10px 20px;
    width: 100%;
    transition: filter 0.2s ease, transform 0.2s ease;
}}
.stButton > button p, div[data-testid="stDownloadButton"] > button p,
[data-testid="stFormSubmitButton"] > button p {{ color: #ffffff !important; }}
.stButton > button:hover, div[data-testid="stDownloadButton"] > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {{
    filter: brightness(1.1);
    border-color: var(--accent);
    color: #ffffff;
}}

/* "Open ..." buttons under the Home tool cards */
div[class*="st-key-nav_btn_"] button {{
    background: var(--surface2);
    border: 1px solid var(--border);
    border-top: none;
    border-radius: 0 0 14px 14px;
    margin-top: -1px;
    font-weight: 500;
}}
div[class*="st-key-nav_btn_"] button p {{ color: var(--text) !important; }}
div[class*="st-key-nav_btn_"] button:hover {{ border-color: var(--accent); filter: none; background: var(--accent-soft); }}

/* ---------- Inputs ---------- */
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"],
[data-baseweb="select"] > div {{
    background-color: var(--surface) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
}}
input, textarea {{ color: var(--text) !important; -webkit-text-fill-color: var(--text) !important; }}
[data-baseweb="select"] * {{ color: var(--text) !important; }}
[data-baseweb="popover"] ul, [data-baseweb="menu"] {{ background: var(--surface) !important; }}
[data-baseweb="popover"] li, [role="option"] {{ color: var(--text) !important; }}
[data-testid="stNumberInput"] button {{ background: var(--surface2) !important; color: var(--text) !important; }}

[data-testid="stForm"] {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px;
}}

button[data-baseweb="tab"] {{ color: var(--muted); }}
button[data-baseweb="tab"][aria-selected="true"] {{ color: var(--accent) !important; }}
[data-baseweb="tab-highlight"] {{ background: var(--accent) !important; }}

[data-testid="stChatMessage"] {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
}}
[data-testid="stBottom"], [data-testid="stBottom"] > div {{ background: var(--bg) !important; }}
[data-testid="stAlert"] {{ border-radius: 12px; }}

.footer {{
    text-align: center; color: var(--muted); font-size: 13px;
    padding: 32px 0 16px; border-top: 1px solid var(--border);
    margin-top: 48px; line-height: 1.7;
}}

{motion_css}
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# UI REUSABLE HELPERS
# =========================================================
def hero(title, subtitle, kicker="HEALTHMATE AI"):
    st.markdown(
        f"""
        <div class="hero">
            <small>{kicker}</small>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card(icon, label, value, desc=""):
    st.markdown(
        f"""
        <div class="card">
            <div class="icon">{icon}</div>
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            <div class="desc">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def go_to_page(target_page):
    """Button callback. Callbacks run BEFORE widgets are re-created, so it is
    allowed to change the value of the 'page' radio widget here."""
    st.session_state.page = target_page


def tool(icon, title, description, target_page=None):
    extra_class = "" if target_page else "tool-static"
    st.markdown(
        f"""
        <div class="tool {extra_class}">
            <div class="tool-icon">{icon}</div>
            <div><b>{title}</b></div>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if target_page:
        st.button(
            f"Open {title}",
            key=f"nav_btn_{target_page}",
            use_container_width=True,
            on_click=go_to_page,
            args=(target_page,),
        )


def show_result(text):
    try:
        box = st.container(border=True, key="result_box")
    except TypeError:  # older Streamlit without container keys
        box = st.container(border=True)
    with box:
        st.markdown(text)


def safe_filename(name, default="report"):
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", str(name)).strip("_")
    return cleaned[:60] or default


def pdf_download(heading_or_input, answer, file_name="Health_Report.pdf", button_label="📄 Download Health Report", key=None):
    if create_pdf is None:
        st.warning("PDF module is unavailable. Keep your report.py in the project folder.")
        return

    try:
        path = create_pdf(heading_or_input, answer)
        with open(path, "rb") as f:
            data = f.read()

        st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
        st.download_button(
            button_label,
            data=data,
            file_name=file_name,
            mime="application/pdf",
            key=key,
            use_container_width=True,
        )
    except Exception as exc:
        st.error(f"PDF creation failed: {exc}")


def save_result(result_key, heading, answer, file_name, button_label, success_text=None):
    """Keep the AI answer in session state so it is still shown after a rerun
    (clicking a download button reruns the script)."""
    st.session_state.results[result_key] = {
        "heading": heading,
        "answer": answer,
        "file_name": file_name,
        "button_label": button_label,
        "success_text": success_text,
    }


def render_saved_result(result_key):
    data = st.session_state.results.get(result_key)
    if not data:
        return
    if data.get("success_text"):
        st.success(data["success_text"])
    show_result(data["answer"])
    pdf_download(
        data["heading"],
        data["answer"],
        file_name=data["file_name"],
        button_label=data["button_label"],
        key=f"pdf_{result_key}",
    )


# =========================================================
# NAVIGATION & SIDEBAR
# =========================================================
pages = [
    "Home",
    "AI Symptom Checker",
    "Medicine Info",
    "BMI Calculator",
    "Water Intake",
    "Diet Planner",
    "Exercise Planner",
    "Calorie Calculator",
    "Sleep Recommendation",
    "Medical Report Analyzer",
    "Health Dashboard",
    "AI Command Center",
    "Settings",
    "About",
]

page_icons = {
    "Home": "🏠",
    "AI Symptom Checker": "🩺",
    "Medicine Info": "💊",
    "BMI Calculator": "📊",
    "Water Intake": "💧",
    "Diet Planner": "🥗",
    "Exercise Planner": "🏋️‍♂️",
    "Calorie Calculator": "🔥",
    "Sleep Recommendation": "😴",
    "Medical Report Analyzer": "🔬",
    "Health Dashboard": "📈",
    "AI Command Center": "💬",
    "Settings": "⚙️",
    "About": "ℹ️",
}

# open the page chosen as "start page" once per session
if "start_applied" not in st.session_state:
    st.session_state.start_applied = True
    _start = st.session_state.settings.get("start_page")
    if _start in pages:
        st.session_state.page = _start

with st.sidebar:
    _ok = has_api_key()
    _pill = "#10b981" if _ok else "#f59e0b"
    _label = "AI connected" if _ok else "API key missing"
    st.markdown(
        f"""
        <div class="brand">
            <div class="brand-badge">🩺</div>
            <div>
                <div class="brand-title">HealthMate AI</div>
                <div class="brand-sub">HEALTH INTELLIGENCE</div>
            </div>
        </div>
        <div style="padding: 0 4px 14px;">
            <span class="status" style="--pill:{_pill};"><span class="dot"></span>{_label}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.radio(
        "Navigation",
        pages,
        format_func=lambda p: f"{page_icons[p]}  {p}",
        key="page",
        label_visibility="collapsed",
    )

page = st.session_state.page


# =========================================================
# PAGE: HOME
# =========================================================
if page == "Home":
    hero(
        "HealthMate AI",
        "Your intelligent health companion for general wellness, calculations, planning, and AI-powered educational assistance.",
        "AI HEALTH PLATFORM",
    )

    user_name = st.session_state.settings.get("name", "").strip()
    if user_name:
        st.markdown(f"### 👋 Welcome, {user_name}")

    st.markdown("### Explore HealthMate Features")

    r1 = st.columns(3)
    with r1[0]:
        tool(
            "🩺",
            "AI Symptom Checker",
            "Describe symptoms for general educational guidance.",
            target_page="AI Symptom Checker",
        )
    with r1[1]:
        tool(
            "💊",
            "Medicine Info",
            "Learn general information about medicines.",
            target_page="Medicine Info",
        )
    with r1[2]:
        tool(
            "📈",
            "Health Dashboard",
            "See values calculated during this session.",
            target_page="Health Dashboard",
        )

    st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)

    r2 = st.columns(3)
    with r2[0]:
        tool(
            "📊",
            "BMI Calculator",
            "Calculate BMI from height and weight.",
            target_page="BMI Calculator",
        )
    with r2[1]:
        tool(
            "💧",
            "Water Intake",
            "Estimate general daily water needs.",
            target_page="Water Intake",
        )
    with r2[2]:
        tool(
            "🥗",
            "Diet Planner",
            "Generate a simple Indian diet plan.",
            target_page="Diet Planner",
        )

    st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)

    r3 = st.columns(3)
    with r3[0]:
        tool(
            "🏋️‍♂️",
            "Exercise Planner",
            "Generate simple workout plans tailored to goals.",
            target_page="Exercise Planner",
        )
    with r3[1]:
        tool(
            "🔥",
            "Calorie Calculator",
            "Estimate calories and macros from meal descriptions.",
            target_page="Calorie Calculator",
        )
    with r3[2]:
        tool(
            "😴",
            "Sleep Recommendation",
            "Get personalized guidance for healthy sleep habits.",
            target_page="Sleep Recommendation",
        )

    st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)

    r4 = st.columns(3)
    with r4[0]:
        tool(
            "🔬",
            "Medical Report Analyzer",
            "Upload image reports for educational AI breakdown.",
            target_page="Medical Report Analyzer",
        )
    with r4[1]:
        tool(
            "💬",
            "AI Command Center",
            "Ask general health & wellness questions in interactive chat.",
            target_page="AI Command Center",
        )

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("### System Status")
    c1, c2 = st.columns(2)
    with c1:
        card("🛠️", "Tools", "12+", "Health utilities")
    with c2:
        card("📄", "Reports", "PDF", "Downloadable reports")

    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        "ℹ️ HealthMate AI provides general educational information only and is not a substitute for professional medical advice."
    )


# =========================================================
# PAGE: AI SYMPTOM CHECKER
# =========================================================
elif page == "AI Symptom Checker":
    hero(
        "AI Symptom Checker",
        "Describe your symptoms and receive general educational information from Gemini.",
    )

    symptoms = st.chat_input(
        "Describe your symptoms...",
        key="symptoms_input",
    )

    if symptoms:
        with st.spinner("Analyzing symptoms..."):
            answer = ask_ai(
                f"""
You are HealthMate AI, a general health education assistant.

User symptoms:
{symptoms}

Give general educational information.
Do not diagnose.
Do not prescribe medication.
Mention important warning signs and when professional medical care may be needed.
Keep the language simple.
"""
            )
        if answer:
            save_result(
                "symptoms",
                symptoms,
                answer,
                "Symptom_Report.pdf",
                "📄 Download Symptom Report",
            )
            st.session_state.results["symptoms"]["user_text"] = symptoms

    saved = st.session_state.results.get("symptoms")
    if saved:
        with st.chat_message("user"):
            st.write(saved.get("user_text", saved["heading"]))
        with st.chat_message("assistant"):
            st.write(saved["answer"])
            pdf_download(
                saved["heading"],
                saved["answer"],
                file_name=saved["file_name"],
                button_label=saved["button_label"],
                key="pdf_symptoms",
            )

    st.info(
        "ℹ️ This response is educational and should not be treated as a medical diagnosis. "
        "If you have severe symptoms, chest pain, difficulty breathing, or an emergency, seek immediate medical care."
    )


# =========================================================
# PAGE: MEDICINE INFO
# =========================================================
elif page == "Medicine Info":
    hero(
        "Medicine Information",
        "Get simple educational information about a medicine without receiving a prescription.",
    )

    medicine = st.text_input(
        "Medicine name",
        placeholder="Example: Paracetamol",
    )

    if st.button("💊 Get Medicine Information"):
        if not medicine.strip():
            st.warning("Please enter a medicine name.")
        else:
            with st.spinner("Preparing information..."):
                answer = ask_ai(
                    f"""
Provide general educational information about:

Medicine: {medicine}

Include:
- What it is generally used for
- Common side effects
- Precautions
- When to consult a doctor

Keep the language simple.
Do not prescribe a dose.
Do not personalize treatment.
"""
                )

            if answer:
                save_result(
                    "medicine",
                    f"Medicine Information: {medicine}",
                    answer,
                    f"Medicine_Info_{safe_filename(medicine, 'medicine')}.pdf",
                    "📄 Download Medicine Guide",
                    "Information ready",
                )

    render_saved_result("medicine")
    st.info("ℹ️ Consult a qualified healthcare professional before taking medicines.")


# =========================================================
# PAGE: BMI CALCULATOR
# =========================================================
elif page == "BMI Calculator":
    hero(
        "BMI Calculator",
        "Calculate your Body Mass Index using height and weight.",
        "BODY METRICS",
    )

    unit_choice = st.radio(
        "Height Unit",
        ["Centimeters (cm)", "Feet & Inches (ft + in)"],
        horizontal=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        if unit_choice == "Centimeters (cm)":
            height = st.number_input(
                "Height (cm)",
                min_value=50.0,
                max_value=250.0,
                value=170.0,
                step=0.5,
            )
            height_m = height / 100.0
        else:
            f_col, i_col = st.columns(2)
            with f_col:
                feet = st.number_input("Feet (ft)", min_value=1, max_value=8, value=5, step=1)
            with i_col:
                inches = st.number_input("Inches (in)", min_value=0, max_value=11, value=7, step=1)
            total_inches = (feet * 12) + inches
            height_m = total_inches * 0.0254

    with c2:
        weight = st.number_input(
            "Weight (kg)",
            min_value=10.0,
            max_value=300.0,
            value=65.0,
            step=0.5,
        )

    if st.button("📊 Calculate BMI"):
        if height_m > 0:
            bmi = weight / (height_m * height_m)
            st.session_state.bmi = bmi

            if bmi < 18.5:
                category = "Underweight"
            elif bmi < 25:
                category = "Healthy Weight"
            elif bmi < 30:
                category = "Overweight"
            else:
                category = "Obesity"

            st.markdown("<br>", unsafe_allow_html=True)
            a, b = st.columns(2)
            with a:
                card("📊", "BMI", f"{bmi:.2f}", "Calculated value")
            with b:
                card("⚖️", "Category", category, "General BMI category")

            st.markdown("<br>", unsafe_allow_html=True)
            st.info(
                "BMI is a general screening measure and should not be used as the only measure of health."
            )


# =========================================================
# PAGE: WATER INTAKE
# =========================================================
elif page == "Water Intake":
    hero(
        "Water Intake Calculator",
        "Estimate general daily water intake from body weight.",
        "HYDRATION",
    )

    weight = st.number_input(
        "Weight (kg)",
        min_value=10.0,
        max_value=250.0,
        value=60.0,
        step=0.5,
    )

    if st.button("💧 Calculate Water Intake"):
        water_ml = weight * 35
        litres = water_ml / 1000
        st.session_state.water = litres

        st.markdown("<br>", unsafe_allow_html=True)
        a, b = st.columns(2)
        with a:
            card("💧", "Recommended", f"{litres:.2f} L", "General daily estimate")
        with b:
            card("🥤", "Millilitres", f"{water_ml:.0f} ml", "Per day estimate")

        st.markdown("<br>", unsafe_allow_html=True)
        st.info("Your actual needs can vary with climate, activity, diet, and health.")


# =========================================================
# PAGE: DIET PLANNER
# =========================================================
elif page == "Diet Planner":
    hero(
        "AI Diet Planner",
        "Generate a simple one-day Indian diet plan.",
        "NUTRITION AI",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        age = st.number_input("Age", 1, 100, 18)
    with c2:
        gender = st.selectbox("Gender", ["Male", "Female"])
    with c3:
        goal = st.selectbox(
            "Goal",
            ["Weight Loss", "Weight Gain", "Healthy Lifestyle"],
        )

    if st.button("🥗 Generate Diet Plan"):
        with st.spinner("Generating diet plan..."):
            answer = ask_ai(
                f"""
Create a simple one-day Indian diet plan.

Age: {age}
Gender: {gender}
Goal: {goal}

Include:
Breakfast
Lunch
Evening Snack
Dinner
Healthy Tips

Keep it simple.
Do not provide medical treatment.
"""
            )

        if answer:
            save_result(
                "diet",
                f"Diet Plan ({goal} | Age: {age}, Gender: {gender})",
                answer,
                f"Diet_Plan_{safe_filename(goal)}.pdf",
                "📄 Download Diet Plan",
                "Diet plan ready",
            )

    render_saved_result("diet")


# =========================================================
# PAGE: EXERCISE PLANNER
# =========================================================
elif page == "Exercise Planner":
    hero(
        "AI Exercise Planner",
        "Generate a simple one-day exercise plan based on fitness level and goal.",
        "FITNESS AI",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        age = st.number_input("Age", 5, 100, 18)
    with c2:
        fitness = st.selectbox(
            "Fitness Level",
            ["Beginner", "Intermediate", "Advanced"],
        )
    with c3:
        goal = st.selectbox(
            "Goal",
            ["Weight Loss", "Muscle Gain", "Stay Fit"],
        )

    if st.button("🏋️‍♂️ Generate Exercise Plan"):
        with st.spinner("Generating workout plan..."):
            answer = ask_ai(
                f"""
Create a simple one-day exercise plan.

Age: {age}
Fitness Level: {fitness}
Goal: {goal}

Include:
- Warm-up
- Main Exercises
- Stretching
- Safety Tips

Keep it simple and suitable for students.
"""
            )

        if answer:
            save_result(
                "exercise",
                f"Exercise Plan ({fitness} | {goal} | Age: {age})",
                answer,
                f"Exercise_Plan_{safe_filename(goal)}.pdf",
                "📄 Download Workout Plan",
                "Exercise plan ready",
            )

    render_saved_result("exercise")


# =========================================================
# PAGE: CALORIE CALCULATOR
# =========================================================
elif page == "Calorie Calculator":
    hero(
        "AI Calorie Calculator",
        "Describe what you ate and get an estimated calorie and nutrition breakdown.",
        "NUTRITION ANALYTICS",
    )

    food = st.text_area(
        "What did you eat today?",
        placeholder="Example: 2 chapati, dal, rice, salad, and milk",
        height=120,
    )

    if st.button("🔥 Calculate Calories"):
        if not food.strip():
            st.warning("Please enter your food items.")
        else:
            with st.spinner("Estimating nutrition..."):
                answer = ask_ai(
                    f"""
Estimate the nutrition for this food:

{food}

Include:
- Estimated total calories
- Protein
- Carbohydrates
- Fat
- Whether the meal is balanced
- Suggestions to improve it

Clearly state that the values are estimates.
"""
                )

            if answer:
                save_result(
                    "calorie",
                    f"Calorie & Nutrition Breakdown: {food}",
                    answer,
                    "Calorie_Report.pdf",
                    "📄 Download Nutrition Breakdown",
                    "Estimate ready",
                )

    render_saved_result("calorie")
    st.info("ℹ️ AI calorie estimates may be inaccurate because portion sizes vary.")


# =========================================================
# PAGE: SLEEP RECOMMENDATION
# =========================================================
elif page == "Sleep Recommendation":
    hero(
        "Sleep Recommendation",
        "Get general sleep guidance based on your age, sleep duration, and lifestyle.",
        "RECOVERY AI",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        age = st.number_input("Your Age", 1, 100, 18)
    with c2:
        sleep_hours = st.slider(
            "Sleep Hours",
            1,
            12,
            7,
        )
    with c3:
        lifestyle = st.selectbox(
            "Lifestyle",
            ["Student", "Working Professional", "Athlete", "Senior Citizen"],
        )

    if st.button("😴 Get Sleep Advice"):
        st.session_state.sleep = sleep_hours
        with st.spinner("Preparing sleep advice..."):
            answer = ask_ai(
                f"""
Provide simple sleep recommendations.

Age: {age}
Sleep Hours: {sleep_hours}
Lifestyle: {lifestyle}

Include:
- Whether the sleep duration is generally adequate
- Tips to improve sleep quality
- Healthy bedtime habits
- When to consult a doctor

Keep the language simple.
"""
            )

        if answer:
            save_result(
                "sleep",
                f"Sleep Guidance (Age: {age}, Hours: {sleep_hours}, Profile: {lifestyle})",
                answer,
                "Sleep_Guidance.pdf",
                "📄 Download Sleep Guidance",
                "Sleep advice ready",
            )

    render_saved_result("sleep")


# =========================================================
# PAGE: MEDICAL REPORT ANALYZER
# =========================================================
elif page == "Medical Report Analyzer":
    hero(
        "Medical Report Analyzer",
        "Upload an image of a medical report for an educational AI breakdown.",
        "REPORT VISION AI",
    )

    uploaded_file = st.file_uploader(
        "Upload Report Image (JPG, PNG)", type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Report", use_container_width=True)

        if st.button("🔬 Analyze Medical Report"):
            with st.spinner("Analyzing report image..."):
                mime = uploaded_file.type or "image/jpeg"
                answer = ask_ai(
                    [
                        types.Part.from_bytes(
                            data=uploaded_file.getvalue(),
                            mime_type=mime,
                        ),
                        "Analyze this medical report image for educational purposes. "
                        "Explain key findings, medical terms, and reference values simply. "
                        "Do not diagnose.",
                    ]
                )

            if answer:
                save_result(
                    "report",
                    "Medical Report Analysis",
                    answer,
                    "Report_Analysis.pdf",
                    "📄 Download Report Analysis",
                    "Analysis Complete",
                )

    render_saved_result("report")
    st.info("ℹ️ This is an educational explanation only. Please discuss your report with your doctor.")


# =========================================================
# PAGE: HEALTH DASHBOARD
# =========================================================
elif page == "Health Dashboard":
    hero(
        "Health Dashboard",
        "Overview of metrics calculated during your current session.",
        "SESSION METRICS",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        bmi_val = (
            f"{st.session_state.bmi:.2f}"
            if st.session_state.bmi is not None
            else "Not Calculated"
        )
        card("📊", "Body Mass Index", bmi_val, "Session BMI Value")
    with c2:
        water_val = (
            f"{st.session_state.water:.2f} L"
            if st.session_state.water is not None
            else "Not Calculated"
        )
        card("💧", "Daily Water Goal", water_val, "Hydration Estimate")
    with c3:
        sleep_val = (
            f"{st.session_state.sleep} Hours"
            if st.session_state.sleep is not None
            else "Not Recorded"
        )
        card("😴", "Target Sleep", sleep_val, "Nightly Rest")


# =========================================================
# PAGE: AI COMMAND CENTER
# =========================================================
elif page == "AI Command Center":
    hero(
        "AI Command Center",
        "Interactive conversational AI assistant for general health and wellness questions.",
        "INTERACTIVE CHAT",
    )

    user_query = st.chat_input("Ask any health & wellness question...")

    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.spinner("Thinking..."):
            resp = ask_ai(
                f"User prompt: {user_query}\n"
                "Provide educational health guidance without giving a medical diagnosis or prescription."
            )
        if resp:
            st.session_state.chat_history.append({"role": "assistant", "content": resp})

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])


# =========================================================
# PAGE: SETTINGS
# =========================================================
elif page == "Settings":
    hero(
        "Settings",
        "Customize theme settings and workspace options.",
        "PREFERENCES",
    )

    cfg = st.session_state.settings

    def pick_index(options, value):
        return options.index(value) if value in options else 0

    with st.form("settings_form"):
        tab_look, tab_ai, tab_profile = st.tabs(
            ["🎨 Appearance", "🤖 AI Preferences", "👤 Profile & Startup"]
        )

        with tab_look:
            l1, l2 = st.columns(2)
            with l1:
                theme_options = list(THEMES.keys())
                new_theme = st.selectbox(
                    "Theme Mode",
                    theme_options,
                    index=pick_index(theme_options, cfg.get("theme")),
                )
                accent_options = list(accent_colors.keys())
                new_accent = st.selectbox(
                    "Accent Color",
                    accent_options,
                    index=pick_index(accent_options, st.session_state.accent),
                )
            with l2:
                size_options = list(FONT_SIZES.keys())
                new_font = st.selectbox(
                    "Text Size",
                    size_options,
                    index=pick_index(size_options, cfg.get("font_size")),
                )
                new_anim = st.toggle(
                    "Smooth animations",
                    value=bool(cfg.get("animations", True)),
                    help="Turn off for a static, faster-feeling interface.",
                )

        with tab_ai:
            a1, a2 = st.columns(2)
            with a1:
                model_options = [AUTO_MODEL] + MODELS_TO_TRY
                new_model = st.selectbox(
                    "AI Model",
                    model_options,
                    index=pick_index(model_options, cfg.get("model")),
                    help="Auto tries the models in order and uses the first that works.",
                )
                lang_options = list(LANGUAGE_RULES.keys())
                new_language = st.selectbox(
                    "Response Language",
                    lang_options,
                    index=pick_index(lang_options, cfg.get("language")),
                )
            with a2:
                detail_options = list(DETAIL_RULES.keys())
                new_detail = st.selectbox(
                    "Answer Detail Level",
                    detail_options,
                    index=pick_index(detail_options, cfg.get("detail")),
                )
                tone_options = list(TONE_RULES.keys())
                new_tone = st.selectbox(
                    "Tone of Voice",
                    tone_options,
                    index=pick_index(tone_options, cfg.get("tone")),
                )

        with tab_profile:
            p1, p2 = st.columns(2)
            with p1:
                new_name = st.text_input(
                    "Your Name (optional)",
                    value=cfg.get("name", ""),
                    max_chars=40,
                    help="Shown as a welcome message on the Home page.",
                )
            with p2:
                new_start = st.selectbox(
                    "Start Page",
                    pages,
                    index=pick_index(pages, cfg.get("start_page")),
                    help="The page that opens when you start the app.",
                )

        saved = st.form_submit_button("💾 Save Settings")

    if saved:
        st.session_state.accent = new_accent
        st.session_state.settings = {
            "model": new_model,
            "language": new_language,
            "detail": new_detail,
            "tone": new_tone,
            "name": new_name.strip(),
            "theme": new_theme,
            "font_size": new_font,
            "animations": bool(new_anim),
            "start_page": new_start,
        }
        file_ok = save_prefs()
        st.toast("Settings saved ✅" if file_ok else "Saved for this session only")
        st.rerun()

    st.markdown("### System Overview")
    k1, k2, k3 = st.columns(3)
    with k1:
        card(
            "🔑",
            "API Key",
            "Connected" if has_api_key() else "Missing",
            "From secrets.toml or environment",
        )
    with k2:
        card("🧠", "Active Model", model_order()[0], "First model tried")
    with k3:
        card(
            "🌐",
            "Response Style",
            cfg.get("language", "English"),
            f"{cfg.get('detail', 'Standard')} · {cfg.get('tone', 'Friendly')}",
        )

    st.markdown("### Tools & Data")
    t1, t2 = st.columns(2)
    with t1:
        if st.button("🔌 Test AI Connection"):
            with st.spinner("Testing connection..."):
                test_answer = ask_ai("Reply with the single word: OK")
            if test_answer:
                st.success("AI connection is working ✅")
    with t2:
        st.download_button(
            "⬇️ Export Settings (JSON)",
            data=json.dumps(
                {"accent": st.session_state.accent, "settings": st.session_state.settings},
                indent=2,
            ),
            file_name="healthmate_settings.json",
            mime="application/json",
            key="export_settings",
        )

    d1, d2, d3 = st.columns(3)
    with d1:
        if st.button("🧹 Clear Chat History"):
            st.session_state.chat_history = []
            st.success("Chat history cleared.")
    with d2:
        if st.button("🗑️ Clear Saved Results"):
            st.session_state.results = {}
            st.success("Saved results cleared.")
    with d3:
        if st.button("♻️ Reset All Settings"):
            st.session_state.accent = "Teal"
            st.session_state.settings = dict(DEFAULT_SETTINGS)
            save_prefs()
            st.toast("Settings reset ♻️")
            st.rerun()


# =========================================================
# PAGE: ABOUT
# =========================================================
elif page == "About":
    hero(
        "About HealthMate AI",
        "Empowering individuals with educational health insights driven by modern AI.",
        "ABOUT PLATFORM",
    )

    st.markdown(
        """
        ### About the Platform
        HealthMate AI is a comprehensive wellness application designed to simplify medical educational content, track basic lifestyle metrics, and help users organize daily diet and exercise goals.

        ### Key Modules
        - **AI Symptom Checker**: Instant general insights on described symptoms.
        - **Medicine Info**: Educational reference for common pharmaceutical usages and side effects.
        - **Calculators**: BMI, daily water needs, and meal calorie estimates.
        - **Planners**: Customized diet and workout schedules.
        - **Report Vision**: Educational image analysis for laboratory reports.

        ### Medical Disclaimer
        *HealthMate AI is strictly for informational and educational purposes. It does not provide medical diagnoses, treatment plans, or prescriptions. Always consult a qualified medical professional for health concerns.*
        """
    )


# =========================================================
# FOOTER
# =========================================================
st.markdown(
    """
    <div class="footer">
        HealthMate AI © 2026 | Educational Health Intelligence Platform<br>
        <small>Not intended for emergency use or clinical decision-making.</small>
    </div>
    """,
    unsafe_allow_html=True,
)
