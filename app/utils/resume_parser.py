import pymupdf


def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF resume using PyMuPDF.
    """

    text_parts = []

    pdf = pymupdf.open(file_path)

    try:
        for page in pdf:
            page_text = page.get_text(
                "text",
                sort=True
            )

            if page_text:
                text_parts.append(page_text)

    finally:
        pdf.close()

    text = "\n".join(text_parts)

    # Clean unnecessary whitespace
    lines = []

    for line in text.splitlines():
        line = line.strip()

        if line:
            lines.append(line)

    return "\n".join(lines)
