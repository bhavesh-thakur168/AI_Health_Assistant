import streamlit as st
from streamlit_option_menu import option_menu
from google import genai
from report import create_pdf

client = genai.Client( api_key=st.secrets["GEMINI_API_KEY"])

# -----------------------------
# Page Settings
# -----------------------------
st.set_page_config(
    page_title="HealthMate AI",
    page_icon="logo.png",
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
            "Medicine Info",
            "BMI Calculator",
            "Water Intake",
            "Diet Planner",
            "Exercise Planner",
            "Calorie Calculator",
            "Sleep Recommendation",
            "About"
        ],
        icons=[
            "house",
            "robot",
            "capsule",
            "activity",
            "cup-straw",
            "egg-fried",
            "heart-pulse",
            "fire",
            "moon-stars",
            "info-circle"
        ],
        default_index=0,
    )

# -----------------------------
# HOME
# -----------------------------
if selected == "Home":

    st.title("🏥 HealthMate AI")

    st.subheader("Your Intelligent Health Companion")

    st.markdown("---")

    st.image(
        "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=1200",
        use_container_width=True
    )

    st.markdown("## 👋 Welcome")

    st.write("""
HealthMate AI is designed to provide general health guidance using Artificial Intelligence.

You can use this application to:

• 🤖 Check common symptoms

• 📊 Calculate BMI

• 💧 Calculate daily water intake

• 🍎 Get healthy lifestyle tips

• 🏃 Improve your fitness

This project is developed using Python, Streamlit and Google's Gemini AI.
""")
   
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🤖 AI Model", "Gemini")

    with col2:
        st.metric("🩺 Features", "6")

    with col3:
        st.metric("📄 Reports", "PDF")


    st.warning(
        "⚠ This application provides educational information only. "
        "It is NOT a substitute for professional medical advice."
    )
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
                    model="gemini-3.1-flash-lite",
                    contents=prompt
                )

            st.success("Analysis Complete")

            st.markdown("## 💡 AI Advice")
            st.write(response.text)

            # Create PDF
            pdf_file = create_pdf(symptoms, response.text)

            # Read PDF
            with open(pdf_file, "rb") as file:
                pdf_data = file.read()

            # Download button
            st.download_button(
                label="📄 Download Health Report",
                data=pdf_data,
                file_name="Health_Report.pdf",
                mime="application/pdf"
            )

            st.info(
                "⚠ This advice is for educational purposes only. "
                "Always consult a qualified healthcare professional for medical concerns."
            )
elif selected == "Medicine Info":

    st.title("💊 AI Medicine Information")

    medicine = st.text_input(
        "Enter Medicine Name",
        placeholder="Example: Paracetamol"
    )

    if st.button("Get Medicine Information"):

        if medicine.strip() == "":
            st.warning("Please enter a medicine name.")

        else:

            with st.spinner("Searching..."):

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

                response = client.models.generate_content(
                    model="gemini-3.1-flash-lite",
                    contents=prompt
                )

            st.success("Information Ready")

            st.write(response.text)

            st.info(
                "⚠ Always consult a doctor before taking any medicine."
            )
elif  selected == "BMI Calculator":
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
elif selected == "Water Intake":

    st.title("💧 Water Intake Calculator")

    st.write("Calculate your recommended daily water intake.")

    weight = st.number_input(
        "Enter your weight (kg)",
        min_value=10.0,
        max_value=250.0,
        value=60.0
    )

    if st.button("Calculate Water Intake"):

        water = weight * 35

        litres = water / 1000

        st.success(f"💧 Recommended Water Intake: {litres:.2f} Litres/day")

        st.info(
            "This is a general recommendation. Your needs may vary depending on climate, activity level, and health."
        )
elif selected == "Diet Planner":

    st.title("🍎 AI Diet Planner")

    age = st.number_input(
        "Age",
        1,
        100,
        18
    )

    gender = st.selectbox(
        "Gender",
        ["Male","Female"]
    )

    goal = st.selectbox(
        "Goal",
        [
            "Weight Loss",
            "Weight Gain",
            "Healthy Lifestyle"
        ]
    )

    if st.button("Generate Diet Plan"):

        with st.spinner("Preparing your AI diet plan..."):

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

            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt
            )

        st.success("Diet Plan Ready")

        st.write(response.text)
elif selected == "Exercise Planner":

    st.title("🏃 AI Exercise Planner")

    age = st.number_input(
        "Age",
        min_value=5,
        max_value=100,
        value=18
    )

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

    if st.button("Generate Exercise Plan"):

        with st.spinner("Creating your workout plan..."):

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

        st.success("Exercise Plan Ready!")

        st.write(response.text)

elif selected == "Calorie Calculator":

    st.title("🔥 AI Calorie Calculator")

    food = st.text_area(
        "What did you eat today?",
        placeholder="Example: 2 chapati, dal, rice, salad and milk"
    )

    if st.button("Calculate Calories"):

        if food.strip() == "":
            st.warning("Please enter your food items.")

        else:

            with st.spinner("Calculating calories..."):

                prompt = f"""
Estimate the calories for the following food.

Food:
{food}

Include:

• Estimated total calories

• Protein

• Carbohydrates

• Fat

• Whether the meal is healthy

• Suggestions to improve it

Keep the answer simple.
"""

                response = client.models.generate_content(
                    model="gemini-3.1-flash-lite",
                    contents=prompt
                )

            st.success("Calories Estimated")

            st.write(response.text)

            st.info("⚠ This is an AI estimate and may not be completely accurate.")
            
elif selected == "Sleep Recommendation":

    st.title("😴 AI Sleep Recommendation")

    age = st.number_input(
        "Your Age",
        min_value=1,
        max_value=100,
        value=18
    )

    sleep_hours = st.slider(
        "How many hours do you sleep each night?",
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

    if st.button("Get Sleep Advice"):

        with st.spinner("Analyzing your sleep..."):

            prompt = f"""
Provide simple sleep recommendations.

Age: {age}
Sleep Hours: {sleep_hours}
Lifestyle: {lifestyle}

Include:
- Is the sleep duration adequate?
- Tips to improve sleep quality.
- Healthy bedtime habits.
- When to consult a doctor.

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
