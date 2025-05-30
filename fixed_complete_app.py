import streamlit as st
import os
from dotenv import load_dotenv
import requests
import json
from datetime import datetime
import PyPDF2
import docx
import io
import tempfile
import uuid

# Load environment variables
load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Initialize session state
if 'uploaded_documents' not in st.session_state:
    st.session_state.uploaded_documents = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []

def call_groq_api(messages, max_tokens=500):
    """Call Groq API with proper error handling"""
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
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error calling Groq API: {e}")
        return None

def extract_text_from_file(uploaded_file):
    """Extract text from uploaded files"""
    try:
        if uploaded_file.type == "text/plain":
            return str(uploaded_file.read(), "utf-8")
        
        elif uploaded_file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(uploaded_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        
        else:
            st.error(f"Unsupported file type: {uploaded_file.type}")
            return None
            
    except Exception as e:
        st.error(f"Error extracting text: {e}")
        return None

def search_documents(query):
    """Search through uploaded documents"""
    results = []
    query_lower = query.lower()
    
    for doc_id, doc_info in st.session_state.uploaded_documents.items():
        content = doc_info['content'].lower()
        if query_lower in content:
            # Find context around the match
            index = content.find(query_lower)
            start = max(0, index - 100)
            end = min(len(content), index + 100)
            context = doc_info['content'][start:end]
            
            results.append({
                'document': doc_info['name'],
                'doc_id': doc_id,
                'context': context,
                'relevance': content.count(query_lower)
            })
    
    # Sort by relevance
    results.sort(key=lambda x: x['relevance'], reverse=True)
    return results

def ai_search(query):
    """AI-powered search using Groq"""
    if not st.session_state.uploaded_documents:
        return "No documents uploaded yet. Please upload some documents first."
    
    # Combine all document content for AI search
    all_content = ""
    doc_names = []
    for doc_id, doc_info in st.session_state.uploaded_documents.items():
        all_content += f"\n\nDocument: {doc_info['name']}\nContent: {doc_info['content'][:2000]}...\n"
        doc_names.append(doc_info['name'])
    
    prompt = f"""You are an AI search assistant. Based on the following documents, answer the user's query.

Available Documents: {', '.join(doc_names)}

Document Contents:
{all_content[:8000]}...

User Query: {query}

Please provide a comprehensive answer based on the document contents. If the information is not in the documents, say so clearly. Include which document(s) contain the relevant information."""
    
    messages = [{"role": "user", "content": prompt}]
    return call_groq_api(messages, max_tokens=600)

# Streamlit App Layout
st.set_page_config(
    page_title="Enhanced AI Sales Coach & Document Research Platform",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    .search-result {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 3px solid #2196f3;
    }
    .chat-message {
        background: #f5f5f5;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    .user-message {
        background: #e3f2fd;
        margin-left: 2rem;
    }
    .ai-message {
        background: #f3e5f5;
        margin-right: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🚀 Enhanced AI Sales Coach & Document Research Platform</h1>
    <p>Advanced AI-powered sales training with comprehensive document analysis and intelligent search</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🎯 Navigation")
page = st.sidebar.selectbox(
    "Choose a feature:",
    ["📄 Document Upload & Analysis", "🔍 AI-Powered Search", "🤖 Document Chatbot", "🎯 Sales Training", "📊 Analytics"]
)

# Document Upload & Analysis Page
if page == "📄 Document Upload & Analysis":
    st.header("📄 Document Upload & Analysis")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload Documents")
        uploaded_files = st.file_uploader(
            "Choose files to upload",
            type=['txt', 'pdf', 'docx'],
            accept_multiple_files=True,
            help="Supported formats: TXT, PDF, DOCX"
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                if st.button(f"Process {uploaded_file.name}", key=f"process_{uploaded_file.name}"):
                    with st.spinner(f"Processing {uploaded_file.name}..."):
                        # Extract text
                        text_content = extract_text_from_file(uploaded_file)
                        
                        if text_content:
                            # Generate document ID
                            doc_id = str(uuid.uuid4())
                            
                            # Generate AI summary
                            summary_prompt = f"Analyze this document and provide a comprehensive summary:\n\n{text_content[:3000]}..."
                            messages = [{"role": "user", "content": summary_prompt}]
                            summary = call_groq_api(messages, max_tokens=300)
                            
                            # Generate themes
                            themes_prompt = f"Identify the main themes and topics in this document:\n\n{text_content[:2000]}..."
                            themes_messages = [{"role": "user", "content": themes_prompt}]
                            themes = call_groq_api(themes_messages, max_tokens=200)
                            
                            # Store document
                            st.session_state.uploaded_documents[doc_id] = {
                                'name': uploaded_file.name,
                                'content': text_content,
                                'summary': summary or "Summary generation failed",
                                'themes': themes or "Theme identification failed",
                                'upload_time': datetime.now().isoformat(),
                                'size': len(text_content)
                            }
                            
                            st.success(f"✅ {uploaded_file.name} processed successfully!")
                        else:
                            st.error(f"❌ Failed to process {uploaded_file.name}")
    
    with col2:
        st.subheader("Uploaded Documents")
        if st.session_state.uploaded_documents:
            for doc_id, doc_info in st.session_state.uploaded_documents.items():
                with st.expander(f"📄 {doc_info['name']}"):
                    st.write(f"**Size:** {doc_info['size']} characters")
                    st.write(f"**Uploaded:** {doc_info['upload_time'][:19]}")
                    st.write(f"**Summary:** {doc_info['summary']}")
                    st.write(f"**Themes:** {doc_info['themes']}")
                    
                    if st.button(f"Delete {doc_info['name']}", key=f"delete_{doc_id}"):
                        del st.session_state.uploaded_documents[doc_id]
                        st.rerun()
        else:
            st.info("No documents uploaded yet.")

# AI-Powered Search Page
elif page == "🔍 AI-Powered Search":
    st.header("🔍 AI-Powered Search")
    
    if not st.session_state.uploaded_documents:
        st.warning("⚠️ Please upload some documents first to enable search functionality.")
    else:
        st.subheader("Search Your Documents")
        
        # Search input
        search_query = st.text_input(
            "Enter your search query:",
            placeholder="e.g., 'What are the main findings about AI?', 'sales strategies', 'customer feedback'"
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🔍 Keyword Search", disabled=not search_query):
                if search_query:
                    with st.spinner("Searching documents..."):
                        results = search_documents(search_query)
                        st.session_state.search_results = results
        
        with col2:
            if st.button("🤖 AI-Powered Search", disabled=not search_query):
                if search_query:
                    with st.spinner("AI is analyzing your documents..."):
                        ai_result = ai_search(search_query)
                        if ai_result:
                            st.subheader("🤖 AI Search Results")
                            st.markdown(f'<div class="search-result"><strong>Query:</strong> {search_query}<br><strong>AI Response:</strong><br>{ai_result}</div>', unsafe_allow_html=True)
        
        # Display keyword search results
        if st.session_state.search_results:
            st.subheader("🔍 Keyword Search Results")
            for result in st.session_state.search_results:
                st.markdown(f"""
                <div class="search-result">
                    <strong>Document:</strong> {result['document']}<br>
                    <strong>Matches:</strong> {result['relevance']}<br>
                    <strong>Context:</strong> ...{result['context']}...
                </div>
                """, unsafe_allow_html=True)

# Document Chatbot Page
elif page == "🤖 Document Chatbot":
    st.header("🤖 Document Chatbot")
    
    if not st.session_state.uploaded_documents:
        st.warning("⚠️ Please upload some documents first to chat about them.")
    else:
        # Document selection
        doc_options = {doc_id: doc_info['name'] for doc_id, doc_info in st.session_state.uploaded_documents.items()}
        selected_doc_id = st.selectbox("Select a document to chat about:", options=list(doc_options.keys()), format_func=lambda x: doc_options[x])
        
        if selected_doc_id:
            selected_doc = st.session_state.uploaded_documents[selected_doc_id]
            st.info(f"💬 Chatting about: **{selected_doc['name']}**")
            
            # Chat interface
            st.subheader("Chat History")
            
            # Display chat history
            for message in st.session_state.chat_history:
                if message['type'] == 'user':
                    st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message ai-message"><strong>AI:</strong> {message["content"]}</div>', unsafe_allow_html=True)
            
            # Chat input
            user_question = st.text_input("Ask a question about the document:", key="chat_input")
            
            if st.button("Send", disabled=not user_question):
                if user_question:
                    # Add user message to history
                    st.session_state.chat_history.append({
                        'type': 'user',
                        'content': user_question,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    with st.spinner("AI is thinking..."):
                        # Generate AI response
                        prompt = f"""Based on the following document, answer the user's question:

Document: {selected_doc['name']}
Content: {selected_doc['content'][:4000]}...

Question: {user_question}

Please provide a helpful and accurate answer based on the document content."""
                        
                        messages = [{"role": "user", "content": prompt}]
                        ai_response = call_groq_api(messages, max_tokens=400)
                        
                        if ai_response:
                            # Add AI response to history
                            st.session_state.chat_history.append({
                                'type': 'ai',
                                'content': ai_response,
                                'timestamp': datetime.now().isoformat()
                            })
                            
                            st.rerun()
                        else:
                            st.error("Failed to generate response. Please try again.")
            
            # Clear chat history
            if st.button("Clear Chat History"):
                st.session_state.chat_history = []
                st.rerun()

# Sales Training Page
elif page == "🎯 Sales Training":
    st.header("🎯 Sales Training")
    
    # Sales scenarios
    scenarios = [
        {
            "id": 1,
            "title": "Enterprise Software Sale",
            "description": "You are selling enterprise software to a large corporation.",
            "customer": "John Smith, CTO at TechCorp Inc.",
            "challenges": ["Implementation timeline", "ROI concerns", "Integration issues"]
        },
        {
            "id": 2,
            "title": "SaaS Solution for Small Business",
            "description": "You are selling a SaaS solution to a price-sensitive small business.",
            "customer": "Sarah Johnson, Owner at Johnson Consulting",
            "challenges": ["Limited budget", "Manual processes", "Technical expertise"]
        }
    ]
    
    st.subheader("Choose a Sales Scenario")
    
    for scenario in scenarios:
        with st.expander(f"🎯 {scenario['title']}"):
            st.write(f"**Description:** {scenario['description']}")
            st.write(f"**Customer:** {scenario['customer']}")
            st.write(f"**Key Challenges:** {', '.join(scenario['challenges'])}")
            
            if st.button(f"Start Simulation", key=f"start_{scenario['id']}"):
                st.session_state.current_scenario = scenario
                st.session_state.sales_chat = [
                    {"speaker": "customer", "message": "Hello! I'm interested in learning more about your solution."}
                ]
                st.rerun()
    
    # Sales simulation
    if 'current_scenario' in st.session_state:
        st.subheader(f"🎭 Simulation: {st.session_state.current_scenario['title']}")
        
        # Display conversation
        for message in st.session_state.sales_chat:
            if message['speaker'] == 'customer':
                st.markdown(f'<div class="chat-message ai-message"><strong>Customer:</strong> {message["message"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {message["message"]}</div>', unsafe_allow_html=True)
        
        # Sales input
        sales_message = st.text_input("Your response:", key="sales_input")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("Send Response", disabled=not sales_message):
                if sales_message:
                    # Add user message
                    st.session_state.sales_chat.append({
                        "speaker": "salesperson",
                        "message": sales_message
                    })
                    
                    with st.spinner("Customer is responding..."):
                        # Generate customer response
                        scenario = st.session_state.current_scenario
                        prompt = f"""You are simulating a customer in a sales scenario.

Scenario: {scenario['description']}
Customer: {scenario['customer']}
Key Challenges: {', '.join(scenario['challenges'])}

Conversation so far:
{chr(10).join([f"{msg['speaker']}: {msg['message']}" for msg in st.session_state.sales_chat])}

Respond as the customer would. Be realistic and reference your challenges. Keep response under 100 words."""
                        
                        messages = [{"role": "user", "content": prompt}]
                        customer_response = call_groq_api(messages, max_tokens=150)
                        
                        if customer_response:
                            st.session_state.sales_chat.append({
                                "speaker": "customer",
                                "message": customer_response
                            })
                            st.rerun()
        
        with col2:
            if st.button("Get AI Feedback"):
                if len(st.session_state.sales_chat) > 2:
                    with st.spinner("Generating feedback..."):
                        conversation_text = "\n".join([f"{msg['speaker']}: {msg['message']}" for msg in st.session_state.sales_chat])
                        
                        feedback_prompt = f"""Analyze this sales conversation and provide feedback:

Scenario: {st.session_state.current_scenario['title']}
{conversation_text}

Provide:
1. Overall score (1-10)
2. Strengths
3. Areas for improvement
4. Specific recommendations"""
                        
                        messages = [{"role": "user", "content": feedback_prompt}]
                        feedback = call_groq_api(messages, max_tokens=500)
                        
                        if feedback:
                            st.subheader("📊 AI Feedback")
                            st.markdown(feedback)

# Analytics Page
elif page == "📊 Analytics":
    st.header("📊 Analytics Dashboard")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📄 Document Statistics")
        if st.session_state.uploaded_documents:
            total_docs = len(st.session_state.uploaded_documents)
            total_size = sum(doc['size'] for doc in st.session_state.uploaded_documents.values())
            
            st.metric("Total Documents", total_docs)
            st.metric("Total Content Size", f"{total_size:,} characters")
            
            # Document sizes
            doc_sizes = [(doc['name'], doc['size']) for doc in st.session_state.uploaded_documents.values()]
            doc_sizes.sort(key=lambda x: x[1], reverse=True)
            
            st.subheader("Document Sizes")
            for name, size in doc_sizes:
                st.write(f"📄 {name}: {size:,} characters")
        else:
            st.info("No documents uploaded yet.")
    
    with col2:
        st.subheader("🤖 AI Usage Statistics")
        st.metric("Groq API Status", "✅ Connected" if GROQ_API_KEY else "❌ Not configured")
        st.metric("Chat Messages", len(st.session_state.chat_history))
        
        if st.session_state.chat_history:
            user_messages = len([msg for msg in st.session_state.chat_history if msg['type'] == 'user'])
            ai_messages = len([msg for msg in st.session_state.chat_history if msg['type'] == 'ai'])
            
            st.metric("User Messages", user_messages)
            st.metric("AI Responses", ai_messages)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🚀 Enhanced AI Sales Coach & Document Research Platform</p>
    <p>Powered by Groq AI • Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
