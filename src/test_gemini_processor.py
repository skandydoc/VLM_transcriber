import unittest
from unittest.mock import Mock, patch
import io
from PIL import Image
import os
from gemini_processor import GeminiProcessor

class TestGeminiProcessor(unittest.TestCase):
    """Test cases for GeminiProcessor class"""
    
    @patch('google.generativeai.GenerativeModel')
    def setUp(self, mock_model):
        """Set up test environment"""
        # Mock environment variable
        os.environ['GOOGLE_API_KEY'] = 'test_api_key'
        
        # Mock Gemini model
        self.mock_model = mock_model
        self.mock_model_instance = Mock()
        mock_model.return_value = self.mock_model_instance
        
        with patch('google.generativeai.configure'):
            self.processor = GeminiProcessor()
    
    def test_validate_image_no_file(self):
        """Test image validation with no file"""
        result = self.processor._validate_image(None)
        self.assertEqual(result, "No image file provided")
    
    def test_validate_image_size_limit(self):
        """Test image validation with file exceeding size limit"""
        mock_file = Mock()
        mock_file.size = 21 * 1024 * 1024  # 21MB
        mock_file.name = "test.jpg"
        
        result = self.processor._validate_image(mock_file)
        self.assertTrue("exceeds 20MB size limit" in result)
    
    def test_post_process_text(self):
        """Test text post-processing"""
        test_text = "This is a test.   With extra spaces.And no space here."
        expected = "This is a test.\nWith extra spaces.\nAnd no space here"
        
        result = self.processor._post_process_text(test_text)
        self.assertEqual(result, expected)
    
    def test_create_error_response(self):
        """Test error response creation"""
        filename = "test.jpg"
        error_msg = "Test error"
        
        result = self.processor._create_error_response(filename, error_msg)
        
        self.assertEqual(result['filename'], filename)
        self.assertEqual(result['error'], error_msg)
        self.assertIsNone(result['extracted_text'])
        self.assertIsNone(result['confidence_score'])
        self.assertEqual(result['status'], 'error')
    
    def test_process_single_image_success(self):
        """Test successful image processing"""
        # Create a small test image
        img = Image.new('RGB', (100, 100), color='white')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        # Mock file object
        mock_file = Mock()
        mock_file.name = "test.jpg"
        mock_file.size = len(img_byte_arr.getvalue())
        mock_file.getvalue = lambda: img_byte_arr.getvalue()
        
        # Mock Gemini response
        mock_response = Mock()
        mock_response.text = "Test extracted text"
        self.mock_model_instance.generate_content.return_value = mock_response
        
        result = self.processor._process_single_image(mock_file)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['filename'], "test.jpg")
        self.assertIsNotNone(result['extracted_text'])
        self.assertIsNotNone(result['processing_time'])
    
    def test_process_images_empty_list(self):
        """Test processing with empty image list"""
        result = self.processor.process_images([])
        self.assertEqual(result, [])
    
    def test_custom_column_names(self):
        """Test custom column name functionality"""
        custom_columns = {
            'filename': 'File Name',
            'extracted_text': 'OCR Text'
        }
        
        # Test setting custom columns
        self.processor.set_column_names(custom_columns)
        current_columns = self.processor.get_column_names()
        
        self.assertEqual(current_columns['filename'], 'File Name')
        self.assertEqual(current_columns['extracted_text'], 'OCR Text')
        
        # Test that non-customized columns retain default names
        self.assertEqual(current_columns['status'], 'Status')
    
    def test_separate_sheets_setting(self):
        """Test separate sheets setting"""
        # Test default value
        self.assertFalse(self.processor.separate_sheets)
        
        # Test setting to True
        self.processor.set_separate_sheets(True)
        self.assertTrue(self.processor.separate_sheets)
        
        # Test setting back to False
        self.processor.set_separate_sheets(False)
        self.assertFalse(self.processor.separate_sheets)
    
    def test_initialization_with_custom_settings(self):
        """Test initialization with custom settings"""
        custom_columns = {'filename': 'Custom File Name'}
        
        with patch('google.generativeai.configure'):
            processor = GeminiProcessor(
                max_retries=5,
                custom_columns=custom_columns,
                separate_sheets=True
            )
        
        self.assertEqual(processor.max_retries, 5)
        self.assertEqual(processor.output_columns['filename'], 'Custom File Name')
        self.assertTrue(processor.separate_sheets)

if __name__ == '__main__':
    unittest.main() 