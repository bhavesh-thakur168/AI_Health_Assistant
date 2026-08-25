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
    page_icon="🩺",
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


def ask_ai(prompt, model="gemini-2.5-flash"):
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
    background: linear-gradient(180deg, #00f2fe 0%, #c084fc 50%, #34d399 100%);
}}

.hero small {{
    color: var(--accent);
    font-family: 'Outfit', sans-serif;
    font-weight: 800;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    font-size: 11px;
    background: rgba(0, 242, 254, 0.18);
    padding: 6px 14px;
    border-radius: 20px;
    border: 1px solid rgba(0, 242, 254, 0.35);
    display: inline-block;
}}

.hero h1 {{
    margin: 14px 0 10px 0;
    font-size: clamp(30px, 4vw, 48px);
    line-height: 1.1;
    background: linear-gradient(120deg, #ffffff 40%, #00f2fe 75%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.hero p {{
    color: #e2e8f0;
    margin: 0;
    font-size: 16px;
    line-height: 1.6;
    max-width: 760px;
}}

.card {{
    background: linear-gradient(145deg, rgba(38, 52, 98, 0.85) 0%, rgba(27, 39, 75, 0.8) 100%);
    backdrop-filter: var(--blur);
    -webkit-backdrop-filter: var(--blur);
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 24px;
    min-height: 140px;
    box-shadow: var(--shadow);
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    display: flex;
    flex-direction: column;
    justify-content: center;
    position: relative;
}}

.card:hover {{
    transform: translateY(-5px);
    border-color: var(--accent);
    box-shadow: 0 16px 36px -6px rgba(0, 242, 254, 0.35);
    background: linear-gradient(145deg, rgba(46, 62, 116, 0.9) 0%, rgba(32, 45, 87, 0.85) 100%);
}}

.card .icon {{
    font-size: 42px !important;
    line-height: 1;
    filter: drop-shadow(0 0 12px rgba(0, 242, 254, 0.45));
    transition: transform 0.3s ease;
}}

.card:hover .icon {{
    transform: scale(1.12);
}}

.card .label {{
    color: #cbd5e1;
    font-size: 11.5px;
    margin-top: 14px;
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 1.5px;
}}

.card .value {{
    color: #ffffff;
    font-family: 'Outfit', sans-serif;
    font-size: 27px;
    font-weight: 800;
    margin-top: 4px;
    letter-spacing: -0.5px;
}}

.card .desc {{
    color: #cbd5e1;
    font-size: 13px;
    margin-top: 4px;
}}

.tool {{
    background: linear-gradient(145deg, rgba(38, 52, 98, 0.85) 0%, rgba(27, 39, 75, 0.8) 100%);
    backdrop-filter: var(--blur);
    -webkit-backdrop-filter: var(--blur);
    border: 1px solid var(--border);
    border-radius: 22px 22px 0 0;
    padding: 24px;
    min-height: 140px;
    box-shadow: var(--shadow);
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}}

.tool:hover {{
    border-color: rgba(0, 242, 254, 0.45);
    background: linear-gradient(145deg, rgba(46, 62, 116, 0.9) 0%, rgba(32, 45, 87, 0.85) 100%);
}}

.tool-static {{
    border-radius: 22px !important;
}}

.tool b {{
    font-family: 'Outfit', sans-serif;
    color: #ffffff;
    font-size: 18.5px;
    display: block;
    margin-top: 12px;
    letter-spacing: -0.3px;
}}

.tool p {{
    color: #cbd5e1;
    font-size: 13.5px;
    line-height: 1.5;
    margin-top: 6px;
    margin-bottom: 0;
}}

.tool-icon {{
    font-size: 44px !important;
    display: inline-block;
    filter: drop-shadow(0 0 12px rgba(0, 242, 254, 0.45));
    transition: transform 0.3s ease;
}}

.tool:hover .tool-icon {{
    transform: scale(1.12);
}}

.status {{
    display: inline-flex;
    gap: 8px;
    align-items: center;
    color: var(--accent);
    background: rgba(0, 242, 254, 0.16);
    border: 1px solid rgba(0, 242, 254, 0.4);
    padding: 6px 14px;
    border-radius: 30px;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
    box-shadow: 0 0 14px rgba(0, 242, 254, 0.25);
}}

.dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 10px var(--accent);
    animation: pulseGlow 1.8s infinite;
}}

