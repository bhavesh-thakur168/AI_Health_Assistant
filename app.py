import time
import streamlit as st
import streamlit.components.v1 as components
from google import genai

# Optional PDF Generator Import
try:
    from report import create_pdf
except Exception:
    create_pdf = None


# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="HealthMate AI - Vibrant Edition",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# 2. AUTOMATIC SIDEBAR AUTO-CLOSE ON MOBILE
# =========================================================
components.html(
    """
    <script>
    const parentDoc = window.parent.document;
    function setupMobileSidebarAutoClose() {
        const labels = parentDoc.querySelectorAll('[data-testid="stSidebar"] label');
        labels.forEach(label => {
            if (!label.dataset.hasAutoClose) {
                label.dataset.hasAutoClose = "true";
                label.addEventListener('click', function() {
                    if (window.innerWidth <= 768) {
                        setTimeout(function() {
                            const closeBtn = parentDoc.querySelector('button[data-testid="stSidebarCollapseButton"]') 
                                          || parentDoc.querySelector('[data-testid="stSidebar"] button');
                            if (closeBtn) {
                                closeBtn.click();
                            }
                        }, 250);
                    }
                });
            }
        });
    }
    setupMobileSidebarAutoClose();
    const observer = new MutationObserver(setupMobileSidebarAutoClose);
    observer.observe(parentDoc.body, { childList: true, subtree: true });
    </script>
    """,
    height=0,
    width=0,
)


# =========================================================
# 3. SESSION STATE INITIALIZATION
# =========================================================
VALID_MODELS = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-flash"]

session_defaults = {
    "page": "Home",
    "chat_history": [],
    "bmi": None,
    "bmi_category": None,
    "bmr": None,
    "water": None,
    "sleep": None,
    "symptom_result": None,
    "med_result": None,
    "diet_result": None,
    "exercise_result": None,
    "sleep_result": None,
    "medical_report_result": None,
    "command_center_result": None,
    "accent": "Vibrant Aurora",
    "enable_animations": True,
    "anim_speed": "Normal (15s)",
    "font_scale": "Balanced",
    "ai_model": "gemini-2.5-flash",
}

for key, default_value in session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

if st.session_state.ai_model not in VALID_MODELS:
    st.session_state.ai_model = "gemini-2.5-flash"


# =========================================================
# 4. GEMINI CLIENT & RATE-LIMIT RESILIENT ENGINE (429 FIX)
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


