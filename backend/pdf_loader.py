from pypdf import PdfReader


def load_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


if __name__ == "__main__":
    pdf_path = "everythingschool.pdf"
    text = load_pdf(pdf_path)

    print("=== PDF LOADED SUCCESSFULLY ===")
    print("Characters:", len(text))
    print("\n--- SAMPLE ---\n")
    print(text[:1000])
