# YouTube Video Summarizer + Notes

A Streamlit-based web application that extracts transcripts from YouTube videos, generates AI-powered summaries and detailed study notes, and allows downloading the notes as a PDF.

## Features

- **Transcript Extraction**: Automatically fetches transcripts from YouTube videos with support for Hindi and English languages.
- **AI-Powered Summarization**: Uses Google's Gemini AI to create concise summaries of video content.
- **Study Notes Generation**: Transforms transcripts into structured, educational study notes optimized for learning and revision.
- **PDF Export**: Downloads generated study notes as a PDF file for offline use.
- **User-Friendly Interface**: Simple Streamlit UI for easy interaction.

## Requirements

- Python 3.8 or higher
- Google API Key for Gemini AI (set in `.env` file)
- Internet connection for YouTube transcript fetching and AI processing

## Installation

1. Clone or download this repository.

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   - Create a `.env` file in the project root.
   - Add your Google API Key:
     ```
     GOOGLE_API_KEY=your_google_api_key_here
     ```

4. Ensure you have the DejaVuSans.ttf font file in the project directory for PDF generation (included in the repository).

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open the provided URL in your browser.

3. Enter a YouTube video URL in the text input field.

4. Click "Process Video" to start the analysis.

5. Use the buttons to view the transcript, summary, or study notes.

6. Download the study notes as a PDF using the download button.

## How It Works

The application uses a LangGraph workflow to process YouTube videos:

1. **Transcript Extraction**: Extracts the video transcript using the YouTubeTranscriptApi, with fallback from Hindi to English.

2. **Summarization**: Sends the transcript to Google's Gemini AI for generating a detailed summary.

3. **Notes Generation**: Creates structured study notes with key takeaways, detailed content, definitions, and potential exam questions.

4. **PDF Creation**: Formats the notes into a PDF using FPDF2 with Unicode support.

## Environment Setup

- **Virtual Environment**: It's recommended to use a virtual environment to avoid dependency conflicts.
  ```
  python -m venv myenv
  myenv\Scripts\activate  # On Windows
  pip install -r requirements.txt
  ```

- **API Key**: Obtain a Google API Key from the Google Cloud Console and enable the Gemini API.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
