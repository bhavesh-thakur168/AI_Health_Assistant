import streamlit as st
from streamlit_option_menu import option_menu
from google import genai
from report import create_pdf


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="HealthMate AI",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)


# =========================================================
# FUTURISTIC CSS
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@500;600;700;800&display=swap');


/* ========================================================
   GLOBAL
======================================================== */

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 10% 10%,
            rgba(0, 229, 255, 0.08),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 20%,
            rgba(139, 92, 246, 0.10),
            transparent 30%
        ),
        radial-gradient(
            circle at 50% 100%,
            rgba(0, 255, 170, 0.05),
            transparent 30%
        ),
        #050816;

    color: #e8f1ff;
}


/* ========================================================
   MAIN CONTAINER
======================================================== */

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}


/* ========================================================
   SIDEBAR
======================================================== */

section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            rgba(7, 14, 35, 0.99),
            rgba(4, 8, 22, 0.99)
        );

    border-right: 1px solid rgba(0, 229, 255, 0.18);
}

section[data-testid="stSidebar"] > div {
    padding-top: 1rem;
}


/* Sidebar Branding */

.sidebar-brand {
    text-align: center;
    padding: 10px 5px 25px 5px;
}

.sidebar-logo {
    font-size: 48px;
    color: #00e5ff;

    text-shadow:
        0 0 10px #00e5ff,
        0 0 25px rgba(0, 229, 255, 0.7);

    margin-bottom: 8px;
}

.sidebar-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 19px;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 1px;
}

.sidebar-subtitle {
    color: #60769d;
    font-size: 10px;
    letter-spacing: 1px;
    margin-top: 6px;
}


/* Navigation */

div[data-testid="stSidebar"] .nav-link {
    border-radius: 12px !important;
    margin: 4px 0 !important;

    color: #9aaac7 !important;

    transition:
        all 0.25s ease !important;
}

div[data-testid="stSidebar"] .nav-link:hover {
    color: #ffffff !important;

    background:
        rgba(0, 229, 255, 0.08) !important;

    transform:
        translateX(3px);
}

div[data-testid="stSidebar"] .nav-link-selected {
    background:
        linear-gradient(
            90deg,
            rgba(0, 229, 255, 0.20),
            rgba(139, 92, 246, 0.18)
        ) !important;

    color: #00e5ff !important;

    border:
        1px solid rgba(0, 229, 255, 0.20);

    box-shadow:
        0 0 25px rgba(0, 229, 255, 0.07),
        inset 0 0 20px rgba(0, 229, 255, 0.03);
}


/* Sidebar System Status */

.sidebar-system {
    margin-top: 25px;

    padding: 14px;

    border-radius: 14px;

    background:
        rgba(0, 229, 255, 0.035);

    border:
        1px solid rgba(0, 229, 255, 0.10);

    text-align: center;
}

.sidebar-online {
    color: #00ffb3;
    font-size: 11px;
    font-weight: 700;
}

.sidebar-engine {
    color: #586b91;
    font-size: 10px;
    margin-top: 5px;
}


/* ========================================================
   HEADINGS
======================================================== */

h1 {
    font-family: 'Orbitron', sans-serif !important;
    color: #ffffff !important;
}

h2, h3 {
    color: #e3edff !important;
}


/* ========================================================
   HERO
======================================================== */

.hero {
    position: relative;

    overflow: hidden;

    padding: 45px;

    border-radius: 28px;

    margin-bottom: 28px;

    background:
        linear-gradient(
            135deg,
            rgba(8, 22, 48, 0.96),
            rgba(22, 12, 52, 0.92)
        );

    border:
        1px solid rgba(0, 229, 255, 0.17);

    box-shadow:
        0 30px 100px rgba(0, 0, 0, 0.35),
        0 0 80px rgba(0, 229, 255, 0.05);
}

.hero::before {
    content: "";

    position: absolute;

    width: 350px;
    height: 350px;

    right: -100px;
    top: -130px;

    border-radius: 50%;

    background:
        rgba(0, 229, 255, 0.10);

    filter:
        blur(70px);
}

