import streamlit as st
import google.generativeai as genai

# Replace with your NEW API key
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Use a current model
model = genai.GenerativeModel("models/gemini-flash-lite-latest")
st.set_page_config(page_title="AI Health Assistant")

st.title("🩺 AI Health Assistant")

symptoms = st.text_area("Describe your symptoms")

if st.button("Get Advice"):
    if symptoms.strip() == "":
        st.warning("Please enter your symptoms.")
    else:
        prompt = f"""
You are an AI Health Assistant.

Rules:
- Give only general health advice.
- Never claim to diagnose diseases.
- Suggest basic home care when appropriate.
- If symptoms are severe, tell the user to consult a doctor immediately.
- Keep the answer simple and easy to understand.

Symptoms:
{symptoms}
"""

        response = model.generate_content(prompt)

        st.subheader("Advice")
        st.write(response.text)

st.markdown("---")
st.caption("⚠️ This AI assistant is for educational purposes only and is not a substitute for professional medical advice.")
