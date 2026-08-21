import os
import streamlit as st
from streamlit_option_menu import option_menu
from google import genai
from google.genai import types

# Optional import wrapper for custom report module
try:
    from report import create_pdf
except ImportError:
    def create_pdf(symptoms, response_text):
        # Fallback dummy file generator if local report.py is absent
        with open("Health_Report.pdf", "w", encoding="utf-8") as f:
            f.write(f"HealthMate AI Diagnostic Report\n\nSymptoms:\n{symptoms}\n\nAnalysis:\n{response_text}")
        return "Health_Report.pdf"

# Initialize Gemini Client
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
client = genai.Client(api_key=api_key)

# -----------------------------
# Futuristic Page Configuration
# -----------------------------
st.set_page_config(
    page_title="HealthMate AI // Quantum Health Nexus",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Cyberpunk / Futuristic Glassmorphism CSS
# -----------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&family=Inter:wght@300;400;600&display=swap');

    :root {
        --bg-primary: #050814;
        --bg-card: rgba(13, 20, 36, 0.75);
        --neon-cyan: #00f2fe;
        --neon-blue: #4facfe;
        --neon-purple: #7f00ff;
        --neon-emerald: #00f5a0;
        --text-main: #e2e8f0;
        --text-dim: #94a3b8;
        --border-glow: rgba(0, 242, 254, 0.25);
    }

    /* Base Body Styling */
    .stApp {
        background: radial-gradient(circle at 15% 15%, #0d1527 0%, #050814 60%, #02040a 100%);
        color: var(--text-main);
        font-family: 'Inter', sans-serif;
    }

    /* Futuristic HUD Headers */
    h1, h2, h3, .hud-title {
        font-family: 'Orbitron', sans-serif !important;
        letter-spacing: 2px !important;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 50%, #00f5a0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-transform: uppercase;
        font-weight: 800;
    }

    /* Glassmorphism Cyber Cards */
    .hud-card {
        background: var(--bg-card);
        border: 1px solid var(--border-glow);
        backdrop-filter: blur(16px);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 242, 254, 0.08), inset 0 0 12px rgba(0, 242, 254, 0.05);
        margin-bottom: 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .hud-card:hover {
        border-color: rgba(0, 242, 254, 0.6);
        box-shadow: 0 12px 40px 0 rgba(0, 242, 254, 0.2), inset 0 0 20px rgba(0, 242, 254, 0.1);
        transform: translateY(-2px);
    }

    /* Futuristic Status Indicators & Metrics */
    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(0, 242, 254, 0.2);
        padding: 16px;
        border-radius: 10px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    div[data-testid="stMetricLabel"] {
        font-family: 'Rajdhani', sans-serif;
        color: var(--neon-cyan) !important;
        font-size: 1rem !important;
        font-weight: 600;
        letter-spacing: 1px;
    }
    div[data-testid="stMetricValue"] {
        font-family: 'Orbitron', sans-serif;
        color: #ffffff !important;
        font-size: 1.6rem !important;
    }

    /* Glowing Buttons */
    .stButton > button {
        background: linear-gradient(135deg, rgba(0, 242, 254, 0.15) 0%, rgba(79, 172, 254, 0.15) 100%) !important;
        border: 1px solid var(--neon-cyan) !important;
        color: var(--neon-cyan) !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.2) !important;
        transition: all 0.25s ease-in-out !important;
        width: 100%;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
        color: #030712 !important;
        box-shadow: 0 0 25px rgba(0, 242, 254, 0.6) !important;
        transform: scale(1.01);
    }

    /* Cyber Download Button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, rgba(0, 245, 160, 0.15) 0%, rgba(0, 217, 245, 0.15) 100%) !important;
        border: 1px solid var(--neon-emerald) !important;
        color: var(--neon-emerald) !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        border-radius: 8px !important;
        width: 100%;
    }

    .stDownloadButton > button:hover {
        background: var(--neon-emerald) !important;
        color: #000 !important;
        box-shadow: 0 0 25px rgba(0, 245, 160, 0.7) !important;
    }

    /* Input Fields & Textareas */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        background-color: rgba(13, 20, 36, 0.8) !important;
        border: 1px solid rgba(0, 242, 254, 0.3) !important;
        color: #00f2fe !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--neon-cyan) !important;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.4) !important;
    }

    /* Custom Futuristic Alerts */
    .stAlert {
        background: rgba(13, 20, 36, 0.85) !important;
        border: 1px solid rgba(0, 242, 254, 0.3) !important;
        backdrop-filter: blur(8px) !important;
        border-radius: 10px !important;
        color: var(--text-main) !important;
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: #040711 !important;
        border-right: 1px solid rgba(0, 242, 254, 0.15) !important;
    }
    
    .hud-badge {
        display: inline-block;
        padding: 4px 10px;
        background: rgba(0, 242, 254, 0.1);
        border: 1px solid var(--neon-cyan);
        border-radius: 4px;
        color: var(--neon-cyan);
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar Navigation
# -----------------------------
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 15px 0 10px 0;'>
        <h2 style='margin:0; font-size: 1.4rem;'>⚡ HEALTHMATE AI</h2>
        <span style='color: #00f2fe; font-size: 0.75rem; letter-spacing: 2px; font-family: Rajdhani;'>QUANTUM BIO-CORE v3.1</span>
    </div>
    """, unsafe_allow_html=True)

    selected = option_menu(
        menu_title=None,
        options=[
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
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#00f2fe", "font-size": "15px"},
            "nav-link": {
                "font-size": "13px",
                "text-align": "left",
                "margin": "3px 0",
                "padding": "10px 14px",
                "color": "#94a3b8",
                "border-radius": "8px",
                "font-family": "Rajdhani, sans-serif",
                "font-weight": "600",
                "letter-spacing": "0.5px"
            },
            "nav-link-selected": {
                "background": "linear-gradient(90deg, rgba(0,242,254,0.2) 0%, rgba(79,172,254,0.05) 100%)",
                "color": "#00f2fe",
                "border-left": "3px solid #00f2fe",
                "font-weight": "700"
            }
        }
    )
    
    st.markdown("---")
    st.markdown("""
    <div style='background: rgba(0, 242, 254, 0.05); padding: 12px; border-radius: 8px; border: 1px solid rgba(0, 242, 254, 0.15); font-size: 0.75rem; color: #64748b;'>
        <b style='color: #00f2fe;'>TELEMETRY:</b> SYSTEM STABLE<br>
        <b style='color: #00f5a0;'>NEURAL ENGINE:</b> ACTIVE (2026)
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# Module 1: HOME
# -----------------------------
if selected == "Home":
    st.markdown("<div class='hud-badge'>Core Interface</div>", unsafe_allow_html=True)
    st.title("🏥 HealthMate AI")
    st.markdown("<p style='color: #94a3b8; font-size: 1.1rem; margin-top: -10px;'>Next-Generation Health Diagnostics & Bio-Analytics Companion</p>", unsafe_allow_html=True)
    st.markdown("---")

    col_img, col_txt = st.columns([1, 1], gap="large")

    with col_img:
        st.image(
            "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=1200",
            use_container_width=True
        )

    with col_txt:
        st.markdown("""
        <div class='hud-card'>
            <h3 style='font-size: 1.2rem; margin-bottom: 12px;'>👋 Welcome to Bio-Interface</h3>
            <p style='color: #cbd5e1; font-size: 0.95rem; line-height: 1.6;'>
                HealthMate AI delivers clinical-grade synthesized wellness intelligence powered by advanced neural models.
            </p>
            <div style='color: #00f2fe; font-family: Rajdhani; font-size: 1rem; line-height: 1.8;'>
                ✦ 🤖 Real-Time Symptom Diagnostics<br>
                ✦ 📊 Biometric BMI & Caloric Matrices<br>
                ✦ 💧 Dynamic Hydration Optimization<br>
                ✦ 🍎 Tailored Nutritional Architecture<br>
                ✦ 🏃 Adaptive Athletic Conditioning
            </div>
        </div>
        """, unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(label="AI ENGINE", value="Gemini 3.1 Flash")
    with m2:
        st.metric(label="DIAGNOSTIC SUITE", value="8 Modules")
    with m3:
        st.metric(label="OUTPUT PIPELINE", value="PDF Telemetry")

    st.warning("⚠ Protocol Notice: This platform provides educational analytics only and is NOT a substitute for licensed medical practitioners.")

# -----------------------------
# Module 2: Health Dashboard
# -----------------------------
elif selected == "Health Dashboard":
    st.markdown("<div class='hud-badge'>Telemetry Overview</div>", unsafe_allow_html=True)
    st.title("📊 Health Telemetry Dashboard")
    st.markdown("<p style='color: #94a3b8; font-size: 1.05rem;'>Real-time operational status of all neural health modules.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🤖 Neural Capabilities", "8 Active Cores")
    with col2:
        st.metric("📄 Report Generator", "Available (Online)")

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.success("✅ BMI Calculator // Online")
    with col2:
        st.success("💧 Water Intake // Online")
    with col3:
        st.success("🍎 Diet Planner // Online")

    col4, col5, col6 = st.columns(3)
    with col4:
        st.success("🤖 Symptom Checker // Ready")
    with col5:
        st.success("💊 Medicine Info // Ready")
    with col6:
        st.success("🔥 Calories Matrix // Ready")

    st.markdown("---")
    st.info("⚡ HealthMate AI combines multi-spectrum wellness diagnostics into a single unified workspace.")

# -----------------------------
# Module 3: AI Symptom Checker
# -----------------------------
elif selected == "AI Symptom Checker":
    st.markdown("<div class='hud-badge'>Neural Diagnostic</div>", unsafe_allow_html=True)
    st.title("🤖 AI Symptom Checker")
    st.write("Describe current symptoms, duration, and physiological discomforts below:")

    symptoms = st.chat_input("Enter your symptoms (e.g., persistent dry cough, mild fever for 2 days)...")

    if symptoms:
        with st.chat_message("user"):
            st.write(symptoms)

        if symptoms.strip() == "":
            st.warning("Please enter your symptoms.")
        else:
            with st.spinner("⚡ Quantum Core Analyzing Symptoms..."):
                prompt = f"""
You are an AI Health Assistant.
Symptoms:
{symptoms}
Provide a structured, clean, educational summary including possible general causes, basic home care advice, and warnings on when to see a physician.
"""
                try:
                    response = client.models.generate_content(
                        model="gemini-3.1-flash-lite",
                        contents=prompt
                    )
                    output_text = response.text
                except Exception as e:
                    output_text = f"Neural processing error: {str(e)}"

            with st.chat_message("assistant"):
                st.markdown(output_text)

            # Generate & provide PDF
            try:
                pdf_file = create_pdf(symptoms, output_text)
                with open(pdf_file, "rb") as file:
                    pdf_data = file.read()

                st.download_button(
                    label="📄 Download Diagnostic PDF Report",
                    data=pdf_data,
                    file_name="Health_Report.pdf",
                    mime="application/pdf"
                )
            except Exception as pdf_err:
                st.caption(f"Note: PDF generation bypassed ({str(pdf_err)})")

            st.info("⚠ Clinical Notice: Educational telemetry only. Always consult a certified physician for medical interventions.")

# -----------------------------
# Module 4: Medicine Info
# -----------------------------
elif selected == "Medicine Info":
    st.markdown("<div class='hud-badge'>Pharmacopeia Engine</div>", unsafe_allow_html=True)
    st.title("💊 AI Medicine Information")

    medicine = st.text_input(
        "Enter Medicine / Molecule Name",
        placeholder="Example: Paracetamol, Metformin, Amoxicillin"
    )

    if st.button("Query Medical Database"):
        if medicine.strip() == "":
            st.warning("Please enter a medicine name.")
        else:
            with st.spinner("Searching neural medical archives..."):
                prompt = f"""
Provide general educational information about this medicine.
Medicine:
{medicine}
Include:
• What it is used for
• Common side effects
• Precautions
• When to consult a doctor
Keep the language simple.
Do NOT prescribe medicines.
"""
                try:
                    response = client.models.generate_content(
                        model="gemini-3.1-flash-lite",
                        contents=prompt
                    )
                    st.success("Information Ready")
                    st.markdown(f"<div class='hud-card'>{response.text}</div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error querying medicine data: {str(e)}")

            st.info("⚠ Warning: Always consult a doctor or certified pharmacist before administering any medication.")

# -----------------------------
# Module 5: BMI Calculator
# -----------------------------
elif selected == "BMI Calculator":
    st.markdown("<div class='hud-badge'>Biometric Analysis</div>", unsafe_allow_html=True)
    st.title("📊 BMI Calculator")
    st.write("Compute your Body Mass Index (BMI) and physiological classification.")

    col1, col2 = st.columns(2)
    with col1:
        height = st.number_input("Enter your height (in cm)", min_value=50.0, max_value=250.0, value=170.0, step=0.5)
    with col2:
        weight = st.number_input("Enter your weight (in kg)", min_value=10.0, max_value=300.0, value=65.0, step=0.5)

    if st.button("Calculate BMI Index"):
        height_m = height / 100
        bmi = weight / (height_m * height_m)

        st.markdown(f"<div class='hud-card'><h2 style='margin:0; font-size:1.6rem;'>Your BMI is: <span style='color:#00f2fe;'>{bmi:.2f}</span></h2></div>", unsafe_allow_html=True)

        if bmi < 18.5:
            st.warning("Status: Underweight classification.")
        elif bmi < 25:
            st.success("Status: Healthy weight optimal baseline.")
        elif bmi < 30:
            st.warning("Status: Overweight classification.")
        else:
            st.error("Status: Obese spectrum.")

        st.info("⚠️ Note: BMI is a baseline anthropometric indicator and does not differentiate muscle mass from adipose tissue.")

# -----------------------------
# Module 6: Water Intake
# -----------------------------
elif selected == "Water Intake":
    st.markdown("<div class='hud-badge'>Hydration Matrix</div>", unsafe_allow_html=True)
    st.title("💧 Water Intake Calculator")
    st.write("Calculate your baseline recommended daily hydration volume.")

    weight = st.number_input("Enter your body weight (kg)", min_value=10.0, max_value=250.0, value=60.0, step=0.5)

    if st.button("Compute Optimal Hydration"):
        water = weight * 35
        litres = water / 1000
        st.success(f"💧 Recommended Daily Hydration: {litres:.2f} Litres / day")
        st.info("Baseline calculation. Dynamic requirements increase with high ambient temperatures, athletic exertion, and clinical states.")

# -----------------------------
# Module 7: Diet Planner
# -----------------------------
elif selected == "Diet Planner":
    st.markdown("<div class='hud-badge'>Nutritional Synthesizer</div>", unsafe_allow_html=True)
    st.title("🍎 AI Diet Planner")

    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input("Age", 1, 100, 18)
    with col2:
        gender = st.selectbox("Gender", ["Male", "Female"])
    with col3:
        goal = st.selectbox("Goal", ["Weight Loss", "Weight Gain", "Healthy Lifestyle"])

    if st.button("Generate Diet Matrix"):
        with st.spinner("Synthesizing tailored nutritional architecture..."):
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
"""
            try:
                response = client.models.generate_content(
                    model="gemini-3.1-flash-lite",
                    contents=prompt
                )
                st.success("Diet Plan Ready")
                st.markdown(f"<div class='hud-card'>{response.text}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Failed to generate diet plan: {str(e)}")

# -----------------------------
# Module 8: Exercise Planner
# -----------------------------
elif selected == "Exercise Planner":
    st.markdown("<div class='hud-badge'>Conditioning Protocol</div>", unsafe_allow_html=True)
    st.title("🏃 AI Exercise Planner")

    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input("Age", min_value=5, max_value=100, value=18)
    with col2:
        fitness = st.selectbo consult a doctor.


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

Technologies Used

Python

Streamlit

Gemini AI

Google GenAI SDK


Developed By

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
