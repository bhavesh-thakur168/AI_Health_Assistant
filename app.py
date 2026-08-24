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
    page_title="HealthMate AI • Precision Health Intelligence",
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
# THEME CONFIGURATION
# =========================================================
accent_colors = {
    "Cyan": "#00f2fe",
    "Blue": "#3b82f6",
    "Purple": "#a855f7",
    "Green": "#10b981",
}

accent = accent_colors.get(st.session_state.accent, "#00f2fe")
accent_glow = f"{accent}33"

# Dark Theme Defaults
background = "#05070e"
surface = "rgba(13, 19, 33, 0.7)"
surface2 = "rgba(22, 31, 52, 0.65)"
text = "#f8fafc"
muted = "#94a3b8"
border = "rgba(255, 255, 255, 0.08)"
card_shadow = "0 10px 30px -10px rgba(0, 0, 0, 0.7)"
glass_blur = "blur(16px)"


# =========================================================
# ADVANCED STYLESHEET & HEAVY ANIMATIONS
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
    --accent-glow: {accent_glow};
    --shadow: {card_shadow};
    --blur: {glass_blur};
}}

/* Global resets & Modern Fonts */
.stApp {{
    background-color: var(--bg);
    background-image: 
        radial-gradient(at 0% 0%, rgba(0, 242, 254, 0.06) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(168, 85, 247, 0.05) 0px, transparent 50%),
        linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 40px 40px, 40px 40px;
    color: var(--text);
    font-family: 'Plus Jakarta Sans', sans-serif;
    animation: fadeInApp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}}

@keyframes fadeInApp {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

/* Typography */
h1, h2, h3, h4, h5, h6 {{
    font-family: 'Outfit', sans-serif !important;
    color: var(--text) !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
}}

/* Sidebar Styling */
[data-testid="stSidebar"] {{
    background-color: rgba(9, 13, 24, 0.85);
    backdrop-filter: var(--blur);
    -webkit-backdrop-filter: var(--blur);
    border-right: 1px solid var(--border);
}}

[data-testid="stSidebar"] div[data-testid="stRadio"] label {{
    border-radius: 14px;
    padding: 12px 16px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    border: 1px solid transparent;
    font-weight: 500;
}}

[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {{
    background-color: var(--surface2);
    border-color: rgba(255, 255, 255, 0.15);
    transform: translateX(6px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}}

/* Hero Section */
.hero {{
    padding: 44px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 28px;
    background: linear-gradient(135deg, rgba(17, 24, 39, 0.85) 0%, rgba(15, 23, 42, 0.6) 100%);
    backdrop-filter: var(--blur);
    -webkit-backdrop-filter: var(--blur);
    box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.7);
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
    animation: heroEntrance 0.9s cubic-bezier(0.16, 1, 0.3, 1);
}}

@keyframes heroEntrance {{
    from {{ opacity: 0; transform: scale(0.97) translateY(12px); }}
    to {{ opacity: 1; transform: scale(1) translateY(0); }}
}}

.hero::after {{
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, var(--accent-glow) 0%, transparent 60%);
    opacity: 0.4;
    animation: rotateGlow 12s linear infinite;
    pointer-events: none;
}}

@keyframes rotateGlow {{
    0% {{ transform: rotate(0deg); }}
    100% {{ transform: rotate(360deg); }}
}}

.hero small {{
    color: var(--accent);
    font-family: 'Outfit', sans-serif;
    font-weight: 800;
    letter-spacing: 3px;
    text-transform: uppercase;
    font-size: 11px;
    display: inline-block;
    padding: 4px 10px;
    background: rgba(255, 255, 255, 0.04);
    border-radius: 6px;
    border: 1px solid rgba(255, 255, 255, 0.06);
}}

.hero h1 {{
    margin: 14px 0 10px 0;
    font-size: clamp(34px, 4.5vw, 54px);
    line-height: 1.05;
    background: linear-gradient(120deg, #ffffff 40%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 35px var(--accent-glow);
}}

.hero p {{
    color: var(--muted);
    margin: 0;
    font-size: 16px;
    max-width: 680px;
    line-height: 1.6;
}}

/* Interactive Cards */
.card {{
    background: var(--surface);
    backdrop-filter: var(--blur);
    -webkit-backdrop-filter: var(--blur);
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 24px;
    min-height: 130px;
    box-shadow: var(--shadow);
    transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    display: flex;
    flex-direction: column;
    justify-content: center;
    position: relative;
    overflow: hidden;
}}

.card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
}}