@keyframes pulseGlow {{
    0% {{ transform: scale(0.9); box-shadow: 0 0 0 0 rgba(0, 242, 254, 0.7); }}
    70% {{ transform: scale(1.15); box-shadow: 0 0 0 7px rgba(0, 242, 254, 0); }}
    100% {{ transform: scale(0.9); box-shadow: 0 0 0 0 rgba(0, 242, 254, 0); }}
}}

.result {{
    background: linear-gradient(135deg, rgba(34, 48, 92, 0.9) 0%, rgba(42, 58, 108, 0.85) 100%);
    backdrop-filter: var(--blur);
    -webkit-backdrop-filter: var(--blur);
    border: 1px solid var(--border);
    border-left: 5px solid var(--accent);
    border-radius: 20px;
    padding: 24px;
    box-shadow: var(--shadow);
    margin-top: 20px;
    line-height: 1.7;
    color: #ffffff;
}}

.stButton > button, div[data-testid="stDownloadButton"] > button {{
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    background: linear-gradient(135deg, rgba(46, 62, 116, 0.95) 0%, rgba(34, 48, 92, 0.95) 100%);
    color: #ffffff;
    font-weight: 600;
    padding: 11px 22px;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    width: 100%;
}}

.stButton > button:hover, div[data-testid="stDownloadButton"] > button:hover {{
    border-color: var(--accent);
    color: var(--accent);
    background: linear-gradient(135deg, rgba(58, 78, 142, 1) 0%, rgba(42, 60, 114, 1) 100%);
    box-shadow: 0 6px 20px rgba(0, 242, 254, 0.35);
    transform: translateY(-2px);
}}

div[data-testid="stColumn"] .stButton > button {{
    border-top-left-radius: 0px;
    border-top-right-radius: 0px;
    border-bottom-left-radius: 20px;
    border-bottom-right-radius: 20px;
    margin-top: -1px;
}}

.footer {{
    text-align: center;
    color: #cbd5e1;
    font-size: 13px;
    padding: 36px 0 16px;
    border-top: 1px solid rgba(255, 255, 255, 0.15);
    margin-top: 50px;
    line-height: 1.7;
}}
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
            f"Open {title}",
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
    """Reusable PDF generator downloader across all tools."""
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