.hero::after {
    content: "";

    position: absolute;

    width: 280px;
    height: 280px;

    left: 35%;
    bottom: -170px;

    border-radius: 50%;

    background:
        rgba(139, 92, 246, 0.13);

    filter:
        blur(70px);
}


/* Hero Status */

.status {
    display: inline-flex;

    align-items: center;

    gap: 8px;

    padding: 7px 13px;

    border-radius: 50px;

    color: #00ffb3;

    background:
        rgba(0, 255, 179, 0.07);

    border:
        1px solid rgba(0, 255, 179, 0.20);

    font-size: 11px;

    font-weight: 600;

    letter-spacing: 0.5px;

    margin-bottom: 20px;
}

.status-dot {
    width: 7px;
    height: 7px;

    background: #00ffb3;

    border-radius: 50%;

    box-shadow:
        0 0 12px #00ffb3;
}


/* Hero Title */

.hero-title {
    position: relative;

    z-index: 2;

    font-family: 'Orbitron', sans-serif;

    font-size: clamp(30px, 5vw, 60px);

    font-weight: 800;

    line-height: 1.05;

    margin-bottom: 18px;

    background:
        linear-gradient(
            90deg,
            #ffffff,
            #00e5ff,
            #8b5cf6
        );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}


/* Hero Subtitle */

.hero-subtitle {
    position: relative;

    z-index: 2;

    color: #8fa4c9;

    font-size: 16px;

    max-width: 760px;

    line-height: 1.7;
}


/* ========================================================
   GLASS CARDS
======================================================== */

.glass-card {
    background:
        linear-gradient(
            135deg,
            rgba(17, 27, 55, 0.82),
            rgba(7, 13, 31, 0.72)
        );

    border:
        1px solid rgba(115, 145, 200, 0.15);

    border-radius: 20px;

    padding: 25px;

    box-shadow:
        0 20px 60px rgba(0, 0, 0, 0.30),
        inset 0 1px 0 rgba(255,255,255,0.04);

    backdrop-filter: blur(18px);

    margin-bottom: 20px;
}

.glass-card:hover {
    border-color:
        rgba(0, 229, 255, 0.25);
}


/* ========================================================
   FEATURE CARDS
======================================================== */

.feature-card {
    min-height: 165px;

    padding: 24px;

    margin-bottom: 20px;

    border-radius: 18px;

    background:
        linear-gradient(
            145deg,
            rgba(15, 29, 59, 0.82),
            rgba(7, 14, 31, 0.78)
        );

    border:
        1px solid rgba(110, 140, 190, 0.13);

    transition:
        all 0.25s ease;
}

.feature-card:hover {
    transform:
        translateY(-5px);

    border-color:
        rgba(0, 229, 255, 0.30);

    box-shadow:
        0 20px 50px rgba(0, 229, 255, 0.07);
}

.feature-icon {
    font-size: 30px;
    margin-bottom: 12px;
}

.feature-title {
    color: #e9f4ff;
    font-weight: 700;
    font-size: 16px;
}

.feature-description {
    color: #778aaa;
    font-size: 13px;
    line-height: 1.6;
    margin-top: 7px;
}


/* ========================================================
   METRICS
======================================================== */

[data-testid="stMetric"] {
    background:
        linear-gradient(
            135deg,
            rgba(15, 28, 58, 0.85),
            rgba(8, 15, 35, 0.80)
        );

    border:
        1px solid rgba(0, 229, 255, 0.12);

    padding: 20px;

    border-radius: 18px;

    box-shadow:
        0 15px 40px rgba(0,0,0,0.20);
}

[data-testid="stMetricLabel"] {
    color: #8293b7 !important;
}

[data-testid="stMetricValue"] {
    color: #00e5ff !important;

    font-family:
        'Orbitron',
        sans-serif;
}


/* ========================================================
   BUTTONS
======================================================== */

.stButton > button {
    width: 100%;

    min-height: 48px;

    border-radius: 12px;

    border:
        1px solid rgba(0, 229, 255, 0.30);

    color: #eafaff;

    font-weight: 700;

    background:
        linear-gradient(
            135deg,
            rgba(0, 229, 255, 0.15),
            rgba(139, 92, 246, 0.15)
        );

    box-shadow:
        0 0 20px rgba(0, 229, 255, 0.05);

    transition:
        all 0.25s ease;
}

