import streamlit as st
import requests
from pypdf import PdfReader
from fpdf import FPDF
import io

st.set_page_config(page_title="PDF Translator Pro")

st.title("📄 Full PDF Translator")
st.caption("Translates segment by segment and generates a new PDF")

model_name = st.sidebar.selectbox("Select Model:", ["gemma:2b", "llama3", "mistral"])

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

def translate_chunk(text, model):
    url = "http://localhost:11434/api/generate"
    prompt = f"Act as a professional scientific translator. Translate the following academic text from English to Spanish. Maintain a formal tone and ensure correct use of Spanish articles (el, la, los, las) and gender agreement. Return ONLY the translated text::\n\n{text}"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3  # Lower temperature = more stable and precise translation
         }
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()['response']
    except Exception as e:
        return f"[Error: {e}]"

if uploaded_file:
    reader = PdfReader(uploaded_file)
    
    if st.button("Start Full Translation"):
        full_translated_text = ""
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # We iterate page by page for better organization
        pages = reader.pages
        total_pages = len(pages)
        
        for i, page in enumerate(pages):
            status_text.text(f"Processing page {i+1} of {total_pages}...")
            page_text = page.extract_text()
            
            # Simple chunking: process the page text
            # (If a page is too long, you could split it more)
            translated_page = translate_chunk(page_text, model_name)
            full_translated_text += translated_page + "\n\n"
            # LIVE LOG: This shows the text on screen immediately
            with st.expander(f"Page {i+1} Preview"):
                st.write(translated_page)
            # Update progress
            progress_bar.progress((i + 1) / total_pages)

        st.success("Translation finished!")

        # --- PDF GENERATION (fpdf2 Version) ---
        st.subheader("Download Result")
        
        # 1. Create PDF object
        # We use 'UTF-8' friendly settings if possible, but keep it KISS with Arial
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=11)
        
        # 2. Process text to avoid encoding crashes
        # fpdf2 handles latin-1 better but let's be safe
        safe_text = full_translated_text.encode('latin-1', 'replace').decode('latin-1')
        
        # 3. Add text to PDF
        pdf.multi_cell(0, 8, txt=safe_text)
        
        # 4. CRITICAL FIX: Convert output to bytes for Streamlit
        try:
            # We get the PDF data as a bytes object
            pdf_data = pdf.output() 
            
            # If pdf_data is bytearray, convert it to bytes
            if isinstance(pdf_data, bytearray):
                pdf_data = bytes(pdf_data)

            st.download_button(
                label="Download Translated PDF",
                data=pdf_data,
                file_name="translated_full.pdf",
                mime="application/pdf"
            )
            st.success("PDF ready for download!")
        except Exception as e:
            st.error(f"Error generating PDF file: {e}")
