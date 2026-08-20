import streamlit as st
from streamlit_option_menu import option_menu
from google import genai
from report import create_pdf

# =========================================================
# CONFIG & STATE INITIALIZATION
# =========================================================

st.set_page_config(
    page_title="HealthMate AI // Quantum Medical Core",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

# =========================================================
# DYNAMIC THEME ENGINE & SCI-FI RGB CSS
# =========================================================

is_dark = st.session_state.theme_mode == "Dark"

theme_vars = f"""
    --bg-base: {'#050816' if is_dark else '#f0f4f9'};
    --bg-panel: {'rgba(12, 22, 45, 0.75)' if is_dark else 'rgba(255, 255, 255, 0.85)'};
    --bg-card: {'rgba(15, 27, 53, 0.70)' if is_dark else 'rgba(240, 246, 255, 0.75)'};
    --bg-input: {'rgba(7, 14, 31, 0.85)' if is_dark else 'rgba(255, 255, 255, 0.95)'};
    --text-main: {'#e8f1ff' if is_dark else '#0a192f'};
    --text-muted: {'#8293b7' if is_dark else '#576f8e'};
    --sidebar-bg: {'linear-gradient(180deg, rgba(7, 14, 35, 0.98), rgba(4, 8, 22, 0.98))' if is_dark else 'linear-gradient(180deg, #ffffff, #e9eff8)'};
    --border-color: {'rgba(0, 229, 255, 0.18)' if is_dark else 'rgba(0, 119, 182, 0.20)'};
"""

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@500;600;700;800&family=Share+Tech+Mono&display=swap');

:root {{
    {theme_vars}
    --neon-cyan: #00f2fe;
    --neon-emerald: #00ff87;
    --neon-purple: #7928ca;
    --neon-crimson: #ff007a;
}}

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

.stApp {{
    background: 
        radial-gradient(circle at 10% 10%, rgba(0, 242, 254, 0.08), transparent 30%),
        radial-gradient(circle at 90% 20%, rgba(121, 40, 202, 0.10), transparent 30%),
        radial-gradient(circle at 50% 100%, rgba(0, 255, 135, 0.06), transparent 30%),
        var(--bg-base);
    color: var(--text-main);
}}

/* ---------- RGB BORDER SYSTEM ---------- */

.rgb-frame {{
    position: relative;
    border-radius: 20px;
    background: var(--bg-panel);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    margin-bottom: 20px;
    z-index: 1;
}}

.rgb-frame::before {{
    content: '';
    position: absolute;
    inset: -2px;
    border-radius: 22px;
    background: linear-gradient(60deg, var(--neon-cyan), var(--neon-emerald), var(--neon-purple), var(--neon-crimson), var(--neon-cyan));
    background-size: 300% 300%;
    animation: rgbBorderFlow 8s linear infinite;
    z-index: -1;
    opacity: 0.85;
}}

@keyframes rgbBorderFlow {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

/* ---------- SIDEBAR ---------- */

section[data-testid="stSidebar"] {{
    background: var(--sidebar-bg);
    border-right: 1px solid var(--border-color);
}}

.sidebar-brand {{
    text-align: center;
    padding: 10px 5px 20px 5px;
}}

.sidebar-brand .logo {{
    font-size: 40px;
    filter: drop-shadow(0 0 15px #00e5ff);
}}

.sidebar-brand h2 {{
    margin: 8px 0 2px 0;
    font-family: 'Orbitron', sans-serif;
    font-size: 19px;
    color: #00e5ff;
    letter-spacing: 1.5px;
}}

.sidebar-brand p {{
    color: var(--text-muted);
    font-size: 11px;
    font-family: 'Share Tech Mono', monospace;
}}

div[data-testid="stSidebar"] .nav-link {{
    border-radius: 12px !important;
    margin: 4px 0 !important;
    color: var(--text-muted) !important;
    transition: all 0.25s ease !important;
}}

div[data-testid="stSidebar"] .nav-link:hover {{
    color: var(--text-main) !important;
    background: rgba(0, 229, 255, 0.08) !important;
    transform: translateX(3px);
}}

div[data-testid="stSidebar"] .nav-link-selected {{
    background: linear-gradient(90deg, rgba(0, 229, 255, 0.2), rgba(139, 92, 246, 0.15)) !important;
    color: #00e5ff !important;
    border: 1px solid rgba(0, 229, 255, 0.35);
    box-shadow: 0 0 20px rgba(0, 229, 255, 0.15);
}}

/* ---------- HERO BANNER ---------- */

.hero {{
    position: relative;
    overflow: hidden;
    padding: 38px 42px;
    border-radius: 20px;
    background: var(--bg-panel);
    border: 1px solid var(--border-color);
}}

.hero-title {{
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(28px, 4vw, 52px);
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 12px;
    background: linear-gradient(90deg, #ffffff, var(--neon-cyan), #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.hero-subtitle {{
    color: var(--text-muted);
    font-size: 15px;
    max-width: 750px;
    line-height: 1.6;
}}

.status {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 5px 12px;
    border-radius: 50px;
    color: var(--neon-emerald);
    background: rgba(0, 255, 135, 0.08);
    border: 1px solid rgba(0, 255, 135, 0.3);
    font-size: 11px;
    font-family: 'Share Tech Mono', monospace;
    margin-bottom: 16px;
}}

.status-dot {{
    width: 8px;
    height: 8px;
    background: var(--neon-emerald);
    border-radius: 50%;
    box-shadow: 0 0 10px var(--neon-emerald);
}}

/* ---------- GLASS CARDS & UI ELEMENTS ---------- */

.glass-card {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 18px;
    padding: 22px;
    backdrop-filter: blur(16px);
    color: var(--text-main);
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
}}

.feature-card {{
    min-height: 160px;
    padding: 22px;
    border-radius: 18px;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    transition: all .25s ease;
}}

.feature-card:hover {{
    transform: translateY(-4px);
    border-color: var(--neon-cyan);
    box-shadow: 0 12px 30px rgba(0, 242, 254, 0.15);
}}

.feature-icon {{ font-size: 28px; margin-bottom: 8px; }}
.feature-title {{ color: var(--text-main); font-weight: 700; font-size: 15px; margin-bottom: 4px; }}
.feature-description {{ color: var(--text-muted); font-size: 12px; line-height: 1.5; }}

/* ---------- INPUTS & BUTTONS ---------- */

.stTextInput input, .stNumberInput input, .stTextArea textarea {{
    background: var(--bg-input) !important;
    color: var(--text-main) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
}}

.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {{
    border-color: var(--neon-cyan) !important;
    box-shadow: 0 0 12px rgba(0, 242, 254, 0.25) !important;
}}

.stButton > button {{
    width: 100%;
    min-height: 46px;
    border-radius: 12px;
    border: 1px solid rgba(0, 242, 254, 0.4);
    color: var(--text-main);
    font-weight: 700;
    background: linear-gradient(135deg, rgba(0, 242, 254, 0.2), rgba(121, 40, 202, 0.2));
    transition: all .25s ease;
}}

.stButton > button:hover {{
    border-color: var(--neon-cyan);
    box-shadow: 0 0 20px rgba(0, 242, 254, 0.4);
    transform: translateY(-2px);
}}

[data-testid="stMetric"] {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    padding: 16px;
    border-radius: 16px;
}}

[data-testid="stMetricLabel"] {{ color: var(--text-muted) !important; }}
[data-testid="stMetricValue"] {{ color: var(--neon-cyan) !important; font-family: 'Orbitron', sans-serif; }}

.footer {{
    text-align: center;
    padding: 30px 10px;
    color: var(--text-muted);
    font-size: 12px;
}}
</style>
""", unsafe_allow_html=True)

# =========================================================
# TOP BAR: THEME TOGGLE & BIOMETRICS HUD
# =========================================================

top_col1, top_col2 = st.columns([8, 2])

with top_col1:
    st.markdown(f"""
    <div style="font-family:'Share Tech Mono', monospace; font-size:12px; color:var(--neon-emerald); display:flex; gap:16px; align-items:center; margin-bottom:12px;">
        <span>● TELEMETRY: LEAD-II ONLINE</span>
        <span style="color:var(--text-muted)">|</span>
        <span>PULSE: 74 BPM</span>
        <span style="color:var(--text-muted)">|</span>
        <span>SpO2: 99%</span>
        <span style="color:var(--text-muted)">|</span>
        <span style="color:var(--neon-cyan)">QUANTUM HEALTH CORE V4.9</span>
    </div>
    """, unsafe_allow_html=True)

with top_col2:
    mode_selection = st.selectbox(
        "Display Mode",
        ["Dark", "Light"],
        index=0 if is_dark else 1,
        label_visibility="collapsed"
    )
    if mode_selection != st.session_state.theme_mode:
        st.session_state.theme_mode = mode_selection
        st.rerun()

# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="logo">◈</div>
        <h2>HEALTHMATE AI</h2>
        <p>AUTONOMOUS BIOMEDICAL SYSTEM</p>
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
            "house", "robot", "capsule", "activity", "cup-straw",
            "egg-fried", "person-running", "fire", "moon-stars",
            "file-earmark-medical", "speedometer2", "info-circle"
        ],
        default_index=0,
    )

    st.markdown("""
    <div style="margin-top:25px; padding:12px; border-radius:12px; background:rgba(0,242,254,0.05); border:1px solid rgba(0,242,254,0.15); text-align:center;">
        <div style="color:var(--neon-emerald); font-size:11px; font-family:'Share Tech Mono';">● CORE STATUS: STABLE</div>
        <div style="color:var(--text-muted); font-size:10px; margin-top:4px;">Gemini 3.1 Flash Core</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# MODULE: HOME
# =========================================================

if selected == "Home":
    st.markdown("""
    <div class="rgb-frame">
        <div class="hero">
            <div class="status">
                <span class="status-dot"></span> AI BIOMEDICAL CORE ONLINE
            </div>
            <div class="hero-title">Your Intelligent<br>Health Companion</div>
            <div class="hero-subtitle">
                HealthMate AI combines clinical reasoning models with biometric analytics 
                to evaluate symptoms, formulate diet plans, and interpret health vitals.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("AI ENGINE", "Gemini 3.1", "OPTIMAL")
    with col2: st.metric("HEALTH MODULES", "12", "SYNCHRONIZED")
    with col3: st.metric("CLINICAL REPORTS", "PDF 4.0", "STANDBY")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### ⚡ Clinical AI Capabilities")

    features = [
        ("🤖", "AI Symptom Checker", "Deep NLP evaluation of symptoms with educational triage."),
        ("💊", "Medicine Intelligence", "Explore contraindications, mechanism, and adverse reactions."),
        ("📊", "BMI Analytics", "Precise anthropometric screening and healthy weight tracking."),
        ("💧", "Hydration Engine", "Dynamic bio-fluid requirements based on body mass."),
        ("🍎", "AI Diet Planner", "Nutrient-balanced meal generation tailored to wellness goals."),
        ("🏃", "Fitness Planner", "Targeted physical conditioning algorithms based on age and profile.")
    ]

    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">{icon}</div>
                <div class="feature-title">{title}</div>
                <div class="feature-description">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.warning("⚠️ HealthMate AI provides educational wellness guidance and is not a substitute for clinical diagnosis.")

# =========================================================
# MODULE: HEALTH DASHBOARD
# =========================================================

elif selected == "Health Dashboard":
    st.markdown("""
    <div class="rgb-frame">
        <div class="hero">
            <div class="status"><span class="status-dot"></span> TELEMETRY CONSOLE ACTIVE</div>
            <div class="hero-title">Command Center</div>
            <div class="hero-subtitle">Supervise and monitor all biomedical intelligence subroutines.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("AI SUBSYSTEMS", "8 Active", "ONLINE")
    with c2: st.metric("WELLNESS ENGINES", "6 Active", "READY")
    with c3: st.metric("REPORT GENERATOR", "PDF Active", "READY")
    with c4: st.metric("CORE LATENCY", "14ms", "NOMINAL")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🧠 Operational Subroutines")

    modules = [
        ("🟢", "BMI Calculator"), ("🟢", "Water Intake"),
        ("🟢", "Diet Planner"), ("🟢", "Exercise Planner"),
        ("🟢", "Symptom Checker"), ("🟢", "Medicine Info"),
        ("🟢", "Calorie Analyzer"), ("🟢", "Sleep Advisor")
    ]

    cols = st.columns(4)
    for i, (status, name) in enumerate(modules):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="glass-card">
                <div style="font-size:18px;">{status}</div>
                <div style="margin-top:6px; font-weight:700; color:var(--text-main);">{name}</div>
                <div style="color:var(--text-muted); font-size:11px; margin-top:4px;">NOMINAL OPERATION</div>
            </div>
            """, unsafe_allow_html=True)

# =========================================================
# MODULE: AI SYMPTOM CHECKER
# =========================================================

elif selected == "AI Symptom Checker":
    st.markdown("""
    <div class="rgb-frame">
        <div class="hero">
            <div class="status"><span class="status-dot"></span> DIAGNOSTIC TRIAGE ACTIVE</div>
            <div class="hero-title">Symptom Intelligence</div>
            <div class="hero-subtitle">Describe clinical signs to receive structured triage insights.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    symptoms = st.chat_input("Describe symptoms (e.g. throbbing headache, mild fatigue since 2 days)...")

    if symptoms:
        with st.chat_message("user"):
            st.write(symptoms)

        if symptoms.strip():
            with st.spinner("Processing neural assessment..."):
                prompt = f"""
You are an advanced clinical wellness AI.
Symptoms reported: {symptoms}

Provide a structured, empathetic, and strictly educational analysis:
1. Potential General Explanations
2. Home Comfort & Hydration Protocol
3. Red Flag Symptoms requiring immediate emergency evaluation
"""
                response = client.models.generate_content(
                    model="gemini-3.1-flash-lite",
                    contents=prompt
                )

            with st.chat_message("assistant"):
                st.write(response.text)

            pdf_file = create_pdf(symptoms, response.text)
            with open(pdf_file, "rb") as file:
                st.download_button(
                    label="📄 EXPORT CLINICAL SUMMARY (PDF)",
                    data=file.read(),
                    file_name="HealthMate_Report.pdf",
                    mime="application/pdf"
                )

# =========================================================
# MODULE: MEDICINE INFO
# =========================================================

elif selected == "Medicine Info":
    st.markdown("""
    <div class="rgb-frame">
        <div class="hero">
            <div class="status"><span class="status-dot"></span> PHARMACOKINETIC DATABASE</div>
            <div class="hero-title">Medicine Intelligence</div>
            <div class="hero-subtitle">Comprehensive pharmacological overview and precaution lookup.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    medicine = st.text_input("Enter Medication Name", placeholder="e.g., Paracetamol, Amoxicillin")

    if st.button("🔎 RUN PHARMACOLOGICAL ANALYSIS"):
        if medicine.strip():
            with st.spinner("Querying molecular and drug database..."):
                prompt = f"""
Provide general educational pharmacological information for: {medicine}
Include:
- Therapeutic Class & General Use
- Common Side Effects
- Crucial Precautions & Interactions
- When to seek physician assistance
Do not prescribe or calculate specific doses.
"""
                response = client.models.generate_content(
                    model="gemini-3.1-flash-lite",
                    contents=prompt
                )

            st.markdown(f"""
            <div class="rgb-frame">
                <div class="glass-card">
                    {response.text}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Please supply a valid medicine identifier.")

# =========================================================
# MODULE: BMI CALCULATOR
# =========================================================

elif selected == "BMI Calculator":
    st.markdown("""
    <div class="rgb-frame">
        <div class="hero">
            <div class="status"><span class="status-dot"></span> BIOMETRIC INDEX MODULE</div>
            <div class="hero-title">BMI Analytics</div>
            <div class="hero-subtitle">Body Mass Index formulation and classification engine.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1: height = st.number_input("Stature / Height (cm)", 50.0, 250.0, 172.0)
    with col2: weight = st.number_input("Mass / Weight (kg)", 10.0, 300.0, 68.0)

    if st.button("⚡ EXECUTE ANTHROPOMETRIC CALCULATION"):
        bmi = weight / ((height / 100) ** 2)
        st.metric("COMPUTED BMI", f"{bmi:.2f}")

        if bmi < 18.5: st.warning("CATEGORY: UNDERWEIGHT")
        elif bmi < 25: st.success("CATEGORY: OPTIMAL / HEALTHY WEIGHT")
        elif bmi < 30: st.warning("CATEGORY: OVERWEIGHT")
        else: st.error("CATEGORY: OBESITY CLASSIFICATION")

# =========================================================
# MODULE: WATER INTAKE
# =========================================================

elif selected == "Water Intake":
    st.markdown("""
    <div class="rgb-frame">
        <div class="hero">
            <div class="status"><span class="status-dot"></span> FLUID EQUILIBRIUM MODULE</div>
            <div class="hero-title">Hydration Engine</div>
            <div class="hero-subtitle">Volumetric fluid calculation tailored to cellular demand.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    weight = st.number_input("Body Weight (kg)", 10.0, 250.0, 65.0)

    if st.button("💧 CALCULATE OPTIMAL HYDRATION"):
        litres = (weight * 35) / 1000
        st.metric("TARGET HYDRATION", f"{litres:.2f} L / day")
        st.success(f"Estimated baseline cellular fluid requirement: {litres:.2f} Litres daily.")

# =========================================================
# MODULE: DIET PLANNER
# =========================================================

elif selected == "Diet Planner":
    st.markdown("""
    <div class="rgb-frame">
        <div class="hero">
            <div class="status"><span class="status-dot"></span> METABOLIC NUTRITION MODULE</div>
            <div class="hero-title">AI Diet Planner</div>
            <div class="hero-subtitle">Micro and macronutrient meal design for athletic or wellness targets.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1: age = st.number_input("Age", 1, 100, 20)
    with col2: gender = st.selectbox("Biological Sex", ["Male", "Female", "Other"])
    goal = st.selectbox("Target Goal", ["Healthy Maintenance", "Lean Weight Loss", "Hypertrophy / Muscle Gain"])

    if st.button("🍎 GENERATE OPTIMAL MEAL PROTOCOL"):
        with st.spinner("Synthesizing macronutrient profile..."):
            prompt = f"Design a 1-day balanced Indian meal plan for a {age} yo {gender} with goal: {goal}. Include Breakfast, Lunch, Snack, Dinner, and Nutritional notes."
            response = client.models.generate_content(model="gemini-3.1-flash-lite", contents=prompt)
            
        st.markdown(f'<div class="rgb-frame"><div class="glass-card">{response.text}</div></div>', unsafe_allow_html=True)

# =========================================================
# MODULE: EXERCISE PLANNER
# =========================================================

elif selected == "Exercise Planner":
    st.markdown("""
    <div class="rgb-frame">
        <div class="hero">
            <div class="status"><span class="status-dot"></span> KINETIC CONDITIONING MODULE</div>
            <div class="hero-title">Exercise Intelligence</div>
            <div class="hero-subtitle">Calibrated fitness routines matched to user experience and endurance.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: age = st.number_input("Age", 5, 100, 20)
    with c2: fit_lvl = st.selectbox("Fitness Level", ["Beginner", "Intermediate", "Advanced"])
    with c3: goal = st.selectbox("Regimen Target", ["Cardiovascular Endurance", "Hypertrophy", "Mobility & Core"])

    if st.button("🏃 GENERATE WORKOUT ROUTINE"):
        with st.spinner("Synthesizing exercise split..."):
            prompt = f"Build a balanced 1-day workout for a {age} year old, level {fit_lvl}, goal: {goal}. Include Warm-up, Main Set, Cool-down, and Injury Prevention notes."
            response = client.models.generate_content(model="gemini-3.1-flash-lite", contents=prompt)

        st.markdown(f'<div class="rgb-frame"><div class="glass-card">{response.text}</div></div>', unsafe_allow_html=True)

# =========================================================
# MODULE: CALORIE CALCULATOR
# =========================================================

elif selected == "Calorie Calculator":
    st.markdown("""
    <div class="rgb-frame">
        <div class="hero">
            <div class="status"><span class="status-dot"></span> THERMODYNAMIC NUTRITION ENGINE</div>
            <div class="hero-title">Calorie Intelligence</div>
            <div class="hero-subtitle">Macronutrient and caloric breakdown via advanced natural language reasoning.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    meal = st.text_area("Consumed Food Items", placeholder="e.g. 2 whole wheat rotis, 1 bowl dal tadka, 100g paneer, mixed salad")

    if st.button("🔥 ANALYZE CALORIC COMPOSITION"):
        if meal.strip():
            with st.spinner("Estimating macro split and energy density..."):
                prompt = f"Estimate calories and macros (Protein, Carbs, Fats) for this meal: {meal}. Provide practical recommendations."
                response = client.models.generate_content(model="gemini-3.1-flash-lite", contents=prompt)
            st.markdown(f'<div class="rgb-frame"><div class="glass-card">{response.text}</div></div>', unsafe_allow_html=True)

# =========================================================
# MODULE: SLEEP
# =========================================================

elif selected == "Sleep Recommendation":
    st.markdown("""
    <div class="rgb-frame">
        <div class="hero">
            <div class="status"><span class="status-dot"></span> CIRCADIAN RESTORATION MODULE</div>
            <div class="hero-title">Sleep Advisor</div>
            <div class="hero-subtitle">Optimize sleep architecture and melatonin regulation.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1: age = st.number_input("Age", 1, 100, 20)
    with c2: hours = st.slider("Typical Sleep Duration (Hours)", 2, 14, 7)
    lifestyle = st.selectbox("Occupational Profile", ["Student / High Cognitive", "Desk Worker", "Athlete / High Strain", "Senior"])

    if st.button("😴 ANALYZE SLEEP RECOVERY"):
        with st.spinner("Evaluating sleep architecture..."):
            prompt = f"Analyze sleep hygiene for a {age} yo {lifestyle} sleeping {hours} hours. Give concrete actionable sleep hygiene protocols."
            response = client.models.generate_content(model="gemini-3.1-flash-lite", contents=prompt)
        st.markdown(f'<div class="rgb-frame"><div class="glass-card">{response.text}</div></div>', unsafe_allow_html=True)

# =========================================================
# MODULE: MEDICAL REPORT ANALYZER (VISION)
# =========================================================

elif selected == "Medical Report Analyzer":
    st.markdown("""
    <div class="rgb-frame">
        <div class="hero">
            <div class="status"><span class="status-dot"></span> COMPUTER VISION DIAGNOSTICS</div>
            <div class="hero-title">Medical Vision Core</div>
            <div class="hero-subtitle">Explain medical documentation, lab metrics, and radiologic reports in plain terms.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Medical Scan / Lab Image", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Clinical Imagery", use_container_width=True)
        if st.button("🔍 RUN MULTIMODAL VISION EVALUATION"):
            with st.spinner("Scanning visual tokens..."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        "Explain this medical image in simple language. Do not diagnose. Describe visible metrics and provide general context.",
                        {"mime_type": uploaded_file.type, "data": uploaded_file.getvalue()}
                    ]
                )
            st.markdown(f'<div class="rgb-frame"><div class="glass-card">{response.text}</div></div>', unsafe_allow_html=True)

# =========================================================
# MODULE: ABOUT
# =========================================================

elif selected == "About":
    st.markdown("""
    <div class="rgb-frame">
        <div class="hero">
            <div class="status"><span class="status-dot"></span> SYSTEM ARCHITECTURE</div>
            <div class="hero-title">About HealthMate AI</div>
            <div class="hero-subtitle">Cutting-edge biomedical interface crafted for the AI Fest Showcase.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="glass-card">
            <h3>⚙️ Engineering Stack</h3>
            <p><strong>Language:</strong> Python 3.11+</p>
            <p><strong>Interface:</strong> Streamlit Quantum Framework</p>
            <p><strong>Reasoning Core:</strong> Google Gemini 3.1 & 2.5 Flash</p>
            <p><strong>Styling:</strong> RGB Fluid Gradient Matrix</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="glass-card">
            <h3>👨‍💻 Lead Developer</h3>
            <div style="font-size:26px; color:#00e5ff; font-family:'Orbitron';">Bhavesh Thakur</div>
            <p style="color:var(--text-muted); margin-top:8px;">
                Designed for AI Fest showcase, bridging foundational LLM clinical intelligence with high-fidelity telemetry interfaces.
            </p>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div class="footer">
    <strong>◈ HEALTHMATE AI</strong> • BIO-QUANTUM INTERFACE<br>
    © 2026 HealthMate AI • Engineered by Bhavesh Thakur • AI Fest Edition
</div>
""", unsafe_allow_html=True)
