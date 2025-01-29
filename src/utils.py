import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Tuple
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
    if 'custom_columns' not in st.session_state:
        st.session_state.custom_columns = {}
    if 'separate_sheets' not in st.session_state:
        st.session_state.separate_sheets = False
    if 'image_descriptions' not in st.session_state:
        st.session_state.image_descriptions = {}

def handle_file_upload() -> Tuple[List[Any], Dict[str, str]]:
    """
    Handle file upload and collect image descriptions.
    
    Returns:
        Tuple[List[Any], Dict[str, str]]: Uploaded files and their descriptions
    """
    uploaded_files = st.file_uploader(
        "Upload images (JPG, JPEG, PNG, WEBP)",
        type=['jpg', 'jpeg', 'png', 'webp'],
        accept_multiple_files=True
    )
    
    descriptions = {}
    
    if uploaded_files:
        if len(uploaded_files) > 100:
            st.error("Maximum 100 images allowed per batch")
            return None, {}
            
        for file in uploaded_files:
            if file.size > 20 * 1024 * 1024:  # 20MB
                st.error(f"File {file.name} exceeds 20MB size limit")
                return None, {}
            
            # Get description for each file
            description = st.text_area(
                f"Description for {file.name}",
                value=st.session_state.image_descriptions.get(file.name, ""),
                key=f"desc_{file.name}",
                help="Provide context or specific instructions for processing this image"
            )
            descriptions[file.name] = description
        
        # Update session state
        st.session_state.image_descriptions.update(descriptions)
                
    return uploaded_files, descriptions

def handle_column_customization(processor):
    """Handle column name customization"""
    st.sidebar.header("Output Settings")
    
    # Get current column names
    current_columns = processor.get_column_names()
    custom_columns = {}
    
    with st.sidebar.expander("Customize Column Names"):
        st.write("Enter custom names for output columns:")
        for key, default_name in current_columns.items():
            custom_name = st.text_input(
                f"{default_name}",
                value=st.session_state.custom_columns.get(key, default_name),
                key=f"col_{key}"
            )
            if custom_name != default_name:
                custom_columns[key] = custom_name
    
    # Update session state and processor if changes made
    if custom_columns != st.session_state.custom_columns:
        st.session_state.custom_columns = custom_columns
        processor.set_column_names(custom_columns)
    
    # Separate sheets option
    separate_sheets = st.sidebar.checkbox(
        "Create separate sheets for each image",
        value=st.session_state.separate_sheets,
        help="If checked, each image will be saved in a separate sheet in Excel export"
    )
    
    if separate_sheets != st.session_state.separate_sheets:
        st.session_state.separate_sheets = separate_sheets
        processor.set_separate_sheets(separate_sheets)

def display_results(results: List[Dict[str, Any]], processor):
    """Display processing results with markdown support"""
    if not results:
        return
    
    # Get custom column names
    columns = processor.get_column_names()
    
    # Display each result in an expander
    for result in results:
        with st.expander(f"Results for {result['filename']}", expanded=True):
            if result.get('description'):
                st.write("**Image Description:**")
                st.write(result['description'])
            
            # Display extracted text as markdown
            st.markdown(result['extracted_text'])
    
    # Create DataFrame for export
    df = pd.DataFrame(results)
    df = df.rename(columns=columns)
    return df

def export_results(results: List[Dict[str, Any]], processor):
    """Export results to CSV/XLSX"""
    if not results:
        return
        
    # Get custom column names
    columns = processor.get_column_names()
    
    # Create DataFrame with custom column names
    df = pd.DataFrame(results)
    df = df.rename(columns=columns)
    
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
    
    if processor.separate_sheets:
        # Create Excel writer object
        with pd.ExcelWriter(excel_file) as writer:
            # Write overview sheet
            df.to_excel(writer, sheet_name='Overview', index=False)
            
            # Write individual sheets
            for _, row in df.iterrows():
                sheet_name = row[columns['filename']][:31]  # Excel sheet names limited to 31 chars
                pd.DataFrame([row]).to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        df.to_excel(excel_file, index=False)
    
    # Read the Excel file for download
    with open(excel_file, 'rb') as f:
        col2.download_button(
            label="Download Excel",
            data=f,
            file_name=excel_file,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    # Clean up the temporary Excel file
    os.remove(excel_file) 