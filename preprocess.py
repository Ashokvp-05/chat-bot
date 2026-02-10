import os
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
import platform


poppler_path = None
if platform.system() == "Windows":
    # Common default install locations for Tesseract
    tesseract_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe")
    ]
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break
            
    base_poppler = os.path.abspath("poppler")
    if os.path.exists(base_poppler):
        for root, dirs, files in os.walk(base_poppler):
            if "pdftoppm.exe" in files:
                poppler_path = root
                break

def extract_text_from_pdf(file_path):
    text = ""
    # Method 1: Try native text extraction
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    
    if len(text.strip()) < 50:
        print(f"Native extraction failed for {file_path}. Trying OCR...")
        try:
            # Note: This requires poppler to be installed and in PATH
            images = convert_from_path(file_path, poppler_path=poppler_path)
            for image in images:
                text += pytesseract.image_to_string(image) + "\n"
        except Exception as e:
            print(f"OCR failed: {e}. Make sure Poppler and Tesseract are installed.")
            
    return text

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def load_documents(folder_path="docs"):
    docs = []
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".pdf") or file_name.endswith(".txt"):
            file_path = os.path.join(folder_path, file_name)
            text = ""
            if file_name.endswith(".pdf"):
                text = extract_text_from_pdf(file_path)
            else:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        text = f.read()
                except Exception as e:
                    print(f"Error reading {file_name}: {e}")
            
            if text.strip():
                docs.extend(chunk_text(text))
            else:
                print(f"Warning: No text extracted from {file_name}")
    return docs

if __name__ == "__main__":
    documents = load_documents()
    print(f"Loaded {len(documents)} text chunks")
