import os
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import PyPDF2
from docx import Document
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Store processed documents in memory (in a real app, use a database)
documents = {}

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

def process_document(file_path, filename):
    # Determine file type and extract text
    if filename.lower().endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif filename.lower().endswith(('.docx', '.doc')):
        text = extract_text_from_docx(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    
    # Basic text processing
    sentences = sent_tokenize(text)
    
    # Generate embeddings for each sentence
    embeddings = model.encode(sentences)
    
    # Simple theme extraction (first few sentences as summary)
    summary = " ".join(sentences[:3])
    
    # Simple keyword extraction (top 10 most common non-stopwords)
    words = [word.lower() for sent in sentences for word in word_tokenize(sent) if word.isalnum()]
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Get top 10 most common words as keywords
    keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        'id': str(uuid.uuid4()),
        'filename': filename,
        'text': text,
        'summary': summary,
        'keywords': [word[0] for word in keywords],
        'sentences': sentences,
        'embeddings': embeddings.tolist()
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the document
        try:
            doc_data = process_document(filepath, filename)
            documents[doc_data['id']] = doc_data
            
            # Return document metadata (not the full text)
            return jsonify({
                'id': doc_data['id'],
                'filename': doc_data['filename'],
                'summary': doc_data['summary'],
                'keywords': doc_data['keywords']
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def list_documents():
    # Return list of document metadata
    docs = []
    for doc_id, doc in documents.items():
        docs.append({
            'id': doc_id,
            'filename': doc['filename'],
            'summary': doc['summary'],
            'keywords': doc['keywords']
        })
    return jsonify(docs)

@app.route('/api/documents/<doc_id>', methods=['GET'])
def get_document(doc_id):
    if doc_id not in documents:
        return jsonify({'error': 'Document not found'}), 404
    
    # Return full document data
    return jsonify(documents[doc_id])

@app.route('/api/search', methods=['POST'])
def search_documents():
    query = request.json.get('query', '')
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    # Encode the query
    query_embedding = model.encode([query])[0]
    
    # Search through all documents
    results = []
    for doc_id, doc in documents.items():
        # Calculate similarity between query and each sentence
        similarities = cosine_similarity(
            [query_embedding],
            doc['embeddings']
        )[0]
        
        # Get top 3 most similar sentences
        top_indices = np.argsort(similarities)[-3:][::-1]
        relevant_sentences = [doc['sentences'][i] for i in top_indices]
        
        results.append({
            'id': doc_id,
            'filename': doc['filename'],
            'sentences': relevant_sentences,
            'max_similarity': float(np.max(similarities))
        })
    
    # Sort by relevance
    results.sort(key=lambda x: x['max_similarity'], reverse=True)
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
