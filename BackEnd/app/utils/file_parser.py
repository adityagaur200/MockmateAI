import PyPDF2


async def extract_text_from_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file.file)

        text = ""

        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"

        return text.strip()

    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")