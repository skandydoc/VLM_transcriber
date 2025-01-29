import streamlit as st
from config import AppConfig
from gemini_processor import GeminiProcessor
from utils import (
    setup_page,
    handle_file_upload,
    display_results,
    export_results,
    initialize_session_state,
    handle_column_customization
)
import logging
import os

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main application function"""
    try:
        # Initialize configuration and session state
        config = AppConfig()
        initialize_session_state()
        
        # Setup page configuration
        setup_page()
        
        # Initialize Gemini processor
        processor = GeminiProcessor()
        
        # Handle column customization in sidebar
        handle_column_customization(processor)
        
        # File uploader section with common description
        uploaded_files, common_description, should_process = handle_file_upload()
        
        if uploaded_files and should_process:
            # Process images with common description
            with st.spinner('Processing images...'):
                # Create descriptions dictionary with common description
                descriptions = {file.name: common_description for file in uploaded_files}
                results = processor.process_images(uploaded_files, descriptions)
                
            # Display and export results
            if results:
                df = display_results(results, processor)
                export_results(results, processor)
                
                # Show success message
                st.success(f"Successfully processed {len(results)} image(s)")
                
        # Add clear button
        if st.button('Clear All'):
            st.session_state.clear()
            st.experimental_rerun()
            
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error(f"An error occurred: {str(e)}")
        st.error("Please check the logs for more details")

if __name__ == "__main__":
    main() 