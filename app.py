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
# ============================================================

elif selected == "Medicine Info":

    page_header(
        "MEDICINE INTELLIGENCE",
        "Medicine Information",
        "Get simple, general educational information about a medicine without receiving a prescription."
    )

    section_header("MEDICINE SEARCH")

    medicine = st.text_input(
        "Medicine Name",
        placeholder="Example: Paracetamol"
    )

    if st.button("◈ GET MEDICINE INFORMATION"):

        if medicine.strip() == "":

            st.warning(
                "Please enter a medicine name."
            )

        else:

            with st.spinner("Searching medicine intelligence..."):

                prompt = f"""
Provide general educational information about this medicine.

Medicine:
{medicine}

Include:

- What it is used for
- Common side effects
- Precautions
- When to consult a doctor

Keep the language simple.

Do NOT prescribe medicines.
"""

                response = client.models.generate_content(
                    model="gemini-3.1-flash-lite",
                    contents=prompt
                )

            st.success(
                "Information Ready"
            )

            st.markdown(
                '<div class="glass-card">',
                unsafe_allow_html=True
            )

            st.write(response.text)

            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )

            st.info(
                "⚠️ Always consult a qualified healthcare professional before taking medicine."
            )


# ============================================================
# BMI CALCULATOR
# ============================================================

elif selected == "BMI Calculator":

    page_header(
        "BODY METRICS",
        "BMI Calculator",
        "Calculate your Body Mass Index using your height and weight."
    )

    section_header("BODY MEASUREMENTS")

    col1, col2 = st.columns(2)

    with col1:

        height = st.number_input(
            "Height (cm)",
            min_value=50.0,
            max_value=250.0,
            value=170.0
        )

    with col2:

        weight = st.number_input(
            "Weight (kg)",
            min_value=10.0,
            max_value=300.0,
            value=65.0
        )

    if st.button("◉ CALCULATE BMI"):

        height_m = height / 100

        bmi = weight / (
            height_m * height_m
        )

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            metric_card(
                "⚖️",
                "YOUR BMI",
                f"{bmi:.2f}"
            )

        if bmi < 18.5:

            category = "Underweight"

            message = "Your BMI falls in the underweight category."

        elif bmi < 25:

            category = "Healthy Weight"

            message = "Your BMI falls in the healthy-weight category."

        elif bmi < 30:

            category = "Overweight"

            message = "Your BMI falls in the overweight category."

        else:

            category = "Obese"

            message = "Your BMI falls in the obese category."

        with col2:
            metric_card(
                "🧬",
                "CATEGORY",
                category
            )

        with col3:
            metric_card(
                "📡",
                "STATUS",
                "CALCULATED"
            )

        st.info(
            message
        )

        st.warning(
            "⚠️ BMI is a general health indicator and should not be used as the only measure of health."
        )


# ============================================================
# WATER INTAKE
# ============================================================

elif selected == "Water Intake":

    page_header(
        "HYDRATION INTELLIGENCE",
        "Water Intake",
        "Estimate a general daily water-intake recommendation based on body weight."
    )

    section_header("HYDRATION INPUT")

    weight = st.number_input(
        "Weight (kg)",
        min_value=10.0,
        max_value=250.0,
        value=60.0
    )

    if st.button("💧 CALCULATE WATER INTAKE"):

        water = weight * 35

        litres = water / 1000

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            metric_card(
                "💧",
                "RECOMMENDED",
                f"{litres:.2f} L"
            )

        with col2:
            metric_card(
                "📡",
                "DAILY STATUS",
                "ESTIMATE"
            )

        st.success(
            f"💧 Recommended Water Intake: {litres:.2f} Litres/day"
        )

        st.info(
            "This is a general recommendation. Your actual needs may vary depending on climate, activity level and health."
        )


# ============================================================
# DIET PLANNER
# ============================================================

