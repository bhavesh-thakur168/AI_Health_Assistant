import streamlit as st
from google import genai

# report.py is kept as your existing PDF generator.
try:
    from report import create_pdf
except Exception:
    create_pdf = None


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="HealthMate Nexus",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "theme": "Dark",
    "accent": "Cyan",
    "selected_page": "Home",
    "chat_history": [],
    "last_result": "",
    "bmi_value": None,
    "water_value": None,
    "sleep_value": None,
    "calorie_text": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# GEMINI CLIENT
# ============================================================

def get_gemini_client():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        return None

    if not api_key:
        return None

    try:
        return genai.Client(api_key=api_key)
    except Exception:
        return None


client = get_gemini_client()


# ============================================================
# THEME
# ============================================================

ACCENTS = {
    "Cyan": {
        "primary": "#62f5df",
        "secondary": "#79a7ff",
        "rgb": "98,245,223",
    },
    "Purple": {
        "primary": "#c084fc",
        "secondary": "#818cf8",
        "rgb": "192,132,252",
    },
    "Blue": {
        "primary": "#60a5fa",
        "secondary": "#22d3ee",
        "rgb": "96,165,250",
    },
    "Green": {
        "primary": "#4ade80",
        "secondary": "#2dd4bf",
        "rgb": "74,222,128",
    },
}

accent = ACCENTS[st.session_state.accent]

if st.session_state.theme == "Light":
    bg = "#eef4f8"
    panel = "rgba(255,255,255,0.88)"
    panel2 = "rgba(247,250,252,0.95)"
    text = "#10202e"
    muted = "#5d7080"
    border = "rgba(20,70,90,0.13)"
    input_bg = "#ffffff"
else:
    bg = "#050811"
    panel = "rgba(11,20,34,0.82)"
    panel2 = "rgba(7,14,26,0.94)"
    text = "#eaffff"
    muted = "#8295aa"
    border = "rgba(255,255,255,0.08)"
    input_bg = "rgba(4,10,20,0.82)"


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@500;600;700;800&display=swap');

:root {{
    --primary: {accent["primary"]};
    --secondary: {accent["secondary"]};
    --accent-rgb: {accent["rgb"]};
    --bg: {bg};
    --panel: {panel};
    --panel2: {panel2};
    --text: {text};
    --muted: {muted};
    --border: {border};
    --input: {input_bg};
}}

.stApp {{
    background:
        radial-gradient(circle at 10% 5%, rgba(var(--accent-rgb),0.10), transparent 28%),
        radial-gradient(circle at 90% 10%, rgba(110,100,255,0.12), transparent 28%),
        radial-gradient(circle at 55% 100%, rgba(0,170,255,0.08), transparent 32%),
        var(--bg);
    color: var(--text);
}}

.stApp::before {{
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    opacity: 0.16;
    background-image:
        linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px);
    background-size: 42px 42px;
    mask-image: linear-gradient(to bottom, black, transparent);
}}

html, body, [class*="css"] {{
    font-family: "Inter", sans-serif;
}}

h1, h2, h3 {{
    color: var(--text) !important;
}}

h1 {{
    font-family: "Orbitron", sans-serif !important;
}}

[data-testid="stSidebar"] {{
    background:
        linear-gradient(180deg, var(--panel2), rgba(3,7,14,0.98));
    border-right: 1px solid rgba(var(--accent-rgb),0.15);
}}

[data-testid="stSidebar"] > div:first-child {{
    padding-top: 1rem;
}}

.brand {{
    text-align: center;
    padding: 8px 5px 20px;
}}

.logo {{
    width: 70px;
    height: 70px;
    margin: 0 auto;
    border-radius: 23px;
    display: flex;
    align-items: center;
    justify-content: center;
    background:
        radial-gradient(circle at 35% 25%, rgba(255,255,255,0.18), transparent 20%),
        linear-gradient(135deg, rgba(var(--accent-rgb),0.18), rgba(120,100,255,0.22));
    border: 1px solid rgba(var(--accent-rgb),0.30);
    box-shadow:
        0 0 35px rgba(var(--accent-rgb),0.12),
        inset 0 0 30px rgba(var(--accent-rgb),0.05);
    animation: pulseLogo 3s ease-in-out infinite;
}}

@keyframes pulseLogo {{
    0%,100% {{ transform: scale(1); }}
    50% {{ transform: scale(1.035); }}
}}