.stButton > button:hover {
    color: #ffffff;

    border-color:
        #00e5ff;

    box-shadow:
        0 0 25px rgba(0, 229, 255, 0.20);

    transform:
        translateY(-2px);
}


/* ========================================================
   INPUTS
======================================================== */

.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    background:
        rgba(7, 14, 31, 0.85) !important;

    color:
        #eaf3ff !important;

    border:
        1px solid rgba(90, 120, 170, 0.22) !important;

    border-radius:
        12px !important;
}

.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus {
    border-color:
        #00e5ff !important;

    box-shadow:
        0 0 15px rgba(0, 229, 255, 0.10) !important;
}


/* Selectbox */

div[data-baseweb="select"] > div {
    background:
        rgba(7, 14, 31, 0.85) !important;

    border:
        1px solid rgba(90, 120, 170, 0.22) !important;

    border-radius:
        12px !important;
}


/* ========================================================
   CHAT
======================================================== */

[data-testid="stChatMessage"] {
    background:
        linear-gradient(
            135deg,
            rgba(15, 27, 53, 0.75),
            rgba(7, 14, 31, 0.70)
        );

    border:
        1px solid rgba(100, 130, 180, 0.12);

    border-radius:
        18px;

    margin-bottom:
        12px;
}


/* ========================================================
   ALERTS
======================================================== */

div[data-testid="stAlert"] {
    border-radius: 14px;
}


/* ========================================================
   FILE UPLOADER
======================================================== */

[data-testid="stFileUploader"] {
    background:
        rgba(7, 14, 31, 0.50);

    border:
        1px dashed rgba(0, 229, 255, 0.25);

    border-radius:
        16px;

    padding:
        10px;
}


/* ========================================================
   FOOTER
======================================================== */

.footer {
    text-align: center;

    padding:
        35px 10px;

    color:
        #5d6e91;

    font-size:
        12px;
}

.footer strong {
    color:
        #00e5ff;
}


/* ========================================================
   SCROLLBAR
======================================================== */

::-webkit-scrollbar {
    width: 7px;
}

::-webkit-scrollbar-track {
    background:
        #050816;
}

::-webkit-scrollbar-thumb {
    background:
        #172640;

    border-radius:
        10px;
}

::-webkit-scrollbar-thumb:hover {
    background:
        #00e5ff;
}


/* ========================================================
   MOBILE
======================================================== */

