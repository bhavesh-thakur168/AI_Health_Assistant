import streamlit as st
from streamlit_option_menu import option_menu
from google import genai
from report import create_pdf


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="HealthMate AI",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# GEMINI
# ============================================================

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)


# ============================================================
# PREMIUM MEDICAL AI THEME
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&family=Orbitron:wght@500;600;700&display=swap');


/* =========================================================
   GLOBAL
========================================================= */

:root {
    --bg: #050a14;
    --bg2: #08111f;
    --panel: #0b1525;
    --panel2: #0d192b;

    --cyan: #38d9ff;
    --cyan-soft: #73e7ff;

    --green: #38e6a0;
    --purple: #8b7cff;

    --text: #edf7ff;
    --muted: #7f91a8;
    --muted2: #566a83;

    --border: rgba(140, 190, 220, 0.12);
}

html, body, [class*="css"] {
    font-family: "Inter", sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 75% 0%,
            rgba(56, 217, 255, 0.07),
            transparent 28%
        ),
        radial-gradient(
            circle at 20% 80%,
            rgba(91, 84, 255, 0.055),
            transparent 28%
        ),
        linear-gradient(
            145deg,
            #030711 0%,
            #06101d 50%,
            #040913 100%
        );

    color: var(--text);
}


/* =========================================================
   REMOVE DEFAULT TOP SPACE
========================================================= */

.block-container {
    max-width: 1480px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}


/* =========================================================
   SIDEBAR
========================================================= */

section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #050b17 0%,
            #06101d 100%
        );

    border-right:
        1px solid rgba(56, 217, 255, 0.10);
}

section[data-testid="stSidebar"] > div {
    padding: 1rem 0.8rem;
}


/* Brand */

.brand {
    padding: 14px 12px 25px;
    text-align: left;
}

.brand-mark {
    width: 42px;
    height: 42px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 12px;

    color: #07101b;
    background:
        linear-gradient(
            135deg,
            #73e7ff,
            #38d9ff
        );

    font-size: 21px;
    font-weight: 800;

    box-shadow:
        0 0 30px rgba(56,217,255,.18);

    margin-bottom: 15px;
}

.brand-name {
    font-family: "Manrope", sans-serif;
    font-size: 18px;
    font-weight: 800;
    letter-spacing: -.4px;
    color: #ffffff;
}

.brand-name span {
    color: var(--cyan);
}

.brand-caption {
    margin-top: 5px;
    color: #536981;
    font-size: 9px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}


/* Navigation */

.nav-link {
    border-radius: 10px !important;
    margin: 3px 0 !important;

    color: #8194aa !important;

    font-size: 13px !important;

    transition:
        background .2s ease,
        color .2s ease,
        transform .2s ease !important;
}

.nav-link:hover {
    color: #eafaff !important;

    background:
        rgba(56,217,255,.055) !important;

    transform:
        translateX(2px);
}

.nav-link-selected {
    color: #ffffff !important;

    background:
        linear-gradient(
            90deg,
            rgba(56,217,255,.14),
            rgba(56,217,255,.025)
        ) !important;

    border-left:
        2px solid var(--cyan);

    box-shadow:
        inset 15px 0 30px rgba(56,217,255,.025);
}


/* Sidebar bottom */

.sidebar-status {
    margin: 25px 8px 5px;
    padding: 13px;

    border:
        1px solid rgba(56,217,255,.09);

    background:
        rgba(255,255,255,.018);

    border-radius: 12px;
}

.sidebar-status-row {
    display: flex;
    justify-content: space-between;
    align-items: center;

    font-size: 10px;
}

.online {
    color: #45e7a5;
}

.version {
    color: #4d6178;
}


/* =========================================================
   TYPOGRAPHY
========================================================= */

h1, h2, h3 {
    font-family: "Manrope", sans-serif !important;
}

h1 {
    font-size: 34px !important;
    font-weight: 800 !important;
}

h2 {
    font-size: 24px !important;
}

h3 {
    font-size: 18px !important;
}


/* =========================================================
   TOP SYSTEM BAR
========================================================= */

.system-bar {
    height: 42px;

    display: flex;
    align-items: center;
    justify-content: space-between;

    padding: 0 15px;

    margin-bottom: 18px;

    border:
        1px solid rgba(140,190,220,.09);

    border-radius: 10px;

    background:
        rgba(7,15,28,.72);

    backdrop-filter: blur(15px);
}

