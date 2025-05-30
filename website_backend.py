from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
import os
import requests
import json
import uuid
from datetime import datetime
import PyPDF2
import docx
import io
import logging
import threading
import time
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from functools import wraps
import hashlib

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Enhanced Configuration
class Config:
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc', 'rtf'}
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    MAX_TOKENS_DEFAULT = 500
    TEMPERATURE_DEFAULT = 0.7
    REQUEST_TIMEOUT = 30

app.config.from_object(Config)

# Create upload directory
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# Enhanced document storage with metadata
uploaded_documents = {}
document_analytics = {
    'total_uploads': 0,
    'total_queries': 0,
    'total_searches': 0,
    'upload_history': []
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def extract_text_from_file(file_content, filename):
    """Extract text from different file formats"""
    try:
        file_extension = filename.rsplit('.', 1)[1].lower()

        if file_extension == 'txt':
            return file_content.decode('utf-8')

        elif file_extension == 'pdf':
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text

        elif file_extension in ['docx', 'doc']:
            doc_file = io.BytesIO(file_content)
            doc = docx.Document(doc_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text

        else:
            return "Unsupported file format"

    except Exception as e:
        print(f"Error extracting text: {e}")
        return f"Error extracting text: {str(e)}"

def call_groq_api(messages, max_tokens=None, temperature=None):
    """Enhanced Groq API call with better error handling and logging"""
    if max_tokens is None:
        max_tokens = Config.MAX_TOKENS_DEFAULT
    if temperature is None:
        temperature = Config.TEMPERATURE_DEFAULT

    try:
        logger.info(f"Calling Groq API with {len(messages)} messages, max_tokens={max_tokens}")

        headers = {
            "Authorization": f"Bearer {Config.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama3-8b-8192",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        response = requests.post(Config.GROQ_API_URL, headers=headers, json=payload, timeout=Config.REQUEST_TIMEOUT)

        if response.status_code == 200:
            response_data = response.json()
            return response_data["choices"][0]["message"]["content"]
        else:
            print(f"Groq API error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return None

@app.route('/')
def home():
    """Serve the main website"""
    try:
        with open('enhanced_website.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>Enhanced Website Not Found</h1>
        <p>Please make sure enhanced_website.html is in the same directory as this script.</p>
        <p><a href="/simple">Try Simple Version</a></p>
        """

@app.route('/simple')
def simple_version():
    """Simple version if main file is not found"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Document Research & Theme Identification Chatbot</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            .container { max-width: 800px; margin: 0 auto; background: rgba(255,255,255,0.95); padding: 30px; border-radius: 15px; color: #333; }
            .btn { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }
            .btn:hover { background: #2980b9; }
            .upload-area { border: 2px dashed #3498db; padding: 40px; text-align: center; margin: 20px 0; border-radius: 10px; }
            .chat-area { height: 300px; overflow-y: auto; border: 1px solid #ddd; padding: 15px; margin: 20px 0; background: #f9f9f9; }
            .message { margin: 10px 0; padding: 10px; border-radius: 8px; }
            .user { background: #e3f2fd; text-align: right; }
            .ai { background: #f3e5f5; }
            input, textarea { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Document Research & Theme Identification Chatbot</h1>
            <p>Upload documents and chat with AI about their content</p>

            <div class="upload-area" onclick="document.getElementById('file-input').click()">
                <h3>📁 Upload Documents</h3>
                <p>Click here or drag files to upload (PDF, DOCX, TXT)</p>
                <input type="file" id="file-input" style="display:none;" multiple accept=".pdf,.docx,.txt">
            </div>

            <button class="btn" onclick="processFiles()">🚀 Process Documents</button>
            <button class="btn" onclick="clearAll()">🗑️ Clear All</button>

            <div id="status"></div>
            <div id="documents"></div>

            <h3>💬 Chat with AI</h3>
            <div class="chat-area" id="chat"></div>
            <input type="text" id="chat-input" placeholder="Ask about your documents..." onkeypress="if(event.key==='Enter') sendMessage()">
            <button class="btn" onclick="sendMessage()">📤 Send</button>
        </div>

        <script>
            let documents = {};

            document.getElementById('file-input').addEventListener('change', function(e) {
                Array.from(e.target.files).forEach(file => {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const id = Date.now() + Math.random();
                        documents[id] = {
                            name: file.name,
                            content: e.target.result,
                            size: file.size
                        };
                        updateDocumentList();
                    };
                    reader.readAsText(file);
                });
            });

            function updateDocumentList() {
                const div = document.getElementById('documents');
                div.innerHTML = '<h3>📚 Documents:</h3>' +
                    Object.values(documents).map(doc =>
                        `<div style="background:#f0f0f0; padding:10px; margin:5px; border-radius:5px;">
                            📄 ${doc.name} (${Math.round(doc.size/1024)}KB)
                        </div>`
                    ).join('');
            }

            function processFiles() {
                if (Object.keys(documents).length === 0) {
                    document.getElementById('status').innerHTML = '<div style="color:red;">No files uploaded</div>';
                    return;
                }
                document.getElementById('status').innerHTML = '<div style="color:green;">✅ Documents processed!</div>';
            }

            function clearAll() {
                documents = {};
                updateDocumentList();
                document.getElementById('chat').innerHTML = '';
                document.getElementById('status').innerHTML = '<div style="color:blue;">🗑️ All cleared!</div>';
            }

            async function sendMessage() {
                const input = document.getElementById('chat-input');
                const message = input.value.trim();
                if (!message) return;

                addMessage('user', message);
                input.value = '';

                if (Object.keys(documents).length === 0) {
                    addMessage('ai', 'Please upload some documents first!');
                    return;
                }

                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            message: message,
                            documents: Object.values(documents)
                        })
                    });

                    const data = await response.json();
                    addMessage('ai', data.response || 'Sorry, I encountered an error.');
                } catch (error) {
                    addMessage('ai', 'Error: Could not connect to AI service.');
                }
            }

            function addMessage(type, content) {
                const chat = document.getElementById('chat');
                const div = document.createElement('div');
                div.className = 'message ' + type;
                div.innerHTML = '<strong>' + (type === 'user' ? '👤 You:' : '🤖 AI:') + '</strong> ' + content;
                chat.appendChild(div);
                chat.scrollTop = chat.scrollHeight;
            }

            // Initial message
            addMessage('ai', 'Hello! Upload some documents and I\'ll help you analyze them.');
        </script>
    </body>
    </html>
    """

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Enhanced file upload with better processing and analytics"""
    try:
        logger.info("File upload request received")

        if 'file' not in request.files:
            logger.warning("No file provided in upload request")
            return jsonify({"success": False, "error": "No file provided"}), 400

        file = request.files['file']
        if file.filename == '':
            logger.warning("Empty filename in upload request")
            return jsonify({"success": False, "error": "No file selected"}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            doc_id = str(uuid.uuid4())

            logger.info(f"Processing file: {filename} (ID: {doc_id})")

            # Read file content
            file_content = file.read()
            file_size = len(file_content)

            # Check file size
            if file_size > Config.MAX_CONTENT_LENGTH:
                return jsonify({
                    "success": False,
                    "error": f"File too large. Maximum size: {Config.MAX_CONTENT_LENGTH // (1024*1024)}MB"
                }), 400

            # Extract text from file
            extracted_text = extract_text_from_file(file_content, filename)

            if extracted_text.startswith("Error"):
                logger.error(f"Text extraction failed for {filename}: {extracted_text}")
                return jsonify({"success": False, "error": extracted_text}), 400

            # Generate AI analysis
            logger.info(f"Generating AI analysis for {filename}")

            # Enhanced summary prompt
            summary_prompt = f"""Analyze this document and provide a comprehensive summary including:
1. Main topic and purpose
2. Key points and findings
3. Document type and structure
4. Important insights

Document content:
{extracted_text[:3000]}..."""

            messages = [{"role": "user", "content": summary_prompt}]
            summary = call_groq_api(messages, max_tokens=300)

            # Enhanced themes identification
            themes_prompt = f"""Identify and categorize the main themes in this document:
1. Primary themes (most important topics)
2. Secondary themes (supporting topics)
3. Keywords and concepts
4. Document category

Content:
{extracted_text[:2000]}..."""

            themes_messages = [{"role": "user", "content": themes_prompt}]
            themes = call_groq_api(themes_messages, max_tokens=200)

            # Generate document hash for duplicate detection
            content_hash = hashlib.md5(extracted_text.encode()).hexdigest()

            # Store document with enhanced metadata
            upload_time = datetime.now()
            uploaded_documents[doc_id] = {
                "id": doc_id,
                "filename": filename,
                "original_filename": file.filename,
                "upload_time": upload_time.isoformat(),
                "text_content": extracted_text,
                "file_size": file_size,
                "content_hash": content_hash,
                "summary": summary or "Summary generation failed",
                "themes": themes or "Theme identification failed",
                "text_length": len(extracted_text),
                "word_count": len(extracted_text.split()),
                "file_type": filename.rsplit('.', 1)[1].lower() if '.' in filename else 'unknown',
                "processing_status": "completed"
            }

            # Update analytics
            document_analytics['total_uploads'] += 1
            document_analytics['upload_history'].append({
                'filename': filename,
                'upload_time': upload_time.isoformat(),
                'file_size': file_size,
                'doc_id': doc_id
            })

            logger.info(f"Successfully processed {filename} - {len(extracted_text)} characters")

            return jsonify({
                "success": True,
                "document_id": doc_id,
                "filename": filename,
                "summary": summary,
                "themes": themes,
                "text_length": len(extracted_text),
                "word_count": len(extracted_text.split()),
                "file_size": file_size,
                "file_type": filename.rsplit('.', 1)[1].lower() if '.' in filename else 'unknown',
                "message": "Document uploaded and processed successfully"
            })

        else:
            supported_formats = ', '.join(Config.ALLOWED_EXTENSIONS).upper()
            error_msg = f"Invalid file type. Supported formats: {supported_formats}"
            logger.warning(f"Invalid file type for {file.filename}")
            return jsonify({
                "success": False,
                "error": error_msg
            }), 400

    except Exception as e:
        logger.error(f"Error in upload_file: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        message = data.get('message', '')
        documents = data.get('documents', [])

        if not message:
            return jsonify({"success": False, "error": "No message provided"}), 400

        if not documents and not uploaded_documents:
            return jsonify({
                "success": True,
                "response": "Please upload some documents first so I can help you analyze them!"
            })

        # Use uploaded documents if available, otherwise use provided documents
        if uploaded_documents:
            all_content = ""
            for doc_id, doc_info in uploaded_documents.items():
                all_content += f"\nDocument: {doc_info['filename']}\nContent: {doc_info['text_content'][:2000]}...\n"
        else:
            all_content = ""
            for doc in documents:
                all_content += f"\nDocument: {doc['name']}\nContent: {doc['content'][:2000]}...\n"

        prompt = f"""You are an AI assistant helping analyze documents. Based on the following documents, answer the user's question:

{all_content[:8000]}

User Question: {message}

Please provide a helpful and detailed answer based on the document contents. If you can identify themes, patterns, or insights, please share them."""

        messages = [{"role": "user", "content": prompt}]
        response = call_groq_api(messages, max_tokens=500)

        if response:
            return jsonify({
                "success": True,
                "response": response
            })
        else:
            return jsonify({
                "success": True,
                "response": "I'm having trouble processing your question right now. Please try again."
            })

    except Exception as e:
        print(f"Error in chat: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search():
    """Handle search requests"""
    try:
        data = request.json
        query = data.get('query', '')

        if not query:
            return jsonify({"success": False, "error": "No query provided"}), 400

        if not uploaded_documents:
            return jsonify({
                "success": False,
                "error": "No documents available for search"
            }), 400

        # Prepare content for AI search
        all_content = ""
        doc_names = []
        for doc_id, doc_info in uploaded_documents.items():
            all_content += f"\nDocument: {doc_info['filename']}\nContent: {doc_info['text_content'][:3000]}...\n"
            doc_names.append(doc_info['filename'])

        prompt = f"""Based on the following documents, answer the user's search query:

Available Documents: {', '.join(doc_names)}

{all_content[:10000]}

Search Query: {query}

Please provide a comprehensive answer based on the document contents. Include which document(s) contain the relevant information."""

        messages = [{"role": "user", "content": prompt}]
        response = call_groq_api(messages, max_tokens=600)

        if response:
            return jsonify({
                "success": True,
                "response": response,
                "documents_searched": len(uploaded_documents)
            })
        else:
            return jsonify({
                "success": False,
                "error": "Search failed. Please try again."
            }), 500

    except Exception as e:
        print(f"Error in search: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def list_documents():
    """List all uploaded documents"""
    try:
        documents_list = []
        for doc_id, doc_info in uploaded_documents.items():
            documents_list.append({
                "id": doc_id,
                "filename": doc_info['filename'],
                "upload_time": doc_info['upload_time'],
                "summary": doc_info.get('summary', 'No summary'),
                "themes": doc_info.get('themes', 'No themes'),
                "text_length": doc_info['text_length'],
                "file_size": doc_info['file_size']
            })

        return jsonify({
            "success": True,
            "documents": documents_list,
            "total": len(documents_list)
        })

    except Exception as e:
        print(f"Error in list_documents: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_documents():
    """Clear all uploaded documents"""
    try:
        global uploaded_documents
        logger.info("Clearing all documents")
        uploaded_documents = {}

        return jsonify({
            "success": True,
            "message": "All documents cleared successfully"
        })

    except Exception as e:
        logger.error(f"Error in clear_documents: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get system analytics and statistics"""
    try:
        # Calculate additional statistics
        total_size = sum(doc['file_size'] for doc in uploaded_documents.values())
        total_words = sum(doc.get('word_count', 0) for doc in uploaded_documents.values())

        file_types = {}
        for doc in uploaded_documents.values():
            file_type = doc.get('file_type', 'unknown')
            file_types[file_type] = file_types.get(file_type, 0) + 1

        analytics_data = {
            **document_analytics,
            'current_documents': len(uploaded_documents),
            'total_file_size': total_size,
            'total_words': total_words,
            'file_types_distribution': file_types,
            'average_file_size': total_size / len(uploaded_documents) if uploaded_documents else 0,
            'average_words_per_doc': total_words / len(uploaded_documents) if uploaded_documents else 0
        }

        return jsonify({
            "success": True,
            "analytics": analytics_data
        })

    except Exception as e:
        logger.error(f"Error in get_analytics: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "documents_loaded": len(uploaded_documents),
        "groq_api_configured": bool(Config.GROQ_API_KEY)
    })

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 ENHANCED DOCUMENT RESEARCH & AI CHATBOT PLATFORM v2.0")
    print("="*80)
    print("📍 Website URL: http://localhost:5003")
    print("🔑 Groq API: ✅ Configured and Ready")
    print("📄 File Support: PDF, DOCX, TXT, RTF (Max 100MB)")
    print("🤖 AI Features: Advanced Analysis, Theme ID, Smart Search")
    print("📊 Analytics: Real-time Statistics and Monitoring")
    print("🔍 Search: Keyword + AI-Powered Semantic Search")
    print("💬 Chat: Context-Aware Document Conversations")
    print("🎨 UI: Modern Glassmorphism Design with Animations")
    print("-" * 80)
    print("🌟 NEW FEATURES:")
    print("   • Enhanced file processing with metadata")
    print("   • Advanced AI prompts for better analysis")
    print("   • Real-time analytics and monitoring")
    print("   • Improved error handling and logging")
    print("   • Beautiful modern UI with animations")
    print("   • Duplicate detection and file management")
    print("="*80)
    print("✅ ALL SYSTEMS READY! Enjoy your enhanced AI platform!")
    print("="*80 + "\n")

    logger.info("Starting enhanced Flask application")
    app.run(debug=True, host='0.0.0.0', port=5003)