elif selected == "Diet Planner":

    page_header(
        "NUTRITION INTELLIGENCE",
        "AI Diet Planner",
        "Generate a simple one-day Indian diet plan based on your age, gender and health goal."
    )

    section_header("PERSONAL PROFILE")

    col1, col2, col3 = st.columns(3)

    with col1:

        age = st.number_input(
            "Age",
            1,
            100,
            18
        )

    with col2:

        gender = st.selectbox(
            "Gender",
            ["Male", "Female"]
        )

    with col3:

        goal = st.selectbox(
            "Goal",
            [
                "Weight Loss",
                "Weight Gain",
                "Healthy Lifestyle"
            ]
        )

    if st.button("🍎 GENERATE DIET PLAN"):

        with st.spinner(
            "Preparing your AI nutrition plan..."
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
Do not claim to provide medical treatment.
"""

            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt
            )

        st.success(
            "Diet Plan Ready"
        )

        st.markdown(
            '<div class="glass-card">',
            unsafe_allow_html=True
        )

        st.write(response.text)

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


# ============================================================
# EXERCISE PLANNER
# ============================================================

elif selected == "Exercise Planner":

    page_header(
        "FITNESS INTELLIGENCE",
        "AI Exercise Planner",
        "Generate a simple one-day exercise plan based on your fitness level and goal."
    )

    section_header("FITNESS PROFILE")

    col1, col2, col3 = st.columns(3)

    with col1:

        age = st.number_input(
            "Age",
            min_value=5,
            max_value=100,
            value=18
        )

    with col2:

        fitness = st.selectbox(
            "Fitness Level",
            [
                "Beginner",
                "Intermediate",
                "Advanced"
            ]
        )

    with col3:

        goal = st.selectbox(
            "Goal",
            [
                "Weight Loss",
                "Muscle Gain",
                "Stay Fit"
            ]
        )

    if st.button("⚡ GENERATE EXERCISE PLAN"):

        with st.spinner(
            "Creating your workout plan..."
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

Keep the language simple and suitable for students.
"""

            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt
            )

        st.success(
            "Exercise Plan Ready!"
        )

        st.markdown(
            '<div class="glass-card">',
            unsafe_allow_html=True
        )

        st.write(response.text)

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


# ============================================================
# CALORIE CALCULATOR
# ============================================================

elif selected == "Calorie Calculator":

    page_header(
        "NUTRITION ANALYTICS",
        "AI Calorie Calculator",
        "Describe what you ate and receive an AI-generated nutritional estimate."
    )

    section_header("FOOD INPUT")

    food = st.text_area(
        "What did you eat today?",
        placeholder="Example: 2 chapati, dal, rice, salad and milk"
    )

    if st.button("🔥 CALCULATE CALORIES"):

        if food.strip() == "":

            st.warning(
                "Please enter your food items."
            )

        else:

            with st.spinner(
                "Calculating nutritional estimate..."
            ):

                prompt = f"""
Estimate the calories for the following food.

Food:
{food}

Include:

- Estimated total calories
- Protein
- Carbohydrates
- Fat
- Whether the meal is healthy
- Suggestions to improve it

Keep the answer simple.

Make clear that the result is only an estimate.
"""

                response = client.models.generate_content(
                    model="gemini-3.1-flash-lite",
                    contents=prompt
                )

            st.success(
                "Calories Estimated"
            )

            st.markdown(
                '<div class="glass-card">',
                unsafe_allow_html=True
            )

            st.write(response.text)

            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )

            st.info(
                "⚠️ This is an AI estimate and may not be completely accurate."
            )


# ============================================================
# SLEEP RECOMMENDATION
# ============================================================

elif selected == "Sleep Recommendation":

    page_header(
        "RECOVERY INTELLIGENCE",
        "Sleep Recommendation",
        "Get general sleep and bedtime recommendations based on your age, sleep duration and lifestyle."
    )

    section_header("SLEEP PROFILE")

    col1, col2, col3 = st.columns(3)

    with col1:

        age = st.number_input(
            "Your Age",
            min_value=1,
            max_value=100,
            value=18
        )

    with col2:

        sleep_hours = st.slider(
            "Sleep Hours",
            1,
            12,
            7
        )

    with col3:

        lifestyle = st.selectbox(
            "Lifestyle",
            [
                "Student",
                "Working Professional",
                "Athlete",
                "Senior Citizen"
            ]
        )

    if st.button("☾ GET SLEEP ADVICE"):

        with st.spinner(
            "Analyzing sleep profile..."
        ):

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

        st.success(
            "Sleep Advice Ready"
        )

        st.markdown(
            '<div class="glass-card">',
            unsafe_allow_html=True
        )

        st.write(response.text)

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

        st.info(
            "⚠️ These are general wellness suggestions and are not a medical diagnosis."
        )


# ============================================================
# MEDICAL REPORT ANALYZER
# ============================================================