.system-left {
    display: flex;
    align-items: center;
    gap: 9px;

    color: #8093a9;
    font-size: 10px;
    letter-spacing: 1px;
}

.system-right {
    color: #52677e;
    font-size: 10px;
}

.pulse {
    width: 6px;
    height: 6px;

    border-radius: 50%;

    background: #38e6a0;

    box-shadow:
        0 0 10px rgba(56,230,160,.8);
}


/* =========================================================
   HERO
========================================================= */

.hero {
    position: relative;

    overflow: hidden;

    min-height: 310px;

    padding: 42px;

    margin-bottom: 22px;

    border:
        1px solid rgba(105,180,210,.13);

    border-radius: 22px;

    background:
        linear-gradient(
            135deg,
            rgba(10,24,40,.94),
            rgba(7,17,30,.92)
        );

    box-shadow:
        0 25px 80px rgba(0,0,0,.25);

    display: flex;
    flex-direction: column;
    justify-content: center;
}


/* subtle medical grid */

.hero-grid {
    position: absolute;

    inset: 0;

    opacity: .22;

    background-image:
        linear-gradient(
            rgba(56,217,255,.04) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(56,217,255,.04) 1px,
            transparent 1px
        );

    background-size: 35px 35px;

    mask-image:
        linear-gradient(
            to right,
            black,
            transparent
        );
}


/* glowing orb */

.hero-orb {
    position: absolute;

    width: 300px;
    height: 300px;

    right: -80px;
    top: -80px;

    border-radius: 50%;

    background:
        radial-gradient(
            circle,
            rgba(56,217,255,.14),
            rgba(56,217,255,.02) 55%,
            transparent 70%
        );
}


/* status */

.hero-status {
    position: relative;
    z-index: 2;

    display: inline-flex;
    align-items: center;

    width: fit-content;

    padding: 7px 11px;

    border:
        1px solid rgba(56,230,160,.16);

    background:
        rgba(56,230,160,.045);

    color: #55e9ad;

    border-radius: 100px;

    font-size: 9px;
    font-weight: 600;

    letter-spacing: 1.1px;
    text-transform: uppercase;
}

.hero-status-dot {
    width: 6px;
    height: 6px;

    margin-right: 7px;

    background: #38e6a0;

    border-radius: 50%;

    box-shadow:
        0 0 10px #38e6a0;
}


/* title */

.hero-title {
    position: relative;
    z-index: 2;

    margin-top: 18px;

    font-family: "Manrope", sans-serif;

    font-size: clamp(35px, 5vw, 64px);

    line-height: 1.02;

    font-weight: 800;

    letter-spacing: -2.8px;

    max-width: 850px;

    color: #f5fbff;
}

.hero-title span {
    color: var(--cyan);
}


/* subtitle */

.hero-description {
    position: relative;
    z-index: 2;

    margin-top: 17px;

    max-width: 670px;

    color: #8195ac;

    font-size: 14px;

    line-height: 1.75;
}


/* =========================================================
   SECTION HEADER
========================================================= */

.section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

    margin: 30px 0 14px;
}

.section-title {
    color: #e9f5ff;

    font-family: "Manrope", sans-serif;

    font-size: 17px;
    font-weight: 700;
}

.section-caption {
    color: #536980;
    font-size: 10px;
    letter-spacing: .8px;
}


/* =========================================================
   METRIC CARDS
========================================================= */

.metric-card {
    position: relative;

    min-height: 115px;

    padding: 20px;

    border:
        1px solid rgba(110,170,205,.11);

    border-radius: 16px;

    background:
        linear-gradient(
            145deg,
            rgba(13,28,46,.88),
            rgba(7,16,29,.90)
        );
}

.metric-card::after {
    content: "";

    position: absolute;

    right: 18px;
    top: 18px;

    width: 5px;
    height: 5px;

    border-radius: 50%;

    background: var(--cyan);

    box-shadow:
        0 0 12px var(--cyan);
}

.metric-label {
    color: #657b94;

    font-size: 9px;

    letter-spacing: 1.2px;

    text-transform: uppercase;
}

