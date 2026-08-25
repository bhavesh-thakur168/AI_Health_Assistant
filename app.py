import time
import streamlit as st
import streamlit.components.v1 as components
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
    page_title="HealthMate AI - Vibrant Edition",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# AUTOMATIC SIDEBAR CLOSE ON MOBILE SELECTION
# =========================================================
components.html(
    """
    <script>
    const parentDoc = window.parent.document;
    function setupMobileSidebarAutoClose() {
        const labels = parentDoc.querySelectorAll('[data-testid="stSidebar"] label');
        labels.forEach(label => {
            if (!label.dataset.hasAutoClose) {
                label.dataset.hasAutoClose = "true";
                label.addEventListener('click', function() {
                    if (window.innerWidth <= 768) {
                        setTimeout(function() {
                            const closeBtn = parentDoc.querySelector('button[data-testid="stSidebarCollapseButton"]') 
                                          || parentDoc.querySelector('[data-testid="stSidebar"] button');
                            if (closeBtn) {
                                closeBtn.click();
                            }
                        }, 250);
                    }
                });
            }
        });
    }
    setupMobileSidebarAutoClose();
    const observer = new MutationObserver(setupMobileSidebarAutoClose);
    observer.observe(parentDoc.body, { childList: true, subtree: true });
    </script>
    """,
    height=0,
    width=0,
)


# =========================================================
# SESSION STATE INITIALIZATION
# =========================================================
VALID_MODELS = ["gemini-3.6-flash", "gemini-3.6-pro"]

session_defaults = {
    "page": "Home",
    "chat_history": [],
    "bmi": None,
    "bmi_category": None,
    "water": None,
    "sleep": None,
    "symptom_result": None,
    "med_result": None,
    "diet_result": None,
    "exercise_result": None,
    "calorie_result": None,
    "sleep_result": None,
    "medical_report_result": None,
    "command_center_result": None,
    "accent": "Vibrant Aurora",
    "enable_animations": True,
    "anim_speed": "Normal (15s)",
    "font_scale": "Balanced",
    "ai_model": "gemini-3.6-flash",
}

for key, default_value in session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# Force reset if an outdated model name was saved in active session state
if st.session_state.ai_model not in VALID_MODELS:
    st.session_state.ai_model = "gemini-3.6-flash"


# =========================================================
# GEMINI CLIENT & EXECUTION SAFEGUARD
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


def ask_ai(prompt, model=None):
    """Executes requests using updated Google GenAI model endpoints."""
    if client is None:
        st.error(
            "Gemini API is not configured. Please add GEMINI_API_KEY "
            "to .streamlit/secrets.toml."
        )
        return None

    selected_model = model or st.session_state.ai_model
    if selected_model not in VALID_MODELS:
        selected_model = "gemini-3.6-flash"

    try:
        response = client.models.generate_content(
            model=selected_model,
            contents=prompt,
        )
        return response.text
    except Exception as exc:
        st.error(f"Gemini request failed: {exc}")
        return None


# =========================================================
# THEME & ANIMATION DYNAMIC CONFIGURATION
# =========================================================
accent_themes = {
    "Vibrant Aurora": {"primary": "#00f2fe", "secondary": "#f43f5e", "gradient": "linear-gradient(135deg, #00f2fe 0%, #a855f7 50%, #ec4899 100%)"},
    "Neon Emerald": {"primary": "#10b981", "secondary": "#06b6d4", "gradient": "linear-gradient(135deg, #10b981 0%, #3b82f6 50%, #6366f1 100%)"},
    "Sunset Fire": {"primary": "#f97316", "secondary": "#ec4899", "gradient": "linear-gradient(135deg, #f97316 0%, #e11d48 50%, #9333ea 100%)"},
    "Electric Purple": {"primary": "#c084fc", "secondary": "#38bdf8", "gradient": "linear-gradient(135deg, #c084fc 0%, #3b82f6 50%, #06b6d4 100%)"},
}

current_theme = accent_themes.get(st.session_state.accent, accent_themes["Vibrant Aurora"])
accent = current_theme["primary"]
theme_gradient = current_theme["gradient"]

