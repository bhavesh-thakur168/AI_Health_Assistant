import streamlit as st
from google import genai

# Your existing PDF generator
try:
    from report import create_pdf
except Exception:
    create_pdf = None


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="HealthMate AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# SESSION STATE
# =========================================================
if "page" not in st.session_state:
    st.session_state.page = "Home"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "bmi" not in st.session_state:
    st.session_state.bmi = None

if "water" not in st.session_state:
    st.session_state.water = None

if "sleep" not in st.session_state:
    st.session_state.sleep = None

if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

if "accent" not in st.session_state:
    st.session_state.accent = "Cyan"


# =========================================================
# GEMINI CLIENT
# Cached so Streamlit does NOT recreate the client every rerun.
# =========================================================
@st.cache_resource
def get_client():
    try:
        key = st.secrets["GEMINI_API_KEY"]
        return genai.Client(api_key=key)
    except Exception:
        return None


client = get_client()


def ask_ai(prompt, model="gemini-3.1-flash-lite"):
    """One lightweight, reusable Gemini function."""
    if client is None:
        st.error(
            "Gemini API is not configured. Add GEMINI_API_KEY "
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
# LIGHTWEIGHT THEME
# =========================================================
accent_colors = {
    "Cyan": "#25e0d0",
    "Blue": "#4da3ff",
    "Purple": "#a970ff",
    "Green": "#45d483",
}

accent = accent_colors[st.session_state.accent]

if st.session_state.theme == "Dark":
    background = "#070b12"
    surface = "#0d1420"
    surface2 = "#111b29"
    text = "#e9f7f8"
    muted = "#8da0b5"
    border = "#1c2a3b"
else:
    background = "#f3f7fa"
    surface = "#ffffff"
    surface2 = "#eef4f8"
    text = "#172432"
    muted = "#627383"
    border = "#d8e1e8"


# =========================================================
# FAST CSS
# No external fonts, no large animations, no heavy DOM.
# =========================================================
st.markdown(
    f"""
<style>
:root {{
    --bg:{background};
    --surface:{surface};
    --surface2:{surface2};
    --text:{text};
    --muted:{muted};
    --border:{border};
    --accent:{accent};
}}

.stApp {{
    background:var(--bg);
    color:var(--text);
}}

[data-testid="stSidebar"] {{
    background:var(--surface);
    border-right:1px solid var(--border);
}}

[data-testid="stSidebar"] div[data-testid="stRadio"] label {{
    border-radius:9px;
    padding:6px 8px;
}}

[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {{
    background:var(--surface2);
}}

h1,h2,h3 {{
    color:var(--text) !important;
}}

.hero {{
    padding:28px;
    border:1px solid var(--border);
    border-radius:18px;
    background:linear-gradient(135deg,var(--surface),var(--surface2));
    margin-bottom:18px;
}}

.hero small {{
    color:var(--accent);
    font-weight:700;
    letter-spacing:1.5px;
}}

.hero h1 {{
    margin:8px 0 6px 0;
    font-size:clamp(30px,4vw,46px);
}}

.hero p {{
    color:var(--muted);
    margin:0;
    line-height:1.6;
}}

.card {{
    background:var(--surface);
    border:1px solid var(--border);
    border-radius:14px;
    padding:18px;
    min-height:110px;
}}

.card .icon {{
    font-size:24px;
}}

.card .label {{
    color:var(--muted);
    font-size:11px;
    margin-top:8px;
    text-transform:uppercase;
    letter-spacing:1px;
}}

.card .value {{
    color:var(--text);
    font-size:23px;
    font-weight:700;
    margin-top:4px;
}}

.card .desc {{
    color:var(--muted);
    font-size:12px;
    margin-top:5px;
}}

.tool {{
    background:var(--surface);
    border:1px solid var(--border);
    border-radius:14px;
    padding:16px;
    min-height:125px;
}}

.tool b {{
    color:var(--text);
}}

.tool p {{
    color:var(--muted);
    font-size:12px;
    line-height:1.5;
}}

.status {{
    display:inline-flex;
    gap:7px;
    align-items:center;
    color:var(--accent);
    background:rgba(37,224,208,.07);
    border:1px solid rgba(37,224,208,.18);
    padding:6px 10px;
    border-radius:30px;
    font-size:11px;
    font-weight:700;
}}

.dot {{
    width:7px;
    height:7px;
    border-radius:50%;
    background:var(--accent);
}}

.result {{
    background:var(--surface);
    border:1px solid var(--border);
    border-left:3px solid var(--accent);
    border-radius:12px;
    padding:18px;
}}

.footer {{
    text-align:center;
    color:var(--muted);
    font-size:11px;
    padding:28px 0 10px;
    border-top:1px solid var(--border);
    margin-top:35px;
}}

.stButton > button {{
    border-radius:9px;
    border:1px solid var(--border);
    background:var(--surface2);
    color:var(--text);
    font-weight:600;
}}

.stButton > button:hover {{
    border-color:var(--accent);
}}

@media (max-width: 700px) {{
    .hero {{padding:20px;}}
}}
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# UI HELPERS
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


def tool(icon, title, description):
    st.markdown(
        f"""
        <div class="tool">
            <div style="font-size:25px">{icon}</div>
            <div style="margin-top:8px"><b>{title}</b></div>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
            "📄 Download Health Report",
            data=data,
            file_name="Health_Report.pdf",
            mime="application/pdf",
        )
    except Exception as exc:
        st.error(f"PDF creation failed: {exc}")


# =========================================================
# SIDEBAR
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

with st.sidebar:
    st.markdown(
        f"""
        <div style="text-align:center;padding:8px 0 18px;">
            <div style="font-size:38px;">🧬</div>
            <div style="font-size:20px;font-weight:800;color:{accent};">
                HealthMate AI
            </div>
            <div style="font-size:10px;color:{muted};letter-spacing:1px;">
                HEALTH INTELLIGENCE
            </div>
            <br>
            <span class="status">
                <span class="dot"></span>
                SYSTEM ONLINE
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

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

    labels = [f"{page_icons[p]}  {p}" for p in pages]

    current_label = f"{page_icons[st.session_state.page]}  {st.session_state.page}"
    current_index = labels.index(current_label)

    selected_label = st.radio(
        "Navigation",
        labels,
        index=current_index,
        label_visibility="collapsed",
    )

    st.session_state.page = selected_label.split("  ", 1)[1]

    st.markdown("---")
    st.caption("Fast mode • Lightweight UI")

    if client:
        st.success("Gemini: Connected")
    else:
        st.warning("Gemini: API key required")


page = st.session_state.page


# =========================================================
# HOME
# =========================================================
if page == "Home":
    hero(
        "HealthMate AI",
        "Your intelligent health companion for general wellness, calculations, planning and AI-powered educational assistance.",
        "AI HEALTH PLATFORM",
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        card("🤖", "AI Engine", "Gemini", "AI assistance")

    with c2:
        card("🧰", "Tools", "12+", "Health utilities")

    with c3:
        card("📄", "Reports", "PDF", "Downloadable reports")

    with c4:
        card("⚡", "Mode", "FAST", "Lightweight interface")

    st.markdown("### Explore HealthMate")

    r1 = st.columns(3)

    with r1[0]:
        tool("🤖", "AI Symptom Checker", "Describe symptoms for general educational guidance.")

    with r1[1]:
        tool("💊", "Medicine Info", "Learn general information about medicines.")

    with r1[2]:
        tool("📊", "Health Dashboard", "See values calculated during this session.")

    r2 = st.columns(3)

    with r2[0]:
        tool("⚖️", "BMI Calculator", "Calculate BMI from height and weight.")

    with r2[1]:
        tool("💧", "Water Intake", "Estimate general daily water needs.")

    with r2[2]:
        tool("🍎", "Diet Planner", "Generate a simple Indian diet plan.")

    st.info(
        "⚠️ HealthMate AI provides general educational information only and is not a substitute for professional medical advice."
    )


# =========================================================
# AI SYMPTOM CHECKER
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
            with st.spinner("Analyzing..."):
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
                pdf_download(symptoms, answer)

        st.info(
            "⚠️ This response is educational and should not be treated as a diagnosis."
        )


# =========================================================
# MEDICINE INFO
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

            st.info("⚠️ Consult a qualified healthcare professional before taking medicines.")


# =========================================================
# BMI
# =========================================================
elif page == "BMI Calculator":
    hero(
        "BMI Calculator",
        "Calculate your Body Mass Index using height and weight.",
        "BODY METRICS",
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

    if st.button("⚖️ Calculate BMI"):
        height_m = height / 100
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

        a, b = st.columns(2)

        with a:
            card("⚖️", "BMI", f"{bmi:.2f}", "Calculated value")

        with b:
            card("🩺", "Category", category, "General BMI category")

        st.info(
            "BMI is a general screening measure and should not be used as the only measure of health."
        )


# =========================================================
# WATER
# =========================================================
elif page == "Water Intake":
    hero(
        "Water Intake",
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

        a, b = st.columns(2)

        with a:
            card("💧", "Recommended", f"{litres:.2f} L", "General daily estimate")

        with b:
            card("🫗", "Millilitres", f"{water_ml:.0f} ml", "Per day estimate")

        st.info(
            "Your actual needs can vary with climate, activity, diet and health."
        )


# =========================================================
# DIET PLANNER
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

    if st.button("🍎 Generate Diet Plan"):
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


# =========================================================
# EXERCISE PLANNER
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

    if st.button("🏃 Generate Exercise Plan"):
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


# =========================================================
# CALORIE CALCULATOR
# =========================================================
elif page == "Calorie Calculator":
    hero(
        "AI Calorie Calculator",
        "Describe what you ate and get an estimated calorie and nutrition breakdown.",
        "NUTRITION ANALYTICS",
    )

    food = st.text_area(
        "What did you eat today?",
        placeholder="Example: 2 chapati, dal, rice, salad and milk",
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

            st.info("⚠️ AI calorie estimates may be inaccurate because portions vary.")


# =========================================================
# SLEEP
# =========================================================
elif page == "Sleep Recommendation":
    hero(
        "Sleep Recommendation",
        "Get general sleep guidance based on your age, sleep duration and lifestyle.",
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

        st.info(
            "⚠️ These are general wellness suggestions, not a medical diagnosis."
        )


# =========================================================
# MEDICAL REPORT ANALYZER
# =========================================================
elif page == "Medical Report Analyzer":
    hero(
        "Medical Report Analyzer",
        "Upload an image for a general AI explanation. The tool does not diagnose conditions.",
        "VISION AI",
    )

    st.warning(
        "⚠️ Do not use this tool as a diagnostic system. Medical concerns should be reviewed by a qualified professional."
    )

    uploaded_file = st.file_uploader(
        "Choose an image",
        type=["png", "jpg", "jpeg"],
    )

    if uploaded_file is not None:
        st.image(
            uploaded_file,
            caption="Uploaded Image",
            use_container_width=True,
        )

        if st.button("🔍 Analyze Image"):
            if client is None:
                st.error("Gemini API is not configured.")
            else:
                with st.spinner("Analyzing image..."):
                    try:
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=[
                                """
Explain this medical image in simple language.

Do not diagnose.
Do not prescribe treatment.
Describe only general information that can reasonably be explained from the image.
Recommend professional medical review when appropriate.
""",
                                {
                                    "mime_type": uploaded_file.type,
                                    "data": uploaded_file.getvalue(),
                                },
                            ],
                        )

                        answer = response.text

                        st.success("Analysis complete")
                        show_result(answer)

                    except Exception as exc:
                        st.error(f"Image analysis failed: {exc}")

                st.info(
                    "⚠️ This is an educational explanation and is not a medical diagnosis."
                )


# =========================================================
# HEALTH DASHBOARD
# =========================================================
elif page == "Health Dashboard":
    hero(
        "Health Dashboard",
        "A lightweight snapshot of values calculated during your current session.",
        "HEALTH CENTER",
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
        card("⚖️", "BMI", bmi_value, "Last calculation")

    with c2:
        card("💧", "Water", water_value, "Last estimate")

    with c3:
        card("😴", "Sleep", sleep_value, "Selected duration")

    with c4:
        card("🤖", "Gemini", "Ready" if client else "Offline", "AI engine")

    st.markdown("### Modules")

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
        for col, item in zip(cols, modules[i:i + 3]):
            with col:
                card(item[0], item[1], "ONLINE", "Available")


# =========================================================
# AI COMMAND CENTER
# =========================================================
elif page == "AI Command Center":
    hero(
        "AI Command Center",
        "Ask general health and wellness questions in a dedicated Gemini conversation.",
        "NEXUS AI",
    )

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    prompt = st.chat_input(
        "Ask HealthMate AI...",
        key="command_chat",
    )

    if prompt:
        st.session_state.chat_history.append(
            {"role": "user", "content": prompt}
        )

        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = ask_ai(
                    f"""
You are HealthMate AI.

User question:
{prompt}

Provide general educational health and wellness information.
Do not diagnose.
Do not prescribe medicine.
If the user describes a potentially serious situation, encourage appropriate professional care.
Use simple language.
"""
                )

            if answer:
                st.write(answer)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": answer}
                )

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Conversation"):
            st.session_state.chat_history = []
            st.rerun()


# =========================================================
# SETTINGS
# =========================================================
elif page == "Settings":
    hero(
        "Settings",
        "Customize the lightweight HealthMate interface.",
        "SYSTEM SETTINGS",
    )

    theme = st.selectbox(
        "Theme",
        ["Dark", "Light"],
        index=0 if st.session_state.theme == "Dark" else 1,
    )

    accent_choice = st.selectbox(
        "Accent Color",
        list(accent_colors.keys()),
        index=list(accent_colors.keys()).index(st.session_state.accent),
    )

    if (
        theme != st.session_state.theme
        or accent_choice != st.session_state.accent
    ):
        st.session_state.theme = theme
        st.session_state.accent = accent_choice
        st.rerun()

    st.markdown("### System Status")

    c1, c2, c3 = st.columns(3)

    with c1:
        card("🤖", "Gemini", "Connected" if client else "Not configured")

    with c2:
        card("📄", "PDF", "Ready" if create_pdf else "Unavailable")

    with c3:
        card("⚡", "UI", "Fast Mode", "Lightweight design")


# =========================================================
# ABOUT
# =========================================================
elif page == "About":
    hero(
        "About HealthMate",
        "A student-built AI health and wellness application.",
        "PROJECT INFORMATION",
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        tool("🐍", "Python", "Application programming language.")

    with c2:
        tool("🌐", "Streamlit", "Web application framework.")

    with c3:
        tool("🤖", "Google Gemini", "AI generation and vision.")

    st.markdown("### Developer")

    st.markdown(
        f"""
        <div class="card">
            <div style="font-size:22px;font-weight:700;color:{accent};">
                Bhavesh Thakur
            </div>
            <div style="color:{muted};margin-top:7px;">
                Creator & Developer
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.warning(
        "⚠️ HealthMate AI is an educational project and is not a medical diagnosis or treatment system."
    )


# =========================================================
# FOOTER
# =========================================================
st.markdown(
    f"""
    <div class="footer">
        <b style="color:{accent};">HEALTHMATE AI</b><br>
        © 2026 • Developed by Bhavesh Thakur • Powered by Google Gemini<br>
        Educational Purpose Only
    </div>
    """,
    unsafe_allow_html=True,
)