.metric-value {
    margin-top: 9px;

    font-family: "Manrope", sans-serif;

    font-size: 27px;

    font-weight: 800;

    color: #f1faff;
}

.metric-value.cyan {
    color: var(--cyan);
}

.metric-change {
    margin-top: 5px;

    color: #42dda0;

    font-size: 9px;
}


/* =========================================================
   FEATURE CARDS
========================================================= */

.feature {
    min-height: 175px;

    padding: 22px;

    margin-bottom: 18px;

    border:
        1px solid rgba(110,170,205,.10);

    border-radius: 16px;

    background:
        rgba(10,22,37,.78);

    transition:
        all .25s ease;
}

.feature:hover {
    border-color:
        rgba(56,217,255,.24);

    transform:
        translateY(-3px);

    box-shadow:
        0 15px 40px rgba(0,0,0,.25);
}

.feature-icon {
    width: 40px;
    height: 40px;

    display: flex;
    align-items: center;
    justify-content: center;

    margin-bottom: 17px;

    border-radius: 11px;

    background:
        rgba(56,217,255,.07);

    border:
        1px solid rgba(56,217,255,.10);

    font-size: 19px;
}

.feature-title {
    color: #eaf6ff;

    font-weight: 700;

    font-size: 14px;
}

.feature-description {
    color: #687d94;

    margin-top: 8px;

    font-size: 11px;

    line-height: 1.65;
}


/* =========================================================
   PROFESSIONAL CONTENT PANEL
========================================================= */

.panel {
    padding: 25px;

    margin-bottom: 20px;

    border:
        1px solid rgba(110,170,205,.10);

    border-radius: 17px;

    background:
        rgba(9,20,34,.80);
}

.panel-title {
    color: var(--cyan);

    font-family: "Manrope", sans-serif;

    font-size: 12px;

    font-weight: 700;

    letter-spacing: .8px;

    text-transform: uppercase;

    margin-bottom: 18px;
}


/* =========================================================
   INPUTS
========================================================= */

label {
    color: #8da1b7 !important;

    font-size: 11px !important;
}

.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    background:
        #07121f !important;

    color:
        #edf8ff !important;

    border:
        1px solid rgba(110,170,205,.13) !important;

    border-radius:
        10px !important;
}

.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus {
    border-color:
        rgba(56,217,255,.55) !important;

    box-shadow:
        0 0 0 1px rgba(56,217,255,.12) !important;
}


/* Selectbox */

div[data-baseweb="select"] > div {
    background:
        #07121f !important;

    border:
        1px solid rgba(110,170,205,.13) !important;

    border-radius:
        10px !important;
}


/* =========================================================
   BUTTON
========================================================= */

.stButton > button {
    min-height: 46px;

    border:
        1px solid rgba(56,217,255,.24);

    border-radius: 10px;

    background:
        linear-gradient(
            135deg,
            rgba(56,217,255,.13),
            rgba(56,217,255,.045)
        );

    color: #e8faff;

    font-weight: 600;

    font-size: 12px;

    letter-spacing: .3px;

    transition:
        all .2s ease;
}

.stButton > button:hover {
    border-color:
        rgba(56,217,255,.65);

    background:
        rgba(56,217,255,.10);

    color: #ffffff;

    box-shadow:
        0 0 25px rgba(56,217,255,.08);
}


/* =========================================================
   DOWNLOAD BUTTON
========================================================= */

.stDownloadButton > button {
    width: 100%;

    border-radius: 10px;

    background:
        rgba(56,230,160,.07);

    border:
        1px solid rgba(56,230,160,.18);

    color: #54e6ad;
}


/* =========================================================
   ALERTS
========================================================= */

div[data-testid="stAlert"] {
    border-radius: 11px;

    background:
        rgba(9,20,34,.72);
}


/* =========================================================
   CHAT
========================================================= */

[data-testid="stChatMessage"] {
    border:
        1px solid rgba(110,170,205,.10);

    background:
        rgba(9,20,34,.72);

    border-radius:
        14px;
}


/* =========================================================
   FILE UPLOADER
========================================================= */

[data-testid="stFileUploader"] {
    padding: 10px;

    border:
        1px dashed rgba(56,217,255,.22);

    border-radius: 14px;

    background:
        rgba(56,217,255,.025);
}


