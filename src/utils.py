import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import os

def setup_page():
    """Configure the Streamlit page"""
    st.set_page_config(
        page_title="VLM Transcriber",
        page_icon="📝",
        layout="wide"
    )
    st.title("VLM Transcriber")
    st.markdown("""
    Extract text from images using Google's Gemini Vision API.
    Upload your images below to get started.
    """)

def initialize_session_state():
    """Initialize session state variables"""
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = []

def handle_file_upload() -> List[Any]:
    """Handle file upload and validation"""
    uploaded_files = st.file_uploader(
        "Upload images (JPG, JPEG, PNG, WEBP)",
        type=['jpg', 'jpeg', 'png', 'webp'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if len(uploaded_files) > 100:
            st.error("Maximum 100 images allowed per batch")
            return None
            
        for file in uploaded_files:
            if file.size > 20 * 1024 * 1024:  # 20MB
                st.error(f"File {file.name} exceeds 20MB size limit")
                return None
                
    return uploaded_files

def display_results(results: List[Dict[str, Any]]):
    """Display processing results in a table"""
    if not results:
        return
        
    df = pd.DataFrame(results)
    st.dataframe(
        df[[
            'filename', 'extracted_text', 'confidence_score',
            'status', 'error', 'processing_time'
        ]],
        use_container_width=True
    )

def export_results(results: List[Dict[str, Any]]):
    """Export results to CSV/XLSX"""
    if not results:
        return
        
    df = pd.DataFrame(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    col1, col2 = st.columns(2)
    
    # Export to CSV
    csv = df.to_csv(index=False)
    col1.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"extracted_text_{timestamp}.csv",
        mime="text/csv"
    )
    
    # Export to XLSX
    excel_file = f"extracted_text_{timestamp}.xlsx"
    df.to_excel(excel_file, index=False)
    with open(excel_file, 'rb') as f:
        col2.download_button(
            label="Download Excel",
            data=f,
            file_name=excel_file,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    # Clean up the temporary Excel file
    os.remove(excel_file) 