speed_map = {
    "Fast (8s)": "8s",
    "Normal (15s)": "15s",
    "Relaxed (25s)": "25s",
}
bg_speed = speed_map.get(st.session_state.anim_speed, "15s")
anim_play_state = "running" if st.session_state.enable_animations else "paused"

font_sizes = {
    "Compact": {"root": "13px", "hero": "22px", "h1": "34px"},
    "Balanced": {"root": "14px", "hero": "24px", "h1": "40px"},
    "Large": {"root": "15.5px", "hero": "26px", "h1": "44px"},
}
scale = font_sizes.get(st.session_state.font_scale, font_sizes["Balanced"])

background = "#030712"
surface = "rgba(15, 23, 42, 0.8)"
surface2 = "rgba(30, 41, 75, 0.75)"
text = "#f8fafc"
muted = "#94a3b8"
border = "rgba(236, 72, 153, 0.25)"
card_shadow = "0 12px 35px 0 rgba(0, 0, 0, 0.65)"
glass_blur = "blur(16px)"


# =========================================================
# STYLESHEET
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
    --gradient: {theme_gradient};
    --shadow: {card_shadow};
    --blur: {glass_blur};
}}

.stApp {{
    background: linear-gradient(-45deg, #030712, #0f172a, #1e1b4b, #31103f, #062033);
    background-size: 400% 400%;
    animation: gradientBG {bg_speed} ease infinite {anim_play_state};
    color: var(--text);
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: {scale['root']};
}}

@keyframes gradientBG {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

.stApp::before {{
    content: '';
    position: fixed;
    top: -140px;
    left: -140px;
    width: 550px;
    height: 550px;
    background: radial-gradient(circle, rgba(236, 72, 153, 0.28) 0%, rgba(168, 85, 247, 0.15) 40%, transparent 70%);
    filter: blur(70px);
    z-index: 0;
    pointer-events: none;
    animation: floatOrb 12s ease-in-out infinite alternate {anim_play_state};
}}

.stApp::after {{
    content: '';
    position: fixed;
    bottom: -140px;
    right: -140px;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(6, 182, 212, 0.28) 0%, rgba(16, 185, 129, 0.15) 40%, transparent 70%);
    filter: blur(75px);
    z-index: 0;
    pointer-events: none;
    animation: floatOrb 16s ease-in-out infinite alternate-reverse {anim_play_state};
}}

@keyframes floatOrb {{
    0% {{ transform: translate(0px, 0px) scale(1); }}
    50% {{ transform: translate(50px, -40px) scale(1.12); }}
    100% {{ transform: translate(-30px, 30px) scale(0.92); }}
}}

.hero, .card, .tool, .result, div[data-testid="stForm"], .master-card {{
    animation: fadeInUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}}

@keyframes fadeInUp {{
    from {{
        opacity: 0;
        transform: translateY(20px) scale(0.97);
    }}
    to {{
        opacity: 1;
        transform: translateY(0) scale(1);
    }}
}}

[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, rgba(8, 12, 26, 0.96) 0%, rgba(18, 10, 32, 0.97) 50%, rgba(10, 16, 35, 0.98) 100%) !important;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-right: 1px solid rgba(236, 72, 153, 0.25);
    box-shadow: 12px 0 40px rgba(0, 0, 0, 0.7);
}}

.sidebar-logo-card {{
    text-align: center;
    padding: 20px 14px;
    border-radius: 20px;
    background: linear-gradient(145deg, rgba(236, 72, 153, 0.08) 0%, rgba(6, 182, 212, 0.08) 100%);
    border: 1px solid rgba(236, 72, 153, 0.3);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}}

.dna-logo-wrapper {{
    width: 90px;
    height: 90px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    filter: drop-shadow(0 0 16px rgba(236, 72, 153, 0.65)) drop-shadow(0 0 25px rgba(6, 182, 212, 0.45));
    animation: pulseLogo 4s ease-in-out infinite alternate;
}}

@keyframes pulseLogo {{
    0% {{ transform: scale(1); filter: drop-shadow(0 0 14px rgba(236, 72, 153, 0.6)); }}
    100% {{ transform: scale(1.06); filter: drop-shadow(0 0 22px rgba(6, 182, 212, 0.8)); }}
}}

