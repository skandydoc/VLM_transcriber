# VLM Transcriber

A Streamlit application that uses Google's Gemini Vision API to extract text from images.

Composed with Cursor - Use with Discretion. AI hallucinations and potential errors are possible.

## Features

- Upload multiple images (JPG, JPEG, PNG, WEBP)
- Extract text using Google's Gemini Vision API
- Display results in a table format
- Export results to CSV or Excel
- Progress tracking for batch processing
- Error handling and retry mechanism
- Image validation (size and format)

## Requirements

- Python 3.8+
- Google API Key with access to Gemini Vision API
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd VLM_transcriber
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory and add your Google API key:
```bash
GOOGLE_API_KEY=your_api_key_here
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run src/app.py
```

2. Open your browser and navigate to the provided URL (usually http://localhost:8501)

3. Upload your images using the file uploader

4. View the extracted text and other details in the results table

5. Download results in CSV or Excel format if needed

## Configuration

- Maximum file size: 20MB
- Supported image formats: JPG, JPEG, PNG, WEBP
- Maximum batch size: 100 images
- API retries: 3 attempts with 1-second delay between retries

## Project Structure

```
VLM_transcriber/
├── src/
│   ├── app.py              # Main Streamlit application
│   ├── config.py           # Configuration settings
│   ├── gemini_processor.py # Gemini Vision API handler
│   └── utils.py           # Utility functions
├── logs/                   # Application logs
├── .env                    # Environment variables
├── .gitignore             # Git ignore rules
├── README.md              # Project documentation
└── requirements.txt       # Python dependencies
```

## Error Handling

The application includes comprehensive error handling for:
- Invalid API keys
- Unsupported file formats
- File size limits
- API rate limits and timeouts
- Network issues
- Image processing errors

## License

This project is licensed under CC BY-SA NC 4.0 (Creative Commons Attribution-ShareAlike Non-commercial 4.0 International licence).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.