@media (max-width: 768px) {

    .hero {
        padding: 28px;
    }

    .hero-title {
        font-size: 34px;
    }

    .hero-subtitle {
        font-size: 14px;
    }

}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def render_hero(status, title, subtitle):
    """
    Render a futuristic hero section.
    """

    st.markdown(
        f"""
        <div class="hero">

            <div class="status">
                <span class="status-dot"></span>
                {status}
            </div>

            <div class="hero-title">
                {title}
            </div>

            <div class="hero-subtitle">
                {subtitle}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


def render_ai_result(title, text):
    """
    Render AI response inside a futuristic card.
    """

    st.markdown(
        f"""
        <div class="glass-card">

            <div style="
                color:#00e5ff;
                font-family:Orbitron;
                font-size:15px;
                margin-bottom:15px;
            ">
                ◈ {title}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.write(text)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">

            <div class="sidebar-logo">
                ◈
            </div>

            <div class="sidebar-title">
                HEALTHMATE AI
            </div>

            <div class="sidebar-subtitle">
                INTELLIGENT HEALTH SYSTEM
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
            "house",
            "robot",
            "capsule",
            "activity",
            "cup-straw",
            "egg-fried",
            "person-running",
            "fire",
            "moon-stars",
            "file-earmark-medical",
            "speedometer2",
            "info-circle"
        ],

        default_index=0
    )

    st.markdown(
        """
        <div class="sidebar-system">

            <div class="sidebar-online">
                ● SYSTEM ONLINE
            </div>

            <div class="sidebar-engine">
                Gemini AI Engine
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# HOME
# =========================================================

if selected == "Home":

    render_hero(
        "AI HEALTH SYSTEM ONLINE",
        "Your Intelligent<br>Health Companion",
        """
        HealthMate AI combines artificial intelligence with
        modern wellness tools to help you understand your
        health, fitness, nutrition and lifestyle.
        """
    )

    # Metrics

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "AI ENGINE",
            "Gemini",
            "ONLINE"
        )

    with col2:
        st.metric(
            "HEALTH TOOLS",
            "12",
            "ACTIVE"
        )

    with col3:
        st.metric(
            "REPORTS",
            "PDF",
            "READY"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        "### ⚡ AI Health Modules"
    )

    features = [
        (
            "🤖",
            "AI Symptom Checker",
            "Describe symptoms and receive general AI-powered health guidance."
        ),

        (
            "💊",
            "Medicine Intelligence",
            "Explore general information, precautions and common side effects."
        ),

        (
            "📊",
            "BMI Analytics",
            "Calculate BMI and understand general weight categories."
        ),

        (
            "💧",
            "Hydration Engine",
            "Estimate your daily water requirements."
        ),

        (
            "🍎",
            "AI Diet Planner",
            "Generate lifestyle-focused meal ideas."
        ),

        (
            "🏃",
            "Fitness Planner",
            "Build a simple AI-generated exercise routine."
        )
    ]

    cols = st.columns(3)

    for i, (icon, title, description) in enumerate(features):

        with cols[i % 3]:

            st.markdown(
                f"""
                <div class="feature-card">

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
        "⚠️ HealthMate AI provides educational wellness information "
        "and is not a replacement for professional medical advice."
    )


# =========================================================
# AI SYMPTOM CHECKER
# =========================================================

