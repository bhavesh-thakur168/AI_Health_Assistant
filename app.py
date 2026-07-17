import streamlit as st
from streamlit_option_menu import option_menu
from google import genai

# -----------------------------
# Gemini API
# -----------------------------
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# -----------------------------
# Page Settings
# -----------------------------
st.set_page_config(
    page_title="HealthMate AI",
    page_icon="🩺",
    layout="wide"
)

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:

    selected = option_menu(
        "HealthMate AI",
        [
            "Home",
            "AI Symptom Checker",
            "BMI Calculator",
            "Water Intake",
            "About"
        ],
        icons=[
            "house",
            "robot",
            "activity",
            "cup-straw",
            "info-circle"
        ],
        default_index=0,
    )

# -----------------------------
# HOME
# -----------------------------
if selected == "Home":

    st.title("🩺 HealthMate AI")

    st.subheader("Your Intelligent Health Companion")

    st.write("---")

    st.success("Welcome!")

    st.write("""
This AI Health Assistant can help you with:

✅ General Health Advice

✅ BMI Calculator

✅ Water Intake Calculator

✅ AI Symptom Checker

✅ Healthy Lifestyle Tips
""")

    st.info(
        "⚠ This application provides educational information only. "
        "It does NOT replace a doctor."
    )

# -----------------------------
# ABOUT
# -----------------------------
elif selected == "AI Symptom Checker":

    st.title("🤖 AI Symptom Checker")

    st.write("Describe your symptoms below.")

    symptoms = st.text_area(
        "Symptoms",
        placeholder="Example: I have a headache, fever and sore throat."
    )

    if st.button("🔍 Analyze Symptoms"):

        if symptoms.strip() == "":
            st.warning("Please enter your symptoms.")

        else:

            with st.spinner("Analyzing your symptoms..."):

                prompt = f"""
You are an AI Health Assistant.

Rules:
- Give only general health advice.
- Never diagnose diseases.
- Suggest simple home care when appropriate.
- Tell users to consult a doctor if symptoms are severe.
- Keep the answer easy to understand.

Symptoms:
{symptoms}
"""

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

            st.success("Analysis Complete")

            st.markdown("## 💡 AI Advice")

            st.write(response.text)

            st.info(
                "⚠ This advice is for educational purposes only. "
                "Always consult a qualified healthcare professional for medical concerns."
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

