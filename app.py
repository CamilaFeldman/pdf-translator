import streamlit as st
import requests
import io
import os
from pypdf import PdfReader, PdfWriter
from fpdf import FPDF
from google.cloud import translate_v3beta1 as translate

# --- CONFIGURACIÓN ---
PROJECT_ID = "pdf-translator-gcp" 
LOCATION = "us-central1" 

st.set_page_config(page_title="Hybrid PDF Translator", layout="wide")

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.title("Configuración")
    engine = st.radio(
        "Motor de Traducción:",
        ("Google Cloud (Profesional - Mantiene Layout)", "Ollama (Local - Solo Texto)")
    )
    
    if engine == "Ollama (Local - Solo Texto)":
        model_name = st.text_input("Modelo de Ollama:", value="gemma:2b")
        st.info("Asegúrate de que Ollama esté corriendo (`ollama serve`)")
    else:
        st.success("GCP preservará imágenes y tablas.")

# --- FUNCIONES DE SOPORTE ---

def translate_chunk(text, model):
    """Función para Ollama"""
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": f"Act as a professional scientific translator. Translate to Spanish: {text}",
        "stream": False
    }
    try:
        response = requests.post(url, json=payload)
        return response.json().get("response", "")
    except Exception as e:
        return f"[Error Ollama: {e}]"

# --- UI PRINCIPAL ---
st.title("📄 Traductor de PDF Híbrido")
uploaded_file = st.file_uploader("Sube tu archivo PDF", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    total_pages = len(reader.pages)
    
    if st.button("Iniciar Traducción Completa"):
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # --- OPCIÓN 1: GOOGLE CLOUD ---
            if "Google Cloud" in engine:
                output_writer = PdfWriter()
                with st.spinner("Traduciendo con Google Cloud (preservando diseño)..."):
                    for i in range(0, total_pages, 20):
                        end_page = min(i + 20, total_pages)
                        status_text.text(f"Enviando páginas {i+1} a {end_page} a Google...")
                        
                        chunk_writer = PdfWriter()
                        for p in range(i, end_page):
                            chunk_writer.add_page(reader.pages[p])
                        
                        chunk_buffer = io.BytesIO()
                        chunk_writer.write(chunk_buffer)
                        
                        # Llamada a la API de Google
                        client = translate.TranslationServiceClient()
                        parent = f"projects/{PROJECT_ID}/locations/{LOCATION}"
                        response = client.translate_document(
                            request={
                                "parent": parent,
                                "target_language_code": "es",
                                "document_input_config": {"content": chunk_buffer.getvalue(), "mime_type": "application/pdf"},
                            }
                        )
                        
                        translated_bytes = response.document_translation.byte_stream_outputs[0]
                        translated_reader = PdfReader(io.BytesIO(translated_bytes))
                        for page in translated_reader.pages:
                            output_writer.add_page(page)
                        
                        progress_bar.progress(end_page / total_pages)

                # Descarga para GCP
                final_buffer = io.BytesIO()
                output_writer.write(final_buffer)
                st.success("✅ ¡Traducción profesional lista!")
                st.download_button("📥 Descargar PDF Traducido (GCP)", final_buffer.getvalue(), "translated_gcp.pdf")

            # --- OPCIÓN 2: OLLAMA ---
            else:
                full_translated_text = ""
                with st.spinner("Traduciendo localmente con Ollama..."):
                    for i, page in enumerate(reader.pages):
                        status_text.text(f"Procesando página {i+1} de {total_pages}...")
                        page_text = page.extract_text()
                        
                        translated_page = translate_chunk(page_text, model_name)
                        full_translated_text += translated_page + "\n\n"
                        
                        with st.expander(f"Vista Previa Página {i+1}"):
                            st.write(translated_page)
                        
                        progress_bar.progress((i + 1) / total_pages)

                # Generación de PDF con fpdf2 para Ollama
                st.subheader("Resultado Local")
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=11)
                safe_text = full_translated_text.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 8, txt=safe_text)
                
                pdf_data = pdf.output()
                if isinstance(pdf_data, bytearray):
                    pdf_data = bytes(pdf_data)

                st.download_button("📥 Descargar PDF (Texto - Ollama)", pdf_data, "translated_ollama.pdf")
                st.success("✅ ¡PDF de texto generado!")

        except Exception as e:
            st.error(f"Se produjo un error: {e}")