with st.sidebar:
    st.markdown(
        f"""
        <div style="text-align:center; padding:14px 0 20px;">
            <div style="font-size:50px; line-height:1; filter: drop-shadow(0 0 14px rgba(0,242,254,0.55));">🩺</div>
            <div style="font-family:'Outfit'; font-size:24px; font-weight:800; color:{accent}; margin-top:8px; letter-spacing:-0.5px;">
                HealthMate AI
            </div>
            <div style="font-size:10px; color:{muted}; letter-spacing:2px; margin-top:2px; font-weight:700;">
                HEALTH INTELLIGENCE
            </div>
            <div style="margin-top:14px;">
                <span class="status">
                    <span class="dot"></span>
                    SYSTEM ONLINE
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    labels = [f"{page_icons[p]}  {p}" for p in pages]
    current_label = f"{page_icons[st.session_state.page]}  {st.session_state.page}"
    current_index = labels.index(current_label) if current_label in labels else 0

    selected_label = st.radio(
        "Navigation",
        labels,
        index=current_index,
        label_visibility="collapsed",
    )

    st.session_state.page = selected_label.split("  ", 1)[1]


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

    st.markdown("### Explore HealthMate Features", unsafe_allow_html=True)

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

    st.markdown("### System Status", unsafe_allow_html=True)
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
        with st.chat_message("user"):
            st.write(symptoms)

        with st.chat_message("assistant"):
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
                st.write(answer)
                pdf_download(
                    symptoms,
                    answer,
                    file_name="Symptom_Report.pdf",
                    button_label="📄 Download Symptom Report",
                    key="pdf_symptoms",
                )

        st.info(
            "ℹ️ This response is educational and should not be treated as a medical diagnosis."
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
                st.success("Information ready")
                show_result(answer)
                pdf_download(
                    f"Medicine Information: {medicine}",
                    answer,
                    file_name=f"Medicine_Info_{medicine}.pdf",
                    button_label="📄 Download Medicine Guide",
                    key="pdf_med",
                )

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
            st.success("Diet plan ready")
            show_result(answer)
            pdf_download(
                f"Diet Plan ({goal} | Age: {age}, Gender: {gender})",
                answer,
                file_name=f"Diet_Plan_{goal.replace(' ', '_')}.pdf",
                button_label="📄 Download Diet Plan",
                key="pdf_diet",
            )


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
            st.success("Exercise plan ready")
            show_result(answer)
            pdf_download(
                f"Exercise Plan ({fitness} | {goal} | Age: {age})",
                answer,
                file_name=f"Exercise_Plan_{goal.replace(' ', '_')}.pdf",
                button_label="📄 Download Workout Plan",
                key="pdf_exercise",
            )


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
                st.success("Estimate ready")
                show_result(answer)
                pdf_download(
                    f"Calorie & Nutrition Breakdown: {food}",
                    answer,
                    file_name="Calorie_Report.pdf",
                    button_label="📄 Download Nutrition Breakdown",
                    key="pdf_calorie",
                )

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
        st.session_state.sleep = sleep_hours
    with c3:
        lifestyle = st.selectbox(
            "Lifestyle",
            ["Student", "Working Professional", "Athlete", "Senior Citizen"],
        )

    if st.button("😴 Get Sleep Advice"):
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
            st.success("Sleep advice ready")
            show_result(answer)
            pdf_download(
                f"Sleep Guidance (Age: {age}, Hours: {sleep_hours}, Profile: {lifestyle})",
                answer,
                file_name="Sleep_Guidance.pdf",
                button_label="📄 Download Sleep Guidance",
                key="pdf_sleep",
            )


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
            if client is None:
                st.error("Gemini API key is not configured.")
            else:
                with st.spinner("Analyzing report image..."):
                    try:
                        bytes_data = uploaded_file.getvalue()
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=[
                                types.Part.from_bytes(
                                    data=bytes_data,
                                    mime_type=uploaded_file.type,
                                ),
                                "Analyze this medical report image for educational purposes. Explain key findings, medical terms, and reference values simply. Do not diagnose.",
                            ],
                        )
                        answer = response.text
                        if answer:
                            st.success("Analysis Complete")
                            show_result(answer)
                            pdf_download(
                                "Medical Report Analysis",
                                answer,
                                file_name="Report_Analysis.pdf",
                                button_label="📄 Download Report Analysis",
                                key="pdf_report",
                            )
                    except Exception as exc:
                        st.error(f"Analysis failed: {exc}")


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

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_query = st.chat_input("Ask any health & wellness question...")

    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.write(user_query)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                resp = ask_ai(
                    f"User prompt: {user_query}\nProvide educational health guidance without giving a medical diagnosis or prescription."
                )
                if resp:
                    st.write(resp)
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": resp}
                    )


# =========================================================
# PAGE: SETTINGS
# =========================================================
elif page == "Settings":
    hero(
        "Settings",
        "Customize theme settings and workspace options.",
        "PREFERENCES",
    )

    selected_accent = st.selectbox(
        "Accent Color Theme",
        list(accent_colors.keys()),
        index=list(accent_colors.keys()).index(st.session_state.accent),
    )

    if st.button("Save Settings"):
        st.session_state.accent = selected_accent
        st.success("Settings updated successfully!")
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
