from app.utils.resume_parser import extract_text_from_pdf


pdf_path = "uploads/resume.pdf"

text = extract_text_from_pdf(pdf_path)

print(text)

