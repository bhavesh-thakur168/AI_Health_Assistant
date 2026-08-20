import streamlit as st
from streamlit_option_menu import option_menu
from google import genai
from report import create_pdf

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="HealthMate AI",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

# =========================================================
# FUTURISTIC UI
# =========================================================

st.markdown("""
<style>

/* ---------- GLOBAL ---------- */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(0, 229, 255, 0.08), transparent 30%),
        radial-gradient(circle at 90% 20%, rgba(139, 92, 246, 0.10), transparent 30%),
        radial-gradient(circle at 50% 100%, rgba(0, 255, 170, 0.05), transparent 30%),
        #050816;
    color: #e8f1ff;
}

/* ---------- SIDEBAR ---------- */

section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            rgba(7, 14, 35, 0.98),
            rgba(4, 8, 22, 0.98)
        );
    border-right: 1px solid rgba(0, 229, 255, 0.18);
}

section[data-testid="stSidebar"] > div {
    padding-top: 1rem;
}

/* Sidebar title */

.sidebar-brand {
    text-align: center;
    padding: 15px 5px 25px 5px;
}

.sidebar-brand .logo {
    font-size: 42px;
    filter: drop-shadow(0 0 15px #00e5ff);
}

.sidebar-brand h2 {
    margin: 8px 0 2px 0;
    font-family: 'Orbitron', sans-serif;
    font-size: 20px;
    color: #00e5ff;
    letter-spacing: 1px;
}

.sidebar-brand p {
    color: #7182a8;
    font-size: 11px;
}

/* Option menu */

div[data-testid="stSidebar"] .nav-link {
    border-radius: 12px !important;
    margin: 4px 0 !important;
    color: #8796b8 !important;
    transition: all 0.25s ease !important;
}

div[data-testid="stSidebar"] .nav-link:hover {
    color: #ffffff !important;
    background: rgba(0, 229, 255, 0.08) !important;
    transform: translateX(3px);
}

div[data-testid="stSidebar"] .nav-link-selected {
    background:
        linear-gradient(
            90deg,
            rgba(0, 229, 255, 0.18),
            rgba(139, 92, 246, 0.15)
        ) !important;
    color: #00e5ff !important;
    border: 1px solid rgba(0, 229, 255, 0.20);
    box-shadow:
        0 0 20px rgba(0, 229, 255, 0.08),
        inset 0 0 20px rgba(0, 229, 255, 0.03);
}

/* ---------- MAIN CONTAINER ---------- */

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* ---------- HEADINGS ---------- */

h1 {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 38px !important;
    font-weight: 700 !important;
    color: #f4f9ff !important;
    letter-spacing: -1px;
}

h2, h3 {
    color: #dce9ff !important;
}

.hero-title {
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(32px, 5vw, 62px);
    font-weight: 800;
    line-height: 1.05;
    margin-bottom: 12px;
    background: linear-gradient(
        90deg,
        #ffffff,
        #00e5ff,
        #8b5cf6
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    color: #8fa4c9;
    font-size: 17px;
    max-width: 700px;
    line-height: 1.7;
}

/* ---------- GLASS CARDS ---------- */

.glass-card {
    background:
        linear-gradient(
            135deg,
            rgba(17, 27, 55, 0.82),
            rgba(7, 13, 31, 0.72)
        );
    border: 1px solid rgba(115, 145, 200, 0.15);
    border-radius: 20px;
    padding: 25px;
    box-shadow:
        0 20px 60px rgba(0, 0, 0, 0.30),
        inset 0 1px 0 rgba(255,255,255,0.04);
    backdrop-filter: blur(18px);
    margin-bottom: 20px;
}

.glass-card:hover {
    border-color: rgba(0, 229, 255, 0.25);
}

/* ---------- HERO ---------- */

.hero {
    position: relative;
    overflow: hidden;
    padding: 45px;
    border-radius: 28px;
    margin-bottom: 28px;
    background:
        linear-gradient(
            135deg,
            rgba(8, 22, 48, 0.94),
            rgba(22, 12, 52, 0.90)
        );
    border: 1px solid rgba(0, 229, 255, 0.16);
    box-shadow:
        0 30px 100px rgba(0,0,0,.35),
        0 0 80px rgba(0,229,255,.05);
}

.hero::before {
    content: "";
    position: absolute;
    width: 350px;
    height: 350px;
    right: -100px;
    top: -130px;
    border-radius: 50%;
    background: rgba(0,229,255,.10);
    filter: blur(70px);
}

.hero::after {
    content: "";
    position: absolute;
    width: 250px;
    height: 250px;
    left: 35%;
    bottom: -150px;
    border-radius: 50%;
    background: rgba(139,92,246,.12);
    filter: blur(70px);
}

/* ---------- STATUS BADGE ---------- */

.status {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 7px 13px;
    border-radius: 50px;
    color: #00ffb3;
    background: rgba(0,255,179,.07);
    border: 1px solid rgba(0,255,179,.20);
    font-size: 12px;
    margin-bottom: 20px;
}

.status-dot {
    width: 7px;
    height: 7px;
    background: #00ffb3;
    border-radius: 50%;
    box-shadow: 0 0 12px #00ffb3;
}

/* ---------- METRICS ---------- */

[data-testid="stMetric"] {
    background:
        linear-gradient(
            135deg,
            rgba(15, 28, 58, .85),
            rgba(8, 15, 35, .80)
        );
    border: 1px solid rgba(0,229,255,.12);
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 15px 40px rgba(0,0,0,.20);
}

[data-testid="stMetricLabel"] {
    color: #8293b7 !important;
}

[data-testid="stMetricValue"] {
    color: #00e5ff !important;
    font-family: 'Orbitron', sans-serif;
}

/* ---------- BUTTONS ---------- */

.stButton > button {
    width: 100%;
    min-height: 48px;
    border-radius: 12px;
    border: 1px solid rgba(0,229,255,.30);
    color: #eafaff;
    font-weight: 700;
    background:
        linear-gradient(
            135deg,
            rgba(0,229,255,.15),
            rgba(139,92,246,.15)
        );
    box-shadow:
        0 0 20px rgba(0,229,255,.05);
    transition: all .25s ease;
}

.stButton > button:hover {
    color: #ffffff;
    border-color: #00e5ff;
    box-shadow:
        0 0 25px rgba(0,229,255,.20);
    transform: translateY(-2px);
}

/* ---------- INPUTS ---------- */

.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"],
.stSlider {
    border-radius: 12px !important;
}

.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    background: rgba(7,14,31,.85) !important;
    color: #eaf3ff !important;
    border: 1px solid rgba(90,120,170,.22) !important;
}

.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus {
    border-color: #00e5ff !important;
    box-shadow: 0 0 15px rgba(0,229,255,.10) !important;
}

/* ---------- CHAT ---------- */

[data-testid="stChatMessage"] {
    background:
        linear-gradient(
            135deg,
            rgba(15,27,53,.75),
            rgba(7,14,31,.70)
        );
    border: 1px solid rgba(100,130,180,.12);
    border-radius: 18px;
    margin-bottom: 12px;
}

/* ---------- ALERTS ---------- */

div[data-testid="stAlert"] {
    border-radius: 14px;
    background: rgba(10,20,40,.70);
}

/* ---------- DIVIDER ---------- */

hr {
    border-color: rgba(100,130,180,.12) !important;
}

/* ---------- FEATURE CARDS ---------- */

.feature-card {
    min-height: 150px;
    padding: 24px;
    border-radius: 18px;
    background:
        linear-gradient(
            145deg,
            rgba(15,29,59,.82),
            rgba(7,14,31,.78)
        );
    border: 1px solid rgba(110,140,190,.13);
    transition: all .25s ease;
}

.feature-card:hover {
    transform: translateY(-5px);
    border-color: rgba(0,229,255,.30);
    box-shadow: 0 20px 50px rgba(0,229,255,.07);
}

.feature-icon {
    font-size: 30px;
    margin-bottom: 10px;
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
}

/* ---------- FOOTER ---------- */

.footer {
    text-align: center;
    padding: 30px 10px;
    color: #5d6e91;
    font-size: 12px;
}

.footer strong {
    color: #00e5ff;
}

/* ---------- SCROLLBAR ---------- */

::-webkit-scrollbar {
    width: 7px;
}

::-webkit-scrollbar-track {
    background: #050816;
}

::-webkit-scrollbar-thumb {
    background: #172640;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #00e5ff;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("""
    <div class="sidebar-brand">
        <div class="logo">◈</div>
        <h2>HEALTHMATE AI</h2>
        <p>INTELLIGENT HEALTH SYSTEM</p>
    </div>
    """, unsafe_allow_html=True)

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
        default_index=0,
    )

    st.markdown("""
    <div style="
        margin-top:30px;
        padding:14px;
        border-radius:14px;
        background:rgba(0,229,255,.04);
        border:1px solid rgba(0,229,255,.10);
        text-align:center;
    ">
        <div style="color:#00ffb3;font-size:11px;">
            ● SYSTEM ONLINE
        </div>
        <div style="color:#596b8e;font-size:10px;margin-top:5px;">
            Gemini AI Engine
        </div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# HOME
# =========================================================

if selected == "Home":

    st.markdown("""
    <div class="hero">

        <div class="status">
            <span class="status-dot"></span>
            AI HEALTH SYSTEM ONLINE
        </div>

        <div class="hero-title">
            Your Intelligent<br>
            Health Companion
        </div>

        <div class="hero-subtitle">
            HealthMate AI combines artificial intelligence with
            modern wellness tools to help you understand your
            health, fitness, nutrition and lifestyle.
        </div>

    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("AI ENGINE", "Gemini", "ONLINE")

    with col2:
        st.metric("HEALTH TOOLS", "12", "ACTIVE")

    with col3:
        st.metric("REPORTS", "PDF", "READY")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### ⚡ AI Health Modules")

    features = [
        ("🤖", "AI Symptom Checker",
         "Describe symptoms and receive general AI-powered health guidance."),

        ("💊", "Medicine Intelligence",
         "Explore general information, precautions and common side effects."),

        ("📊", "BMI Analytics",
         "Calculate BMI and understand general weight categories."),

        ("💧", "Hydration Engine",
         "Estimate your daily water requirements."),

        ("🍎", "AI Diet Planner",
         "Generate personalized lifestyle-focused meal ideas."),

        ("🏃", "Fitness Planner",
         "Build a simple AI-generated exercise routine.")
    ]

    cols = st.columns(3)

    for i, (icon, title, description) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">{icon}</div>
                <div class="feature-title">{title}</div>
                <div class="feature-description">
                    {description}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.warning(
        "⚠️ HealthMate AI provides educational wellness information "
        "and is not a replacement for professional medical advice."
    )


# =========================================================
# HEALTH DASHBOARD
# =========================================================

elif selected == "Health Dashboard":

    st.markdown("""
    <div class="hero">
        <div class="status">
            <span class="status-dot"></span>
            DASHBOARD ONLINE
        </div>

        <div class="hero-title">
            Health Command Center
        </div>

        <div class="hero-subtitle">
            Monitor your available AI health tools from one futuristic
            control panel.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("AI FEATURES", "8", "ACTIVE")

    with c2:
        st.metric("WELLNESS TOOLS", "6", "READY")

    with c3:
        st.metric("PDF REPORTS", "READY", "●")

    with c4:
        st.metric("SYSTEM", "ONLINE", "100%")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 🧠 System Modules")

    modules = [
        ("🟢", "BMI Calculator"),
        ("🟢", "Water Intake"),
        ("🟢", "Diet Planner"),
        ("🟢", "Exercise Planner"),
        ("🟢", "Symptom Checker"),
        ("🟢", "Medicine Info"),
        ("🟢", "Calories"),
        ("🟢", "Sleep Advisor"),
    ]

    cols = st.columns(4)

    for i, (status, name) in enumerate(modules):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="glass-card">
                <div style="font-size:20px">{status}</div>
                <div style="
                    margin-top:8px;
                    color:#dce9ff;
                    font-weight:700;
                ">
                    {name}
                </div>
                <div style="
                    color:#607394;
                    font-size:11px;
                    margin-top:5px;
                ">
                    READY FOR USE
                </div>
            </div>
            """, unsafe_allow_html=True)


# =========================================================
# AI SYMPTOM CHECKER
# =========================================================

elif selected == "AI Symptom Checker":

    st.markdown("""
    <div class="hero">
        <div class="status">
            <span class="status-dot"></span>
            AI DIAGNOSTIC ASSISTANT
        </div>

        <div class="hero-title">
            Symptom Intelligence
        </div>

        <div class="hero-subtitle">
            Describe what you're experiencing and receive
            general educational health information.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
        <b style="color:#00e5ff;">◉ AI INPUT</b>
        <br><br>
        Describe your symptoms in natural language.
    </div>
    """, unsafe_allow_html=True)

    symptoms = st.chat_input(
        "Describe your symptoms..."
    )

    if symptoms:

        with st.chat_message("user"):
            st.write(symptoms)

        if symptoms.strip() == "":
            st.warning("Please enter your symptoms.")

        else:

            with st.spinner("AI engine analyzing..."):

                prompt = f"""
You are an AI Health Assistant.

Symptoms:
{symptoms}

Provide general educational information.
Do not provide a definitive diagnosis.
Mention when professional medical care may be appropriate.
"""

                response = client.models.generate_content(
                    model="gemini-3.1-flash-lite",
                    contents=prompt
                )

            with st.chat_message("assistant"):
                st.write(response.text)

            pdf_file = create_pdf(
                symptoms,
                response.text
            )

            with open(pdf_file, "rb") as file:
                pdf_data = file.read()

            st.download_button(
                label="📄 DOWNLOAD AI HEALTH REPORT",
                data=pdf_data,
                file_name="Health_Report.pdf",
                mime="application/pdf"
            )

            st.info(
                "⚠️ Educational information only. Consult a qualified "
                "healthcare professional for medical concerns."
            )


# =========================================================
# MEDICINE INFO
# =========================================================

elif selected == "Medicine Info":

    st.markdown("""
    <div class="hero">
        <div class="status">
            <span class="status-dot"></span>
            MEDICINE INFORMATION ENGINE
        </div>

        <div class="hero-title">
            Medicine Intelligence
        </div>

        <div class="hero-subtitle">
            Get simple educational information about medicines.
        </div>
    </div>
    """, unsafe_allow_html=True)

    medicine = st.text_input(
        "Medicine Name",
        placeholder="Example: Paracetamol"
    )

    if st.button("🔎 ANALYZE MEDICINE"):

        if medicine.strip() == "":
            st.warning("Please enter a medicine name.")

        else:

            with st.spinner("Accessing AI medicine knowledge..."):

                prompt = f"""
Provide general educational information about:

Medicine:
{medicine}

Include:

- What it is generally used for
- Common side effects
- Precautions
- When to consult a doctor

Keep the language simple.

Do NOT prescribe medicines or recommend dosage.
"""

                response = client.models.generate_content(
                    model="gemini-3.1-flash-lite",
                    contents=prompt
                )

            st.success("Information Ready")

            st.markdown(
                '<div class="glass-card">',
                unsafe_allow_html=True
            )

            st.write(response.text)

            st.markdown("</div>", unsafe_allow_html=True)

            st.info(
                "⚠️ Always consult a qualified healthcare professional "
                "before taking medication."
            )


# =========================================================
# BMI
# =========================================================

elif selected == "BMI Calculator":

    st.markdown("""
    <div class="hero">
        <div class="status">
            <span class="status-dot"></span>
            BODY METRIC ENGINE
        </div>

        <div class="hero-title">
            BMI Analytics
        </div>

        <div class="hero-subtitle">
            Calculate your Body Mass Index using height and weight.
        </div>
    </div>
    """, unsafe_allow_html=True)

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

    if st.button("⚡ CALCULATE BMI"):

        height_m = height / 100
        bmi = weight / (height_m * height_m)

        st.metric(
            "YOUR BMI",
            f"{bmi:.2f}"
        )

        if bmi < 18.5:
            st.warning("UNDERWEIGHT")

        elif bmi < 25:
            st.success("HEALTHY WEIGHT")

        elif bmi < 30:
            st.warning("OVERWEIGHT")

        else:
            st.error("OBESITY CATEGORY")

        st.info(
            "BMI is a general screening indicator and should not be "
            "used as the only measure of health."
        )


# =========================================================
# WATER
# =========================================================

elif selected == "Water Intake":

    st.markdown("""
    <div class="hero">
        <div class="status">
            <span class="status-dot"></span>
            HYDRATION ENGINE
        </div>

        <div class="hero-title">
            Hydration Intelligence
        </div>

        <div class="hero-subtitle">
            Estimate a general daily water requirement based on body weight.
        </div>
    </div>
    """, unsafe_allow_html=True)

    weight = st.number_input(
        "Body Weight (kg)",
        min_value=10.0,
        max_value=250.0,
        value=60.0
    )

    if st.button("💧 CALCULATE HYDRATION"):

        water = weight * 35
        litres = water / 1000

        st.metric(
            "RECOMMENDED DAILY WATER",
            f"{litres:.2f} L"
        )

        st.success(
            f"💧 Estimated intake: {litres:.2f} litres/day"
        )

        st.info(
            "This is a general estimate. Water needs can vary based on "
            "activity, climate and individual health circumstances."
        )


# =========================================================
# DIET PLANNER
# =========================================================

elif selected == "Diet Planner":

    st.markdown("""
    <div class="hero">
        <div class="status">
            <span class="status-dot"></span>
            NUTRITION AI
        </div>

        <div class="hero-title">
            AI Diet Planner
        </div>

        <div class="hero-subtitle">
            Generate a simple Indian-style one-day meal plan.
        </div>
    </div>
    """, unsafe_allow_html=True)

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
            ["Male", "Female"]
        )

    goal = st.selectbox(
        "Primary Goal",
        [
            "Weight Loss",
            "Weight Gain",
            "Healthy Lifestyle"
        ]
    )

    if st.button("🍎 GENERATE DIET PLAN"):

        with st.spinner("AI nutrition engine working..."):

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
Do not provide medical treatment or extreme dieting advice.
"""

            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt
            )

        st.success("DIET PLAN GENERATED")

        st.markdown(
            '<div class="glass-card">',
            unsafe_allow_html=True
        )

        st.write(response.text)

        st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# EXERCISE
# =========================================================

elif selected == "Exercise Planner":

    st.markdown("""
    <div class="hero">
        <div class="status">
            <span class="status-dot"></span>
            FITNESS AI
        </div>

        <div class="hero-title">
            Exercise Intelligence
        </div>

        <div class="hero-subtitle">
            Build a simple AI-generated daily exercise routine.
        </div>
    </div>
    """, unsafe_allow_html=True)

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

    if st.button("🏃 GENERATE WORKOUT"):

        with st.spinner("Building fitness protocol..."):

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

        st.success("WORKOUT GENERATED")

        st.markdown(
            '<div class="glass-card">',
            unsafe_allow_html=True
        )

        st.write(response.text)

        st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# CALORIE CALCULATOR
# =========================================================

elif selected == "Calorie Calculator":

    st.markdown("""
    <div class="hero">
        <div class="status">
            <span class="status-dot"></span>
            NUTRITION ANALYTICS
        </div>

        <div class="hero-title">
            Calorie Intelligence
        </div>

        <div class="hero-subtitle">
            Use AI to estimate calories and macronutrients from your meal.
        </div>
    </div>
    """, unsafe_allow_html=True)

    food = st.text_area(
        "Food consumed",
        placeholder="Example: 2 chapati, dal, rice, salad and milk"
    )

    if st.button("🔥 ANALYZE MEAL"):

        if food.strip() == "":
            st.warning("Please enter your food items.")

        else:

            with st.spinner("Calculating nutrition estimate..."):

                prompt = f"""
Estimate calories for:

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

            st.success("NUTRITION ANALYSIS READY")

            st.markdown(
                '<div class="glass-card">',
                unsafe_allow_html=True
            )

            st.write(response.text)

            st.markdown("</div>", unsafe_allow_html=True)

            st.info(
                "⚠️ AI calorie estimates may not be completely accurate."
            )


# =========================================================
# SLEEP
# =========================================================

elif selected == "Sleep Recommendation":

    st.markdown("""
    <div class="hero">
        <div class="status">
            <span class="status-dot"></span>
            SLEEP INTELLIGENCE
        </div>

        <div class="hero-title">
            Sleep Advisor
        </div>

        <div class="hero-subtitle">
            Explore general sleep recommendations based on your lifestyle.
        </div>
    </div>
    """, unsafe_allow_html=True)

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

    if st.button("😴 ANALYZE SLEEP"):

        with st.spinner("Analyzing sleep pattern..."):

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

        st.success("SLEEP ANALYSIS READY")

        st.markdown(
            '<div class="glass-card">',
            unsafe_allow_html=True
        )

        st.write(response.text)

        st.markdown("</div>", unsafe_allow_html=True)

        st.info(
            "⚠️ General wellness suggestions only; not a medical diagnosis."
        )


# =========================================================
# MEDICAL REPORT ANALYZER
# =========================================================

elif selected == "Medical Report Analyzer":

    st.markdown("""
    <div class="hero">
        <div class="status">
            <span class="status-dot"></span>
            VISION AI ENGINE
        </div>

        <div class="hero-title">
            Medical Vision
        </div>

        <div class="hero-subtitle">
            Upload an image and receive a general educational explanation.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
        <b style="color:#00e5ff;">
            📷 SUPPORTED INPUT
        </b>
        <br><br>
        Medical reports • Blood test images • X-ray images •
        Skin images
        <br><br>
        <span style="color:#657796;font-size:12px;">
        The AI does not provide a medical diagnosis.
        </span>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload Image",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file is not None:

        st.image(
            uploaded_file,
            caption="Uploaded Medical Image",
            use_container_width=True
        )

        if st.button("🔍 ANALYZE IMAGE"):

            with st.spinner("Vision AI analyzing image..."):

                image_bytes = uploaded_file.getvalue()

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        """
                        Explain this medical image in simple language.

                        Do not diagnose.

                        Describe visible/general information only.
                        Mention when professional medical evaluation
                        may be appropriate.
                        """,
                        {
                            "mime_type": uploaded_file.type,
                            "data": image_bytes,
                        },
                    ],
                )

            st.success("VISION ANALYSIS COMPLETE")

            st.markdown(
                '<div class="glass-card">',
                unsafe_allow_html=True
            )

            st.write(response.text)

            st.markdown("</div>", unsafe_allow_html=True)

            st.info(
                "⚠️ This explanation is educational and is not a medical diagnosis."
            )