def ask_ai(prompt: str, model: str = None, max_retries: int = 3) -> str:
    """Executes AI prompts with automatic backoff retry logic to handle rate limits (HTTP 429)."""
    if client is None:
        st.error(
            "⚠️ Gemini API Key missing. Please define `GEMINI_API_KEY` in your `.streamlit/secrets.toml` file."
        )
        return None

    selected_model = model or st.session_state.ai_model
    if selected_model not in VALID_MODELS:
        selected_model = "gemini-2.5-flash"

    # Model fallback hierarchy if current model hits quota limit
    model_fallback_queue = [selected_model] + [m for m in VALID_MODELS if m != selected_model]

    for current_model in model_fallback_queue:
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=current_model,
                    contents=prompt,
                )
                return response.text
            except Exception as exc:
                err_msg = str(exc)
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                    wait_time = (attempt + 1) * 6
                    st.info(f"⏳ Free quota limit reached on `{current_model}`. Retrying in {wait_time}s (Attempt {attempt + 1}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    st.error(f"Execution Error: {exc}")
                    return None

    st.error(
        "❌ **API Quota Depleted:** Google AI Studio Free Tier rate limit exceeded across models. "
        "Please wait 60 seconds before trying again."
    )
    return None


# =========================================================
# 5. DYNAMIC THEME & TYPOGRAPHY
# =========================================================
accent_themes = {
    "Vibrant Aurora": {"primary": "#00f2fe", "secondary": "#f43f5e", "gradient": "linear-gradient(135deg, #00f2fe 0%, #a855f7 50%, #ec4899 100%)"},
    "Neon Emerald": {"primary": "#10b981", "secondary": "#06b6d4", "gradient": "linear-gradient(135deg, #10b981 0%, #3b82f6 50%, #6366f1 100%)"},
    "Sunset Fire": {"primary": "#f97316", "secondary": "#ec4899", "gradient": "linear-gradient(135deg, #f97316 0%, #e11d48 50%, #9333ea 100%)"},
    "Electric Purple": {"primary": "#c084fc", "secondary": "#38bdf8", "gradient": "linear-gradient(135deg, #c084fc 0%, #3b82f6 50%, #06b6d4 100%)"},
}

current_theme = accent_themes.get(st.session_state.accent, accent_themes["Vibrant Aurora"])
accent = current_theme["primary"]
theme_gradient = current_theme["gradient"]

speed_map = {"Fast (8s)": "8s", "Normal (15s)": "15s", "Relaxed (25s)": "25s"}
bg_speed = speed_map.get(st.session_state.anim_speed, "15s")
anim_play_state = "running" if st.session_state.enable_animations else "paused"

font_sizes = {
    "Compact": {"root": "13px", "hero": "22px", "h1": "34px"},
    "Balanced": {"root": "14px", "hero": "24px", "h1": "40px"},
    "Large": {"root": "15.5px", "hero": "26px", "h1": "44px"},
}
scale = font_sizes.get(st.session_state.font_scale, font_sizes["Balanced"])


# =========================================================
# 6. APPLICATION STYLESHEET
# =========================================================
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

:root {{
    --bg: #030712;
    --surface: rgba(15, 23, 42, 0.85);
    --surface2: rgba(30, 41, 75, 0.75);
    --text: #f8fafc;
    --muted: #94a3b8;
    --border: rgba(236, 72, 153, 0.25);
    --accent: {accent};
    --gradient: {theme_gradient};
    --shadow: 0 12px 35px 0 rgba(0, 0, 0, 0.65);
    --blur: blur(16px);
}}

.stApp {{
    background: linear-gradient(-45deg, #030712, #0f172a, #1e1b4b, #31103f, #062033);
    background-size: 400% 400%;
    animation: gradientBG {bg_speed} ease infinite {anim_play_state};
    color: var(--text);
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: {scale['root']};
}}

@keyframes gradientBG {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, rgba(8, 12, 26, 0.96) 0%, rgba(18, 10, 32, 0.97) 50%, rgba(10, 16, 35, 0.98) 100%) !important;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-right: 1px solid rgba(236, 72, 153, 0.25);
    box-shadow: 12px 0 40px rgba(0, 0, 0, 0.7);
}}

.sidebar-logo-card {{
    text-align: center;
    padding: 20px 14px;
    border-radius: 20px;
    background: linear-gradient(145deg, rgba(236, 72, 153, 0.08) 0%, rgba(6, 182, 212, 0.08) 100%);
    border: 1px solid rgba(236, 72, 153, 0.3);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    margin-bottom: 20px;
}}

.dna-logo-wrapper {{
    width: 80px;
    height: 80px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    filter: drop-shadow(0 0 16px rgba(236, 72, 153, 0.65));
}}

[data-testid="stSidebar"] div[data-testid="stRadio"] label {{
    border-radius: 14px;
    padding: 11px 16px;
    transition: all 0.28s ease;
    cursor: pointer;
    border: 1px solid transparent;
    font-size: 13.5px;
    font-weight: 600;
    color: #cbd5e1;
    margin-bottom: 5px;
    background: rgba(15, 23, 42, 0.4);
}}

[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {{
    background: linear-gradient(90deg, rgba(236, 72, 153, 0.18), rgba(6, 182, 212, 0.18));
    border-color: rgba(236, 72, 153, 0.45);
    color: #ffffff;
    transform: translateX(4px);
}}

[data-testid="stSidebar"] div[data-testid="stRadio"] [aria-checked="true"] + div label,
[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"] {{
    background: linear-gradient(90deg, rgba(236, 72, 153, 0.3) 0%, rgba(6, 182, 212, 0.3) 100%) !important;
    border: 1px solid rgba(0, 242, 254, 0.5) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 20px rgba(0, 242, 254, 0.35) !important;
}}