/* =========================================================
   FOOTER
========================================================= */

.footer {
    margin-top: 50px;

    padding-top: 25px;

    border-top:
        1px solid rgba(110,170,205,.08);

    text-align: center;

    color: #465b73;

    font-size: 10px;

    line-height: 1.8;
}

.footer strong {
    color: #6cdef7;
}


/* =========================================================
   SCROLLBAR
========================================================= */

::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-track {
    background: #040914;
}

::-webkit-scrollbar-thumb {
    background: #182b40;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #2d536e;
}


/* =========================================================
   MOBILE
========================================================= */

@media (max-width: 768px) {

    .hero {
        min-height: 260px;
        padding: 28px;
    }

    .hero-title {
        font-size: 37px;
        letter-spacing: -1.5px;
    }

    .hero-description {
        font-size: 13px;
    }

}

</style>
""", unsafe_allow_html=True)


# ============================================================
# UI HELPERS
# ============================================================

def hero(status, title, description):

    st.markdown(
        f"""
        <div class="hero">

            <div class="hero-grid"></div>
            <div class="hero-orb"></div>

            <div class="hero-status">
                <span class="hero-status-dot"></span>
                {status}
            </div>

            <div class="hero-title">
                {title}
            </div>

            <div class="hero-description">
                {description}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


