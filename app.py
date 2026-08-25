import os
import time
import streamlit as st
from PIL import Image

# =========================================================
# SDK IMPORT & COMPATIBILITY LAYER
# =========================================================
SDK_TYPE = None
try:
    from google import genai
    from google.genai import types
    SDK_TYPE = "genai"
except ImportError:
    try:
        import google.generativeai as genai
        SDK_TYPE = "generativeai"
    except ImportError:
        SDK_TYPE = None

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
# GEMINI CLIENT & API CALL RETRY HANDLER
# =========================================================
def get_api_key():
    """Retrieves API key from Streamlit secrets or environment variables."""
    key = st.secrets.get("GEMINI_API_KEY") if hasattr(st, "secrets") else None
    if not key:
        key = os.environ.get("GEMINI_API_KEY")
    return key


def ask_ai(prompt, image=None, max_retries=3):
    """Unified API execution supporting retries, quota limits, and SDK fallback."""
    api_key = get_api_key()
    if not api_key:
        st.error(
            "🔑 API Key Missing: Please set `GEMINI_API_KEY` in `.streamlit/secrets.toml` or environment variables."
        )
        return None

    if SDK_TYPE is None:
        st.error("SDK Error: Please install google-genai or google-generativeai (`pip install google-genai`).")
        return None

    models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash"]
    
    for model_name in models_to_try:
        for attempt in range(max_retries):
            try:
                if SDK_TYPE == "genai":
                    client = genai.Client(api_key=api_key)
                    if image:
                        bytes_data = image.getvalue()
                        content_payload = [
                            types.Part.from_bytes(data=bytes_data, mime_type=image.type),
                            prompt,
                        ]
                    else:
                        content_payload = prompt

                    response = client.models.generate_content(
                        model=model_name,
                        contents=content_payload,
                    )
                    return response.text

                elif SDK_TYPE == "generativeai":
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(model_name)
                    if image:
                        img_pil = Image.open(image)
                        response = model.generate_content([img_pil, prompt])
                    else:
                        response = model.generate_content(prompt)
                    return response.text

            except Exception as exc:
                err_msg = str(exc)
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                    if attempt < max_retries - 1:
                        time.sleep(2 * (attempt + 1))
                        continue
                    else:
                        st.warning(
                            "⏳ Rate Limit Reached (429): Google free tier quota exceeded. "
                            "Please wait about 60 seconds before submitting another request."
                        )
                        return None
                elif "404" in err_msg or "not found" in err_msg.lower():
                    # Fallback to next model if current model isn't available
                    break
                else:
                    st.error(f"API Error: {exc}")
                    return None
    return None


# =========================================================
# THEME CONFIGURATION
# =========================================================
accent_colors = {
    "Cyan": "#00f2fe",
    "Blue": "#38bdf8",
    "Purple": "#c084fc",
    "Green": "#34d399",
}

accent = accent_colors.get(st.session_state.accent, "#00f2fe")
background = "#131b38"
surface = "rgba(30, 41, 78, 0.72)"
surface2 = "rgba(45, 62, 115, 0.75)"
text = "#ffffff"
muted = "#cbd5e1"
border = "rgba(255, 255, 255, 0.18)"
card_shadow = "0 14px 40px 0 rgba(10, 16, 40, 0.45)"
glass_blur = "blur(20px)"


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
}}

.card .icon {{
    font-size: 42px !important;
    line-height: 1;
    filter: drop-shadow(0 0 12px rgba(0, 242, 254, 0.45));
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
    transition: all 0.25s ease;
    width: 100%;
}}