.hero {{
    padding: 30px 34px;
    border: 1px solid rgba(236, 72, 153, 0.3);
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 15, 45, 0.85) 100%);
    backdrop-filter: var(--blur);
    box-shadow: 0 16px 45px rgba(0, 0, 0, 0.5);
    margin-bottom: 24px;
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
    background: var(--gradient);
}}

.hero small {{
    color: #00f2fe;
    font-family: 'Outfit', sans-serif;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-size: 10.5px;
    background: linear-gradient(90deg, rgba(0, 242, 254, 0.15), rgba(236, 72, 153, 0.15));
    padding: 6px 14px;
    border-radius: 18px;
    border: 1px solid rgba(0, 242, 254, 0.35);
    display: inline-block;
}}

.hero h1 {{
    margin: 12px 0 6px 0;
    font-size: clamp(24px, 4vw, {scale['h1']});
    line-height: 1.15;
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.hero p {{
    color: #cbd5e1;
    margin: 0;
    font-size: {scale['hero']};
    line-height: 1.5;
}}

.card {{
    background: linear-gradient(145deg, rgba(20, 28, 55, 0.85) 0%, rgba(12, 18, 38, 0.8) 100%);
    backdrop-filter: var(--blur);
    border: 1px solid rgba(236, 72, 153, 0.25);
    border-radius: 20px;
    padding: 18px;
    min-height: 120px;
    box-shadow: var(--shadow);
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    justify-content: center;
}}

.card .icon {{
    font-size: 32px !important;
}}

.card .label {{
    color: #94a3b8;
    font-size: 11px;
    margin-top: 8px;
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 1.2px;
}}

.card .value {{
    color: #ffffff;
    font-family: 'Outfit', sans-serif;
    font-size: 22px;
    font-weight: 800;
    margin-top: 2px;
}}

.card .desc {{
    color: #38bdf8;
    font-size: 12px;
    margin-top: 2px;
}}

.tool {{
    background: linear-gradient(145deg, rgba(20, 28, 55, 0.85) 0%, rgba(12, 18, 38, 0.8) 100%);
    backdrop-filter: var(--blur);
    border: 1px solid rgba(0, 242, 254, 0.2);
    border-radius: 20px 20px 0 0;
    padding: 18px;
    box-shadow: var(--shadow);
}}

.tool-static {{
    border-radius: 20px !important;
}}

.tool b {{
    font-family: 'Outfit', sans-serif;
    color: #ffffff;
    font-size: 16px;
    display: block;
    margin-top: 8px;
}}

.tool p {{
    color: #94a3b8;
    font-size: 12.5px;
    line-height: 1.45;
    margin-top: 4px;
}}

.status {{
    display: inline-flex;
    gap: 8px;
    align-items: center;
    color: #10b981;
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.4);
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 10px;
    font-weight: 800;
}}

.dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #10b981;
    box-shadow: 0 0 10px #10b981;
}}

.result {{
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.92) 0%, rgba(25, 15, 45, 0.9) 100%);
    backdrop-filter: var(--blur);
    border: 1px solid rgba(236, 72, 153, 0.3);
    border-left: 5px solid #ec4899;
    border-radius: 18px;
    padding: 22px;
    box-shadow: var(--shadow);
    margin-top: 18px;
    line-height: 1.65;
    color: #ffffff;
}}

.stButton > button, div[data-testid="stDownloadButton"] > button {{
    border-radius: 12px;
    border: 1px solid rgba(236, 72, 153, 0.35);
    background: linear-gradient(135deg, rgba(30, 20, 50, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%);
    color: #ffffff;
    font-weight: 700;
    padding: 10px 18px;
    transition: all 0.25s ease;
    width: 100%;
}}

.stButton > button:hover {{
    border-color: #00f2fe;
    color: #00f2fe;
    box-shadow: 0 4px 20px rgba(0, 242, 254, 0.35);
}}

.footer {{
    text-align: center;
    color: #64748b;
    font-size: 12px;
    padding: 24px 0 14px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    margin-top: 40px;
}}
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# 7. UI HELPERS & CALCULATORS
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
            f"Open {title} →",
            key=f"nav_btn_{target_page}",
            use_container_width=True,
        ):
            st.session_state.page = target_page
            st.rerun()


