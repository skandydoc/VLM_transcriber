import time
from typing import List, Dict, Any, Optional
import google.generativeai as genai
import streamlit as st
from PIL import Image
import io
import logging
import os
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiProcessor:
    """
    Handles image processing using Google's Gemini Vision API.
    
    This class provides functionality to process images and extract text using
    Google's Gemini Vision API. It handles image validation, processing, and
    error management.
    
    Attributes:
        model: The Gemini vision model instance
        max_retries: Maximum number of retries for failed API calls
        output_columns: Custom column names for output
        separate_sheets: Whether to create separate sheets for each image in Excel
    """
    
    DEFAULT_COLUMNS = {
        'filename': 'Filename',
        'extracted_text': 'Extracted Text',
        'description': 'Image Description'
    }
    
    def __init__(self, max_retries: int = 3, custom_columns: Dict[str, str] = None, separate_sheets: bool = False):
        """
        Initialize the Gemini processor.
        
        Args:
            max_retries (int): Maximum number of retries for failed API calls
            custom_columns (Dict[str, str]): Custom column names for output
            separate_sheets (bool): Whether to create separate sheets for each image in Excel
            
        Raises:
            ValueError: If GOOGLE_API_KEY environment variable is not found
            Exception: If there's an error initializing the Gemini client
        """
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key or api_key == "your_api_key_here":
                raise ValueError("Valid GOOGLE_API_KEY environment variable not found")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.max_retries = max_retries
            self.output_columns = {**self.DEFAULT_COLUMNS, **(custom_columns or {})}
            self.separate_sheets = separate_sheets
            logger.info("Successfully initialized Gemini processor")
            
        except Exception as e:
            logger.error(f"Error initializing Gemini processor: {str(e)}")
            raise
    
    def get_column_names(self) -> Dict[str, str]:
        """Get the current column names mapping"""
        return self.output_columns
    
    def set_column_names(self, custom_columns: Dict[str, str]) -> None:
        """Update column names mapping"""
        self.output_columns = {**self.DEFAULT_COLUMNS, **custom_columns}
    
    def set_separate_sheets(self, separate_sheets: bool) -> None:
        """Update separate sheets setting"""
        self.separate_sheets = separate_sheets
    
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
    
    def _format_medical_data(self, text: str) -> str:
        """
        Format medical form data into a structured table format.
        
        Args:
            text (str): Raw extracted text
            
        Returns:
            str: Formatted text in markdown table format
        """
        try:
            # Split text into lines and clean up
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            # Initialize structured data
            structured_data = {
                'Patient Information': {
                    'fields': ['Name', 'Age', 'Sex', 'ID'],
                    'data': {}
                },
                'Contact Details': {
                    'fields': ['Address', 'Mobile', 'Phone'],
                    'data': {}
                },
                'Medical Records': {
                    'fields': ['Test ID', 'Lab ID', 'Record Number', 'Vehicle Registration'],
                    'data': {}
                }
            }
            
            # Process each line
            for line in lines:
                # Convert to lowercase for matching but keep original for display
                line_lower = line.lower()
                
                # Try to split into field and value
                if ':' in line:
                    field, value = line.split(':', 1)
                else:
                    # Try to identify field and value based on common patterns
                    for pattern in ['name', 'age', 'sex', 'address', 'mobile', 'phone', 'id']:
                        if pattern in line_lower:
                            parts = line_lower.split(pattern)
                            if len(parts) == 2:
                                field = pattern.title()
                                value = parts[1]
                                break
                    else:
                        continue
                
                field = field.strip()
                value = value.strip()
                
                # Categorize the field
                field_lower = field.lower()
                if any(f.lower() in field_lower for f in structured_data['Patient Information']['fields']):
                    structured_data['Patient Information']['data'][field] = value
                elif any(f.lower() in field_lower for f in structured_data['Contact Details']['fields']):
                    structured_data['Contact Details']['data'][field] = value
                elif any(f.lower() in field_lower for f in structured_data['Medical Records']['fields']):
                    structured_data['Medical Records']['data'][field] = value
            
            # Format as markdown tables
            formatted_text = ""
            
            for category, info in structured_data.items():
                if info['data']:
                    formatted_text += f"\n### {category}\n\n"
                    formatted_text += "| Field | Value |\n"
                    formatted_text += "|-------|--------|\n"
                    
                    # Sort fields based on the predefined order
                    sorted_fields = sorted(
                        info['data'].keys(),
                        key=lambda x: next(
                            (i for i, f in enumerate(info['fields']) if f.lower() in x.lower()),
                            len(info['fields'])
                        )
                    )
                    
                    for field in sorted_fields:
                        value = info['data'][field]
                        formatted_text += f"| {field} | {value} |\n"
                    
                    formatted_text += "\n"
            
            # Add any unmatched data in a separate table
            unmatched = [line for line in lines if ':' in line and 
                        not any(field.lower() in line.lower() 
                               for info in structured_data.values() 
                               for field in info['fields'])]
            
            if unmatched:
                formatted_text += "\n### Additional Information\n\n"
                formatted_text += "| Field | Value |\n"
                formatted_text += "|-------|--------|\n"
                for line in unmatched:
                    field, value = line.split(':', 1)
                    formatted_text += f"| {field.strip()} | {value.strip()} |\n"
            
            return formatted_text if formatted_text.strip() else text
            
        except Exception as e:
            logger.warning(f"Error in formatting medical data: {str(e)}")
            return text
    
    def _process_single_image(self, image_file, description: str = "") -> Dict[str, Any]:
        """
        Process a single image and extract text.
        
        Args:
            image_file: The image file to process
            description (str): Optional description of the image to guide processing
            
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
                
                # Prepare prompt for medical form processing
                prompt = f"""
                Extract and structure information from this medical form image.
                
                Image Context: {description if description else 'Medical form containing patient information'}
                
                Please extract:
                1. Patient details (Name, Age, Sex)
                2. Contact information (Address, Mobile number)
                3. Medical record numbers or IDs
                4. Test results or medical observations
                
                Format the information clearly, preserving relationships between fields and values.
                Maintain the original structure of the form.
                If there are tables, preserve the tabular format.
                """
                
                # Process with Gemini
                response = self.model.generate_content([prompt, image])
                
                if not response or not response.text:
                    raise ValueError("No text extracted from the image")
                
                # Format the extracted text
                formatted_text = self._format_medical_data(response.text)
                
                return {
                    'filename': image_file.name,
                    'extracted_text': formatted_text,
                    'description': description
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
            'extracted_text': f"Error: {error_message}",
            'description': None
        }
    
    def process_images(self, image_files: List[Any], descriptions: Dict[str, str] = None) -> List[Dict[str, Any]]:
        """
        Process multiple images and return results.
        
        Args:
            image_files (List[Any]): List of image files to process
            descriptions (Dict[str, str]): Optional mapping of filenames to descriptions
            
        Returns:
            List[Dict[str, Any]]: List of processing results for each image
        """
        if not image_files:
            logger.warning("No image files provided for processing")
            return []
            
        results = []
        total_files = len(image_files)
        descriptions = descriptions or {}
        
        # Create progress container
        progress_container = st.empty()
        status_container = st.empty()
        
        for idx, image_file in enumerate(image_files, 1):
            try:
                # Update progress bar and status
                progress = idx / total_files
                progress_container.progress(progress)
                status_container.text(f"Processing image {idx} of {total_files}: {image_file.name}")
                
                # Get description for this image
                description = descriptions.get(image_file.name, "")
                
                result = self._process_single_image(image_file, description)
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error processing image {idx}: {str(e)}")
                results.append(self._create_error_response(
                    getattr(image_file, 'name', f'image_{idx}'),
                    f"Unexpected error: {str(e)}"
                ))
        
        # Clear progress indicators
        progress_container.empty()
        status_container.empty()
            
        return results 