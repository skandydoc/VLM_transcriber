import time
from typing import List, Dict, Any, Optional
import google.generativeai as genai
import streamlit as st
from PIL import Image
import io
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class GeminiProcessor:
    """
    Handles image processing using Google's Gemini Vision API.
    
    This class provides functionality to process images and extract text using
    Google's Gemini Vision API. It handles image validation, processing, and
    error management.
    
    Attributes:
        client: The Gemini API client instance
        model: The name of the Gemini model to use
        max_retries: Maximum number of retries for failed API calls
    """
    
    def __init__(self, max_retries: int = 3):
        """
        Initialize the Gemini processor.
        
        Args:
            max_retries (int): Maximum number of retries for failed API calls
            
        Raises:
            ValueError: If GOOGLE_API_KEY environment variable is not found
            Exception: If there's an error initializing the Gemini client
        """
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key or api_key == "your_api_key_here":
                raise ValueError("Valid GOOGLE_API_KEY environment variable not found")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro-vision')
            self.max_retries = max_retries
            logger.info("Successfully initialized Gemini processor")
            
        except Exception as e:
            logger.error(f"Error initializing Gemini processor: {str(e)}")
            raise
    
    def _validate_image(self, image_file) -> Optional[str]:
        """
        Validate the image file before processing.
        
        Args:
            image_file: The uploaded image file
            
        Returns:
            Optional[str]: Error message if validation fails, None if successful
        """
        try:
            if not image_file:
                return "No image file provided"
                
            # Check file size (20MB limit)
            if image_file.size > 20 * 1024 * 1024:
                return f"File {image_file.name} exceeds 20MB size limit"
                
            # Validate image format
            image = Image.open(io.BytesIO(image_file.getvalue()))
            if image.format.lower() not in ['jpeg', 'jpg', 'png', 'webp']:
                return f"Unsupported image format: {image.format}"
                
            return None
            
        except Exception as e:
            return f"Error validating image: {str(e)}"
    
    def _process_single_image(self, image_file) -> Dict[str, Any]:
        """
        Process a single image and extract text.
        
        Args:
            image_file: The image file to process
            
        Returns:
            Dict[str, Any]: Processing results including extracted text and metadata
        """
        validation_error = self._validate_image(image_file)
        if validation_error:
            return self._create_error_response(image_file.name, validation_error)
            
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                
                # Read image file
                image_bytes = image_file.getvalue()
                image = Image.open(io.BytesIO(image_bytes))
                
                # Prepare prompt
                prompt = """
                Extract all text from this image. Format the output as plain text.
                Focus on accuracy and maintain the original formatting where possible.
                If there are any tables, preserve the tabular structure.
                """
                
                # Process with Gemini
                response = self.model.generate_content([prompt, image])
                
                processing_time = time.time() - start_time
                
                return {
                    'filename': image_file.name,
                    'extracted_text': response.text,
                    'confidence_score': 1.0,  # Placeholder as Gemini doesn't provide confidence scores
                    'status': 'success',
                    'error': None,
                    'processing_time': round(processing_time, 2)
                }
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed for {image_file.name}: {str(e)}")
                if attempt == self.max_retries - 1:
                    return self._create_error_response(image_file.name, str(e))
                time.sleep(1)  # Wait before retrying
    
    def _create_error_response(self, filename: str, error_message: str) -> Dict[str, Any]:
        """
        Create a standardized error response.
        
        Args:
            filename (str): Name of the processed file
            error_message (str): Error message to include
            
        Returns:
            Dict[str, Any]: Standardized error response
        """
        return {
            'filename': filename,
            'extracted_text': None,
            'confidence_score': None,
            'status': 'error',
            'error': error_message,
            'processing_time': None
        }
    
    def process_images(self, image_files: List[Any]) -> List[Dict[str, Any]]:
        """
        Process multiple images and return results.
        
        Args:
            image_files (List[Any]): List of image files to process
            
        Returns:
            List[Dict[str, Any]]: List of processing results for each image
        """
        if not image_files:
            logger.warning("No image files provided for processing")
            return []
            
        results = []
        total_files = len(image_files)
        
        for idx, image_file in enumerate(image_files, 1):
            # Update progress bar
            progress = idx / total_files
            st.progress(progress, text=f"Processing image {idx} of {total_files}")
            
            result = self._process_single_image(image_file)
            results.append(result)
            
        return results 