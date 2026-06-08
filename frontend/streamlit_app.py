import streamlit as st
import requests
import os

# Page configuration
st.set_page_config(
    page_title="Ask My Docs",
    page_icon="📚",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# API Endpoint
API_URL = "http://127.0.0.1:8000"

st.title("📚 Ask My Documents")
st.markdown("### Privacy-first local RAG platform powered by Ollama.")

# Sidebar for file upload
with st.sidebar:
    st.header("Upload Documents")
    uploaded_file = st.file_uploader("Choose a PDF, DOCX or TXT file", type=["pdf", "docx", "txt"])
    
    if uploaded_file is not None:
        if st.button("Process Document"):
            with st.spinner("Ingesting document..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                try:
                    response = requests.post(f"{API_URL}/upload", files=files)
                    if response.status_code == 200:
                        st.success(f"Successfully processed {uploaded_file.name}")
                    else:
                        st.error(f"Error: {response.json().get('detail')}")
                except Exception as e:
                    st.error(f"Could not connect to API: {e}")

st.divider()

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "citations" in message and message["citations"]:
            with st.expander("Sources"):
                for cite in message["citations"]:
                    st.info(f"📄 {cite.get('source')} (Page {cite.get('page', 'N/A')})")

# Chat input
if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Reasoning..."):
            try:
                response = requests.post(
                    f"{API_URL}/query", 
                    json={"question": prompt}
                )
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer")
                    citations = data.get("citations", [])
                    
                    st.markdown(answer)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "citations": citations
                    })
                    
                    if citations:
                        with st.expander("Sources"):
                            for cite in citations:
                                st.info(f"📄 {cite.get('source')} (Page {cite.get('page', 'N/A')})")
                else:
                    st.error(f"API Error: {response.json().get('detail')}")
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")