def section(title, caption=""):

    st.markdown(
        f"""
        <div class="section-header">

            <div class="section-title">
                {title}
            </div>

            <div class="section-caption">
                {caption}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


def metric_card(label, value, change="", cyan=True):

    color = "cyan" if cyan else ""

    st.markdown(
        f"""
        <div class="metric-card">

            <div class="metric-label">
                {label}
            </div>

            <div class="metric-value {color}">
                {value}
            </div>

            <div class="metric-change">
                {change}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


def panel_start(title):

    st.markdown(
        f"""
        <div class="panel">

            <div class="panel-title">
                {title}
            </div>
        """,
        unsafe_allow_html=True
    )


def panel_end():

    st.markdown(
        """
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="brand">

            <div class="brand-mark">
                ✦
            </div>

            <div class="brand-name">
                HEALTHMATE <span>AI</span>
            </div>

            <div class="brand-caption">
                Intelligent Health Platform
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    selected = option_menu(
        None,

        [
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
            "About"
        ],

        icons=[
            "grid-1x2",
            "activity",
            "capsule",
            "speedometer2",
            "droplet",
            "apple",
            "person-walking",
            "fire",
            "moon-stars",
            "file-earmark-medical",
            "bar-chart-line",
            "info-circle"
        ],

        default_index=0,

        styles={
            "container": {
                "padding": "0!important",
                "background-color": "transparent"
            },

            "icon": {
                "color": "#63778f",
                "font-size": "14px"
            },

            "nav-link": {
                "font-size": "12px",
                "text-align": "left",
                "margin": "2px 0",
                "padding": "10px 12px",
                "border-radius": "10px"
            },

            "nav-link-selected": {
                "background-color": "rgba(56,217,255,0.10)",
                "color": "#ffffff"
            }
        }
    )

    st.markdown(
        """
        <div class="sidebar-status">

            <div class="sidebar-status-row">

                <span class="online">
                    ● SYSTEM OPERATIONAL
                </span>

                <span class="version">
                    v2.0
                </span>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# TOP BAR
# ============================================================

st.markdown(
    """
    <div class="system-bar">

        <div class="system-left">
            <span class="pulse"></span>
            HEALTHMATE AI
            <span style="color:#344b62;">/</span>
            SECURE HEALTH INTERFACE
        </div>

        <div class="system-right">
            GEMINI ENGINE • ONLINE
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HOME
# ============================================================

if selected == "Home":

    hero(
        "AI HEALTH PLATFORM • ONLINE",

        "Intelligent health,<br><span>reimagined.</span>",

        """
        A unified AI wellness platform for symptom education,
        nutrition, fitness, hydration and health insights —
        designed around a clean, intelligent experience.
        """
    )

    section(
        "Platform Overview",
        "REAL-TIME SYSTEM STATUS"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "AI ENGINE",
            "Gemini",
            "● ONLINE"
        )

    with c2:
        metric_card(
            "HEALTH MODULES",
            "12",
            "● ACTIVE"
        )

    with c3:
        metric_card(
            "VISION AI",
            "READY",
            "● AVAILABLE"
        )

    with c4:
        metric_card(
            "REPORT ENGINE",
            "PDF",
            "● READY"
        )

    section(
        "Intelligent Health Modules",
        "SELECT A MODULE FROM THE SIDEBAR"
    )

    features = [
        (
            "◉",
            "AI Symptom Checker",
            "Describe symptoms and receive general educational health information."
        ),
        (
            "⌬",
            "Medicine Intelligence",
            "Explore general medicine information, precautions and common side effects."
        ),
        (
            "◈",
            "BMI Analytics",
            "Calculate BMI and understand general weight categories."
        ),
        (
            "◌",
            "Hydration Engine",
            "Estimate a general daily hydration requirement."
        ),
        (
            "◇",
            "Nutrition Planner",
            "Generate simple AI-assisted meal and lifestyle ideas."
        ),
        (
            "△",
            "Fitness Intelligence",
            "Create simple workout routines based on fitness goals."
        )
    ]

    cols = st.columns(3)

    for i, (icon, title, description) in enumerate(features):

        with cols[i % 3]:

            st.markdown(
                f"""
                <div class="feature">

                    <div class="feature-icon">
                        {icon}
                    </div>

                    <div class="feature-title">
                        {title}
                    </div>

                    <div class="feature-description">
                        {description}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    st.warning(
        "HealthMate AI provides general educational and wellness "
        "information. It does not replace professional medical diagnosis "
        "or treatment."
    )


# ============================================================
# AI SYMPTOM CHECKER
# ============================================================

elif selected == "AI Symptom Checker":

    hero(
        "AI CLINICAL EDUCATION ENGINE",

        "Symptom<br><span>Intelligence.</span>",

        """
        Describe what you are experiencing in natural language.
        HealthMate AI will provide general educational information,
        possible considerations and guidance on when professional
        evaluation may be appropriate.
        """
    )

    panel_start("Symptom Input")

    symptoms = st.chat_input(
        "Describe your symptoms..."
    )

    st.markdown(
        """
        <div style="
            color:#536a82;
            font-size:10px;
            margin-top:10px;
        ">
            AI-generated information • Not a medical diagnosis
        </div>
        """,
        unsafe_allow_html=True
    )

    panel_end()

    if symptoms:

        with st.chat_message("user"):
            st.write(symptoms)

        with st.spinner("Analyzing health information..."):

            prompt = f"""
You are an AI health education assistant.

User symptoms:
{symptoms}

Provide general educational information.

Do not provide a definitive diagnosis.

Include:

1. Possible general explanations
2. Common considerations
3. Basic general self-care information where appropriate
4. Warning signs
5. When professional medical attention may be appropriate

If symptoms could indicate an emergency, clearly recommend
urgent medical care.

Keep the response clear and easy to understand.
"""

            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt
            )

        st.success("ANALYSIS COMPLETE")

        panel_start("AI Health Analysis")

        st.write(response.text)

        panel_end()

        try:

            pdf_file = create_pdf(
                symptoms,
                response.text
            )

            with open(
                pdf_file,
                "rb"
            ) as file:

                pdf_data = file.read()

            st.download_button(
                "DOWNLOAD HEALTH REPORT",
                data=pdf_data,
                file_name="Health_Report.pdf",
                mime="application/pdf"
            )

        except Exception as e:

            st.warning(
                f"Report generation unavailable: {e}"
            )


# ============================================================
# MEDICINE
# ============================================================

elif selected == "Medicine Info":

    hero(
        "PHARMACOLOGY INFORMATION ENGINE",

        "Medicine<br><span>Intelligence.</span>",

        """
        Explore general educational information about medicines,
        including common uses, side effects, precautions and
        situations where medical advice may be appropriate.
        """
    )

    panel_start("Medicine Query")

    medicine = st.text_input(
        "Medicine name",
        placeholder="Example: Paracetamol"
    )

    if st.button("ANALYZE MEDICINE"):

        if not medicine.strip():

            st.warning(
                "Please enter a medicine name."
            )

        else:

            with st.spinner(
                "Processing medicine information..."
            ):

                prompt = f"""
Provide general educational information about:

Medicine:
{medicine}

Include:

- What it is generally used for
- Common side effects
- Important precautions
- When to consult a doctor

Keep language simple.

Do not prescribe the medicine.
Do not recommend dosage.
"""

                response = client.models.generate_content(
                    model="gemini-3.1-flash-lite",
                    contents=prompt
                )

            panel_end()

            st.success("INFORMATION READY")

            panel_start("Medicine Intelligence")

            st.write(response.text)

            panel_end()

            st.info(
                "Always consult a qualified healthcare professional "
                "before using medication."
            )

    else:

        panel_end()


# ============================================================
# BMI
# ============================================================

elif selected == "BMI Calculator":

    hero(
        "BODY METRICS",

        "BMI<br><span>Analytics.</span>",

        """
        Calculate Body Mass Index using height and weight.
        BMI is a general screening measure and is not a complete
        assessment of individual health.
        """
    )

    panel_start("Body Measurements")

    c1, c2 = st.columns(2)

    with c1:

        height = st.number_input(
            "Height (cm)",
            min_value=50.0,
            max_value=250.0,
            value=170.0
        )

    with c2:

        weight = st.number_input(
            "Weight (kg)",
            min_value=10.0,
            max_value=300.0,
            value=65.0
        )

    if st.button("CALCULATE BMI"):

        height_m = height / 100

        bmi = weight / (
            height_m ** 2
        )

        panel_end()

        section(
            "BMI Result",
            "BODY METRIC ANALYSIS"
        )

        metric_card(
            "BODY MASS INDEX",
            f"{bmi:.2f}",
            "CALCULATED"
        )

        if bmi < 18.5:

            st.warning(
                "General category: Underweight"
            )

        elif bmi < 25:

            st.success(
                "General category: Healthy weight"
            )

        elif bmi < 30:

            st.warning(
                "General category: Overweight"
            )

        else:

            st.error(
                "General category: Obesity"
            )

    else:

        panel_end()


# ============================================================
# WATER
# ============================================================

elif selected == "Water Intake":

    hero(
        "HYDRATION ENGINE",

        "Hydration<br><span>Intelligence.</span>",

        """
        Estimate a general daily water requirement based on
        body weight. Individual requirements can vary significantly.
        """
    )

    panel_start("Hydration Parameters")

    weight = st.number_input(
        "Body weight (kg)",
        min_value=10.0,
        max_value=250.0,
        value=60.0
    )

    if st.button("CALCULATE HYDRATION"):

        litres = (
            weight * 35
        ) / 1000

        panel_end()

        section(
            "Hydration Estimate",
            "GENERAL WELLNESS CALCULATION"
        )

        metric_card(
            "DAILY WATER",
            f"{litres:.2f} L",
            "ESTIMATED"
        )

        st.info(
            "This is a general estimate. Activity level, climate, "
            "diet and health conditions can affect hydration needs."
        )

    else:

        panel_end()


# ============================================================
# DIET PLANNER
# ============================================================

elif selected == "Diet Planner":

    hero(
        "NUTRITION AI",

        "Personalized<br><span>Nutrition.</span>",

        """
        Generate a simple one-day Indian-style meal plan
        based on age, gender and wellness goals.
        """
    )

    panel_start("Nutrition Profile")

    c1, c2 = st.columns(2)

    with c1:

        age = st.number_input(
            "Age",
            1,
            100,
            18
        )

    with c2:

        gender = st.selectbox(
            "Gender",
            [
                "Male",
                "Female"
            ]
        )

    goal = st.selectbox(
        "Primary goal",
        [
            "Weight Loss",
            "Weight Gain",
            "Healthy Lifestyle"
        ]
    )

    if st.button("GENERATE NUTRITION PLAN"):

        with st.spinner(
            "Designing nutrition plan..."
        ):

            prompt = f"""
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

Keep the language simple.

Do not provide extreme dieting advice.
"""

            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt
            )

        panel_end()

        st.success(
            "NUTRITION PLAN READY"
        )

        panel_start("AI Nutrition Plan")

        st.write(response.text)

        panel_end()

    else:

        panel_end()


# ============================================================
# EXERCISE
# ============================================================

elif selected == "Exercise Planner":

    hero(
        "FITNESS INTELLIGENCE",

        "Exercise<br><span>Protocol.</span>",

        """
        Generate a simple daily workout plan based on fitness
        level and personal goal.
        """
    )

    panel_start("Fitness Profile")

    c1, c2 = st.columns(2)

    with c1:

        age = st.number_input(
            "Age",
            5,
            100,
            18
        )

    with c2:

        fitness = st.selectbox(
            "Fitness level",
            [
                "Beginner",
                "Intermediate",
                "Advanced"
            ]
        )

    goal = st.selectbox(
        "Goal",
        [
            "Weight Loss",
            "Muscle Gain",
            "Stay Fit"
        ]
    )

    if st.button("GENERATE WORKOUT"):

        with st.spinner(
            "Building exercise protocol..."
        ):

            prompt = f"""
Create a simple one-day exercise plan.

Age: {age}
Fitness Level: {fitness}
Goal: {goal}

Include:

- Warm-up
- Main Exercises
- Stretching
- Safety Tips

Keep the language simple.
"""

            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt
            )

        panel_end()

        st.success(
            "WORKOUT READY"
        )

        panel_start("AI Exercise Protocol")

        st.write(response.text)

        panel_end()

    else:

        panel_end()


