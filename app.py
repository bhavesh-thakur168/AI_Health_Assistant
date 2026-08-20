import streamlit as st
from google import genai
from report import create_pdf


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="HealthMate AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       GLOBAL
       ====================================================== */

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 10%, rgba(0, 255, 200, 0.08), transparent 30%),
            radial-gradient(circle at 90% 20%, rgba(90, 70, 255, 0.10), transparent 30%),
            radial-gradient(circle at 50% 100%, rgba(0, 180, 255, 0.06), transparent 35%),
            #050811;
        color: #e9f7ff;
    }

    .main {
        background: transparent;
    }

    /* ======================================================
       SIDEBAR
       ====================================================== */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                rgba(7, 13, 25, 0.98),
                rgba(4, 8, 17, 0.98)
            );

        border-right: 1px solid rgba(0, 255, 220, 0.14);
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.2rem;
    }

    .brand {
        padding: 10px 8px 20px 8px;
        text-align: center;
    }

    .brand-logo {
        width: 68px;
        height: 68px;
        margin: auto;
        border-radius: 22px;

        display: flex;
        align-items: center;
        justify-content: center;

        font-size: 32px;

        background:
            linear-gradient(
                135deg,
                rgba(0,255,210,0.20),
                rgba(90,80,255,0.22)
            );

        border: 1px solid rgba(0,255,220,0.28);

        box-shadow:
            0 0 25px rgba(0,255,220,0.12),
            inset 0 0 25px rgba(0,255,220,0.05);
    }

    .brand-name {
        margin-top: 12px;

        font-family: 'Orbitron', sans-serif;
        font-size: 20px;
        font-weight: 700;

        letter-spacing: 1px;

        background: linear-gradient(
            90deg,
            #6ffff0,
            #70a7ff
        );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .brand-subtitle {
        color: #71839b;
        font-size: 10px;
        letter-spacing: 2px;
        margin-top: 5px;
    }

    /* ======================================================
       NAVIGATION
       ====================================================== */

    div[data-testid="stRadio"] > label {
        display: none;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] {
        gap: 6px;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        border-radius: 12px;
        padding: 10px 13px;
        border: 1px solid transparent;
        transition: all 0.2s ease;
        color: #8fa4bd;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        background: rgba(0,255,220,0.06);
        border-color: rgba(0,255,220,0.10);
        color: #d9ffff;
    }

    /* ======================================================
       HEADINGS
       ====================================================== */

    h1 {
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    h2, h3 {
        font-weight: 700 !important;
    }

    /* ======================================================
       HERO
       ====================================================== */

    .hero {
        position: relative;

        padding: 38px;

        border-radius: 28px;

        background:
            linear-gradient(
                135deg,
                rgba(12, 25, 43, 0.94),
                rgba(8, 13, 28, 0.88)
            );

        border: 1px solid rgba(0,255,220,0.16);

        box-shadow:
            0 20px 60px rgba(0,0,0,0.25),
            inset 0 1px 0 rgba(255,255,255,0.03);

        overflow: hidden;
    }

    .hero:before {
        content: "";
        position: absolute;

        width: 260px;
        height: 260px;

        right: -100px;
        top: -100px;

        border-radius: 50%;

        background: rgba(0,255,220,0.12);

        filter: blur(50px);
    }

    .hero-kicker {
        color: #55e8d0;
        font-size: 12px;
        letter-spacing: 3px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .hero-title {
        font-family: 'Orbitron', sans-serif;
        font-size: clamp(30px, 5vw, 52px);
        line-height: 1.1;
        font-weight: 800;

        background:
            linear-gradient(
                90deg,
                #ffffff,
                #72f7df,
                #7ba5ff
            );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-text {
        max-width: 720px;
        margin-top: 16px;
        color: #8fa5bd;
        font-size: 15px;
        line-height: 1.7;
    }

    /* ======================================================
       STATUS
       ====================================================== */

    .status {
        display: inline-flex;
        align-items: center;
        gap: 8px;

        padding: 7px 12px;

        border-radius: 999px;

        background: rgba(0,255,180,0.07);
        border: 1px solid rgba(0,255,180,0.15);

        color: #73eacb;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1px;
    }

    .status-dot {
        width: 7px;
        height: 7px;

        border-radius: 50%;

        background: #4dffd0;

        box-shadow: 0 0 12px #4dffd0;
    }

    /* ======================================================
       CARDS
       ====================================================== */

    .glass-card {
        padding: 22px;

        border-radius: 20px;

        background:
            linear-gradient(
                145deg,
                rgba(16, 27, 45, 0.82),
                rgba(7, 13, 26, 0.88)
            );

        border: 1px solid rgba(255,255,255,0.07);

        box-shadow:
            0 12px 35px rgba(0,0,0,0.20),
            inset 0 1px 0 rgba(255,255,255,0.025);

        transition: transform 0.2s ease;
    }

    .glass-card:hover {
        transform: translateY(-2px);
        border-color: rgba(0,255,220,0.16);
    }

    .metric-label {
        color: #72859d;
        font-size: 11px;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    .metric-value {
        margin-top: 7px;
        font-family: 'Orbitron', sans-serif;
        font-size: 25px;
        font-weight: 700;
        color: #e9ffff;
    }

    .metric-icon {
        font-size: 25px;
        margin-bottom: 8px;
    }

    /* ======================================================
       SECTION HEADER
       ====================================================== */

    .section-header {
        margin-top: 30px;
        margin-bottom: 15px;

        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .section-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 17px;
        font-weight: 700;
        color: #dffcff;
    }

    .section-line {
        height: 1px;
        flex: 1;

        margin-left: 20px;

        background:
            linear-gradient(
                90deg,
                rgba(0,255,220,0.25),
                transparent
            );
    }

    /* ======================================================
       BUTTONS
       ====================================================== */

    .stButton > button {
        width: 100%;

        border-radius: 13px;

        padding: 12px 18px;

        background:
            linear-gradient(
                135deg,
                rgba(0,255,210,0.14),
                rgba(90,100,255,0.14)
            );

        border: 1px solid rgba(0,255,220,0.22);

        color: #dffefa;

        font-weight: 700;

        transition:
            transform 0.2s ease,
            box-shadow 0.2s ease,
            border-color 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);

        border-color: rgba(0,255,220,0.55);

        box-shadow:
            0 0 25px rgba(0,255,220,0.10);
    }

    /* ======================================================
       INPUTS
       ====================================================== */

    div[data-baseweb="input"] {
        background: rgba(5,11,22,0.80);
        border-radius: 12px;
    }

    div[data-baseweb="input"] input {
        color: #eaffff !important;
    }

    div[data-baseweb="select"] {
        background: rgba(5,11,22,0.80);
        border-radius: 12px;
    }

    textarea {
        background: rgba(5,11,22,0.80) !important;
        color: #eaffff !important;
        border-radius: 12px !important;
    }

    /* ======================================================
       CHAT
       ====================================================== */

    [data-testid="stChatMessage"] {
        background: rgba(10,20,34,0.55);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 18px;
        margin-bottom: 10px;
    }

    /* ======================================================
       ALERTS
       ====================================================== */

    div[data-testid="stAlert"] {
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.06);
    }

    /* ======================================================
       FILE UPLOADER
       ====================================================== */

    section[data-testid="stFileUploaderDropzone"] {
        background: rgba(5,11,22,0.65);
        border: 1px dashed rgba(0,255,220,0.25);
        border-radius: 18px;
    }

    /* ======================================================
       FOOTER
       ====================================================== */

    .footer {
        margin-top: 60px;
        padding: 25px;

        text-align: center;

        color: #60748d;

        border-top: 1px solid rgba(255,255,255,0.05);

        font-size: 12px;
    }

    .footer strong {
        color: #8df8e6;
    }

    /* ======================================================
       SMALL DEVICES
       ====================================================== */

    @media (max-width: 800px) {

        .hero {
            padding: 25px;
        }

        .hero-title {
            font-size: 30px;
        }

    }

    </style>
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

            <div class="brand-logo">
                🧬
            </div>

            <div class="brand-name">
                HEALTHMATE
            </div>

            <div class="brand-subtitle">
                AI HEALTH INTELLIGENCE
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="status">
            <span class="status-dot"></span>
            AI SYSTEM ONLINE
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        "<small style='color:#52657d;'>NAVIGATION</small>",
        unsafe_allow_html=True
    )

    pages = [
        "⌂  Home",
        "◈  AI Symptom Checker",
        "▣  Medicine Info",
        "◉  BMI Calculator",
        "◌  Water Intake",
        "◇  Diet Planner",
        "⚡  Exercise Planner",
        "◍  Calorie Calculator",
        "☾  Sleep Recommendation",
        "▧  Medical Report Analyzer",
        "◫  Health Dashboard",
        "ⓘ  About"
    ]

    selected_page = st.radio(
        "Navigation",
        pages,
        label_visibility="collapsed"
    )

    selected = selected_page.split("  ", 1)[-1]

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="
            padding:15px;
            border-radius:15px;
            background:rgba(0,255,220,0.04);
            border:1px solid rgba(0,255,220,0.08);
        ">
            <div style="font-size:11px;color:#647991;">
                POWERED BY
            </div>

            <div style="
                margin-top:5px;
                color:#a6fff1;
                font-weight:700;
            ">
                GOOGLE GEMINI
            </div>

            <div style="
                margin-top:8px;
                color:#53677f;
                font-size:10px;
            ">
                Health intelligence engine
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def page_header(kicker, title, description):

    st.markdown(
        f"""
        <div class="hero">

            <div class="hero-kicker">
                {kicker}
            </div>

            <div class="hero-title">
                {title}
            </div>

            <div class="hero-text">
                {description}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


def section_header(title):

    st.markdown(
        f"""
        <div class="section-header">

            <div class="section-title">
                {title}
            </div>

            <div class="section-line"></div>

        </div>
        """,
        unsafe_allow_html=True
    )


def metric_card(icon, label, value):

    st.markdown(
        f"""
        <div class="glass-card">

            <div class="metric-icon">
                {icon}
            </div>

            <div class="metric-label">
                {label}
            </div>

            <div class="metric-value">
                {value}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


def feature_card(icon, title, description):

    st.markdown(
        f"""
        <div class="glass-card">

            <div style="
                font-size:30px;
                margin-bottom:12px;
            ">
                {icon}
            </div>

            <div style="
                font-size:16px;
                font-weight:700;
                color:#e7ffff;
            ">
                {title}
            </div>

            <div style="
                margin-top:8px;
                color:#72869e;
                font-size:13px;
                line-height:1.6;
            ">
                {description}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# HOME
# ============================================================

if selected == "Home":

    page_header(
        "WELCOME TO YOUR PERSONAL HEALTH SYSTEM",
        "HealthMate AI",
        "An intelligent wellness companion that brings AI-powered health tools, lifestyle guidance and personal health utilities into one futuristic interface."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("🤖", "AI ENGINE", "Gemini")

    with col2:
        metric_card("🧠", "AI TOOLS", "8+")

    with col3:
        metric_card("⚡", "HEALTH TOOLS", "12")

    with col4:
        metric_card("📄", "REPORTS", "PDF")

    section_header("INTELLIGENCE MODULES")

    col1, col2, col3 = st.columns(3)

    with col1:
        feature_card(
            "🤖",
            "AI Symptom Checker",
            "Describe symptoms and receive general educational information from the AI health assistant."
        )

    with col2:
        feature_card(
            "💊",
            "Medicine Intelligence",
            "Explore general educational information about medicines, precautions and common side effects."
        )

    with col3:
        feature_card(
            "📷",
            "Medical Report Analyzer",
            "Upload supported medical images for a general AI-generated explanation."
        )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        feature_card(
            "📊",
            "BMI Calculator",
            "Calculate your BMI and view the corresponding general category."
        )

    with col2:
        feature_card(
            "💧",
            "Water Intelligence",
            "Estimate a general daily water-intake recommendation."
        )

    with col3:
        feature_card(
            "🍎",
            "AI Diet Planner",
            "Generate a simple one-day Indian diet plan based on your selected goal."
        )

    section_header("SYSTEM NOTICE")

    st.warning(
        "⚠️ HealthMate AI provides educational and general wellness information only. "
        "It does not replace professional medical diagnosis, treatment or advice."
    )


# ============================================================
# AI SYMPTOM CHECKER
# ============================================================

elif selected == "AI Symptom Checker":

    page_header(
        "AI HEALTH INTELLIGENCE",
        "Symptom Checker",
        "Describe what you're experiencing and let the AI generate general educational information about possible health considerations."
    )

    section_header("AI CONVERSATION")

    symptoms = st.chat_input(
        "Describe your symptoms..."
    )

    if symptoms:

        with st.chat_message("user"):
            st.write(symptoms)

        if symptoms.strip() == "":

            st.warning(
                "Please enter your symptoms."
            )

        else:

            with st.chat_message("assistant"):

                with st.spinner("AI health engine analyzing..."):

                    prompt = f"""
You are an AI Health Assistant.

Symptoms:
{symptoms}

Provide general educational information.

Do not diagnose the user.
Do not prescribe medicines.
Mention when professional medical care may be appropriate.
Keep the language clear and simple.
"""

                    response = client.models.generate_content(
                        model="gemini-3.1-flash-lite",
                        contents=prompt
                    )

                st.write(response.text)

            pdf_file = create_pdf(
                symptoms,
                response.text
            )

            with open(pdf_file, "rb") as file:

                pdf_data = file.read()

            st.download_button(
                label="📄 Download Health Report",
                data=pdf_data,
                file_name="Health_Report.pdf",
                mime="application/pdf"
            )

            st.info(
                "⚠️ This information is educational only. "
                "Consult a qualified healthcare professional for medical concerns."
            )


# ============================================================
# MEDICINE INFORMATION
# ==========================================             )

            st.success("Calories Estimated")

            st.write(response.text)

            st.info("⚠ This is an AI estimate and may not be completely accurate.")

elif selected == "Sleep Recommendation":

    st.title("😴 AI Sleep Recommendation")

    age = st.number_input(
        "Your Age",
        min_value=1,
        max_value=100,
        value=18
    )

    sleep_hours = st.slider(
        "How many hours do you sleep each night?",
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

    if st.button("Get Sleep Advice"):

        with st.spinner("Analyzing your sleep..."):

            prompt = f"""
Provide simple sleep recommendations.

Age: {age}
Sleep Hours: {sleep_hours}
Lifestyle: {lifestyle}

Include:
- Is the sleep duration adequate?
- Tips to improve sleep quality.
- Healthy bedtime habits.
- When to consult a doctor.

Keep the language simple.
"""

            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt
            )

        st.success("Sleep Advice Ready")

        st.write(response.text)

        st.info(
            "⚠️ These are general wellness suggestions and are not a medical diagnosis."
        )
elif selected == "Medical Report Analyzer":

    st.title("📷 Medical Report Analyzer")

    st.write(
        "Upload a medical report, X-ray, skin image, or blood test report for a general AI explanation."
    )

    uploaded_file = st.file_uploader(
        "Choose an image",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file is not None:

        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

        if st.button("🔍 Analyze Image"):

            with st.spinner("Analyzing image..."):

                image_bytes = uploaded_file.getvalue()

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        "Explain this medical image in simple language. Do not diagnose. Suggest consulting a doctor if necessary.",
                        {
                            "mime_type": uploaded_file.type,
                            "data": image_bytes,
                        },
                    ],
                )

            st.success("Analysis Complete")

            st.write(response.text)

            st.info(
                "⚠ This explanation is for educational purposes only and is not a medical diagnosis."
            )
elif selected == "About":

    st.title("About Project")

    st.write("""
### Technologies Used

- Python
- Streamlit
- Gemini AI
- Google GenAI SDK

### Developed By

Bhavesh Thakur
            
""")
    
    st.markdown("---")

st.caption(
    "© 2026 HealthMate AI | Developed by Bhavesh Thakur | Educational Purpose Only"
)
st.markdown("---")

st.markdown(
    """
    <div style='text-align:center'>
        ❤️ Developed by <b>Bhavesh Thakur</b><br>
        HealthMate AI • Powered by Google Gemini
    </div>
    """,
    unsafe_allow_html=True
)