.stButton > button:hover, div[data-testid="stDownloadButton"] > button:hover {{
    border-color: var(--accent);
    color: var(--accent);
    background: linear-gradient(135deg, rgba(58, 78, 142, 1) 0%, rgba(42, 60, 114, 1) 100%);
    box-shadow: 0 6px 20px rgba(0, 242, 254, 0.35);
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


def tool(icon, title, description, target_page=None):
    st.markdown(
        f"""
        <div class="tool">
            <div class="tool-icon">{icon}</div>
            <div><b>{title}</b></div>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if target_page:
        if st.button(f"Open {title}", key=f"nav_btn_{target_page}"):
            st.session_state.page = target_page
            st.rerun()


def show_result(text):
    st.markdown('<div class="result">', unsafe_allow_html=True)
    st.markdown(text)
    st.markdown("</div>", unsafe_allow_html=True)


def pdf_download(heading_or_input, answer, file_name="Health_Report.pdf", button_label="📄 Download Health Report", key=None):
    if create_pdf is None:
        st.warning("PDF module unavailable. Keep report.py in your app folder to enable downloads.")
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
                <span class="status">● SYSTEM ONLINE</span>
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
# ROUTING BY PAGE
# =========================================================

if page == "Home":
    hero("HealthMate AI", "Your intelligent health companion for general wellness, calculations, and AI educational assistance.")
    st.markdown("### Explore HealthMate Features")

    r1 = st.columns(3)
    with r1[0]:
        tool("🩺", "AI Symptom Checker", "Describe symptoms for general educational guidance.", "AI Symptom Checker")
    with r1[1]:
        tool("💊", "Medicine Info", "Learn general information about medicines.", "Medicine Info")
    with r1[2]:
        tool("📈", "Health Dashboard", "See values calculated during this session.", "Health Dashboard")

    st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)

    r2 = st.columns(3)
    with r2[0]:
        tool("📊", "BMI Calculator", "Calculate BMI from height and weight.", "BMI Calculator")
    with r2[1]:
        tool("💧", "Water Intake", "Estimate general daily water needs.", "Water Intake")
    with r2[2]:
        tool("🥗", "Diet Planner", "Generate a simple Indian diet plan.", "Diet Planner")

    st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)

    r3 = st.columns(3)
    with r3[0]:
        tool("🏋️‍♂️", "Exercise Planner", "Generate simple workout plans tailored to goals.", "Exercise Planner")
    with r3[1]:
        tool("🔥", "Calorie Calculator", "Estimate calories and macros from meal descriptions.", "Calorie Calculator")
    with r3[2]:
        tool("😴", "Sleep Recommendation", "Get personalized guidance for healthy sleep habits.", "Sleep Recommendation")

    st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)

    r4 = st.columns(3)
    with r4[0]:
        tool("🔬", "Medical Report Analyzer", "Upload image reports for educational AI breakdown.", "Medical Report Analyzer")
    with r4[1]:
        tool("💬", "AI Command Center", "Ask general health & wellness questions in chat.", "AI Command Center")


elif page == "AI Symptom Checker":
    hero("AI Symptom Checker", "Describe your symptoms and receive general educational information from Gemini.")
    symptoms = st.chat_input("Describe your symptoms...", key="symptoms_input")
    if symptoms:
        with st.chat_message("user"):
            st.write(symptoms)
        with st.chat_message("assistant"):
            with st.spinner("Analyzing symptoms..."):
                answer = ask_ai(
                    f"You are HealthMate AI. Provide educational health information for these symptoms without prescribing or diagnosing: {symptoms}"
                )
            if answer:
                st.write(answer)
                pdf_download(symptoms, answer, "Symptom_Report.pdf", "📄 Download Symptom Report", key="pdf_symptoms")


elif page == "Medicine Info":
    hero("Medicine Information", "Get simple educational information about a medicine.")
    medicine = st.text_input("Medicine name", placeholder="Example: Paracetamol")
    if st.button("💊 Get Medicine Information"):
        if medicine.strip():
            with st.spinner("Fetching details..."):
                answer = ask_ai(
                    f"Provide simple educational info (usage, side effects, precautions) for medicine: {medicine}. Do not give dosage or prescription."
                )
            if answer:
                show_result(answer)
                pdf_download(f"Medicine Info: {medicine}", answer, f"Medicine_{medicine}.pdf", "📄 Download Guide", key="pdf_med")


elif page == "BMI Calculator":
    hero("BMI Calculator", "Calculate your Body Mass Index using height and weight.", "BODY METRICS")
    unit_choice = st.radio("Height Unit", ["Centimeters (cm)", "Feet & Inches (ft + in)"], horizontal=True)

    c1, c2 = st.columns(2)
    with c1:
        if unit_choice == "Centimeters (cm)":
            height = st.number_input("Height (cm)", 50.0, 250.0, 170.0, 0.5)
            height_m = height / 100.0
        else:
            f_col, i_col = st.columns(2)
            feet = f_col.number_input("Feet (ft)", 1, 8, 5)
            inches = i_col.number_input("Inches (in)", 0, 11, 7)
            height_m = ((feet * 12) + inches) * 0.0254
    with c2:
        weight = st.number_input("Weight (kg)", 10.0, 300.0, 65.0, 0.5)

    if st.button("📊 Calculate BMI"):
        if height_m > 0:
            bmi = weight / (height_m * height_m)
            st.session_state.bmi = bmi
            cat = "Underweight" if bmi < 18.5 else ("Healthy Weight" if bmi < 25 else ("Overweight" if bmi < 30 else "Obesity"))
            st.markdown("<br>", unsafe_allow_html=True)
            a, b = st.columns(2)
            with a: card("📊", "BMI", f"{bmi:.2f}", "Calculated value")
            with b: card("⚖️", "Category", cat, "General classification")


elif page == "Water Intake":
    hero("Water Intake Calculator", "Estimate general daily water intake from body weight.", "HYDRATION")
    weight = st.number_input("Weight (kg)", 10.0, 250.0, 60.0, 0.5)
    if st.button("💧 Calculate Water Intake"):
        water_ml = weight * 35
        litres = water_ml / 1000.0
        st.session_state.water = litres
        st.markdown("<br>", unsafe_allow_html=True)
        a, b = st.columns(2)
        with a: card("💧", "Recommended", f"{litres:.2f} L", "Daily Target")
        with b: card("🥤", "Millilitres", f"{water_ml:.0f} ml", "Per Day Estimate")


elif page == "Diet Planner":
    hero("AI Diet Planner", "Generate a simple one-day Indian diet plan.", "NUTRITION AI")
    c1, c2, c3 = st.columns(3)
    age = c1.number_input("Age", 1, 100, 18)
    gender = c2.selectbox("Gender", ["Male", "Female"])
    goal = c3.selectbox("Goal", ["Weight Loss", "Weight Gain", "Healthy Lifestyle"])
    if st.button("🥗 Generate Diet Plan"):
        with st.spinner("Generating plan..."):
            answer = ask_ai(f"Create a simple one-day Indian diet plan for a {age}yo {gender} aiming for {goal}.")
        if answer:
            show_result(answer)
            pdf_download(f"Diet Plan ({goal})", answer, "Diet_Plan.pdf", "📄 Download Diet Plan", key="pdf_diet")


elif page == "Exercise Planner":
    hero("AI Exercise Planner", "Generate a simple daily fitness routine.", "FITNESS AI")
    c1, c2, c3 = st.columns(3)
    age = c1.number_input("Age", 5, 100, 18)
    fitness = c2.selectbox("Level", ["Beginner", "Intermediate", "Advanced"])
    goal = c3.selectbox("Goal", ["Weight Loss", "Muscle Gain", "Stay Fit"])
    if st.button("🏋️‍♂️ Generate Workout Plan"):
        with st.spinner("Creating routine..."):
            answer = ask_ai(f"Create a simple safe 1-day exercise plan for a {fitness} level {age}yo user with goal: {goal}.")
        if answer:
            show_result(answer)
            pdf_download(f"Workout Plan", answer, "Workout_Plan.pdf", "📄 Download Workout Plan", key="pdf_ex")


elif page == "Calorie Calculator":
    hero("AI Calorie Calculator", "Estimate calories and macros from your meal.", "NUTRITION ANALYTICS")
    food = st.text_area("What did you eat today?", placeholder="Example: 2 chapati, dal, rice, salad")
    if st.button("🔥 Calculate Calories"):
        if food.strip():
            with st.spinner("Analyzing meal..."):
                answer = ask_ai(f"Estimate total calories, protein, carbs, and fat for this meal: {food}. State clearly these are estimates.")
            if answer:
                show_result(answer)
                pdf_download("Calorie Report", answer, "Calorie_Report.pdf", "📄 Download Nutrition Report", key="pdf_cal")


elif page == "Sleep Recommendation":
    hero("Sleep Guidance", "Get guidance based on sleep duration and habits.", "RECOVERY AI")
    c1, c2, c3 = st.columns(3)
    age = c1.number_input("Your Age", 1, 100, 18)
    sleep_hours = c2.slider("Sleep Hours", 1, 12, 7)
    lifestyle = c3.selectbox("Profile", ["Student", "Working Professional", "Athlete", "Senior Citizen"])
    st.session_state.sleep = sleep_hours
    if st.button("😴 Get Advice"):
        with st.spinner("Analyzing rest..."):
            answer = ask_ai(f"Provide healthy sleep advice for a {age}yo {lifestyle} getting {sleep_hours} hours of sleep.")
        if answer:
            show_result(answer)


elif page == "Medical Report Analyzer":
    hero("Medical Report Analyzer", "Upload a report image for educational breakdown.", "REPORT VISION AI")
    uploaded_file = st.file_uploader("Upload Report Image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Report", use_container_width=True)
        if st.button("🔬 Analyze Medical Report"):
            with st.spinner("Analyzing image..."):
                answer = ask_ai(
                    "Analyze this medical report image for educational purposes. Explain key findings, medical terms, and reference values simply. Do not diagnose.",
                    image=uploaded_file,
                )
            if answer:
                show_result(answer)
                pdf_download("Medical Report Analysis", answer, "Report_Analysis.pdf", "📄 Download Report Analysis", key="pdf_rep")


elif page == "Health Dashboard":
    hero("Health Dashboard", "Overview of metrics calculated during this session.", "SESSION METRICS")
    c1, c2, c3 = st.columns(3)
    c1.metric("Body Mass Index", f"{st.session_state.bmi:.2f}" if st.session_state.bmi else "Not Calculated")
    c2.metric("Daily Water Goal", f"{st.session_state.water:.2f} L" if st.session_state.water else "Not Calculated")
    c3.metric("Target Sleep", f"{st.session_state.sleep} Hours" if st.session_state.sleep else "Not Recorded")


elif page == "AI Command Center":
    hero("AI Command Center", "Interactive health & wellness chat assistant.", "INTERACTIVE CHAT")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    user_query = st.chat_input("Ask any health question...")
    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.write(user_query)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                resp = ask_ai(f"Provide educational health guidance for: {user_query}")
                if resp:
                    st.write(resp)
                    st.session_state.chat_history.append({"role": "assistant", "content": resp})


elif page == "Settings":
    hero("Settings", "Customize layout themes.", "PREFERENCES")
    selected_accent = st.selectbox("Accent Color Theme", list(accent_colors.keys()), index=list(accent_colors.keys()).index(st.session_state.accent))
    if st.button("Save Settings"):
        st.session_state.accent = selected_accent
        st.success("Theme saved!")
        st.rerun()


elif page == "About":
    hero("About HealthMate AI", "Empowering individuals with educational health insights.", "ABOUT PLATFORM")
    st.markdown("### Educational Health Intelligence\nHealthMate AI helps users calculate lifestyle metrics, plan meals/fitness, and understand general medical terms safely.")


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