.brand-title {{
    margin-top: 12px;
    font-family: "Orbitron", sans-serif;
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 1.5px;
    background: linear-gradient(90deg, var(--primary), var(--secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.brand-sub {{
    margin-top: 5px;
    color: var(--muted);
    font-size: 9px;
    letter-spacing: 2px;
}}

.status-pill {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 7px 11px;
    border-radius: 999px;
    background: rgba(var(--accent-rgb),0.06);
    border: 1px solid rgba(var(--accent-rgb),0.15);
    color: var(--primary);
    font-size: 10px;
    letter-spacing: 1px;
    font-weight: 700;
}}

.status-dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--primary);
    box-shadow: 0 0 12px var(--primary);
    animation: blink 1.7s infinite;
}}

@keyframes blink {{
    0%,100% {{ opacity: 1; }}
    50% {{ opacity: .35; }}
}}

div[data-testid="stRadio"] > label {{
    display: none;
}}

div[data-testid="stRadio"] div[role="radiogroup"] {{
    gap: 5px;
}}

div[data-testid="stRadio"] div[role="radiogroup"] > label {{
    border: 1px solid transparent;
    border-radius: 12px;
    padding: 9px 10px;
    color: var(--muted);
    transition: all .2s ease;
}}

div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {{
    color: var(--text);
    background: rgba(var(--accent-rgb),0.055);
    border-color: rgba(var(--accent-rgb),0.12);
}}

.hero {{
    position: relative;
    overflow: hidden;
    padding: 38px;
    border-radius: 28px;
    background:
        linear-gradient(135deg, rgba(var(--accent-rgb),0.065), rgba(90,90,255,0.065)),
        var(--panel);
    border: 1px solid rgba(var(--accent-rgb),0.14);
    box-shadow: 0 25px 70px rgba(0,0,0,.18), inset 0 1px rgba(255,255,255,.035);
    animation: appear .45s ease-out;
}}

.hero::after {{
    content: "";
    position: absolute;
    width: 300px;
    height: 300px;
    right: -120px;
    top: -140px;
    border-radius: 50%;
    background: rgba(var(--accent-rgb),0.10);
    filter: blur(55px);
}}

.hero-kicker {{
    color: var(--primary);
    font-size: 10px;
    letter-spacing: 3px;
    font-weight: 800;
}}