# =========================================================
# ABOUT
# =========================================================

elif selected == "About":

    st.markdown("""
    <div class="hero">

        <div class="status">
            <span class="status-dot"></span>
            SYSTEM INFORMATION
        </div>

        <div class="hero-title">
            About HealthMate
        </div>

        <div class="hero-subtitle">
            An AI-powered wellness platform built with Python,
            Streamlit and Google's Gemini AI.
        </div>

    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("""
        <div class="glass-card">

        ### ⚙️ Technology Stack

        **Python**

        Core application logic.

        **Streamlit**

        Interactive web application framework.

        **Google Gemini**

        Artificial intelligence engine.

        **Google GenAI SDK**

        AI model integration.

        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown("""
        <div class="glass-card">

        ### 👨‍💻 Developer

        <div style="
            font-size:30px;
            color:#00e5ff;
            font-family:Orbitron;
        ">
        Bhavesh Thakur
        </div>

        <br>

        HealthMate AI is designed as an educational
        health and wellness technology project.

        </div>
        """, unsafe_allow_html=True)


# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div class="footer">
    <strong>◈ HEALTHMATE AI</strong><br><br>
    Intelligent Health • Wellness • AI<br><br>
    © 2026 HealthMate AI • Developed by Bhavesh Thakur<br>
    Educational Purpose Only
</div>
""", unsafe_allow_html=True)
```