.card:hover {{
    transform: translateY(-6px) scale(1.02);
    border-color: var(--accent);
    box-shadow: 0 16px 35px -8px var(--accent-glow);
}}

.card .icon {{
    font-size: 32px;
    line-height: 1;
    filter: drop-shadow(0 0 8px var(--accent-glow));
}}

.card .label {{
    color: var(--muted);
    font-size: 11px;
    margin-top: 14px;
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 1.5px;
}}

.card .value {{
    color: var(--text);
    font-size: 28px;
    font-family: 'Outfit', sans-serif;
    font-weight: 800;
    margin-top: 4px;
    letter-spacing: -0.5px;
}}

.card .desc {{
    color: var(--muted);
    font-size: 13px;
    margin-top: 4px;
}}

/* Tool Module Cards */
.tool {{
    background: var(--surface);
    backdrop-filter: var(--blur);
    -webkit-backdrop-filter: var(--blur);
    border: 1px solid var(--border);
    border-radius: 22px 22px 0 0;
    padding: 24px;
    min-height: 130px;
    box-shadow: var(--shadow);
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}}

.tool:hover {{
    border-color: rgba(255, 255, 255, 0.2);
    background: var(--surface2);
}}

.tool-static {{
    border-radius: 22px !important;
}}

.tool b {{
    font-family: 'Outfit', sans-serif;
    color: var(--text);
    font-size: 18px;
    display: block;
    margin-top: 12px;
    letter-spacing: -0.3px;
}}

.tool p {{
    color: var(--muted);
    font-size: 13px;
    line-height: 1.5;
    margin-top: 8px;
    margin-bottom: 0;
}}

/* Animated Radar Pulse Status */
.status {{
    display: inline-flex;
    gap: 10px;
    align-items: center;
    color: var(--accent);
    background: rgba(0, 242, 254, 0.06);
    border: 1px solid rgba(0, 242, 254, 0.25);
    padding: 8px 18px;
    border-radius: 40px;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
    box-shadow: 0 0 15px var(--accent-glow);
}}

.dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 12px var(--accent);
    animation: pulseRing 1.8s infinite;
}}

@keyframes pulseRing {{
    0% {{ transform: scale(0.9); box-shadow: 0 0 0 0 var(--accent); }}
    70% {{ transform: scale(1.1); box-shadow: 0 0 0 6px rgba(0, 242, 254, 0); }}
    100% {{ transform: scale(0.9); box-shadow: 0 0 0 0 rgba(0, 242, 254, 0); }}
}}

/* Results & Buttons */
.result {{
    background: var(--surface);
    backdrop-filter: var(--blur);
    -webkit-backdrop-filter: var(--blur);
    border: 1px solid var(--border);
    border-left: 5px solid var(--accent);
    border-radius: 20px;
    padding: 28px;
    box-shadow: var(--shadow);
    margin-top: 22px;
    line-height: 1.7;
    animation: slideUpFade 0.5s ease-out;
}}

