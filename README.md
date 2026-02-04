# 📄 Hybrid PDF Translator (Local LLM & Google Cloud)

A high-performance PDF translating tool (English -> Spanish) designed to handle everything from small private files to extensive academic papers (200+ pages) while preserving the original layout and structure.
<img width="1919" height="898" alt="imagen" src="https://github.com/user-attachments/assets/af1bf009-ebd4-41af-a6d9-07819ae96fef" />

## 🚀 Features

The system offers two distinct translation engines:

1.  **Professional Mode (Google Cloud Translation API):**
    * **Full Fidelity:** Preserves the original layout, including tables, images, and text alignment.
    * **Scalability:** Implements an "Auto-Splitting" algorithm that breaks large PDFs into 20-page chunks (bypassing Cloud API limits) and merges them back automatically.
    * **Enterprise Quality:** Powered by Google's neural machine translation for documents.

2.  **Private Mode (Local Ollama):**
    * **Privacy First:** Data never leaves your local machine.
    * **Zero Cost:** Utilizes open-source models like `Gemma`, `Llama3`, or `Mistral` running locally.
    * **Live Preview:** View translations page-by-page in real-time through an interactive UI.


## 🛠️ Prerequisites

### For Local Mode:
- [Ollama](https://ollama.ai/) installed and running.
- A downloaded model (e.g., `ollama pull gemma:2b`).

### For Google Cloud Mode:
- A [Google Cloud Console](https://console.cloud.google.com/) account.
- **Cloud Translation API** enabled.
- Authentication configured via the Google Cloud CLI:
  ```gcloud auth application-default login```

## 🔧 Installation

1. **Clone the repository:**
```git clone [https://github.com/CamilaFeldman/pdf-translator.git](https://github.com/CamilaFeldman/pdf-translator.git)```
    ```cd pdf-translator```

2. **Install dependencies:**
```pip install requirement.txt```


3. **Run the application:**
```streamlit run app.py```
## 📖 How to Use

1. **Select Engine:** Use the sidebar to choose between "Google Cloud" or "Ollama".
2. **Upload PDF:** Drag and drop your file into the uploader.
3. **Translate:** Click the "Start Full Translation" button.
4. **Download:** Once finished, download your translated PDF using the generated button.


## 🏗️ Technical Architecture

* **Frontend:** Streamlit for a reactive user interface.
* **PDF Processing:** `pypdf` for structural manipulation (splitting/merging) and `fpdf2` for local document generation.
* **AI Integration:** REST API (Ollama) and gRPC (Google Cloud SDK).
* **Memory Management:** Utilizes `io.BytesIO` for in-memory file processing to ensure high performance and disk safety.

## 🛡️ Security Note

This project uses **Application Default Credentials (ADC)**. 

## 🐳 Docker & NAS Deployment

This project includes a `Dockerfile` because it is designed to be **containerized**. 

While you can run it locally for development, the ultimate goal is to migrate the application to a **NAS (Network Attached Storage)** using Docker/Container Station. This allows:
- **24/7 Availability:** The translator stays accessible to anyone on the local network without keeping a PC turned on.
- **Resource Management:** Runs in an isolated environment, ensuring dependencies don't conflict with the NAS operating system.
- **Self-Hosting:** Complete control over your tools and data.

To build the image:
```docker build -t pdf-translator```
