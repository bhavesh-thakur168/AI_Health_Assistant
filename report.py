from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def create_pdf(symptoms, advice):

    filename = "Health_Report.pdf"

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("<b>HealthMate AI</b>", styles["Title"]))

    story.append(Paragraph("<b>Health Report</b>", styles["Heading2"]))

    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph("<b>Symptoms:</b>", styles["Heading3"]))
    story.append(Paragraph(symptoms, styles["BodyText"]))

    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph("<b>AI Advice:</b>", styles["Heading3"]))
    story.append(Paragraph(advice, styles["BodyText"]))

    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph(
        "<b>Disclaimer:</b> This report is for educational purposes only. "
        "Consult a qualified healthcare professional for medical advice.",
        styles["Italic"]
    ))

    doc.build(story)

    return filename