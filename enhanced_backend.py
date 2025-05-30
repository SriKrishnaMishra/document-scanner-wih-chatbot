from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import random
import requests
import os
import tempfile
import uuid
from datetime import datetime
import traceback
from werkzeug.utils import secure_filename
import PyPDF2
import docx
import io
import base64

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc'}

# Create upload directory
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# API Configuration
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Store uploaded documents
uploaded_documents = {}

# Sales scenarios
scenarios = [
    {
        "id": 1,
        "title": "Enterprise Software Sale",
        "description": "You are selling enterprise software to a large corporation. The prospect is concerned about implementation time and ROI.",
        "difficulty": "Medium",
        "customer_profile": {
            "name": "John Smith",
            "position": "CTO",
            "company": "TechCorp Inc.",
            "pain_points": ["Long implementation times", "Uncertain ROI", "Integration with existing systems"],
            "budget": "High",
            "decision_timeline": "3 months"
        }
    },
    {
        "id": 2,
        "title": "SaaS Solution for Small Business",
        "description": "You are selling a SaaS solution to a small business owner who is price-sensitive but needs to improve efficiency.",
        "difficulty": "Easy",
        "customer_profile": {
            "name": "Sarah Johnson",
            "position": "Owner",
            "company": "Johnson Consulting",
            "pain_points": ["Limited budget", "Manual processes taking too much time", "Lack of technical expertise"],
            "budget": "Low",
            "decision_timeline": "1 month"
        }
    },
    {
        "id": 3,
        "title": "Healthcare Software Solution",
        "description": "You are selling specialized healthcare software to a hospital network.",
        "difficulty": "Hard",
        "customer_profile": {
            "name": "Dr. Emily Rodriguez",
            "position": "Chief Medical Officer",
            "company": "Metropolitan Healthcare Network",
            "pain_points": ["Compliance with regulations", "Integration with existing EMR systems", "Staff training"],
            "budget": "High",
            "decision_timeline": "6 months"
        }
    }
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

def call_groq_api(messages, max_tokens=500):
    """Enhanced Groq API call with better error handling"""
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama3-8b-8192",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        
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
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Enhanced AI Sales Coach & Document Research Platform</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; margin-bottom: 40px; }
            .header h1 { font-size: 3em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
            .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 40px; }
            .feature-card { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); transition: transform 0.3s; }
            .feature-card:hover { transform: translateY(-5px); }
            .feature-card h3 { font-size: 1.5em; margin-bottom: 15px; }
            .api-section { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; margin-bottom: 20px; }
            .endpoint { background: rgba(0,0,0,0.2); padding: 15px; margin: 10px 0; border-radius: 8px; font-family: monospace; }
            .method { color: #4CAF50; font-weight: bold; margin-right: 10px; }
            .btn { background: linear-gradient(45deg, #FF6B6B, #4ECDC4); color: white; padding: 15px 30px; border: none; border-radius: 25px; font-size: 16px; font-weight: bold; text-decoration: none; display: inline-block; margin: 10px; transition: all 0.3s; }
            .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
            .status { color: #4CAF50; font-weight: bold; font-size: 1.2em; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Enhanced AI Sales Coach</h1>
                <h2>& Document Research Platform</h2>
                <p class="status">✅ Advanced Backend API Running Successfully!</p>
                <p>AI-powered sales training with comprehensive document analysis</p>
            </div>
            
            <div class="features">
                <div class="feature-card">
                    <h3>🎯 Advanced Sales Simulation</h3>
                    <p>Practice with AI customers across multiple scenarios and difficulty levels. Get real-time feedback and performance analytics.</p>
                </div>
                
                <div class="feature-card">
                    <h3>📄 Smart Document Processing</h3>
                    <p>Upload PDF, DOCX, and TXT files. Advanced text extraction with AI-powered analysis and summarization.</p>
                </div>
                
                <div class="feature-card">
                    <h3>🤖 Intelligent Chatbot</h3>
                    <p>Ask complex questions about your documents. Context-aware responses with citation and source tracking.</p>
                </div>
                
                <div class="feature-card">
                    <h3>📊 Performance Analytics</h3>
                    <p>Detailed AI feedback on sales conversations with specific recommendations and improvement strategies.</p>
                </div>
            </div>
            
            <div class="api-section">
                <h3>🔗 API Endpoints</h3>
                <div class="endpoint"><span class="method">GET</span> /api/scenarios - Get all sales scenarios</div>
                <div class="endpoint"><span class="method">POST</span> /api/simulate - Simulate sales conversation</div>
                <div class="endpoint"><span class="method">POST</span> /api/upload-document - Upload document files</div>
                <div class="endpoint"><span class="method">POST</span> /api/upload-text - Upload text content</div>
                <div class="endpoint"><span class="method">POST</span> /api/ask-document - Ask questions about documents</div>
                <div class="endpoint"><span class="method">GET</span> /api/documents - List uploaded documents</div>
                <div class="endpoint"><span class="method">POST</span> /api/feedback - Get AI feedback</div>
                <div class="endpoint"><span class="method">POST</span> /api/analyze-document - Analyze document themes</div>
            </div>
            
            <div style="text-align: center;">
                <a href="/demo" class="btn">🎮 Try Interactive Demo</a>
                <a href="/test" class="btn">🧪 Test Document Processing</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/api/upload-document', methods=['POST'])
def upload_document():
    """Enhanced file upload with multiple format support"""
    try:
        print("=== DOCUMENT UPLOAD ENDPOINT CALLED ===")
        
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "error": "No file selected"}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            doc_id = str(uuid.uuid4())
            
            # Read file content
            file_content = file.read()
            file_size = len(file_content)
            
            print(f"Processing file: {filename} ({file_size} bytes)")
            
            # Extract text from file
            extracted_text = extract_text_from_file(file_content, filename)
            
            if extracted_text.startswith("Error"):
                return jsonify({"success": False, "error": extracted_text}), 400
            
            # Generate AI summary
            summary_prompt = f"Analyze this document and provide a comprehensive summary (max 300 words):\n\n{extracted_text[:3000]}..."
            messages = [{"role": "user", "content": summary_prompt}]
            summary = call_groq_api(messages, max_tokens=300)
            
            # Generate themes
            themes_prompt = f"Identify the main themes and topics in this document:\n\n{extracted_text[:2000]}..."
            themes_messages = [{"role": "user", "content": themes_prompt}]
            themes = call_groq_api(themes_messages, max_tokens=200)
            
            # Store document
            uploaded_documents[doc_id] = {
                "id": doc_id,
                "filename": filename,
                "upload_time": datetime.now().isoformat(),
                "text_content": extracted_text,
                "file_size": file_size,
                "summary": summary or "Summary generation failed",
                "themes": themes or "Theme identification failed",
                "text_length": len(extracted_text)
            }
            
            print(f"Document stored successfully. ID: {doc_id}")
            
            return jsonify({
                "success": True,
                "document_id": doc_id,
                "filename": filename,
                "summary": uploaded_documents[doc_id]["summary"],
                "themes": uploaded_documents[doc_id]["themes"],
                "text_length": len(extracted_text),
                "file_size": file_size,
                "message": "Document uploaded and processed successfully"
            })
        
        else:
            return jsonify({
                "success": False,
                "error": "Invalid file type. Supported formats: TXT, PDF, DOCX"
            }), 400
            
    except Exception as e:
        print(f"Error in upload_document: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/upload-text', methods=['POST'])
def upload_text():
    """Upload text content directly"""
    try:
        print("=== TEXT UPLOAD ENDPOINT CALLED ===")
        data = request.json
        
        text = data.get('text', '') if data else ''
        title = data.get('title', f'Document {len(uploaded_documents) + 1}') if data else f'Document {len(uploaded_documents) + 1}'
        
        if not text.strip():
            return jsonify({"success": False, "error": "No text provided"}), 400
        
        doc_id = str(uuid.uuid4())
        
        # Generate AI summary
        summary_prompt = f"Analyze this text and provide a comprehensive summary:\n\n{text[:3000]}..."
        messages = [{"role": "user", "content": summary_prompt}]
        summary = call_groq_api(messages, max_tokens=300)
        
        # Generate themes
        themes_prompt = f"Identify the main themes and topics in this text:\n\n{text[:2000]}..."
        themes_messages = [{"role": "user", "content": themes_prompt}]
        themes = call_groq_api(themes_messages, max_tokens=200)
        
        uploaded_documents[doc_id] = {
            "id": doc_id,
            "filename": title,
            "upload_time": datetime.now().isoformat(),
            "text_content": text,
            "file_size": len(text.encode('utf-8')),
            "summary": summary or "Summary generation failed",
            "themes": themes or "Theme identification failed",
            "text_length": len(text)
        }
        
        return jsonify({
            "success": True,
            "document_id": doc_id,
            "title": title,
            "summary": summary,
            "themes": themes,
            "text_length": len(text),
            "message": "Text uploaded and processed successfully"
        })
        
    except Exception as e:
        print(f"Error in upload_text: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/ask-document', methods=['POST'])
def ask_document():
    """Enhanced document Q&A with context awareness"""
    try:
        print("=== ASK DOCUMENT ENDPOINT CALLED ===")
        data = request.json
        
        document_id = data.get('document_id')
        question = data.get('question')
        
        if not document_id or not question:
            return jsonify({"success": False, "error": "Document ID and question required"}), 400
        
        if document_id not in uploaded_documents:
            return jsonify({"success": False, "error": "Document not found"}), 404
        
        document = uploaded_documents[document_id]
        
        # Enhanced prompt with context
        prompt = f"""You are an AI assistant analyzing a document. Answer the user's question based on the document content.

Document: {document['filename']}
Summary: {document.get('summary', 'No summary available')}
Themes: {document.get('themes', 'No themes identified')}

Full Content: {document['text_content'][:4000]}...

Question: {question}

Please provide a detailed, accurate answer based on the document. If the information is not in the document, clearly state that."""
        
        messages = [{"role": "user", "content": prompt}]
        answer = call_groq_api(messages, max_tokens=500)
        
        if answer:
            return jsonify({
                "success": True,
                "answer": answer,
                "document_filename": document['filename'],
                "question": question,
                "source": "groq_ai"
            })
        else:
            fallback_answer = f"I'm having trouble processing your question about '{document['filename']}'. Please try rephrasing your question or try again later."
            return jsonify({
                "success": True,
                "answer": fallback_answer,
                "document_filename": document['filename'],
                "source": "fallback"
            })
            
    except Exception as e:
        print(f"Error in ask_document: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/analyze-document', methods=['POST'])
def analyze_document():
    """Comprehensive document analysis"""
    try:
        data = request.json
        document_id = data.get('document_id')
        
        if not document_id:
            return jsonify({"success": False, "error": "Document ID required"}), 400
        
        if document_id not in uploaded_documents:
            return jsonify({"success": False, "error": "Document not found"}), 404
        
        document = uploaded_documents[document_id]
        
        # Comprehensive analysis prompt
        analysis_prompt = f"""Perform a comprehensive analysis of this document:

Document: {document['filename']}
Content: {document['text_content'][:3000]}...

Please provide:
1. Main themes and topics
2. Key insights and findings
3. Important entities (people, organizations, locations)
4. Sentiment analysis
5. Document structure and organization
6. Potential applications or use cases

Format your response in a structured way."""
        
        messages = [{"role": "user", "content": analysis_prompt}]
        analysis = call_groq_api(messages, max_tokens=800)
        
        if analysis:
            return jsonify({
                "success": True,
                "analysis": analysis,
                "document_filename": document['filename'],
                "source": "groq_ai"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Analysis generation failed"
            }), 500
            
    except Exception as e:
        print(f"Error in analyze_document: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def list_documents():
    """Enhanced document listing with metadata"""
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
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/scenarios', methods=['GET'])
def get_scenarios():
    return jsonify({
        "success": True,
        "scenarios": scenarios,
        "total": len(scenarios)
    })

@app.route('/api/simulate', methods=['POST'])
def simulate_conversation():
    """Enhanced sales simulation"""
    try:
        data = request.json
        scenario_id = data.get('scenario_id', 1)
        user_message = data.get('message', '')
        conversation_history = data.get('conversation_history', [])
        
        scenario = next((s for s in scenarios if s["id"] == scenario_id), scenarios[0])
        
        # Enhanced system prompt
        system_prompt = f"""You are an AI simulating a realistic customer in a sales scenario.

SCENARIO: {scenario['description']}

CHARACTER PROFILE:
- Name: {scenario['customer_profile']['name']}
- Position: {scenario['customer_profile']['position']}
- Company: {scenario['customer_profile']['company']}
- Pain Points: {', '.join(scenario['customer_profile']['pain_points'])}
- Budget Level: {scenario['customer_profile']['budget']}
- Decision Timeline: {scenario['customer_profile']['decision_timeline']}

INSTRUCTIONS:
- Stay in character as this specific customer
- Be realistic and professional
- Show appropriate skepticism and ask relevant questions
- Reference your specific pain points and constraints
- Keep responses under 100 words
- Vary your responses to avoid repetition"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for entry in conversation_history:
            role = "user" if entry["speaker"] == "salesperson" else "assistant"
            messages.append({"role": role, "content": entry["message"]})
        
        messages.append({"role": "user", "content": user_message})
        
        ai_response = call_groq_api(messages, max_tokens=150)
        
        if ai_response:
            return jsonify({
                "success": True,
                "response": ai_response,
                "customer_name": scenario['customer_profile']['name'],
                "source": "groq_ai"
            })
        else:
            fallback_responses = [
                "That's interesting. Can you tell me more about how your solution addresses our specific challenges?",
                "I'm concerned about the implementation timeline. How long does this typically take?",
                "What kind of ROI can we expect, and do you have case studies from similar companies?",
                "How does your pricing compare to other solutions we're evaluating?",
                "What kind of support and training do you provide during implementation?"
            ]
            return jsonify({
                "success": True,
                "response": random.choice(fallback_responses),
                "customer_name": scenario['customer_profile']['name'],
                "source": "fallback"
            })
            
    except Exception as e:
        print(f"Error in simulate_conversation: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/feedback', methods=['POST'])
def get_feedback():
    """Enhanced feedback with detailed analysis"""
    try:
        data = request.json
        scenario_id = data.get('scenario_id')
        conversation = data.get('conversation', [])
        
        if not conversation:
            return jsonify({"success": False, "error": "No conversation provided"}), 400
        
        scenario = next((s for s in scenarios if s["id"] == scenario_id), scenarios[0]) if scenario_id else None
        
        conversation_text = ""
        for entry in conversation:
            speaker = "Salesperson" if entry["speaker"] == "salesperson" else "Customer"
            conversation_text += f"{speaker}: {entry['message']}\n"
        
        # Enhanced feedback prompt
        feedback_prompt = f"""As an expert sales coach, analyze this sales conversation and provide comprehensive feedback.

SCENARIO CONTEXT: {scenario['description'] if scenario else 'General sales conversation'}
CUSTOMER PROFILE: {scenario['customer_profile']['name'] if scenario else 'Unknown'} - {scenario['customer_profile']['position'] if scenario else 'Unknown position'}

CONVERSATION:
{conversation_text}

Please provide detailed feedback including:

1. OVERALL PERFORMANCE SCORE (1-10 with explanation)
2. KEY STRENGTHS (3-4 specific points)
3. AREAS FOR IMPROVEMENT (3-4 specific points)
4. SPECIFIC RECOMMENDATIONS (actionable advice)
5. NEXT STEPS (what to do in follow-up)

Format your response clearly with headers and bullet points."""
        
        messages = [{"role": "user", "content": feedback_prompt}]
        feedback = call_groq_api(messages, max_tokens=700)
        
        if feedback:
            return jsonify({
                "success": True,
                "feedback": feedback,
                "source": "groq_ai"
            })
        else:
            fallback_feedback = """# Sales Performance Feedback

## Overall Score: 7/10
Good effort with room for improvement.

## Strengths:
- Professional communication style
- Good product knowledge demonstration
- Appropriate questioning techniques

## Areas for Improvement:
- Address customer objections more directly
- Provide more specific examples and case studies
- Better discovery of customer needs

## Recommendations:
- Use more open-ended questions to understand pain points
- Prepare relevant case studies for similar customers
- Practice objection handling techniques"""
            
            return jsonify({
                "success": True,
                "feedback": fallback_feedback,
                "source": "fallback"
            })
            
    except Exception as e:
        print(f"Error in get_feedback: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Enhanced AI Sales Coach & Document Research Platform...")
    print("📍 Server available at: http://localhost:5002")
    print("🔑 Using Groq API for AI responses")
    print("📄 Advanced document processing enabled (PDF, DOCX, TXT)")
    print("🤖 Enhanced chatbot with context awareness")
    print("🎯 Comprehensive sales training features")
    print("\n" + "="*70)
    print("✅ All enhanced systems ready!")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5002)