.hero-title {{
    position: relative;
    z-index: 1;
    margin-top: 10px;
    font-family: "Orbitron", sans-serif;
    font-size: clamp(31px, 5vw, 54px);
    font-weight: 800;
    line-height: 1.08;
    background: linear-gradient(90deg, var(--text), var(--primary), var(--secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.hero-text {{
    position: relative;
    z-index: 1;
    max-width: 850px;
    margin-top: 15px;
    color: var(--muted);
    font-size: 14px;
    line-height: 1.75;
}}

@keyframes appear {{
    from {{ opacity:0; transform:translateY(8px); }}
    to {{ opacity:1; transform:translateY(0); }}
}}

.section {{
    margin: 30px 0 14px;
    display: flex;
    align-items: center;
    gap: 18px;
}}

.section-title {{
    font-family: "Orbitron", sans-serif;
    font-size: 14px;
    font-weight: 700;
    color: var(--text);
    letter-spacing: .5px;
}}

.section-line {{
    height: 1px;
    flex: 1;
    background: linear-gradient(90deg, rgba(var(--accent-rgb),0.25), transparent);
}}

.card {{
    padding: 21px;
    border-radius: 19px;
    background:
        linear-gradient(145deg, rgba(var(--accent-rgb),0.035), transparent),
        var(--panel);
    border: 1px solid var(--border);
    box-shadow: 0 14px 40px rgba(0,0,0,.14), inset 0 1px rgba(255,255,255,.025);
    transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
    min-height: 126px;
}}

.card:hover {{
    transform: translateY(-3px);
    border-color: rgba(var(--accent-rgb),0.22);
    box-shadow: 0 18px 48px rgba(0,0,0,.20), 0 0 25px rgba(var(--accent-rgb),0.04);
}}

.card-icon {{
    font-size: 26px;
    margin-bottom: 11px;
}}

.card-label {{
    color: var(--muted);
    font-size: 10px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}}

.card-value {{
    margin-top: 7px;
    font-family: "Orbitron", sans-serif;
    font-size: 24px;
    font-weight: 700;
    color: var(--text);
}}

.card-desc {{
    margin-top: 8px;
    color: var(--muted);
    font-size: 12px;
    line-height: 1.55;
}}

.tool-card {{
    padding: 21px;
    border-radius: 19px;
    background: var(--panel);
    border: 1px solid var(--border);
    min-height: 170px;
}}

.tool-icon {{
    font-size: 30px;
}}

.tool-title {{
    margin-top: 12px;
    font-size: 16px;
    font-weight: 800;
    color: var(--text);
}}

.tool-text {{
    margin-top: 8px;
    color: var(--muted);
    font-size: 12px;
    line-height: 1.6;
}}

.ai-core {{
    text-align: center;
    padding: 34px 22px;
    border-radius: 25px;
    background:
        radial-gradient(circle at 50% 35%, rgba(var(--accent-rgb),0.13), transparent 35%),
        var(--panel);
    border: 1px solid rgba(var(--accent-rgb),0.16);
}}

.ai-orb {{
    width: 112px;
    height: 112px;
    margin: 0 auto 18px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 46px;
    background:
        radial-gradient(circle at 35% 25%, rgba(255,255,255,.20), transparent 18%),
        linear-gradient(135deg, rgba(var(--accent-rgb),.20), rgba(100,90,255,.20));
    border: 1px solid rgba(var(--accent-rgb),.30);
    box-shadow:
        0 0 30px rgba(var(--accent-rgb),.14),
        0 0 90px rgba(var(--accent-rgb),.06),
        inset 0 0 25px rgba(var(--accent-rgb),.08);
    animation: orb 3s ease-in-out infinite;
}}

@keyframes orb {{
    0%,100% {{ transform:scale(1); box-shadow:0 0 30px rgba(var(--accent-rgb),.14),0 0 90px rgba(var(--accent-rgb),.06); }}
    50% {{ transform:scale(1.05); box-shadow:0 0 42px rgba(var(--accent-rgb),.25),0 0 110px rgba(var(--accent-rgb),.09); }}
}}

.ai-title {{
    font-family: "Orbitron", sans-serif;
    font-size: 19px;
    font-weight: 800;
}}

.ai-sub {{
    margin-top: 7px;
    color: var(--muted);
    font-size: 12px;
}}

.result {{
    padding: 24px;
    border-radius: 19px;
    background: var(--panel);
    border: 1px solid rgba(var(--accent-rgb),0.13);
    line-height: 1.7;
}}

.progress-shell {{
    height: 10px;
    overflow: hidden;
    border-radius: 99px;
    background: rgba(120,140,160,.12);
}}

.progress-bar {{
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, var(--primary), var(--secondary));
    box-shadow: 0 0 15px rgba(var(--accent-rgb),.18);
}}

.stButton > button {{
    width: 100%;
    min-height: 44px;
    border-radius: 13px;
    color: var(--text);
    background: linear-gradient(135deg, rgba(var(--accent-rgb),.10), rgba(100,90,255,.10));
    border: 1px solid rgba(var(--accent-rgb),.20);
    font-weight: 800;
    transition: all .2s ease;
}}

.stButton > button:hover {{
    transform: translateY(-2px);
    border-color: rgba(var(--accent-rgb),.50);
    box-shadow: 0 0 25px rgba(var(--accent-rgb),.10);
}}

div[data-baseweb="input"],
div[data-baseweb="select"],
textarea {{
    background: var(--input) !important;
    border-radius: 12px !important;
}}

div[data-baseweb="input"] input,
textarea {{
    color: var(--text) !important;
}}

div[data-testid="stFileUploaderDropzone"] {{
    background: var(--input);
    border: 1px dashed rgba(var(--accent-rgb),.25);
    border-radius: 16px;
}}

div[data-testid="stMetric"] {{
    background: var(--panel);
    border: 1px solid var(--border);
    padding: 14px;
    border-radius: 16px;
}}

[data-testid="stAlert"] {{
    border-radius: 14px;
}}

[data-testid="stChatMessage"] {{
    border: 1px solid var(--border);
    border-radius: 17px;
    background: rgba(var(--accent-rgb),.025);
}}

.footer {{
    margin-top: 55px;
    padding: 26px 10px;
    text-align: center;
    color: var(--muted);
    border-top: 1px solid var(--border);
    font-size: 11px;
}}

.footer strong {{
    color: var(--primary);
}}

@media (max-width: 800px) {{
    .hero {{ padding: 25px; }}
    .hero-title {{ font-size: 30px; }}
}}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def section_title(title):
    st.markdown(
        f"""
        <div class="section">
            <div class="section-title">{title}</div>
            <div class="section-line"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero(kicker, title, description):
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-kicker">{kicker}</div>
            <div class="hero-title">{title}</div>
            <div class="hero-text">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(icon, label, value, description=""):
    st.markdown(
        f"""
        <div class="card">
            <div class="card-icon">{icon}</div>
            <div class="card-label">{label}</div>
            <div class="card-value">{value}</div>
            <div class="card-desc">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def tool_card(icon, title, description):
    st.markdown(
        f"""
        <div class="tool-card">
            <div class="tool-icon">{icon}</div>
            <div class="tool-title">{title}</div>
            <div class="tool-text">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def result_card(text):
    st.markdown('<div class="result">', unsafe_allow_html=True)
    st.markdown(text)
    st.markdown("</div>", unsafe_allow_html=True)


def require_client():
    if client is None:
        st.error(
            "Gemini is not configured. Add GEMINI_API_KEY to "
            ".streamlit/secrets.toml and restart the app."
        )
        return False
    return True


def ask_gemini(prompt, model="gemini-3.1-flash-lite"):
    if not require_client():
        return None

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        return response.text
    except Exception as exc:
        st.error(f"AI request failed: {exc}")
        return None


def safe_pdf(symptoms, answer):
    if create_pdf is None:
        st.warning(
            "report.py could not be imported, so PDF generation is unavailable. "
            "The rest of the application can still run."
        )
        return

    try:
        pdf_file = create_pdf(symptoms, answer)

        with open(pdf_file, "rb") as file:
            pdf_data = file.read()

        st.download_button(
            "📄 Download Health Report",
            data=pdf_data,
            file_name="Health_Report.pdf",
            mime="application/pdf",
        )
    except Exception as exc:
        st.error(f"Could not create the PDF report: {exc}")


def navigation_pages():
    return [
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
        "⌘  AI Command Center",
        "⚙  Settings",
        "ⓘ  About",
    ]


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="logo">🧬</div>
            <div class="brand-title">HEALTHMATE</div>
            <div class="brand-sub">AI HEALTH INTELLIGENCE</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="text-align:center;">
            <span class="status-pill">
                <span class="status-dot"></span>
                SYSTEM ONLINE
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        "<div style='font-size:10px;color:var(--muted);letter-spacing:1.5px;'>NAVIGATION</div>",
        unsafe_allow_html=True,
    )

    pages = navigation_pages()

    current_index = 0
    current_clean = st.session_state.selected_page

    for i, item in enumerate(pages):
        if item.split("  ", 1)[-1] == current_clean:
            current_index = i
            break

    selected_raw = st.radio(
        "Navigation",
        pages,
        index=current_index,
        label_visibility="collapsed",
    )

    selected = selected_raw.split("  ", 1)[-1]
    st.session_state.selected_page = selected

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        "<div style='font-size:10px;color:var(--muted);letter-spacing:1.5px;'>QUICK COMMAND</div>",
        unsafe_allow_html=True,
    )

    command = st.selectbox(
        "Command",
        [
            "Open dashboard",
            "Ask HealthMate AI",
            "Calculate BMI",
            "Calculate water intake",
            "Create diet plan",
            "Create exercise plan",
            "Analyze medical report",
        ],
        label_visibility="collapsed",
    )

    if st.button("⚡ EXECUTE COMMAND", key="execute_command"):
        command_map = {
            "Open dashboard": "Health Dashboard",
            "Ask HealthMate AI": "AI Command Center",
            "Calculate BMI": "BMI Calculator",
            "Calculate water intake": "Water Intake",
            "Create diet plan": "Diet Planner",
            "Create exercise plan": "Exercise Planner",
            "Analyze medical report": "Medical Report Analyzer",
        }
        st.session_state.selected_page = command_map[command]
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="card" style="min-height:auto;padding:15px;">
            <div class="card-label">AI ENGINE</div>
            <div class="card-value" style="font-size:17px;">GEMINI</div>
            <div class="card-desc">
                {"Connected" if client else "Configuration required"}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HOME
# ============================================================

if selected == "Home":
    hero(
        "PERSONAL HEALTH INTELLIGENCE",
        "HealthMate Nexus",
        "A futuristic AI-powered wellness workspace combining health calculators, lifestyle planning, medical-image explanation and Gemini-powered assistance in one application.",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("🤖", "AI ENGINE", "GEMINI", "Intelligent health assistance")

    with c2:
        metric_card("⚡", "MODULES", "14", "Integrated health tools")

    with c3:
        metric_card("📄", "REPORTS", "PDF", "Downloadable AI report")

    with c4:
        metric_card("●", "SYSTEM", "ONLINE", "HealthMate core ready")

    section_title("AI HEALTH CORE")

    st.markdown(
        """
        <div class="ai-core">
            <div class="ai-orb">🧠</div>
            <div class="ai-title">HEALTHMATE AI CORE</div>
            <div class="ai-sub">
                Ask questions, explore wellness topics or open an intelligent module.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    ai_home_question = st.chat_input(
        "Ask HealthMate something...",
        key="home_chat",
    )

    if ai_home_question:
        answer = ask_gemini(
            f"""
You are HealthMate AI, a general health and wellness assistant.

User question:
{ai_home_question}

Give general educational information.
Do not diagnose.
Do not prescribe medication.
Recommend professional medical care when appropriate.
Use clear, simple language.
"""
        )

        if answer:
            result_card(answer)

    section_title("INTELLIGENCE MODULES")

    row1 = st.columns(3)

    with row1[0]:
        tool_card(
            "🤖",
            "AI Symptom Checker",
            "Describe symptoms and receive general educational information."
        )

    with row1[1]:
        tool_card(
            "💊",
            "Medicine Intelligence",
            "Learn general information, common side effects and precautions."
        )

    with row1[2]:
        tool_card(
            "📷",
            "Medical Vision",
            "Upload supported images for general AI explanation."
        )

    row2 = st.columns(3)

    with row2[0]:
        tool_card(
            "⚖️",
            "BMI",
            "Calculate body mass index and its general category."
        )

    with row2[1]:
        tool_card(
            "💧",
            "Hydration",
            "Estimate general daily water intake."
        )

    with row2[2]:
        tool_card(
            "🍎",
            "Nutrition",
            "Generate a simple AI diet plan."
        )

    st.warning(
        "⚠️ HealthMate AI provides general educational and wellness information. "
        "It is not a substitute for a qualified healthcare professional."
    )


# ============================================================
# AI SYMPTOM CHECKER
# ============================================================

elif selected == "AI Symptom Checker":
    hero(
        "AI HEALTH INTELLIGENCE",
        "Symptom Checker",
        "Describe your symptoms and receive a general educational response from the HealthMate AI engine.",
    )

    section_title("AI CONVERSATION")

    symptoms = st.chat_input(
        "Describe your symptoms...",
        key="symptom_chat",
    )

    if symptoms:
        with st.chat_message("user"):
            st.write(symptoms)

        with st.chat_message("assistant"):
            with st.spinner("HealthMate AI is analyzing..."):
                answer = ask_gemini(
                    f"""
You are an AI Health Assistant.

Symptoms described by the user:
{symptoms}

Provide general educational information only.
Do not diagnose the person.
Do not prescribe medication.
Mention warning signs or situations where professional medical care may be appropriate.
Keep the answer clear and simple.
"""
                )

            if answer:
                st.write(answer)
                st.session_state.last_result = answer
                safe_pdf(symptoms, answer)

        st.info(
            "⚠️ Educational information only. A qualified healthcare professional should evaluate medical concerns."
        )


# ============================================================
# MEDICINE INFO
# ============================================================

elif selected == "Medicine Info":
    hero(
        "MEDICINE INTELLIGENCE",
        "Medicine Information",
        "Explore general educational information about a medicine. This tool does not prescribe medication.",
    )

    section_title("MEDICINE SEARCH")

    medicine = st.text_input(
        "Medicine name",
        placeholder="Example: Paracetamol",
    )

    if st.button("💊 GET MEDICINE INFORMATION"):
        if not medicine.strip():
            st.warning("Please enter a medicine name.")
        else:
            with st.spinner("Searching medicine intelligence..."):
                answer = ask_gemini(
                    f"""
Provide general educational information about this medicine.

Medicine:
{medicine}

Include:
- What it is generally used for
- Common side effects
- Precautions
- Important situations where a healthcare professional should be consulted

Keep the language simple.
Do not prescribe it.
Do not provide a personalized dose.
"""
                )

            if answer:
                st.success("Information ready")
                result_card(answer)

            st.info(
                "⚠️ Always consult a qualified healthcare professional before taking or changing medicines."
            )


# ============================================================
# BMI
# ============================================================

elif selected == "BMI Calculator":
    hero(
        "BODY METRICS",
        "BMI Calculator",
        "Calculate Body Mass Index from height and weight.",
    )

    section_title("BODY MEASUREMENTS")

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

    if st.button("⚖️ CALCULATE BMI"):
        height_m = height / 100
        bmi = weight / (height_m * height_m)
        st.session_state.bmi_value = bmi

        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Healthy"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obesity"

        a, b, c = st.columns(3)

        with a:
            metric_card("⚖️", "BMI", f"{bmi:.2f}", "Calculated value")

        with b:
            metric_card("🧬", "CATEGORY", category, "General BMI category")

        with c:
            metric_card("●", "STATUS", "READY", "Calculation complete")

        st.markdown("<br>", unsafe_allow_html=True)

        progress = min(max(bmi / 40, 0), 1)

        st.markdown(
            f"""
            <div class="card" style="min-height:auto;">
                <div class="card-label">BMI VISUALIZATION</div>
                <div style="margin-top:13px;" class="progress-shell">
                    <div class="progress-bar" style="width:{progress*100:.1f}%;"></div>
                </div>
                <div class="card-desc">
                    BMI is a general screening measure and should not be used alone to assess health.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.info(
            f"General category: {category}. BMI does not account for every factor affecting health."
        )


# ============================================================
# WATER
# ============================================================

elif selected == "Water Intake":
    hero(
        "HYDRATION INTELLIGENCE",
        "Water Intake",
        "Estimate a general daily water-intake recommendation using body weight.",
    )

    section_title("HYDRATION PROFILE")

    weight = st.number_input(
        "Weight (kg)",
        min_value=10.0,
        max_value=250.0,
        value=60.0,
        step=0.5,
    )

    if st.button("💧 CALCULATE WATER INTAKE"):
        water_ml = weight * 35
        litres = water_ml / 1000
        st.session_state.water_value = litres

        c1, c2, c3 = st.columns(3)

        with c1:
            metric_card("💧", "DAILY WATER", f"{litres:.2f} L", "General estimate")

        with c2:
            metric_card("🫗", "MILLILITRES", f"{water_ml:.0f}", "Per day estimate")

        with c3:
            metric_card("●", "STATUS", "READY", "Calculation complete")

        progress = min(litres / 4, 1)

        st.markdown(
            f"""
            <div class="card" style="margin-top:15px;min-height:auto;">
                <div class="card-label">HYDRATION TARGET VISUALIZER</div>
                <div style="margin-top:13px;" class="progress-shell">
                    <div class="progress-bar" style="width:{progress*100:.1f}%;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.info(
            "This is a general estimate. Water needs can vary with climate, activity, diet and health."
        )


# ============================================================
# DIET
# ============================================================

elif selected == "Diet Planner":
    hero(
        "NUTRITION INTELLIGENCE",
        "AI Diet Planner",
        "Generate a simple one-day Indian diet plan based on the information you provide.",
    )

    section_title("PERSONAL PROFILE")

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

    if st.button("🍎 GENERATE DIET PLAN"):
        with st.spinner("Building nutrition plan..."):
            answer = ask_gemini(
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

Keep the language simple.
Do not claim to provide medical treatment.
"""
            )

        if answer:
            st.success("Diet plan ready")
            result_card(answer)


# ============================================================
# EXERCISE
# ============================================================

elif selected == "Exercise Planner":
    hero(
        "FITNESS INTELLIGENCE",
        "AI Exercise Planner",
        "Generate a simple one-day exercise plan based on age, fitness level and goal.",
    )

    section_title("FITNESS PROFILE")

    c1, c2, c3 = st.columns(3)

    with c1:
        age = st.number_input(
            "Age",
            min_value=5,
            max_value=100,
            value=18,
        )

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

    if st.button("⚡ GENERATE EXERCISE PLAN"):
        with st.spinner("Building workout plan..."):
            answer = ask_gemini(
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
Do not provide medical treatment.
"""
            )

        if answer:
            st.success("Exercise plan ready")
            result_card(answer)


# ============================================================
# CALORIES
# ============================================================

elif selected == "Calorie Calculator":
    hero(
        "NUTRITION ANALYTICS",
        "AI Calorie Calculator",
        "Describe a meal and receive an AI-generated nutritional estimate.",
    )

    section_title("FOOD INPUT")

    food = st.text_area(
        "What did you eat today?",
        placeholder="Example: 2 chapati, dal, rice, salad and milk",
        height=140,
    )

    if st.button("🔥 CALCULATE CALORIES"):
        if not food.strip():
            st.warning("Please enter your food items.")
        else:
            with st.spinner("Estimating nutrition..."):
                answer = ask_gemini(
                    f"""
Estimate the calories and nutrition for the following food.

Food:
{food}

Include:
- Estimated total calories
- Protein
- Carbohydrates
- Fat
- Whether the meal appears balanced
- Suggestions to improve it

Make clear that the numbers are estimates.
"""
                )

            if answer:
                st.session_state.calorie_text = answer
                st.success("Nutrition estimate ready")
                result_card(answer)

            st.info(
                "⚠️ AI nutrition estimates can be inaccurate because portions and preparation methods vary."
            )


# ============================================================
# SLEEP
# ============================================================

elif selected == "Sleep Recommendation":
    hero(
        "RECOVERY INTELLIGENCE",
        "Sleep Recommendation",
        "Get general sleep and bedtime recommendations based on age, sleep duration and lifestyle.",
    )

    section_title("SLEEP PROFILE")

    c1, c2, c3 = st.columns(3)

    with c1:
        age = st.number_input(
            "Your Age",
            min_value=1,
            max_value=100,
            value=18,
        )

    with c2:
        sleep_hours = st.slider(
            "Sleep Hours",
            1,
            12,
            7,
        )
        st.session_state.sleep_value = sleep_hours

    with c3:
        lifestyle = st.selectbox(
            "Lifestyle",
            [
                "Student",
                "Working Professional",
                "Athlete",
                "Senior Citizen",
            ],
        )

    if st.button("☾ GET SLEEP ADVICE"):
        with st.spinner("Analyzing sleep profile..."):
            answer = ask_gemini(
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
            result_card(answer)

        st.info(
            "⚠️ General wellness information only. Persistent sleep problems should be discussed with a healthcare professional."
        )


# ============================================================
# MEDICAL REPORT ANALYZER
# ============================================================

elif selected == "Medical Report Analyzer":
    hero(
        "VISUAL HEALTH INTELLIGENCE",
        "Medical Report Analyzer",
        "Upload a supported medical image for a general AI-generated explanation. This tool does not diagnose medical conditions.",
    )

    st.warning(
        "⚠️ Do not use this tool as a diagnostic system. Seek professional medical evaluation for medical concerns."
    )

    section_title("UPLOAD IMAGE")

    uploaded_file = st.file_uploader(
        "Choose an image",
        type=["png", "jpg", "jpeg"],
    )

    if uploaded_file is not None:
        st.image(
            uploaded_file,
            caption="Uploaded image",
            use_container_width=True,
        )

        if st.button("🔍 ANALYZE IMAGE"):
            if not require_client():
                st.stop()

            with st.spinner("AI vision engine analyzing..."):
                try:
                    image_bytes = uploaded_file.getvalue()

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[
                            """
Explain this medical image in simple language.

Do not diagnose.
Do not prescribe treatment.
Only describe general information that can reasonably be explained from the image.
Mention that a qualified healthcare professional should review medical concerns.
""",
                            {
                                "mime_type": uploaded_file.type,
                                "data": image_bytes,
                            },
                        ],
                    )

                    answer = response.text

                except Exception as exc:
                    answer = None
                    st.error(f"Image analysis failed: {exc}")

            if answer:
                st.success("Analysis complete")
                result_card(answer)

            st.info(
                "⚠️ This is an educational explanation and is not a medical diagnosis."
            )


# ============================================================
# HEALTH DASHBOARD
# ============================================================

elif selected == "Health Dashboard":
    hero(
        "HEALTH INTELLIGENCE CENTER",
        "Your Dashboard",
        "A central view of HealthMate's health utilities and the latest values calculated during this session.",
    )

    section_title("HEALTH SNAPSHOT")

    bmi_display = (
        f"{st.session_state.bmi_value:.1f}"
        if st.session_state.bmi_value is not None
        else "—"
    )

    water_display = (
        f"{st.session_state.water_value:.1f} L"
        if st.session_state.water_value is not None
        else "—"
    )

    sleep_display = (
        f"{st.session_state.sleep_value} h"
        if st.session_state.sleep_value is not None
        else "—"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("⚖️", "BMI", bmi_display, "Last calculated value")

    with c2:
        metric_card("💧", "WATER", water_display, "Last estimate")

    with c3:
        metric_card("☾", "SLEEP", sleep_display, "Selected duration")

    with c4:
        metric_card("🤖", "AI ENGINE", "READY" if client else "OFFLINE", "Gemini status")

    section_title("HEALTH VISUALIZER")

    c1, c2 = st.columns(2)

    with c1:
        bmi_value = st.session_state.bmi_value or 0
        bmi_progress = min(max(bmi_value / 40, 0), 1)

        st.markdown(
            f"""
            <div class="card" style="min-height:auto;">
                <div class="card-label">BMI SIGNAL</div>
                <div class="card-value">{bmi_display}</div>
                <div style="margin-top:14px;" class="progress-shell">
                    <div class="progress-bar" style="width:{bmi_progress*100:.1f}%;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        sleep_value = st.session_state.sleep_value or 0
        sleep_progress = min(max(sleep_value / 10, 0), 1)

        st.markdown(
            f"""
            <div class="card" style="min-height:auto;">
                <div class="card-label">SLEEP SIGNAL</div>
                <div class="card-value">{sleep_display}</div>
                <div style="margin-top:14px;" class="progress-shell">
                    <div class="progress-bar" style="width:{sleep_progress*100:.1f}%;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    section_title("SYSTEM MODULES")

    modules = [
        ("🤖", "AI Symptom Checker"),
        ("💊", "Medicine Information"),
        ("⚖️", "BMI Calculator"),
        ("💧", "Water Intake"),
        ("🍎", "Diet Planner"),
        ("🏃", "Exercise Planner"),
        ("🔥", "Calorie Calculator"),
        ("☾", "Sleep Recommendation"),
        ("📷", "Medical Report Analyzer"),
    ]

    for start in range(0, len(modules), 3):
        cols = st.columns(3)

        for col, (icon, name) in zip(cols, modules[start:start + 3]):
            with col:
                st.markdown(
                    f"""
                    <div class="card" style="min-height:auto;margin-bottom:12px;">
                        <div style="font-size:22px;">{icon}</div>
                        <div style="margin-top:8px;font-weight:700;color:var(--text);">
                            {name}
                        </div>
                        <div style="margin-top:5px;color:var(--primary);font-size:10px;">
                            ● ONLINE
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ============================================================
# AI COMMAND CENTER
# ============================================================

elif selected == "AI Command Center":
    hero(
        "NEXUS AI CORE",
        "AI Command Center",
        "A dedicated conversational workspace for general health and wellness questions.",
    )

    section_title("AI CORE")

    st.markdown(
        """
        <div class="ai-core">
            <div class="ai-orb">🤖</div>
            <div class="ai-title">HEALTHMATE INTELLIGENCE ENGINE</div>
            <div class="ai-sub">
                SYSTEM READY • GENERAL HEALTH & WELLNESS MODE
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.chat_history:
        section_title("CONVERSATION")

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    prompt = st.chat_input(
        "Ask HealthMate AI...",
        key="command_center_chat",
    )

    if prompt:
        st.session_state.chat_history.append(
            {"role": "user", "content": prompt}
        )

        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("AI core processing..."):
                answer = ask_gemini(
                    f"""
You are HealthMate AI.

The user is asking:
{prompt}

Provide general educational health and wellness information.
Do not diagnose.
Do not prescribe medicines.
Do not present uncertain information as a diagnosis.
If the question describes an emergency or serious symptoms, encourage appropriate urgent professional care.
Use clear, practical language.
"""
                )

            if answer:
                st.write(answer)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": answer}
                )

    if st.session_state.chat_history:
        if st.button("🗑️ CLEAR AI CONVERSATION"):
            st.session_state.chat_history = []
            st.rerun()


# ============================================================
# SETTINGS
# ============================================================

elif selected == "Settings":
    hero(
        "SYSTEM CONFIGURATION",
        "Settings",
        "Customize the visual appearance of your HealthMate Nexus interface.",
    )

    section_title("APPEARANCE")

    theme = st.selectbox(
        "Theme",
        ["Dark", "Light"],
        index=0 if st.session_state.theme == "Dark" else 1,
    )

    accent_name = st.selectbox(
        "Accent Color",
        list(ACCENTS.keys()),
        index=list(ACCENTS.keys()).index(st.session_state.accent),
    )

    if theme != st.session_state.theme or accent_name != st.session_state.accent:
        st.session_state.theme = theme
        st.session_state.accent = accent_name
        st.rerun()

    section_title("SYSTEM STATUS")

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card("🤖", "GEMINI", "ONLINE" if client else "OFFLINE")

    with c2:
        metric_card("📄", "PDF ENGINE", "ONLINE" if create_pdf else "OFFLINE")

    with c3:
        metric_card("🎨", "THEME", st.session_state.theme.upper())

    st.info(
        "Settings are stored for the current Streamlit session."
    )


# ============================================================
# ABOUT
# ============================================================

elif selected == "About":
    hero(
        "SYSTEM INFORMATION",
        "About HealthMate",
        "A student-built AI health and wellness application combining Python, Streamlit and Google's Gemini AI.",
    )

    section_title("TECHNOLOGY")

    c1, c2, c3 = st.columns(3)

    with c1:
        tool_card("🐍", "Python", "Application and AI integration layer.")

    with c2:
        tool_card("◈", "Streamlit", "Interactive application interface.")

    with c3:
        tool_card("🤖", "Google Gemini", "AI generation and vision capabilities.")

    section_title("DEVELOPER")

    st.markdown(
        """
        <div class="card" style="min-height:auto;">
            <div style="font-family:Orbitron;font-size:23px;font-weight:800;color:var(--primary);">
                BHAVESH THAKUR
            </div>
            <div style="margin-top:7px;color:var(--muted);">
                Creator & Developer
            </div>
            <div style="margin-top:17px;color:var(--muted);line-height:1.7;">
                HealthMate AI is an educational project exploring the use of
                artificial intelligence and modern interfaces for general
                health and wellness utilities.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.warning(
        "⚠️ HealthMate AI is an educational application and does not provide professional medical diagnosis or treatment."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        <strong>HEALTHMATE NEXUS</strong><br>
        AI Health Intelligence Platform<br><br>
        © 2026 • Developed by <strong>Bhavesh Thakur</strong> • Powered by Google Gemini<br><br>
        EDUCATIONAL PURPOSE ONLY
    </div>
    """,
    unsafe_allow_html=True,
)
