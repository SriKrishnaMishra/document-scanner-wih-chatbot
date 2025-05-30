# Document Research & Theme Identification Chatbot UI

This project provides a modern, responsive web UI for the Document Research & Theme Identification Chatbot.

## Features

- **Document Upload**: Upload PDF, DOCX, or TXT files for analysis
- **Theme Extraction**: Identify key themes in your documents
- **Interactive Chat**: Ask questions about your documents and get AI-generated answers
- **Visualizations**: View word frequency charts and theme networks
- **Document Summary**: Get concise summaries of your documents
- **Responsive Design**: Works on desktop and mobile devices

## Project Structure

```
├── app.py                 # Original Streamlit application
├── web_app.py             # Flask server for the web UI
├── templates/
│   └── index.html         # Main HTML template
├── static/
│   ├── css/
│   │   └── styles.css     # CSS styles
│   └── js/
│       └── main.js        # JavaScript functionality
└── README.md              # This file
```

## How to Run

### Option 1: Run the Web UI

1. Install Flask:
   ```
   pip install flask
   ```

2. Run the Flask server:
   ```
   python web_app.py
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

### Option 2: Run the Original Streamlit App

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

2. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:8501
   ```

## Using the Web UI

1. **Upload a Document**:
   - Click on "Upload Document" in the sidebar
   - Select a PDF, DOCX, or TXT file
   - Click "Process Document"

2. **Explore Themes**:
   - Click on the "Themes & Analysis" tab
   - View the extracted themes and document summary
   - Explore the word frequency chart and theme network

3. **Chat with Your Document**:
   - Click on the "Chat" tab
   - Type a question in the input field
   - Get AI-generated answers based on your document

4. **View Document Content**:
   - Click on the "Document Text" tab
   - Read the full content of your document

## Technical Details

The web UI is built with:
- HTML5, CSS3, and JavaScript
- Chart.js for visualizations
- Flask for serving the web application

The UI communicates with the backend through JavaScript functions that simulate the document processing and question answering functionality. In a production environment, these functions would make API calls to the backend services.

## Notes

This is a client-side implementation that simulates the document processing and AI functionality. In a production environment, you would need to:

1. Create API endpoints in the Flask server to handle document processing
2. Connect the JavaScript functions to these API endpoints
3. Implement proper error handling and security measures

The current implementation stores document data in the browser's localStorage, which has limitations on storage size and is not secure for sensitive documents.
