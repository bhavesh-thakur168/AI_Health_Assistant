# =========================================================
# PAGE: MEDICAL REPORT ANALYZER
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
                        # Construct proper byte Part payload for the google-genai SDK
                        image_part = types.Part.from_bytes(
                            data=uploaded_file.getvalue(),
                            mime_type=uploaded_file.type,
                        )

                        response = client.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=[
                                """
Explain this medical image in simple language.

Do not diagnose.
Do not prescribe treatment.
Describe only general information that can reasonably be explained from the image.
Recommend professional medical review when appropriate.
""",
                                image_part,
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
