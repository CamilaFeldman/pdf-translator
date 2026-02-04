import streamlit as st
from google.cloud import translate_v3beta1 as translate
from pypdf import PdfReader, PdfWriter
import io  
import os
# --- CONFIGURATION ---
# Your project ID from gcloud CLI
PROJECT_ID = "pdf-translator-gcp" 
LOCATION = "us-central1" 

st.set_page_config(page_title="Pro PDF Translator")

st.title("🚀 Google Cloud PDF Translator")
st.caption("Perfect layout, images, and tables preservation.")

uploaded_file = st.file_uploader("Upload an academic PDF", type="pdf")

if uploaded_file:
    if st.button("Translate Entire Document"):
        with st.spinner("Processing a large document... splitting into chunks of 20 pages."):
            try:
                reader = PdfReader(uploaded_file)
                total_pages = len(reader.pages)
                translated_writer = PdfWriter()
                
                # Progress tracking
                progress_bar = st.progress(0)
                
                # Process in chunks of 20
                for i in range(0, total_pages, 20):
                    chunk_writer = PdfWriter()
                    end_page = min(i + 20, total_pages)
                    
                    # Create a temporary PDF for the current chunk
                    for page_num in range(i, end_page):
                        chunk_writer.add_page(reader.pages[page_num])
                    
                    chunk_buffer = io.BytesIO()
                    chunk_writer.write(chunk_buffer)
                    
                    # Send chunk to Google
                    client = translate.TranslationServiceClient()
                    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}"
                    
                    response = client.translate_document(
                        request={
                            "parent": parent,
                            "target_language_code": "es",
                            "document_input_config": {
                                "content": chunk_buffer.getvalue(),
                                "mime_type": "application/pdf",
                            },
                        }
                    )
                    
                    # Read the translated chunk back and add to the final writer
                    translated_chunk_bytes = response.document_translation.byte_stream_outputs[0]
                    translated_chunk_reader = PdfReader(io.BytesIO(translated_chunk_bytes))
                    
                    for page in translated_chunk_reader.pages:
                        translated_writer.add_page(page)
                    
                    # Update progress
                    progress_bar.progress(end_page / total_pages)

                # Final result
                final_buffer = io.BytesIO()
                translated_writer.write(final_buffer)
                
                st.success(f"✅ Finished! Translated {total_pages} pages.")
                st.download_button(
                    label="📥 Download Full Translated PDF",
                    data=final_buffer.getvalue(),
                    file_name=f"translated_full_{uploaded_file.name}",
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"Error: {e}")