def show_result(text):
    st.markdown('<div class="result">', unsafe_allow_html=True)
    st.markdown(text)
    st.markdown("</div>", unsafe_allow_html=True)


def pdf_download(heading_or_input, answer, file_name="Health_Report.pdf", button_label="📄 Download Health Report", key=None):
    if create_pdf is None:
        st.warning("PDF module is unavailable. Place `report.py` in your project root directory.")
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


def compute_bmi(weight_kg, height_cm):
    if height_cm > 0 and weight_kg > 0:
        height_m = height_cm / 100.0
        bmi_val = round(weight_kg / (height_m ** 2), 1)
        if bmi_val < 18.5:
            cat = "Underweight"
        elif 18.5 <= bmi_val <= 24.9:
            cat = "Normal weight"
        elif 25.0 <= bmi_val <= 29.9:
            cat = "Overweight"
        else:
            cat = "Obese"
        return bmi_val, cat
    return None, None


def generate_master_summary():
    summary_data = []
    if st.session_state.bmi:
        summary_data.append(f"### Body Metrics\n* **BMI**: {st.session_state.bmi} ({st.session_state.bmi_category})\n* **Hydration Target**: {st.session_state.water or '--'} L/day\n* **Sleep Target**: {st.session_state.sleep or '--'} hrs/day")
    if st.session_state.command_center_result:
        summary_data.append(f"### AI Command Center Output\n{st.session_state.command_center_result}")
    if st.session_state.symptom_result:
        summary_data.append(f"### Symptom Assessment\n{st.session_state.symptom_result}")
    if st.session_state.medical_report_result:
        summary_data.append(f"### Medical Report Analysis\n{st.session_state.medical_report_result}")
    if st.session_state.diet_result:
        summary_data.append(f"### Diet & Nutrition Plan\n{st.session_state.diet_result}")
    if st.session_state.exercise_result:
        summary_data.append(f"### Exercise & Workout Plan\n{st.session_state.exercise_result}")
    if st.session_state.sleep_result:
        summary_data.append(f"### Sleep Evaluation\n{st.session_state.sleep_result}")

    if not summary_data:
        return "No active session health data recorded yet. Calculate your metrics or use AI tools to generate outputs."

    return "\n\n---\n\n".join(summary_data)


# =========================================================
# 8. SIDEBAR NAVIGATION
# =========================================================
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-logo-card">
            <div class="dna-logo-wrapper">
                <svg viewBox="0 0 100 100" width="60" height="60">
                    <path d="M30 15 Q50 35 70 15 Q50 50 30 85 Q50 65 70 85" fill="none" stroke="#00f2fe" stroke-width="6" stroke-linecap="round"/>
                    <path d="M70 15 Q50 35 30 15 Q50 50 70 85 Q50 65 30 85" fill="none" stroke="#ec4899" stroke-width="6" stroke-linecap="round"/>
                    <line x1="38" y1="26" x2="62" y2="26" stroke="#00f2fe" stroke-width="3" opacity="0.8"/>
                    <line x1="44" y1="40" x2="56" y2="40" stroke="#ec4899" stroke-width="3" opacity="0.8"/>
                    <line x1="44" y1="60" x2="56" y2="60" stroke="#00f2fe" stroke-width="3" opacity="0.8"/>
                </svg>
            </div>
            <h3 style="margin-top: 8px; margin-bottom: 2px; font-size: 17px; color: #ffffff;">HealthMate AI</h3>
            <div class="status"><span class="dot"></span> SYSTEM ONLINE</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    nav_options = [
        "Home",
        "AI Command Center",
        "AI Symptom Tracker",
        "Medical Report Analyzer",
        "Diet & Nutrition",
        "Exercise & Fitness",
        "Sleep & Wellness",
        "Master Health Summary",
        "Settings",
    ]

    current_idx = nav_options.index(st.session_state.page) if st.session_state.page in nav_options else 0

    selected_page = st.radio(
        "Navigation",
        nav_options,
        index=current_idx,
        key="nav_radio",
    )

    if selected_page != st.session_state.page:
        st.session_state.page = selected_page
        st.rerun()