@keyframes slideUpFade {{
    from {{ opacity: 0; transform: translateY(12px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

.stButton > button {{
    border-radius: 14px;
    border: 1px solid var(--border);
    background: linear-gradient(135deg, var(--surface2) 0%, rgba(17, 24, 39, 0.8) 100%);
    color: var(--text);
    font-weight: 600;
    padding: 12px 24px;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    width: 100%;
    letter-spacing: 0.2px;
}}

.stButton > button:hover {{
    border-color: var(--accent);
    color: var(--accent);
    box-shadow: 0 6px 25px -4px var(--accent-glow);
    transform: translateY(-3px);
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
    color: var(--muted);
    font-size: 13px;
    padding: 45px 0 20px;
    border-top: 1px solid var(--border);
    margin-top: 60px;
    line-height: 1.8;
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
            <div style="font-size:32px;">{icon}</div>
            <div><b>{title}</b></div>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if target_page:
        if st.button(
            f"Launch {title} →",
            key=f"nav_btn_{target_page}",
            use_container_width=True,
        ):
            st.session_state.page = target_page
            st.rerun()


def show_result(text):
    st.markdown('<div class="result">', unsafe_allow_html=True)
    st.markdown(text)
    st.markdown("</div>", unsafe_allow_html=True)


def pdf_download(symptoms, answer):
    if create_pdf is None:
        st.warning("PDF module is unavailable. Keep your report.py in the project folder.")
        return

    try:
        path = create_pdf(symptoms, answer)
        with open(path, "rb") as f:
            data = f.read()

        st.download_button(
            "📄 Download Clinical Report",
            data=data,
            file_name="Health_Report.pdf",
            mime="application/pdf",
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
    "Home": "⌂",
    "AI Symptom Checker": "🤖",
    "Medicine Info": "💊",
    "BMI Calculator": "⚖️",
    "Water Intake": "💧",
    "Diet Planner": "🍎",
    "Exercise Planner": "🏃",
    "Calorie Calculator": "🔥",
    "Sleep Recommendation": "😴",
    "Medical Report Analyzer": "📷",
    "Health Dashboard": "📊",
    "AI Command Center": "🧠",
    "Settings": "⚙️",
    "About": "ⓘ",
}

with st.sidebar:
    st.markdown(
        f"""
        <div style="text-align:center; padding:16px 0 24px;">
            <div style="font-size:50px; line-height:1; filter: drop-shadow(0 0 10px {accent_glow});">🧬</div>
            <div style="font-family:'Outfit'; font-size:26px; font-weight:800; color:{accent}; margin-top:10px; letter-spacing:-0.5px;">
                HealthMate AI
            </div>
            <div style="font-size:10px; color:{muted}; letter-spacing:2px; margin-top:3px; font-weight:700;">
                PRECISION INTELLIGENCE
            </div>
            <div style="margin-top:18px;">
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

    st.markdown("---")
    st.caption("⚡ Precision Engine • Fast Neural Mode")

    if client:
        st.success("Gemini: Online & Connected")
    else:
        st.warning("Gemini: Key Required")


page = st.session_state.page


# =========================================================
# PAGE: HOME
# =========================================================
if page == "Home":
    hero(
        "AI-Powered Health Intelligence",
        "Your real-time health companion for general wellness, diagnostic exploration, smart nutrition planning, and advanced medical analysis.",
        "HEALTH PLATFORM",
    )

    st.markdown("### ⚡ Diagnostic & Wellness Suite", unsafe_allow_html=True)

    # Row 1
    r1 = st.columns(3)
    with r1[0]:
        tool(
            "🤖",
            "AI Symptom Checker",
            "Describe symptoms for educational triage and insights.",
            target_page="AI Symptom Checker",
        )
    with r1[1]:
        tool(
            "💊",
            "Medicine Info",
            "Understand dosages, interactions, and precautions.",
            target_page="Medicine Info",
        )
    with r1[2]:
        tool(
            "📊",
            "Health Dashboard",
            "Review session calculations and personal health telemetry.",
            target_page="Health Dashboard",
        )

    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

    # Row 2
    r2 = st.columns(3)
    with r2[0]:
        tool(
            "⚖️",
            "BMI Calculator",
            "Compute Body Mass Index with metabolic insights.",
            target_page="BMI Calculator",
        )
    with r2[1]:
        tool(
            "💧",
            "Water Intake",
            "Hydration targets calibrated to body composition.",
            target_page="Water Intake",
        )
    with r2[2]:
        tool(
            "🍎",
            "Diet Planner",
            "Custom-calibrated nutrition plans tailored to your goals.",
            target_page="Diet Planner",
        )

    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

    # Row 3
    r3 = st.columns(3)
    with r3[0]:
        tool(
            "🏃",
            "Exercise Planner",
            "Personalized physical conditioning routines.",
            target_page="Exercise Planner",
        )
    with r3[1]:
        tool(
            "🔥",
            "Calorie Calculator",
            "Deconstruct macro & micronutrients instantly.",
            target_page="Calorie Calculator",
        )
    with r3[2]:
        tool(
            "😴",
            "Sleep Recommendation",
            "Optimize circadian recovery and sleep architecture.",
            target_page="Sleep Recommendation",
        )

    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

    # Row 4
    r4 = st.columns(3)
    with r4[0]:
        tool(
            "📷",
            "Medical Report Analyzer",
            "Upload lab reports and scans for automated breakdown.",
            target_page="Medical Report Analyzer",
        )
    with r4[1]:
        tool(
            "🧠",
            "AI Command Center",
            "Direct conversation with conversational health intelligence.",
            target_page="AI Command Center",
        )

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("### 🖥️ Real-time Telemetry", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        card("🤖", "Neural Core", "Gemini 2.5", "High-speed reasoning")
    with c2:
        card("🧰", "Diagnostic Tools", "12 Active", "Full suite ready")
    with c3:
        card("📄", "Export Engine", "PDF 2.0", "Clinical-grade format")
    with c4:
        card("⚡", "Response Latency", "< 800ms", "Optimized inference")

    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        "⚠️ **Disclaimer:** HealthMate AI provides general wellness and educational analysis. It does not provide medical diagnoses or replace clinical examinations."
    )


# =========================================================
# PAGE: AI SYMPTOM CHECKER
# =========================================================
elif page == "AI Symptom Checker":
    hero(
        "Clinical Symptom Triage",
        "Describe your symptoms in detail for structured educational analysis and critical triage flags.",
        "TRIAGE AI",
    )

    symptoms = st.chat_input(
        "Describe what you're experiencing (e.g. mild fever for 2 days, dry cough)...",
        key="symptoms_input",
    )

    if symptoms:
        with st.chat_message("user"):
            st.write(symptoms)

        with st.chat_message("assistant"):
            with st.spinner("Processing clinical ontology..."):
                answer = ask_ai(
                    f"""
You are HealthMate AI, an advanced clinical education assistant.

User Symptoms:
{symptoms}

Provide a structured, easy-to-read educational summary:
1. Potential General Explanations (Educational only, non-diagnostic)
2. Self-Care & Hydration Considerations
3. Red Flag Symptoms (When to seek urgent or emergency medical care)
4. Questions to Discuss with a Doctor

Keep your tone professional, empathetic, and clear.
"""
                )

            if answer:
                st.write(answer)
                pdf_download(symptoms, answer)

        st.info("⚠️ Educational triage summary. Not a formal diagnostic opinion.")


# =========================================================
# PAGE: MEDICINE INFO
# =========================================================
elif page == "Medicine Info":
    hero(
        "Pharmacology Database",
        "Search pharmaceutical compounds for mechanism of action, precautions, and contraindications.",
        "PHARMACORE",
    )

    medicine = st.text_input(
        "Compound or Brand Name",
        placeholder="Example: Metformin, Ibuprofen, Amoxicillin",
    )

    if st.button("💊 Query Pharmacology Database"):
        if not medicine.strip():
            st.warning("Please specify a medication name.")
        else:
            with st.spinner("Accessing pharmacology database..."):
                answer = ask_ai(
                    f"""
Provide educational pharmacology details for:

Medicine: {medicine}

Include:
- Primary Clinical Uses
- General Mechanism of Action (Simplified)
- Common & Rare Side Effects
- Critical Contraindications & Interactions
- Physician Consultation Recommendations

Do not specify dosages or personalize therapy.
"""
                )

            if answer:
                st.success("Pharmacology summary generated")
                show_result(answer)

            st.info("⚠️ Consult a certified physician or pharmacist before starting or adjusting medication.")


# =========================================================
# PAGE: BMI CALCULATOR
# =========================================================
elif page == "BMI Calculator":
    hero(
        "Body Composition Index",
        "Calculate your Body Mass Index (BMI) and metabolic baseline.",
        "METRIC ENGINE",
    )

    c1, c2 = st.columns(2)
    with c1:
        height = st.number_input(
            "Height (cm)",
            min_value=50.0,
            max_value=250.0,
            value=170.0,
            step=0.5,
        )
    with c2:
        weight = st.number_input(
            "Weight (kg)",
            min_value=10.0,
            max_value=300.0,
            value=65.0,
            step=0.5,
        )

    if st.button("⚖️ Calculate Metrics"):
        height_m = height / 100
        bmi = weight / (height_m * height_m)
        st.session_state.bmi = bmi

        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Optimal Weight"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obese Range"

        st.markdown("<br>", unsafe_allow_html=True)
        a, b = st.columns(2)
        with a:
            card("⚖️", "Calculated BMI", f"{bmi:.2f}", "kg/m²")
        with b:
            card("🩺", "Classification", category, "WHO standard range")

        st.markdown("<br>", unsafe_allow_html=True)
        st.info("BMI does not account for muscle-to-fat distribution or athletic conditioning.")


# =========================================================
# PAGE: WATER INTAKE
# =========================================================
elif page == "Water Intake":
    hero(
        "Hydration Architecture",
        "Calculate target daily fluid intake adjusted for body mass.",
        "CELLULAR HEALTH",
    )

    weight = st.number_input(
        "Weight (kg)",
        min_value=10.0,
        max_value=250.0,
        value=60.0,
        step=0.5,
    )

    if st.button("💧 Compute Hydration Target"):
        water_ml = weight * 35
        litres = water_ml / 1000
        st.session_state.water = litres

        st.markdown("<br>", unsafe_allow_html=True)
        a, b = st.columns(2)
        with a:
            card("💧", "Daily Target", f"{litres:.2f} L", "Recommended hydration volume")
        with b:
            card("🫗", "Volume", f"{water_ml:.0f} mL", "Equivalent total liquid")

        st.markdown("<br>", unsafe_allow_html=True)
        st.info("Adjust upward by 500-1000 mL for intense physical training or hot climates.")


# =========================================================
# PAGE: DIET PLANNER
# =========================================================
elif page == "Diet Planner":
    hero(
        "Precision Nutrition Plan",
        "Generate macronutrient-balanced nutritional frameworks tailored to your profile.",
        "NUTRITION AI",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        age = st.number_input("Age", 1, 100, 22)
    with c2:
        gender = st.selectbox("Biological Sex", ["Male", "Female", "Prefer not to say"])
    with c3:
        goal = st.selectbox(
            "Primary Objective",
            ["Weight Loss & Fat Reduction", "Lean Muscle Hypertrophy", "Cardiovascular & Metabolic Health"],
        )

    if st.button("🍎 Generate Nutrition Regimen"):
        with st.spinner("Formulating nutritional strategy..."):
            answer = ask_ai(
                f"""
Create a structured one-day balanced nutrition plan.

Demographics:
- Age: {age}
- Biological Sex: {gender}
- Primary Objective: {goal}

Structure output with:
1. Macronutrient Focus
2. Breakfast Strategy
3. Lunch Composition
4. Evening Snack / Energy Stabilization
5. Dinner Regimen
6. Practical Micronutrient Tips
"""
            )

        if answer:
            st.success("Nutrition blueprint ready")
            show_result(answer)


# =========================================================
# PAGE: EXERCISE PLANNER
# =========================================================
elif page == "Exercise Planner":
    hero(
        "Biomechanics & Conditioning",
        "Structured physical training programs matched to your current capacity.",
        "FITNESS ENGINE",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        age = st.number_input("Age", 5, 100, 22)
    with c2:
        fitness = st.selectbox(
            "Current Fitness Tier",
            ["Beginner (Foundation)", "Intermediate (Progressive)", "Advanced (High Performance)"],
        )
    with c3:
        goal = st.selectbox(
            "Training Focus",
            ["Fat Oxidation & Mobility", "Hypertrophy & Strength", "Aerobic Conditioning"],
        )

    if st.button("🏃 Build Workout Program"):
        with st.spinner("Designing regimen..."):
            answer = ask_ai(
                f"""
Design a structured one-day workout session.

Profile:
- Age: {age}
- Tier: {fitness}
- Focus: {goal}

Include:
- Dynamic Mobility Warm-up (5-8 min)
- Core Resistance / Cardiovascular Blocks (Sets, Reps, RPE)
- Cool-down & Static Decompression
- Injury Prevention & Form Cues
"""
            )

        if answer:
            st.success("Training routine active")
            show_result(answer)


# =========================================================
# PAGE: CALORIE CALCULATOR
# =========================================================
elif page == "Calorie Calculator":
    hero(
        "Macronutrient Analytics",
        "Deconstruct complex meal logs into estimated calories, proteins, lipids, and carbohydrates.",
        "METABOLIC AI",
    )

    food = st.text_area(
        "Log Meals & Ingredients",
        placeholder="Example: 2 whole wheat rotis, 1 cup yellow dal, 150g grilled paneer, cucumber salad with olive oil",
        height=130,
    )

    if st.button("🔥 Run Nutritional Decomposition"):
        if not food.strip():
            st.warning("Please enter your meal log.")
        else:
            with st.spinner("Decomposing food matrix..."):
                answer = ask_ai(
                    f"""
Deconstruct this meal intake into estimated macronutrients:

Logged Meals:
{food}

Provide:
- Estimated Total Caloric Value (kcal)
- Macronutrient Breakdown (Protein, Carbs, Fats in grams)
- Glycemic & Satiety Profile
- Optimization Suggestions
"""
                )

            if answer:
                st.success("Analysis complete")
                show_result(answer)

            st.info("⚠️ Portion estimates are approximate and may vary.")


# =========================================================
# PAGE: SLEEP RECOMMENDATION
# =========================================================
elif page == "Sleep Recommendation":
    hero(
        "Circadian Optimization",
        "Evaluate sleep architecture and circadian rhythm consistency.",
        "RECOVERY PROTOCOL",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        age = st.number_input("Age", 1, 100, 22)
    with c2:
        sleep_hours = st.slider(
            "Average Nightly Sleep (Hours)",
            1,
            12,
            7,
        )
        st.session_state.sleep = sleep_hours
    with c3:
        lifestyle = st.selectbox(
            "Occupational Profile",
            ["High Cognitive Load / Student", "Desk-Bound Professional", "Active Athlete", "Shift Worker"],
        )

    if st.button("😴 Evaluate Sleep Profile"):
        with st.spinner("Analyzing circadian parameters..."):
            answer = ask_ai(
                f"""
Evaluate the sleep profile and provide actionable recovery protocols:

- Age: {age}
- Duration: {sleep_hours} hours
- Profile: {lifestyle}

Include:
- Sleep Debt & Adequacy Assessment
- Sleep Hygiene & Temperature Optimization Protocols
- Screen & Melatonin Management
- Next Steps if Insomnia Persists
"""
            )

        if answer:
            st.success("Circadian recommendations generated")
            show_result(answer)


# =========================================================
# PAGE: MEDICAL REPORT ANALYZER
# =========================================================
elif page == "Medical Report Analyzer":
    hero(
        "Vision Report Diagnostics",
        "Upload lab reports, prescriptions, or imaging for educational breakdown.",
        "COMPUTER VISION",
    )

    st.warning(
        "⚠️ Diagnostic tools are for educational comprehension only. Have all results confirmed by a licensed clinician."
    )

    uploaded_file = st.file_uploader(
        "Upload Document / Lab Report (JPG, PNG)",
        type=["png", "jpg", "jpeg"],
    )

    if uploaded_file is not None:
        st.image(
            uploaded_file,
            caption="Report Upload Preview",
            use_container_width=True,
        )

        if st.button("🔍 Run Neural Vision Analysis"):
            if client is None:
                st.error("Gemini API key is not configured.")
            else:
                with st.spinner("Parsing medical imagery and values..."):
                    try:
                        image_part = types.Part.from_bytes(
                            data=uploaded_file.getvalue(),
                            mime_type=uploaded_file.type,
                        )

                        prompt_text = """
Explain this medical document or diagnostic image clearly and educationally.

1. Summary of Identified Test Parameters
2. Normal Range vs. Indicated Values (General context)
3. Plain-Language Translation of Complex Terminology
4. Key Questions to Ask the Ordering Physician

Do not offer definitive diagnoses or prescribe medications.
"""

                        max_retries = 3
                        response = None

                        for attempt in range(max_retries):
                            try:
                                response = client.models.generate_content(
                                    model="gemini-2.5-flash",
                                    contents=[prompt_text, image_part],
                                )
                                break
                            except Exception as err:
                                err_msg = str(err)
                                if ("503" in err_msg or "UNAVAILABLE" in err_msg) and attempt < max_retries - 1:
                                    time.sleep(2 * (attempt + 1))
                                    continue
                                raise err

                        if response and response.text:
                            st.success("Vision extraction complete")
                            show_result(response.text)

                    except Exception as exc:
                        if "503" in str(exc) or "UNAVAILABLE" in str(exc):
                            st.error("Gemini Vision service is temporarily busy. Please retry in a few seconds.")
                        else:
                            st.error(f"Image analysis failed: {exc}")


# =========================================================
# PAGE: HEALTH DASHBOARD
# =========================================================
elif page == "Health Dashboard":
    hero(
        "Biometric Telemetry Hub",
        "Aggregate status of all evaluations recorded during your active session.",
        "TELEMETRY CENTER",
    )

    bmi_value = (
        f"{st.session_state.bmi:.2f}"
        if st.session_state.bmi is not None
        else "—"
    )

    water_value = (
        f"{st.session_state.water:.2f} L"
        if st.session_state.water is not None
        else "—"
    )

    sleep_value = (
        f"{st.session_state.sleep} h"
        if st.session_state.sleep is not None
        else "—"
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        card("⚖️", "Session BMI", bmi_value, "Calculated score")
    with c2:
        card("💧", "Hydration", water_value, "Daily requirement")
    with c3:
        card("😴", "Sleep Log", sleep_value, "Target duration")
    with c4:
        card("🤖", "Neural Engine", "Connected" if client else "Offline", "Real-time AI core")

    st.markdown("<br>### ⚡ Diagnostic Module Registry", unsafe_allow_html=True)

    modules = [
        ("🤖", "AI Symptom Checker"),
        ("💊", "Medicine Info"),
        ("⚖️", "BMI Calculator"),
        ("💧", "Water Intake"),
        ("🍎", "Diet Planner"),
        ("🏃", "Exercise Planner"),
        ("🔥", "Calorie Calculator"),
        ("😴", "Sleep Recommendation"),
        ("📷", "Medical Report Analyzer"),
    ]

    for i in range(0, len(modules), 3):
        cols = st.columns(3)
        for col, item in zip(cols, modules[i : i + 3]):
            with col:
                card(item[0], item[1], "ACTIVE", "Telemetry Online")
        st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)


# =========================================================
# PAGE: AI COMMAND CENTER
# =========================================================
elif page == "AI Command Center":
    hero(
        "Neural Command Interface",
        "Unrestricted conversational AI for medical context exploration, biochemistry, and wellness.",
        "SYNAPSE CORE",
    )

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    prompt = st.chat_input(
        "Ask anything regarding physiology, pharmacology, recovery, or wellness...",
        key="command_chat",
    )

    if prompt:
        st.session_state.chat_history.append(
            {"role": "user", "content": prompt}
        )

        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Synthesizing clinical knowledge..."):
                answer = ask_ai(
                    f"""
You are HealthMate AI Command Center.

User Question:
{prompt}

Deliver an articulate, scientifically sound, and accessible explanation.
Highlight key takeaways with clear formatting.
If the situation hints at medical emergency, advise immediate clinical care.
"""
                )

            if answer:
                st.write(answer)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": answer}
                )

    if st.session_state.chat_history:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Purge Active Session Memory"):
            st.session_state.chat_history = []
            st.rerun()


# =========================================================
# PAGE: SETTINGS
# =========================================================
elif page == "Settings":
    hero(
        "System Preferences",
        "Customize visual telemetry, dynamic accents, and interface parameters.",
        "CONFIGURATION",
    )

    accent_choice = st.selectbox(
        "Interface Accent Color",
        list(accent_colors.keys()),
        index=list(accent_colors.keys()).index(st.session_state.accent),
    )

    if accent_choice != st.session_state.accent:
        st.session_state.accent = accent_choice
        st.rerun()

    st.markdown("<br>### 🖥️ Diagnostics & Connection Status", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        card("🤖", "Gemini Core", "Connected" if client else "Key Missing")
    with c2:
        card("📄", "PDF Engine", "Ready" if create_pdf else "Offline")
    with c3:
        card("⚡", "Rendering", "Hardware Accelerated", "CSS3 / WebGL")


# =========================================================
# PAGE: ABOUT
# =========================================================
elif page == "About":
    hero(
        "About HealthMate AI",
        "Next-generation AI architecture developed for consumer health literacy and wellness tracking.",
        "PROJECT INFORMATION",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        tool("🐍", "Python 3", "High-performance computational backend.")
    with c2:
        tool("🌐", "Streamlit UI", "Reactive web runtime interface.")
    with c3:
        tool("🤖", "Google Gemini", "Multimodal intelligence & reasoning.")

    st.markdown("<br>### 👨‍💻 Lead Architect", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="card">
            <div style="font-family:'Outfit'; font-size:26px; font-weight:800; color:{accent};">
                Bhavesh Thakur
            </div>
            <div style="color:{muted}; margin-top:6px; font-size:14px; font-weight:500;">
                Creator & Full-Stack Developer
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.warning(
        "⚠️ HealthMate AI is an educational platform and is not designed to replace professional diagnosis, treatment, or clinical assessment."
    )


# =========================================================
# FOOTER
# =========================================================
st.markdown(
    f"""
    <div class="footer">
        <b style="color:{accent}; font-family:'Outfit'; font-size:15px; font-weight:800; letter-spacing:1px;">HEALTHMATE AI SYSTEMS</b><br>
        © 2026 • Developed by Bhavesh Thakur • Powered by Google Gemini<br>
        <span style="opacity:0.75;">Designed for Health Literacy & Wellness Optimization</span>
    </div>
    """,
    unsafe_allow_html=True,
)
