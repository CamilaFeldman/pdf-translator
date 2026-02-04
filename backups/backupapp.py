import streamlit as st
import requests
from pypdf import PdfReader

# Page configuration
st.set_page_config(page_title="Local PDF Translator")

st.title("📄 Academic PDF Translator")
st.caption("Running locally with Ollama (CPU-friendly)")

# Sidebar for model selection
# Tip: Use 'gemma:2b' if your CPU is struggling
model_name = st.sidebar.selectbox("Select Model:", ["gemma:2b", "llama3", "mistral"])

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file:
    # 1. Extract text from PDF
    reader = PdfReader(uploaded_file)
    raw_text = ""
    for page in reader.pages:
        raw_text += page.extract_text()
    
    st.success(f"Successfully loaded {len(reader.pages)} pages.")

    # 2. Translation Button
    if st.button("Translate first 2000 characters"):
        #DOCKER        
        # Local Ollama API endpoint
        #url = "http://host.docker.internal:11434/api/generate"
        # Use 'localhost' for manual run, 'host.docker.internal' for Docker
        url = "http://localhost:11434/api/generate"
        # Slicing text to avoid CPU timeout
        text_to_translate = raw_text[:2000]
        
        # Formatting the prompt for the LLM
        prompt_query = f"Translate the following academic text to Spanish. Only return the translation: \n\n{text_to_translate}"
        
        payload = {
            "model": model_name,
            "prompt": prompt_query,
            "stream": False
        }

        with st.spinner("Processing on CPU... please wait."):
            try:
                # Sending request to Ollama
                response = requests.post(url, json=payload)
                response.raise_for_status() # Check for HTTP errors
                
                result = response.json()['response']
                
                # 3. Display Result
                st.subheader("Spanish Translation:")
                st.write(result)
                
            except Exception as e:
                st.error(f"Error: {e}")
                st.info("Make sure Ollama is running (`ollama serve`) and the model is downloaded.")