# ============================================================
# CALORIES
# ============================================================

elif selected == "Calorie Calculator":

    hero(
        "NUTRITION ANALYTICS",

        "Calorie<br><span>Intelligence.</span>",

        """
        Describe your meal and receive an AI-generated estimate
        of calories and macronutrients.
        """
    )

    panel_start("Meal Input")

    food = st.text_area(
        "What did you eat?",
        placeholder=(
            "Example: 2 chapati, dal, rice, salad and milk"
        )
    )

    if st.button("ANALYZE MEAL"):

        if not food.strip():

            st.warning(
                "Please enter your food items."
            )

        else:

            with st.spinner(
                "Analyzing nutritional content..."
            ):

                prompt = f"""
Estimate the nutrition for:

{food}

Include:

- Estimated total calories
- Protein
- Carbohydrates
- Fat
- General health assessment
- Suggestions to improve the meal

Clearly explain that the result is an estimate.
"""

                response = client.models.generate_content(
                    model="gemini-3.1-flash-lite",
                    contents=prompt
                )

            panel_end()

            st.success(
                "NUTRITION ANALYSIS READY"
            )

            panel_start("AI Nutrition Analysis")

            st.write(response.text)

            panel_end()

            st.info(
                "AI nutritional estimates may not be completely accurate."
            )

    else:

        panel_end()


