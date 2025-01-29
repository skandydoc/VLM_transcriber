import streamlit as st
from config import AppConfig
from gemini_processor import GeminiProcessor
from utils import (
    setup_page,
    handle_file_upload,
    display_results,
    export_results,
    initialize_session_state
)
import logging

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
        
        # File uploader section
        uploaded_files = handle_file_upload()
        
        if uploaded_files:
            # Process images
            with st.spinner('Processing images...'):
                results = processor.process_images(uploaded_files)
                
            # Display and export results
            if results:
                display_results(results)
                export_results(results)
                
        # Add clear button
        if st.button('Clear All'):
            st.session_state.clear()
            st.experimental_rerun()
            
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 