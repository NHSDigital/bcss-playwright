from pypdf import PdfReader

def extract_nhs_no_from_pdf(file: str):
    reader = PdfReader(file)
    nhs_number = []
    # For loop looping through all pages of the file to find the NHS Number
    for pages in reader.pages:
        text = pages.extract_text()
        if "NHS No" in text:
            # If NHS number is found split the text by every new line into a list
            text = text.splitlines(True)
            for split_text in text:
                if "NHS No" in split_text:
                    # If a string is found containing "NHS No" only digits are stored into nhs_no
                    nhs_no = "".join([ele for ele in split_text if ele.isdigit()])
                    nhs_number.append(nhs_no)
                    break
    return nhs_number