elif selected == "AI Symptom Checker":

    render_hero(
        "AI HEALTH ASSISTANT",
        "Symptom<br>Intelligence",
        """
        Describe your symptoms and receive general educational
        health information powered by Gemini AI.
        """
    )

    st.markdown(
        """
        <div class="glass-card">

            <div style="
                color:#00e5ff;
                font-weight:700;
                font-family:Orbitron;
            ">
                ◉ AI INPUT
            </div>

            <div style="
                color:#7184a7;
                margin-top:10px;
                font-size:13px;
            ">
                Describe what you're experiencing in natural language.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

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

            with st.spinner(
                "AI engine analyzing symptoms..."
            ):

                prompt = f"""
You are an AI Health Assistant.

Symptoms:
{symptoms}

Provide general educational health information.

Do NOT provide a definitive diagnosis.

Explain possible general causes or considerations,
basic self-care information when appropriate,
and when professional medical attention may be appropriate.

If symptoms could represent an emergency,
clearly advise seeking urgent medical care.
"""

                response = client.models.generate_content(
                    model="gemini-3.1-flash-lite",
                    contents=prompt
                )

            with st.chat_message("assistant"):

                st.write(
                    response.text
                )

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
                    label="📄 DOWNLOAD HEALTH REPORT",
                    data=pdf_data,
                    file_name="Health_Report.pdf",
                    mime="application/pdf"
                )

            except Exception as e:

                st.warning(
                    f"PDF generation unavailable: {e}"
                )

            st.info(
                "⚠️ This information is for educational purposes only. "
                "Consult a qualified healthcare professional for medical concerns."
            )


# =========================================================
# MEDICINE INFO
# =========================================================

elif selected == "Medicine Info":

    render_hero(
        "MEDICINE INFORMATION ENGINE",
        "Medicine<br>Intelligence",
        """
        Get simple educational information about medicines,
        common uses, precautions and side effects.
        """
    )

    medicine = st.text_input(
        "Medicine Name",
        placeholder="Example: Paracetamol"
    )

    if st.button(
        "🔎 ANALYZE MEDICINE"
    ):

        if medicine.strip() == "":

            st.warning(
                "Please enter a medicine name."
            )

        else:

            with st.spinner(
                "Accessing AI medicine knowledge..."
            ):

                prompt = f"""
Provide general educational information about this medicine.

Medicine:
{medicine}

Include:

- What it is generally used for
- Common side effects
- Precautions
- When to consult a doctor

Keep the language simple.

Do NOT prescribe medicines.
Do NOT recommend dosage.
"""

                response = client.models.generate_content(
                    model="gemini-3.1-flash-lite",
                    contents=prompt
                )

            st.success(
                "INFORMATION READY"
            )

            st.markdown(
                """
                <div class="glass-card">
                """,
                unsafe_allow_html=True
            )

            st.write(
                response.text
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

            st.info(
                "⚠️ Always consult a qualified healthcare professional "
                "before taking medication."
            )


# =========================================================
# BMI CALCULATOR
# =========================================================

elif selected == "BMI Calculator":

    render_hero(
        "BODY METRIC ENGINE",
        "BMI<br>Analytics",
        """
        Calculate your Body Mass Index using your height
        and weight.
        """
    )

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

    if st.button(
        "⚡ CALCULATE BMI"
    ):

        height_m = height / 100

        bmi = weight / (
            height_m * height_m
        )

        st.metric(
            "YOUR BMI",
            f"{bmi:.2f}"
        )

        if bmi < 18.5:

            st.warning(
                "UNDERWEIGHT"
            )

        elif bmi < 25:

            st.success(
                "HEALTHY WEIGHT"
            )

        elif bmi < 30:

            st.warning(
                "OVERWEIGHT"
            )

        else:

            st.error(
                "OBESITY CATEGORY"
            )

        st.info(
            "BMI is a general screening indicator and should not "
            "be used as the only measure of health."
        )


# =========================================================
# WATER INTAKE
# =========================================================

elif selected == "Water Intake":

    render_hero(
        "HYDRATION ENGINE",
        "Hydration<br>Intelligence",
        """
        Estimate a general daily water requirement based
        on body weight.
        """
    )

    weight = st.number_input(
        "Body Weight (kg)",
        min_value=10.0,
        max_value=250.0,
        value=60.0
    )

    if st.button(
        "💧 CALCULATE HYDRATION"
    ):

        water = weight * 35

        litres = water / 1000

        st.metric(
            "DAILY WATER ESTIMATE",
            f"{litres:.2f} L"
        )

        st.success(
            f"💧 Estimated intake: "
            f"{litres:.2f} litres/day"
        )

        st.info(
            "This is a general estimate. Water needs vary depending "
            "on activity, climate and individual health circumstances."
        )


# =========================================================
# DIET PLANNER
# =========================================================

elif selected == "Diet Planner":

    render_hero(
        "NUTRITION AI",
        "AI Diet<br>Planner",
        """
        Generate a simple Indian-style one-day meal plan
        based on your lifestyle goal.
        """
    )

    col1, col2 = st.columns(2)

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
            [
                "Male",
                "Female"
            ]
        )

    goal = st.selectbox(
        "Primary Goal",
        [
            "Weight Loss",
            "Weight Gain",
            "Healthy Lifestyle"
        ]
    )

    if st.button(
        "🍎 GENERATE DIET PLAN"
    ):

        with st.spinner(
            "AI nutrition engine working..."
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

        st.success(
            "DIET PLAN GENERATED"
        )

        st.markdown(
            """
            <div class="glass-card">
            """,
            unsafe_allow_html=True
        )

        st.write(
            response.text
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


# =========================================================
# EXERCISE PLANNER
# =========================================================

elif selected == "Exercise Planner":

    render_hero(
        "FITNESS AI",
        "Exercise<br>Intelligence",
        """
        Generate a simple AI-powered daily exercise routine
        based on your fitness level and goal.
        """
    )

    col1, col2 = st.columns(2)

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

    goal = st.selectbox(
        "Goal",
        [
            "Weight Loss",
            "Muscle Gain",
            "Stay Fit"
        ]
    )

    if st.button(
        "🏃 GENERATE WORKOUT"
    ):

        with st.spinner(
            "Building fitness protocol..."
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
            "WORKOUT GENERATED"
        )

        st.markdown(
            """
            <div class="glass-card">
            """,
            unsafe_allow_html=True
        )

        st.write(
            response.text
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


# =========================================================
# CALORIE CALCULATOR
# =========================================================

elif selected == "Calorie Calculator":

    render_hero(
        "NUTRITION ANALYTICS",
        "Calorie<br>Intelligence",
        """
        Use AI to estimate calories and macronutrients
        from your meal.
        """
    )

    food = st.text_area(
        "Food consumed",
        placeholder=(
            "Example: 2 chapati, dal, rice, salad and milk"
        )
    )

    if st.button(
        "🔥 ANALYZE MEAL"
    ):

        if food.strip() == "":

            st.warning(
                "Please enter your food items."
            )

        else:

            with st.spinner(
                "Calculating nutrition estimate..."
            ):

                prompt = f"""
Estimate calories for the following food.

Food:
{food}

Include:

- Estimated total calories
- Protein
- Carbohydrates
- Fat
- General health assessment
- Suggestions to improve the meal

Clearly state that the result is an estimate.
"""

                response = client.models.generate_content(
                    model="gemini-3.1-flash-lite",
                    contents=prompt
                )

            st.success(
                "NUTRITION ANALYSIS READY"
            )

            st.markdown(
                """
                <div class="glass-card">
                """,
                unsafe_allow_html=True
            )

            st.write(
                response.text
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

            st.info(
                "⚠️ AI calorie estimates may not be completely accurate."
            )


# =========================================================
# SLEEP RECOMMENDATION
# =========================================================

elif selected == "Sleep Recommendation":

    render_hero(
        "SLEEP INTELLIGENCE",
        "Sleep<br>Advisor",
        """
        Explore general sleep recommendations based on
        your age, sleep duration and lifestyle.
        """
    )

    age = st.number_input(
        "Your Age",
        min_value=1,
        max_value=100,
        value=18
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

    if st.button(
        "😴 ANALYZE SLEEP"
    ):

        with st.spinner(
            "Analyzing sleep pattern..."
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

        st.success(
            "SLEEP ANALYSIS READY"
        )

        st.markdown(
            """
            <div class="glass-card">
            """,
            unsafe_allow_html=True
        )

        st.write(
            response.text
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

        st.info(
            "⚠️ General wellness suggestions only; "
            "this is not a medical diagnosis."
        )


# =========================================================
# MEDICAL REPORT ANALYZER
# =========================================================

elif selected == "Medical Report Analyzer":

    render_hero(
        "VISION AI ENGINE",
        "Medical<br>Vision",
        """
        Upload a medical image and receive a general
        educational explanation from Gemini Vision AI.
        """
    )

    st.markdown(
        """
        <div class="glass-card">

            <div style="
                color:#00e5ff;
                font-family:Orbitron;
                font-size:15px;
            ">
                📷 SUPPORTED INPUT
            </div>

            <div style="
                color:#8293b7;
                margin-top:12px;
                line-height:1.8;
            ">
                Medical reports<br>
                Blood test images<br>
                X-ray images<br>
                Skin images
            </div>

            <div style="
                color:#5f7194;
                font-size:11px;
                margin-top:15px;
            ">
                AI does not provide a medical diagnosis.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "Upload Medical Image",
        type=[
            "png",
            "jpg",
            "jpeg"
        ]
    )

    if uploaded_file is not None:

        st.image(
            uploaded_file,
            caption="Uploaded Medical Image",
            use_container_width=True
        )

        if st.button(
            "🔍 ANALYZE IMAGE"
        ):

            with st.spinner(
                "Vision AI analyzing image..."
            ):

                image_bytes = uploaded_file.getvalue()

                response = client.models.generate_content(
                    model="gemini-2.5-flash",

                    contents=[
                        """
Explain this medical image in simple language.

Do not diagnose.

Describe general visible information only.

Mention when professional medical evaluation
may be appropriate.

If the image appears potentially urgent,
recommend seeking appropriate medical care.
""",

                        {
                            "mime_type": uploaded_file.type,
                            "data": image_bytes
                        }
                    ]
                )

            st.success(
                "VISION ANALYSIS COMPLETE"
            )

            st.markdown(
                """
                <div class="glass-card">
                """,
                unsafe_allow_html=True
            )

            st.write(
                response.text
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

            st.info(
                "⚠️ This explanation is educational and "
                "is not a medical diagnosis."
            )


# =========================================================
# HEALTH DASHBOARD
# =========================================================

elif selected == "Health Dashboard":

    render_hero(
        "DASHBOARD ONLINE",
        "Health Command<br>Center",
        """
        Monitor your available AI health and wellness
        tools from one centralized control panel.
        """
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "AI FEATURES",
            "8",
            "ACTIVE"
        )

    with col2:

        st.metric(
            "WELLNESS TOOLS",
            "12",
            "READY"
        )

    with col3:

        st.metric(
            "PDF REPORTS",
            "READY",
            "●"
        )

    with col4:

        st.metric(
            "SYSTEM",
            "ONLINE",
            "100%"
        )

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )

    st.markdown(
        "### 🧠 System Modules"
    )

    modules = [
        ("🟢", "BMI Calculator"),
        ("🟢", "Water Intake"),
        ("🟢", "Diet Planner"),
        ("🟢", "Exercise Planner"),
        ("🟢", "Symptom Checker"),
        ("🟢", "Medicine Info"),
        ("🟢", "Calories"),
        ("🟢", "Sleep Advisor"),
        ("🟢", "Medical Vision"),
        ("🟢", "PDF Reports"),
        ("🟢", "Gemini AI"),
        ("🟢", "Health Analytics")
    ]

    cols = st.columns(4)

    for i, (status, name) in enumerate(modules):

        with cols[i % 4]:

            st.markdown(
                f"""
                <div class="glass-card">

                    <div style="
                        font-size:20px;
                    ">
                        {status}
                    </div>

                    <div style="
                        margin-top:8px;
                        color:#dce9ff;
                        font-weight:700;
                    ">
                        {name}
                    </div>

                    <div style="
                        color:#607394;
                        font-size:10px;
                        margin-top:5px;
                    ">
                        READY FOR USE
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    st.info(
        "HealthMate AI combines multiple AI-powered wellness "
        "tools in one application."
    )


# =========================================================
# ABOUT
# =========================================================

elif selected == "About":

    render_hero(
        "SYSTEM INFORMATION",
        "About<br>HealthMate AI",
        """
        An AI-powered wellness platform built with Python,
        Streamlit and Google's Gemini AI.
        """
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            """
            <div class="glass-card">

                <div style="
                    color:#00e5ff;
                    font-family:Orbitron;
                    font-size:18px;
                    margin-bottom:20px;
                ">
                    ⚙️ TECHNOLOGY STACK
                </div>

                <div style="
                    color:#dce9ff;
                    line-height:2;
                ">

                    <b>Python</b><br>
                    Core application logic.

                    <br><br>

                    <b>Streamlit</b><br>
                    Interactive web application framework.

                    <br><br>

                    <b>Google Gemini</b><br>
                    Artificial intelligence engine.

                    <br><br>

                    <b>Google GenAI SDK</b><br>
                    AI model integration.

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            """
            <div class="glass-card">

                <div style="
                    color:#00e5ff;
                    font-family:Orbitron;
                    font-size:18px;
                    margin-bottom:20px;
                ">
                    👨‍💻 DEVELOPER
                </div>

                <div style="
                    font-family:Orbitron;
                    font-size:28px;
                    color:#ffffff;
                ">
                    Bhavesh Thakur
                </div>

                <div style="
                    margin-top:20px;
                    color:#7f92b5;
                    line-height:1.8;
                ">
                    HealthMate AI is designed as an educational
                    health and wellness technology project.

                    <br><br>

                    The platform combines AI-powered tools
                    with simple health and fitness utilities.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )

    st.warning(
        "⚠️ HealthMate AI is an educational project and "
        "should not be used as a substitute for professional "
        "medical diagnosis or treatment."
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">

        <strong>◈ HEALTHMATE AI</strong>

        <br><br>

        Intelligent Health • Wellness • Artificial Intelligence

        <br><br>

        © 2026 HealthMate AI
        • Developed by Bhavesh Thakur

        <br>

        Educational Purpose Only

    </div>
    """,
    unsafe_allow_html=True
)