[data-testid="stSidebar"] div[data-testid="stRadio"] label {{
    border-radius: 14px;
    padding: 11px 16px;
    transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    border: 1px solid transparent;
    font-size: 13.5px;
    font-weight: 600;
    color: #cbd5e1;
    margin-bottom: 5px;
    display: flex;
    align-items: center;
    background: rgba(15, 23, 42, 0.4);
}}

[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {{
    background: linear-gradient(90deg, rgba(236, 72, 153, 0.18), rgba(6, 182, 212, 0.18));
    border-color: rgba(236, 72, 153, 0.45);
    color: #ffffff;
    transform: translateX(5px);
    box-shadow: 0 4px 15px rgba(236, 72, 153, 0.25);
}}

[data-testid="stSidebar"] div[data-testid="stRadio"] [aria-checked="true"] + div label,
[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"] {{
    background: linear-gradient(90deg, rgba(236, 72, 153, 0.3) 0%, rgba(6, 182, 212, 0.3) 100%) !important;
    border: 1px solid rgba(0, 242, 254, 0.5) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 20px rgba(0, 242, 254, 0.35) !important;
}}

h1, h2, h3, h4, h5, h6 {{
    font-family: 'Outfit', sans-serif !important;
    color: var(--text) !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em !important;
}}

.hero {{
    padding: 34px 38px;
    border: 1px solid rgba(236, 72, 153, 0.3);
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 15, 45, 0.85) 100%);
    backdrop-filter: var(--blur);
    -webkit-backdrop-filter: var(--blur);
    box-shadow: 0 16px 45px rgba(0, 0, 0, 0.5);
    margin-bottom: 24px;
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
    background: var(--gradient);
}}

.hero small {{
    color: #00f2fe;
    font-family: 'Outfit', sans-serif;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-size: 10.5px;
    background: linear-gradient(90deg, rgba(0, 242, 254, 0.15), rgba(236, 72, 153, 0.15));
    padding: 6px 14px;
    border-radius: 18px;
    border: 1px solid rgba(0, 242, 254, 0.35);
    display: inline-block;
}}

.hero h1 {{
    margin: 14px 0 8px 0;
    font-size: clamp(24px, 4vw, {scale['h1']});
    line-height: 1.15;
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.hero p {{
    color: #cbd5e1;
    margin: 0;
    font-size: {scale['hero']};
    line-height: 1.6;
    max-width: 780px;
}}

.card {{
    background: linear-gradient(145deg, rgba(20, 28, 55, 0.85) 0%, rgba(12, 18, 38, 0.8) 100%);
    backdrop-filter: var(--blur);
    -webkit-backdrop-filter: var(--blur);
    border: 1px solid rgba(236, 72, 153, 0.25);
    border-radius: 20px;
    padding: 20px;
    min-height: 130px;
    box-shadow: var(--shadow);
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    justify-content: center;
}}

.card:hover {{
    transform: translateY(-4px);
    border-color: #ec4899;
    box-shadow: 0 12px 32px rgba(236, 72, 153, 0.3);
}}

.card .icon {{
    font-size: 36px !important;
    line-height: 1;
    filter: drop-shadow(0 0 10px rgba(236, 72, 153, 0.6));
}}

.card .label {{
    color: #94a3b8;
    font-size: 11px;
    margin-top: 10px;
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 1.2px;
}}

.card .value {{
    color: #ffffff;
    font-family: 'Outfit', sans-serif;
    font-size: 24px;
    font-weight: 800;
    margin-top: 2px;
}}

.card .desc {{
    color: #38bdf8;
    font-size: 12.5px;
    margin-top: 2px;
}}

.tool {{
    background: linear-gradient(145deg, rgba(20, 28, 55, 0.85) 0%, rgba(12, 18, 38, 0.8) 100%);
    backdrop-filter: var(--blur);
    -webkit-backdrop-filter: var(--blur);
    border: 1px solid rgba(0, 242, 254, 0.2);
    border-radius: 20px 20px 0 0;
    padding: 20px;
    min-height: 130px;
    box-shadow: var(--shadow);
    transition: all 0.3s ease;
}}

.tool:hover {{
    border-color: rgba(236, 72, 153, 0.5);
}}

.tool-static {{
    border-radius: 20px !important;
}}

.tool b {{
    font-family: 'Outfit', sans-serif;
    color: #ffffff;
    font-size: 17px;
    display: block;
    margin-top: 10px;
}}

.tool p {{
    color: #94a3b8;
    font-size: 13px;
    line-height: 1.5;
    margin-top: 4px;
    margin-bottom: 0;
}}

.tool-icon {{
    font-size: 38px !important;
    display: inline-block;
    filter: drop-shadow(0 0 12px rgba(6, 182, 212, 0.6));
}}

.status {{
    display: inline-flex;
    gap: 8px;
    align-items: center;
    color: #10b981;
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.4);
    padding: 6px 14px;
    border-radius: 24px;
    font-size: 10.5px;
    font-weight: 800;
    letter-spacing: 1px;
}}

.dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #10b981;
    box-shadow: 0 0 10px #10b981;
    animation: pulseGlow 1.8s infinite;
}}

