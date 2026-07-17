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
elif selected == "BMI Calculator":

    st.title("📊 BMI Calculator")

    st.write("Calculate your Body Mass Index (BMI).")

    height = st.number_input(
        "Enter your height (in cm)",
        min_value=50.0,
        max_value=250.0,
        value=170.0
    )

    weight = st.number_input(
        "Enter your weight (in kg)",
        min_value=10.0,
        max_value=300.0,
        value=65.0
    )

    if st.button("Calculate BMI"):

        height_m = height / 100
        bmi = weight / (height_m * height_m)

        st.subheader(f"Your BMI is: {bmi:.2f}")

        if bmi < 18.5:
            st.warning("You are Underweight.")

        elif bmi < 25:
            st.success("You have a Healthy Weight.")

        elif bmi < 30:
            st.warning("You are Overweight.")

        else:
            st.error("You are in the Obese category.")

        st.info("⚠️ BMI is a general health indicator and should not be used as the only measure of health.")
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
