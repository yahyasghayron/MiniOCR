import base64
import io
import json
from PyPDF2 import PdfReader
from PIL import Image, UnidentifiedImageError
import pytesseract

def decode_base64_file(base64_str):
    file_data = base64.b64decode(base64_str)
    
    # Check if the data is a PDF
    if file_data[:4] == b'%PDF':
        return file_data, 'pdf'
    
    # Check if the data is an image by trying to open it with PIL
    try:
        image = Image.open(io.BytesIO(file_data))
        return image, 'image'
    except UnidentifiedImageError:
        print("Unsupported file format")
        return None, 'unknown'

def extract_text_from_image(image):
    return pytesseract.image_to_string(image)

def extract_text_from_pdf(pdf_data):
    text = ""
    with io.BytesIO(pdf_data) as f:
        pdf_reader = PdfReader(f)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def base64_to_json(base64_str):
    file_data, file_type = decode_base64_file(base64_str)
    if file_data is None:
        return json.dumps({"error": "Invalid file data"})
    
    if file_type == 'image':
        text = extract_text_from_image(file_data)
    elif file_type == 'pdf':
        text = extract_text_from_pdf(file_data)
    else:
        return json.dumps({"error": "Unsupported file format"})
    
    json_data = json.dumps({"extracted_text": text}, indent=4)
    return json_data

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python ocr.py <base64_string>")
        sys.exit(1)
    
    base64_input = sys.argv[1]
    
    if base64_input.startswith('@'):
        base64_input = base64_input[1:]
        with open(base64_input, 'r') as f:
            base64_str = f.read().strip()
    else:
        base64_str = base64_input
    
    json_output = base64_to_json(base64_str)
    print(json_output)