@keyframes pulseGlow {{
    0% {{ transform: scale(0.9); opacity: 0.7; }}
    50% {{ transform: scale(1.3); opacity: 1; }}
    100% {{ transform: scale(0.9); opacity: 0.7; }}
}}

.result {{
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.92) 0%, rgba(25, 15, 45, 0.9) 100%);
    backdrop-filter: var(--blur);
    -webkit-backdrop-filter: var(--blur);
    border: 1px solid rgba(236, 72, 153, 0.3);
    border-left: 5px solid #ec4899;
    border-radius: 18px;
    padding: 22px;
    box-shadow: var(--shadow);
    margin-top: 18px;
    line-height: 1.65;
    color: #ffffff;
    word-break: break-word;
}}

.master-card {{
    background: linear-gradient(135deg, rgba(236, 72, 153, 0.15) 0%, rgba(168, 85, 247, 0.15) 50%, rgba(6, 182, 212, 0.15) 100%);
    backdrop-filter: var(--blur);
    border: 1px solid rgba(236, 72, 153, 0.4);
    border-radius: 24px;
    padding: 24px;
    margin-top: 24px;
    margin-bottom: 24px;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.4);
}}

.stButton > button, div[data-testid="stDownloadButton"] > button {{
    border-radius: 12px;
    border: 1px solid rgba(236, 72, 153, 0.35);
    background: linear-gradient(135deg, rgba(30, 20, 50, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%);
    color: #ffffff;
    font-weight: 700;
    padding: 12px 20px;
    transition: all 0.25s ease;
    width: 100%;
    min-height: 48px;
}}

.stButton > button:hover, div[data-testid="stDownloadButton"] > button:hover {{
    border-color: #00f2fe;
    color: #00f2fe;
    background: linear-gradient(135deg, rgba(40, 25, 65, 0.95) 0%, rgba(20, 30, 55, 0.95) 100%);
    box-shadow: 0 4px 20px rgba(0, 242, 254, 0.35);
}}

div[data-testid="stColumn"] .stButton > button {{
    border-top-left-radius: 0px;
    border-top-right-radius: 0px;
    border-bottom-left-radius: 18px;
    border-bottom-right-radius: 18px;
    margin-top: -1px;
}}

.footer {{
    text-align: center;
    color: #64748b;
    font-size: 12.5px;
    padding: 28px 0 16px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    margin-top: 45px;
    line-height: 1.6;
}}

@media (max-width: 768px) {{
    .hero {{
        padding: 22px 18px !important;
        border-radius: 18px !important;
        margin-bottom: 18px !important;
    }}
    .hero h1 {{
        font-size: 24px !important;
    }}
    .hero p {{
        font-size: 13.5px !important;
    }}
    .card, .tool {{
        padding: 16px !important;
        border-radius: 16px !important;
        min-height: auto !important;
    }}
    .tool {{
        border-radius: 16px 16px 0 0 !important;
    }}
    .result {{
        padding: 16px !important;
        border-radius: 14px !important;
    }}
    [data-testid="stSidebar"] {{
        width: 84vw !important;
    }}
}}
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# UI HELPERS & PDF DOWNLOAD HANDLER
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
        if st.button(
            f"Open {title} →",
            key=f"nav_btn_{target_page}",
            use_container_width=True,
        ):
            st.session_state.page = target_page
            st.rerun()


def show_result(text):
    st.markdown('<div class="result">', unsafe_allow_html=True)
    st.markdown(text)
    st.markdown("</div>", unsafe_allow_html=True)


def pdf_download(heading_or_input, answer, file_name="Health_Report.pdf", button_label="📄 Download Health Report", key=None):
    if create_pdf is None:
        st.warning("PDF module is unavailable. Place report.py in your project root directory.")
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


def generate_master_summary():
    summary_data = []
    if st.session_state.bmi:
        summary_data.append(f"### BMI Metric\n* Value: {st.session_state.bmi} ({st.session_state.bmi_category})")
    if st.session_state.command_center_result:
        summary_data.append(f"### AI Command Center Execution\n{st.session_state.command_center_result}")
    if st.session_state.symptom_result:
        summary_data.append(f"### Symptom Assessment\n{st.session_state.symptom_result}")
    if st.session_state.medical_report_result:
        summary_data.append(f"### Medical Report Analysis\n{st.session_state.medical_report_result}")
    if st.session_state.diet_result:
        summary_data.append(f"### Diet & Nutrition Plan\n{st.session_state.diet_result}")
    if st.session_state.exercise_result:
        summary_data.append(f"### Exercise & Workout Plan\n{st.session_state.exercise_result}")
    if st.session_state.sleep_result:
        summary_data.append(f"### Sleep Evaluation\n{st.session_state.sleep_result}")
    
    if not summary_data:
        return "No health metrics or assessment data recorded yet in this session. Use the available tools to generate outputs."
    
    return "\n\n---\n\n".join(summary_data)


# =========================================================
# SIDEBAR NAVIGATION & BRANDING
# =========================================================
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-logo-card">
            <div class="dna-logo-wrapper">
                <svg viewBox="0 0 100 100" width="70" height="70">
                    <path d="M30 15 Q50 35 70 15 Q50 50 30 85 Q50 65 70 85" fill="none" stroke="url(#dna-grad1)" stroke-width="6" stroke-linecap="round"/>
                    <path d="M70 15 Q50 35 30 15 Q50 50 70 85 Q50 65 30 85" fill="none" stroke="url(#dna-grad2)" stroke-width="6" stroke-linecap="round"/>
                    <line x1="38" y1="26" x2="62" y2="26" stroke="#00f2fe" stroke-width="3" opacity="0.8"/>
                    <line x1="44" y1="40" x2="56" y2="40" stroke="#ec4899" stroke-width="3" opacity="0.8"/>
                    <line x1="44" y1="60" x2="56" y2="60" stroke="#00f2fe" stroke-width="3" opacity="0.8"/>
                    <line x1="38" y1="74" x2="62" y2="74" stroke="#ec4899" stroke-width="3" opacity="0.8"/>
                    <defs>
                        <linearGradient id="dna-grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="#00f2fe" />
                            <stop offset="100%" stop-color="#ec4899" />
                        </linearGradient>
                        <linearGradient id="dna-grad2" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="#ec4899" />
                            <stop offset="100%" stop-color="#00f2fe" />
                        </linearGradient>
                    </defs>
                </svg>
            </div>
            <h3 style="margin-top: 10px; margin-bottom: 2px; font-size: 18px; color: #ffffff;">HealthMate AI</h3>
            <div class="status"><span class="dot"></span> SYSTEM ONLINE</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    nav_options = [
        "Home",
        "AI Command Center",
        "AI Symptom Tracker",
        "Medical Report Analyzer",
        "Diet & Nutrition",
        "Exercise & Fitness",
        "Sleep & Wellness",
        "Master Health Summary",
        "Settings",
    ]

    current_idx = nav_options.index(st.session_state.page) if st.session_state.page in nav_options else 0

    selected_page = st.radio(
        "Navigation",
        nav_options,
        index=current_idx,
        key="nav_radio",
    )

    if selected_page != st.session_state.page:
        st.session_state.page = selected_page
        st.rerun()


# =========================================================
# PAGE ROUTING
# =========================================================

# ---------------------------------------------------------
# 1. HOMEPAGE / DASHBOARD
# ---------------------------------------------------------
if st.session_state.page == "Home":
    hero(
        "AI-Powered Personal Health Suite",
        "Access instant symptom triaging, report analysis, personalized nutrition, and wellness plans.",
        "DASHBOARD OVERVIEW",
    )

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        card("⚖️", "Body Mass Index", st.session_state.bmi or "--", st.session_state.bmi_category or "Not calculated")
    with col_m2:
        card("💧", "Hydration Target", f"{st.session_state.water} L/day" if st.session_state.water else "--", "Daily fluid intake")
    with col_m3:
        card("🌙", "Sleep Target", f"{st.session_state.sleep} hrs" if st.session_state.sleep else "--", "Rest duration")
    with col_m4:
        card("🩺", "Triage Status", "Active" if st.session_state.symptom_result else "Ready", "Diagnostic engine")

    st.write("")
    st.write("")

    tool(
        "🤖",
        "AI Command Center",
        "Central operational hub for executing global AI commands, query dispatching, and custom health system instructions.",
        "AI Command Center",
    )

    st.write("")

    tool(
        "🩺",
        "AI Symptom Tracker",
        "Evaluate acute symptoms, receive triage urgency ratings, and access educational care guidance.",
        "AI Symptom Tracker",
    )

    st.write("")

    grid_col1, grid_col2 = st.columns(2)
    with grid_col1:
        tool(
            "📄",
            "Medical Report Analyzer",
            "Extract findings and medical terminology from lab tests and clinical summaries.",
            "Medical Report Analyzer",
        )
        st.write("")
        tool(
            "🥗",
            "Diet & Nutrition Planner",
            "Generate customized meal plans, macro breakdowns, and dietary strategies.",
            "Diet & Nutrition",
        )

    with grid_col2:
        tool(
            "🏋️‍♂️",
            "Exercise & Fitness Planner",
            "Design custom workout routines structured around your fitness level and goals.",
            "Exercise & Fitness",
        )
        st.write("")
        tool(
            "🌙",
            "Sleep & Wellness Advisor",
            "Optimize circadian cycles, improve sleep architecture, and recover faster.",
            "Sleep & Wellness",
        )


# ---------------------------------------------------------
# 2. AI COMMAND CENTER
# ---------------------------------------------------------
elif st.session_state.page == "AI Command Center":
    hero(
        "AI Command Center",
        "Unified operational hub to dispatch custom health queries, system prompts, and automated actions.",
        "PRIMARY HUB",
    )

    with st.container(border=True):
        st.subheader("Global AI Dispatcher")
        cmd_input = st.text_area(
            "Enter operational command or health query:",
            placeholder="e.g., Provide a comprehensive outline on managing hypertension through lifestyle and dietary changes.",
            height=140,
        )

        col_c1, col_c2 = st.columns([1, 4])
        with col_c1:
            run_cmd = st.button("Execute Command ⚡", use_container_width=True)

    if run_cmd and cmd_input.strip():
        with st.spinner("Executing command across clinical AI model..."):
            prompt = f"Act as an authoritative medical AI assistant. Execute the following operational request in detail:\n\n{cmd_input}"
            res = ask_ai(prompt)
            if res:
                st.session_state.command_center_result = res

    if st.session_state.command_center_result:
        show_result(st.session_state.command_center_result)
        pdf_download("AI Command Execution Report", st.session_state.command_center_result, file_name="AI_Command_Report.pdf", key="cmd_pdf")


# ---------------------------------------------------------
# 3. AI SYMPTOM TRACKER
# ---------------------------------------------------------
elif st.session_state.page == "AI Symptom Tracker":
    hero(
        "AI Symptom Tracker",
        "Input current symptoms for intelligent triage, severity categorization, and medical guidance.",
        "TRIAGE ENGINE",
    )

    with st.form("symptom_form"):
        symptoms = st.text_area(
            "Describe your symptoms in detail:",
            placeholder="e.g., Mild headache for 2 days, slight fever of 100°F, fatigue...",
            height=130,
        )
        c1, c2 = st.columns(2)
        with c1:
            duration = st.text_input("Duration of symptoms:", placeholder="e.g., 3 days")
        with c2:
            severity = st.select_slider("Severity Scale:", options=["Mild", "Moderate", "Severe", "Critical"])

        submitted = st.form_submit_button("Analyze Symptoms 🩺")

    if submitted and symptoms.strip():
        with st.spinner("Analyzing symptoms and evaluating triage guidance..."):
            prompt = f"""
            Perform a medical symptom triage assessment based on:
            - Symptoms: {symptoms}
            - Duration: {duration}
            - Severity Self-Assessment: {severity}

            Provide:
            1. Triage Level (Low / Moderate / High Urgency)
            2. Possible Causes (Educational only)
            3. Red Flag Symptoms to watch out for
            4. Next Steps & General Self-Care Measures
            """
            res = ask_ai(prompt)
            if res:
                st.session_state.symptom_result = res

    if st.session_state.symptom_result:
        show_result(st.session_state.symptom_result)
        pdf_download("Symptom Assessment Report", st.session_state.symptom_result, file_name="Symptom_Triage_Report.pdf", key="symp_pdf")


# ---------------------------------------------------------
# 4. MEDICAL REPORT ANALYZER
# ---------------------------------------------------------
elif st.session_state.page == "Medical Report Analyzer":
    hero(
        "Medical Report Analyzer",
        "Translate complex lab reports, blood tests, and clinical findings into clear explanations.",
        "LAB INTERPRETER",
    )

    report_text = st.text_area(
        "Paste lab test or diagnostic report text here:",
        height=180,
        placeholder="e.g., Hemoglobin: 11.2 g/dL, Total WBC: 11,500 /mcL, Fasting Glucose: 110 mg/dL...",
    )

    if st.button("Analyze Report 📄") and report_text.strip():
        with st.spinner("Analyzing laboratory metrics..."):
            prompt = f"Analyze the following medical report text and break down key terms, abnormal values, and recommendations:\n\n{report_text}"
            res = ask_ai(prompt)
            if res:
                st.session_state.medical_report_result = res

    if st.session_state.medical_report_result:
        show_result(st.session_state.medical_report_result)
        pdf_download("Medical Report Analysis", st.session_state.medical_report_result, file_name="Medical_Report_Analysis.pdf", key="med_pdf")


# ---------------------------------------------------------
# 5. DIET & NUTRITION
# ---------------------------------------------------------
elif st.session_state.page == "Diet & Nutrition":
    hero(
        "Diet & Nutrition Planner",
        "Personalized meal plans optimized for your daily caloric needs and fitness objectives.",
        "NUTRITION SUITE",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        goal = st.selectbox("Goal:", ["Weight Loss", "Muscle Gain", "Maintenance", "Keto", "Balanced"])
    with c2:
        diet_pref = st.selectbox("Preference:", ["Non-Vegetarian", "Vegetarian", "Vegan", "Eggetarian"])
    with c3:
        cals = st.number_input("Target Daily Calories:", min_value=1000, max_value=5000, value=2000, step=100)

    if st.button("Generate Meal Plan 🥗"):
        with st.spinner("Creating custom nutrition blueprint..."):
            prompt = f"Create a detailed 1-day meal plan (Breakfast, Lunch, Dinner, Snacks) for a target of {cals} calories. Goal: {goal}, Preference: {diet_pref}."
            res = ask_ai(prompt)
            if res:
                st.session_state.diet_result = res

    if st.session_state.diet_result:
        show_result(st.session_state.diet_result)
        pdf_download("Diet & Nutrition Plan", st.session_state.diet_result, file_name="Diet_Plan.pdf", key="diet_pdf")


# ---------------------------------------------------------
# 6. EXERCISE & FITNESS
# ---------------------------------------------------------
elif st.session_state.page == "Exercise & Fitness":
    hero(
        "Exercise & Fitness Planner",
        "Targeted workout routines tailored to your experience level and equipment availability.",
        "FITNESS SUITE",
    )

    c1, c2 = st.columns(2)
    with c1:
        level = st.selectbox("Fitness Level:", ["Beginner", "Intermediate", "Advanced"])
    with c2:
        equipment = st.selectbox("Equipment:", ["Full Gym", "Dumbbells Only", "Bodyweight / Home"])

    if st.button("Generate Workout Routine 🏋️‍♂️"):
        with st.spinner("Designing workout program..."):
            prompt = f"Create a structured workout routine for a {level} level individual with access to {equipment}."
            res = ask_ai(prompt)
            if res:
                st.session_state.exercise_result = res

    if st.session_state.exercise_result:
        show_result(st.session_state.exercise_result)
        pdf_download("Exercise Routine", st.session_state.exercise_result, file_name="Exercise_Routine.pdf", key="ex_pdf")


# ---------------------------------------------------------
# 7. SLEEP & WELLNESS
# ---------------------------------------------------------
elif st.session_state.page == "Sleep & Wellness":
    hero(
        "Sleep & Wellness Advisor",
        "Actionable recommendations to improve sleep quality and circadian balance.",
        "WELLNESS ENGINE",
    )

    sleep_hrs = st.slider("Average nightly sleep (hours):", 3.0, 12.0, 7.0, 0.5)
    quality = st.select_slider("Restfulness rating:", ["Poor", "Fair", "Good", "Excellent"])

    if st.button("Analyze Sleep Profile 🌙"):
        st.session_state.sleep = sleep_hrs
        with st.spinner("Evaluating sleep parameters..."):
            prompt = f"Provide tailored sleep optimization advice for someone sleeping {sleep_hrs} hours per night with a self-reported restfulness rating of '{quality}'."
            res = ask_ai(prompt)
            if res:
                st.session_state.sleep_result = res

    if st.session_state.sleep_result:
        show_result(st.session_state.sleep_result)
        pdf_download("Sleep Analysis", st.session_state.sleep_result, file_name="Sleep_Analysis.pdf", key="sleep_pdf")


# ---------------------------------------------------------
# 8. MASTER HEALTH SUMMARY
# ---------------------------------------------------------
elif st.session_state.page == "Master Health Summary":
    hero(
        "Master Health Summary",
        "Consolidated health record compiling all analyses generated during your session.",
        "EXECUTIVE REPORT",
    )

    summary_text = generate_master_summary()

    st.markdown('<div class="master-card">', unsafe_allow_html=True)
    st.markdown(summary_text)
    st.markdown("</div>", unsafe_allow_html=True)

    pdf_download("Master Health Summary Report", summary_text, file_name="Master_Health_Summary.pdf", button_label="📄 Download Full Master Health Report", key="master_pdf")


# ---------------------------------------------------------
# 9. SETTINGS
# ---------------------------------------------------------
elif st.session_state.page == "Settings":
    hero(
        "Application Settings",
        "Customize visual themes, animations, typography, and AI model backends.",
        "CONFIGURATION",
    )

    with st.container(border=True):
        st.subheader("🎨 Appearance & Styling")
        selected_accent = st.selectbox("Color Palette Theme:", list(accent_themes.keys()), index=list(accent_themes.keys()).index(st.session_state.accent))
        selected_scale = st.selectbox("Typography Scale:", list(font_sizes.keys()), index=list(font_sizes.keys()).index(st.session_state.font_scale))

        c1, c2 = st.columns(2)
        with c1:
            enable_anim = st.toggle("Enable Background Animations", value=st.session_state.enable_animations)
        with c2:
            anim_speed = st.selectbox("Animation Cycle Speed:", list(speed_map.keys()), index=list(speed_map.keys()).index(st.session_state.anim_speed))

    st.write("")

    with st.container(border=True):
        st.subheader("⚙️ AI Engine Configuration")
        model_index = VALID_MODELS.index(st.session_state.ai_model) if st.session_state.ai_model in VALID_MODELS else 0
        selected_model = st.selectbox("Gemini Model:", VALID_MODELS, index=model_index)

    if st.button("Save Settings 💾", type="primary"):
        st.session_state.accent = selected_accent
        st.session_state.font_scale = selected_scale
        st.session_state.enable_animations = enable_anim
        st.session_state.anim_speed = anim_speed
        st.session_state.ai_model = selected_model
        st.success("Settings saved successfully!")
        st.rerun()


# =========================================================
# FOOTER
# =========================================================
st.markdown(
    """
    <div class="footer">
        HealthMate AI • Educational & Triage Platform<br>
        <i>Disclaimer: This platform provides AI-generated assistance for educational purposes only and does not replace professional medical evaluation.</i>
    </div>
    """,
    unsafe_allow_html=True,
)