# =========================================================
# 9. PAGE ROUTING & FEATURES
# =========================================================

# ---------------------------------------------------------
# HOMEPAGE / DASHBOARD
# ---------------------------------------------------------
if st.session_state.page == "Home":
    hero(
        "AI-Powered Personal Health Suite",
        "Instant medical triaging, lab analysis, personalized nutrition, and fitness plans.",
        "DASHBOARD OVERVIEW",
    )

    # Top Metric Dashboard Cards
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        card("⚖️", "Body Mass Index", st.session_state.bmi or "--", st.session_state.bmi_category or "Not calculated")
    with col_m2:
        card("💧", "Hydration Target", f"{st.session_state.water} L/day" if st.session_state.water else "--", "Recommended intake")
    with col_m3:
        card("🌙", "Sleep Target", f"{st.session_state.sleep} hrs" if st.session_state.sleep else "--", "Rest duration")
    with col_m4:
        card("🩺", "Triage Status", "Active" if st.session_state.symptom_result else "Ready", "Diagnostic engine")

    st.write("")

    # Interactive Body Metrics Calculator Widget
    with st.expander("🧮 **Body Metrics & Health Calculator (BMI & Hydration)**", expanded=(st.session_state.bmi is None)):
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            weight_in = st.number_input("Weight (kg):", min_value=20.0, max_value=250.0, value=70.0, step=0.5)
        with col_b2:
            height_in = st.number_input("Height (cm):", min_value=100.0, max_value=250.0, value=172.0, step=1.0)
        with col_b3:
            activity_in = st.selectbox("Activity Level:", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"])

        if st.button("Calculate & Update Profile Metrics ⚡"):
            bmi_val, bmi_cat = compute_bmi(weight_in, height_in)
            st.session_state.bmi = bmi_val
            st.session_state.bmi_category = bmi_cat
            st.session_state.water = round(weight_in * 0.035, 1)  # standard hydration formula
            st.session_state.sleep = 8.0 if activity_in in ["Very Active", "Moderately Active"] else 7.5
            st.success("Health profile metrics calculated and saved to session!")
            st.rerun()

    st.write("")

    # Feature Grid
    g1, g2 = st.columns(2)
    with g1:
        tool(
            "🤖",
            "AI Command Center",
            "Central operational hub for executing global custom health prompts and system commands.",
            "AI Command Center",
        )
        st.write("")
        tool(
            "🩺",
            "AI Symptom Tracker",
            "Evaluate acute symptoms, receive triage urgency ratings, and home care tips.",
            "AI Symptom Tracker",
        )
        st.write("")
        tool(
            "📄",
            "Medical Report Analyzer",
            "Extract findings and medical terminology from laboratory blood tests and clinical reports.",
            "Medical Report Analyzer",
        )

    with g2:
        tool(
            "🥗",
            "Diet & Nutrition Planner",
            "Generate customized meal plans, macro breakdowns, and caloric target strategies.",
            "Diet & Nutrition",
        )
        st.write("")
        tool(
            "🏋️‍♂️",
            "Exercise & Fitness Planner",
            "Design workout routines structured around your fitness level and available equipment.",
            "Exercise & Fitness",
        )
        st.write("")
        tool(
            "🌙",
            "Sleep & Wellness Advisor",
            "Optimize circadian cycles, improve sleep quality, and reduce daily fatigue.",
            "Sleep & Wellness",
        )


# ---------------------------------------------------------
# AI COMMAND CENTER
# ---------------------------------------------------------
elif st.session_state.page == "AI Command Center":
    hero(
        "AI Command Center",
        "Unified operational hub to dispatch custom health queries, system instructions, and general AI analysis.",
        "PRIMARY HUB",
    )

    with st.container(border=True):
        st.subheader("Global AI Dispatcher")
        
        # Preset Prompt Buttons
        st.markdown("**Quick Action Presets:**")
        p_col1, p_col2, p_col3 = st.columns(3)
        preset_text = None
        with p_col1:
            if st.button("💡 Standard Cardio Health Guide"):
                preset_text = "Provide a comprehensive guide on maintaining cardiovascular health through diet, exercise, and stress management."
        with p_col2:
            if st.button("🩸 Understanding Lipid Panel"):
                preset_text = "Explain the key parameters of a lipid panel test (HDL, LDL, Triglycerides) and normal reference ranges."
        with p_col3:
            if st.button("🧘 Stress Reduction Routine"):
                preset_text = "Create a 5-step daily routine to reduce chronic stress and lower cortisol levels."

        cmd_input = st.text_area(
            "Enter operational command or medical query:",
            value=preset_text or "",
            placeholder="e.g., Explain the potential side effects and dietary interactions of Iron supplements...",
            height=130,
        )

        if st.button("Execute Command ⚡", use_container_width=True) and cmd_input.strip():
            with st.spinner("Executing prompt across medical AI model..."):
                prompt = f"Act as an expert clinical AI assistant. Execute the following health command thoroughly:\n\n{cmd_input}"
                res = ask_ai(prompt)
                if res:
                    st.session_state.command_center_result = res

    if st.session_state.command_center_result:
        show_result(st.session_state.command_center_result)
        pdf_download("AI Command Execution Report", st.session_state.command_center_result, file_name="AI_Command_Report.pdf", key="cmd_pdf")


# ---------------------------------------------------------
# AI SYMPTOM TRACKER
# ---------------------------------------------------------
elif st.session_state.page == "AI Symptom Tracker":
    hero(
        "AI Symptom Tracker",
        "Input symptoms for intelligent triage evaluation, urgency ratings, and medical guidance.",
        "TRIAGE ENGINE",
    )

    with st.form("symptom_form"):
        symptoms = st.text_area(
            "Describe symptoms in detail:",
            placeholder="e.g., Sharp pain in lower right abdomen starting 4 hours ago, accompanied by mild nausea...",
            height=130,
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            duration = st.text_input("Duration:", placeholder="e.g., 2 days")
        with c2:
            patient_age = st.number_input("Age:", min_value=1, max_value=120, value=25)
        with c3:
            severity = st.select_slider("Severity Level:", options=["Mild", "Moderate", "Severe", "Critical"])

        submitted = st.form_submit_button("Analyze Symptoms 🩺")

    if submitted and symptoms.strip():
        with st.spinner("Running medical triage algorithm..."):
            prompt = f"""
            Act as a clinical triage expert. Analyze the following patient symptoms:
            - Age: {patient_age}
            - Primary Symptoms: {symptoms}
            - Duration: {duration}
            - Self-Reported Severity: {severity}

            Structure your response with:
            1. 🔴 Urgency Triage Level (Low / Moderate / High / Emergency)
            2. 💡 Potential Educational Causes (Non-definitive)
            3. 🚩 Red Flag Warning Symptoms (When to seek ER immediately)
            4. 📋 Recommended Next Steps & Home Care Measures
            """
            res = ask_ai(prompt)
            if res:
                st.session_state.symptom_result = res

    if st.session_state.symptom_result:
        show_result(st.session_state.symptom_result)
        pdf_download("Symptom Assessment Report", st.session_state.symptom_result, file_name="Symptom_Triage_Report.pdf", key="symp_pdf")


# ---------------------------------------------------------
# MEDICAL REPORT ANALYZER
# ---------------------------------------------------------
elif st.session_state.page == "Medical Report Analyzer":
    hero(
        "Medical Report Analyzer",
        "Translate complex lab reports, blood work, and clinical findings into layman explanations.",
        "LAB INTERPRETER",
    )

    report_text = st.text_area(
        "Paste lab report text or test results here:",
        height=180,
        placeholder="e.g., Total Cholesterol: 240 mg/dL, Fasting Glucose: 115 mg/dL, TSH: 4.8 mIU/L, HbA1c: 6.1%...",
    )

    if st.button("Analyze Report 📄") and report_text.strip():
        with st.spinner("Decoding laboratory metrics..."):
            prompt = f"""
            Analyze the following medical report text and provide:
            1. Summary of Abnormal or High-Risk Values
            2. Explanation of Key Medical Terms in Plain English
            3. Questions to ask your primary care physician regarding these findings
            
            Report Data:
            {report_text}
            """
            res = ask_ai(prompt)
            if res:
                st.session_state.medical_report_result = res

    if st.session_state.medical_report_result:
        show_result(st.session_state.medical_report_result)
        pdf_download("Medical Report Analysis", st.session_state.medical_report_result, file_name="Medical_Report_Analysis.pdf", key="med_pdf")


# ---------------------------------------------------------
# DIET & NUTRITION
# ---------------------------------------------------------
elif st.session_state.page == "Diet & Nutrition":
    hero(
        "Diet & Nutrition Planner",
        "Personalized meal plans optimized for your daily caloric targets and wellness goals.",
        "NUTRITION SUITE",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        goal = st.selectbox("Diet Goal:", ["Weight Loss", "Muscle Building", "Maintenance", "Keto", "Diabetic Friendly", "Low Sodium"])
    with c2:
        diet_pref = st.selectbox("Preference:", ["Non-Vegetarian", "Vegetarian", "Vegan", "Eggetarian"])
    with c3:
        cals = st.number_input("Target Daily Calories:", min_value=1000, max_value=5000, value=2000, step=100)

    allergies = st.text_input("Allergies / Dietary Exclusions (optional):", placeholder="e.g., Dairy-free, Peanuts")

    if st.button("Generate Meal Plan 🥗"):
        with st.spinner("Designing tailored nutrition plan..."):
            prompt = f"Create a structured 1-day meal plan (Breakfast, Lunch, Dinner, Snack) for a total target of {cals} kcal. Goal: {goal}, Preference: {diet_pref}, Allergies/Exclusions: {allergies or 'None'}."
            res = ask_ai(prompt)
            if res:
                st.session_state.diet_result = res

    if st.session_state.diet_result:
        show_result(st.session_state.diet_result)
        pdf_download("Diet Plan", st.session_state.diet_result, file_name="Diet_Plan.pdf", key="diet_pdf")


# ---------------------------------------------------------
# EXERCISE & FITNESS
# ---------------------------------------------------------
elif st.session_state.page == "Exercise & Fitness":
    hero(
        "Exercise & Fitness Planner",
        "Targeted workout routines tailored to your experience level and equipment availability.",
        "FITNESS SUITE",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        level = st.selectbox("Fitness Level:", ["Beginner", "Intermediate", "Advanced"])
    with c2:
        equipment = st.selectbox("Equipment:", ["Full Gym", "Dumbbells Only", "Bodyweight / Home"])
    with c3:
        days = st.slider("Workout Days Per Week:", 1, 7, 4)

    if st.button("Generate Workout Plan 🏋️‍♂️"):
        with st.spinner("Building custom workout routine..."):
            prompt = f"Create a structured weekly workout routine for a {level} level person training {days} days per week using {equipment}."
            res = ask_ai(prompt)
            if res:
                st.session_state.exercise_result = res

    if st.session_state.exercise_result:
        show_result(st.session_state.exercise_result)
        pdf_download("Exercise Routine", st.session_state.exercise_result, file_name="Workout_Plan.pdf", key="ex_pdf")


# ---------------------------------------------------------
# SLEEP & WELLNESS
# ---------------------------------------------------------
elif st.session_state.page == "Sleep & Wellness":
    hero(
        "Sleep & Wellness Advisor",
        "Actionable recommendations to improve sleep quality, reduce brain fog, and optimize rest.",
        "WELLNESS ENGINE",
    )

    c1, c2 = st.columns(2)
    with c1:
        sleep_hrs = st.slider("Average Nightly Sleep (Hours):", 3.0, 12.0, 7.0, 0.5)
    with c2:
        quality = st.select_slider("Restfulness Rating:", ["Poor", "Fair", "Good", "Excellent"])

    issues = st.multiselect("Common Sleep Disturbers:", ["Trouble Falling Asleep", "Waking Up Frequently", "Morning Grogginess", "Daytime Fatigue", "Night Stress"])

    if st.button("Analyze Sleep Profile 🌙"):
        st.session_state.sleep = sleep_hrs
        with st.spinner("Generating circadian optimization guide..."):
            prompt = f"Provide personalized sleep hygiene and recovery advice for someone sleeping {sleep_hrs} hours per night with rest quality '{quality}'. Main challenges: {', '.join(issues) if issues else 'None'}."
            res = ask_ai(prompt)
            if res:
                st.session_state.sleep_result = res

    if st.session_state.sleep_result:
        show_result(st.session_state.sleep_result)
        pdf_download("Sleep Analysis", st.session_state.sleep_result, file_name="Sleep_Analysis.pdf", key="sleep_pdf")


# ---------------------------------------------------------
# MASTER HEALTH SUMMARY
# ---------------------------------------------------------
elif st.session_state.page == "Master Health Summary":
    hero(
        "Master Health Summary",
        "Consolidated medical record compiling all metrics and analyses generated during your session.",
        "EXECUTIVE REPORT",
    )

    summary_text = generate_master_summary()

    st.markdown('<div class="result">', unsafe_allow_html=True)
    st.markdown(summary_text)
    st.markdown("</div>", unsafe_allow_html=True)

    pdf_download("Master Health Summary Report", summary_text, file_name="Master_Health_Summary.pdf", button_label="📄 Download Full Master PDF Report", key="master_pdf")


# ---------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------
elif st.session_state.page == "Settings":
    hero(
        "Application Settings",
        "Customize theme themes, font scaling, animations, and AI model backends.",
        "CONFIGURATION",
    )

    with st.container(border=True):
        st.subheader("🎨 Appearance & Styling")
        selected_accent = st.selectbox("Color Palette Theme:", list(accent_themes.keys()), index=list(accent_themes.keys()).index(st.session_state.accent))
        selected_scale = st.selectbox("Typography Scale:", list(font_sizes.keys()), index=list(font_sizes.keys()).index(st.session_state.font_scale))

        c1, c2 = st.columns(2)
        with c1:
            enable_anim = st.toggle("Enable Background Animations", value=st.session_state.enable_animations)
        with c2:
            anim_speed = st.selectbox("Animation Cycle Speed:", list(speed_map.keys()), index=list(speed_map.keys()).index(st.session_state.anim_speed))

    st.write("")

    with st.container(border=True):
        st.subheader("⚙️ AI Engine Configuration")
        model_index = VALID_MODELS.index(st.session_state.ai_model) if st.session_state.ai_model in VALID_MODELS else 0
        selected_model = st.selectbox("Preferred Gemini Model:", VALID_MODELS, index=model_index)

    if st.button("Save Settings 💾", type="primary"):
        st.session_state.accent = selected_accent
        st.session_state.font_scale = selected_scale
        st.session_state.enable_animations = enable_anim
        st.session_state.anim_speed = anim_speed
        st.session_state.ai_model = selected_model
        st.success("Settings saved successfully!")
        st.rerun()


# =========================================================
# 10. FOOTER
# =========================================================
st.markdown(
    """
    <div class="footer">
        HealthMate AI • Educational & Triage Platform<br>
        <i>Disclaimer: This application is for educational purposes only and does not replace professional medical evaluation or diagnosis.</i>
    </div>
    """,
    unsafe_allow_html=True,
)