elif selected == "Medical Report Analyzer":

    page_header(
        "VISUAL HEALTH INTELLIGENCE",
        "Medical Report Analyzer",
        "Upload a supported medical image or report and receive a general AI-generated explanation."
    )

    st.warning(
        "⚠️ This tool is for educational explanation only. "
        "It must not be used as a medical diagnosis."
    )

    section_header("UPLOAD MEDICAL IMAGE")

    uploaded_file = st.file_uploader(
        "Choose an image",
        type=[
            "png",
            "jpg",
            "jpeg"
        ]
    )

    if uploaded_file is not None:

        st.image(
            uploaded_file,
            caption="Uploaded Image",
            use_container_width=True
        )

        if st.button("🔍 ANALYZE IMAGE"):

            with st.spinner(
                "AI vision engine analyzing image..."
            ):

                image_bytes = uploaded_file.getvalue()

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        """
Explain this medical image in simple language.

Do not diagnose.

Describe only general visible information that can reasonably be explained from the image.

Suggest consulting an appropriate healthcare professional when necessary.
""",
                        {
                            "mime_type": uploaded_file.type,
                            "data": image_bytes,
                        },
                    ],
                )

            st.success(
                "Analysis Complete"
            )

            st.markdown(
                '<div class="glass-card">',
                unsafe_allow_html=True
            )

            st.write(response.text)

            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )

            st.info(
                "⚠️ This explanation is for educational purposes only and is not a medical diagnosis."
            )


# ============================================================
# HEALTH DASHBOARD
# ============================================================

elif selected == "Health Dashboard":

    page_header(
        "HEALTH INTELLIGENCE CENTER",
        "Health Dashboard",
        "Your central command center for HealthMate AI tools and capabilities."
    )

    section_header("SYSTEM OVERVIEW")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card(
            "🤖",
            "AI FEATURES",
            "8+"
        )

    with col2:
        metric_card(
            "⚡",
            "HEALTH TOOLS",
            "12"
        )

    with col3:
        metric_card(
            "📄",
            "PDF REPORTS",
            "READY"
        )

    with col4:
        metric_card(
            "●",
            "SYSTEM",
            "ONLINE"
        )

    section_header("MODULE STATUS")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.success(
            "✓ BMI Calculator — ONLINE"
        )

    with col2:

        st.success(
            "✓ Water Intake — ONLINE"
        )

    with col3:

        st.success(
            "✓ Diet Planner — ONLINE"
        )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.success(
            "✓ Symptom Checker — ONLINE"
        )

    with col2:

        st.success(
            "✓ Medicine Info — ONLINE"
        )

    with col3:

        st.success(
            "✓ Calorie Intelligence — ONLINE"
        )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.success(
            "✓ Exercise Planner — ONLINE"
        )

    with col2:

        st.success(
            "✓ Sleep Intelligence — ONLINE"
        )

    with col3:

        st.success(
            "✓ Medical Vision — ONLINE"
        )

    section_header("HEALTHMATE INTELLIGENCE")

    st.info(
        "HealthMate AI combines multiple AI-powered wellness tools "
        "into a single health intelligence platform."
    )


# ============================================================
# ABOUT
# ============================================================

elif selected == "About":

    page_header(
        "SYSTEM INFORMATION",
        "About HealthMate",
        "A student-built AI health and wellness platform designed to combine useful health utilities with artificial intelligence."
    )

    section_header("TECHNOLOGY STACK")

    col1, col2, col3 = st.columns(3)

    with col1:
        feature_card(
            "🐍",
            "Python",
            "Core application language powering the HealthMate system."
        )

    with col2:
        feature_card(
            "◈",
            "Streamlit",
            "Interactive web application framework used for the interface."
        )

    with col3:
        feature_card(
            "🤖",
            "Google Gemini",
            "AI engine powering HealthMate's intelligent features."
        )

    section_header("DEVELOPER")

    st.markdown(
        """
        <div class="glass-card">

            <div style="
                font-family:'Orbitron';
                font-size:22px;
                color:#8fffee;
            ">
                BHAVESH THAKUR
            </div>

            <div style="
                margin-top:10px;
                color:#71859d;
            ">
                Creator & Developer
            </div>

            <div style="
                margin-top:20px;
                color:#9aafc5;
                line-height:1.7;
            ">
                HealthMate AI is an educational project exploring
                the combination of Python, artificial intelligence
                and modern health-focused user interfaces.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.info(
        "HealthMate AI is an educational project and does not provide professional medical diagnosis or treatment."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

        <strong>HEALTHMATE AI</strong>
        <br>

        AI Health Intelligence Platform

        <br><br>

        © 2026 HealthMate AI
        • Developed by <strong>Bhavesh Thakur</strong>
        • Powered by Google Gemini

        <br><br>

        <span style="font-size:10px;">
            EDUCATIONAL PURPOSE ONLY
        </span>

    </div>
    """,
    unsafe_allow_html=True
)