# ============================================================
# SLEEP
# ============================================================

elif selected == "Sleep Recommendation":

    hero(
        "SLEEP INTELLIGENCE",

        "Sleep<br><span>Advisor.</span>",

        """
        Review general sleep recommendations based on age,
        current sleep duration and lifestyle.
        """
    )

    panel_start("Sleep Profile")

    age = st.number_input(
        "Age",
        1,
        100,
        18
    )

    sleep_hours = st.slider(
        "Average sleep per night",
        1,
        12,
        7
    )

    lifestyle = st.selectbox(
        "Lifestyle",
        [
            "Student",
            "Working Professional",
            "Athlete",
            "Senior Citizen"
        ]
    )

    if st.button("ANALYZE SLEEP"):

        with st.spinner(
            "Analyzing sleep profile..."
        ):

            prompt = f"""
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

            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt
            )

        panel_end()

        st.success(
            "SLEEP ANALYSIS READY"
        )

        panel_start("AI Sleep Recommendations")

        st.write(response.text)

        panel_end()

    else:

        panel_end()


# ============================================================
# MEDICAL REPORT ANALYZER
# ============================================================

elif selected == "Medical Report Analyzer":

    hero(
        "VISION AI",

        "Medical<br><span>Vision.</span>",

        """
        Upload a medical image or report and receive a general
        educational explanation. This system does not diagnose.
        """
    )

    panel_start("Medical Image Upload")

    uploaded_file = st.file_uploader(
        "Upload image",
        type=[
            "png",
            "jpg",
            "jpeg"
        ]
    )

    if uploaded_file:

        st.image(
            uploaded_file,
            use_container_width=True
        )

        if st.button("ANALYZE IMAGE"):

            with st.spinner(
                "Vision AI processing image..."
            ):

                image_bytes = uploaded_file.getvalue()

                response = client.models.generate_content(
                    model="gemini-2.5-flash",

                    contents=[
                        """
Explain this medical image in simple educational language.

Do not diagnose.

Describe general visible information only.

Mention when professional medical evaluation
may be appropriate.
""",

                        {
                            "mime_type": uploaded_file.type,
                            "data": image_bytes
                        }
                    ]
                )

            panel_end()

            st.success(
                "VISION ANALYSIS COMPLETE"
            )

            panel_start("AI Vision Report")

            st.write(response.text)

            panel_end()

        else:

            panel_end()

    else:

        panel_end()


# ============================================================
# HEALTH DASHBOARD
# ============================================================

elif selected == "Health Dashboard":

    hero(
        "SYSTEM MONITOR",

        "Health<br><span>Command Center.</span>",

        """
        A centralized overview of HealthMate AI's intelligent
        health, wellness and analysis modules.
        """
    )

    section(
        "System Overview",
        "PLATFORM STATUS"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "AI ENGINE",
            "ONLINE",
            "GEMINI"
        )

    with c2:
        metric_card(
            "AI MODULES",
            "08",
            "ACTIVE"
        )

    with c3:
        metric_card(
            "WELLNESS TOOLS",
            "12",
            "READY"
        )

    with c4:
        metric_card(
            "REPORT SYSTEM",
            "READY",
            "PDF"
        )

    section(
        "Platform Modules",
        "SYSTEM CAPABILITIES"
    )

    modules = [
        ("◉", "Symptom Intelligence"),
        ("⌬", "Medicine Information"),
        ("◈", "BMI Analytics"),
        ("◌", "Hydration Engine"),
        ("◇", "Nutrition AI"),
        ("△", "Fitness AI"),
        ("◐", "Calorie Analysis"),
        ("☾", "Sleep Intelligence"),
        ("▣", "Medical Vision"),
        ("▤", "PDF Reporting"),
        ("✦", "Gemini AI"),
        ("◎", "Health Dashboard")
    ]

    cols = st.columns(4)

    for i, (icon, name) in enumerate(modules):

        with cols[i % 4]:

            st.markdown(
                f"""
                <div class="feature">

                    <div class="feature-icon">
                        {icon}
                    </div>

                    <div class="feature-title">
                        {name}
                    </div>

                    <div class="feature-description">
                        <span style="color:#42dda0;">
                            ● Operational
                        </span>
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# ABOUT
# ============================================================

elif selected == "About":

    hero(
        "PLATFORM INFORMATION",

        "Built for the<br><span>future of health.</span>",

        """
        HealthMate AI is an educational AI wellness platform
        combining modern web technology with Google's Gemini
        artificial intelligence.
        """
    )

    c1, c2 = st.columns(2)

    with c1:

        panel_start("Technology Stack")

        st.markdown("""
        **Python**  
        Application logic and calculations.

        **Streamlit**  
        Interactive web application framework.

        **Google Gemini**  
        AI-powered health information engine.

        **Google GenAI SDK**  
        Gemini API integration.

        **ReportLab**  
        PDF health report generation.
        """)

        panel_end()

    with c2:

        panel_start("Developer")

        st.markdown(
            """
            <div style="
                font-family:'Manrope';
                font-size:30px;
                font-weight:800;
                color:#edf8ff;
                margin-bottom:12px;
            ">
                Bhavesh Thakur
            </div>

            <div style="
                color:#71869e;
                line-height:1.8;
                font-size:12px;
            ">
                HealthMate AI is an educational project
                focused on combining artificial intelligence,
                health utilities and modern user experience
                design.
            </div>
            """,
            unsafe_allow_html=True
        )

        panel_end()

    st.warning(
        "HealthMate AI is an educational wellness application. "
        "It is not intended to diagnose, treat or replace professional "
        "medical care."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

        <strong>HEALTHMATE AI</strong>

        <br>

        Intelligent Health • AI • Wellness • Analytics

        <br>

        © 2026 HealthMate AI
        • Developed by Bhavesh Thakur

        <br>

        Educational Purpose Only

    </div>
    """,
    unsafe_allow_html=True
)
