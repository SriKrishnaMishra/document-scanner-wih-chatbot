# 🤖 Enhanced Document Research & AI Chatbot Platform

A cutting-edge AI-powered document analysis platform with modern UI/UX design, featuring advanced document processing, intelligent search, and conversational AI capabilities.

![Platform Preview](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-2.0+-red)
![AI](https://img.shields.io/badge/AI-Groq%20Powered-purple)
![UI](https://img.shields.io/badge/UI-Modern%20Glassmorphism-cyan)

## ✨ Features

### 🚀 **Core Capabilities**
- **Multi-Format Document Processing**: PDF, DOCX, TXT, RTF support (up to 100MB)
- **AI-Powered Analysis**: Advanced document summarization and theme identification
- **Intelligent Search**: Both keyword and semantic AI-powered search
- **Conversational AI**: Context-aware chatbot for document Q&A
- **Real-time Analytics**: Comprehensive usage statistics and monitoring

### 🎨 **Modern UI/UX**
- **Glassmorphism Design**: Beautiful frosted glass effects with backdrop blur
- **Smooth Animations**: CSS3 keyframes and transitions throughout
- **Responsive Layout**: Works perfectly on desktop, tablet, and mobile
- **Dark Theme**: Professional cyberpunk-inspired color scheme
- **Interactive Elements**: Hover effects, shimmer animations, and micro-interactions

### 🔧 **Technical Features**
- **Enhanced Error Handling**: Comprehensive logging and error management
- **Performance Optimized**: Efficient file processing and memory management
- **Duplicate Detection**: Content hashing to prevent duplicate uploads
- **Health Monitoring**: Built-in health checks and system status
- **Docker Ready**: Complete containerization support

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Git
- Groq API key (free at [console.groq.com](https://console.groq.com/))

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/SriKrishnaMishra/document-scanner-wih-chatbot.git
   cd document-scanner-wih-chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install streamlit python-dotenv requests PyPDF2 python-docx flask flask-cors
   ```

3. **Configure environment**
   ```bash
   # Create .env file
   echo "GROQ_API_KEY=your_groq_api_key_here" > .env
   ```

4. **Run the application**
   ```bash
   python website_backend.py
   ```

5. **Access the platform**
   Open your browser and navigate to `http://localhost:5003`

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)
```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d --build
```

### Manual Docker Build
```bash
# Build the image
docker build -t document-chatbot .

# Run the container
docker run -p 5003:5003 --env-file .env document-chatbot
```

## 📖 Usage Guide

### 1. **Document Upload**
- Drag and drop files or click to browse
- Supports PDF, DOCX, TXT, RTF formats
- Automatic AI analysis and theme identification
- Real-time processing status updates

### 2. **AI-Powered Search**
- **Keyword Search**: Find specific terms across all documents
- **AI Search**: Ask natural language questions
- **Context-Aware Results**: Get relevant snippets and references

### 3. **Document Chatbot**
- Select any uploaded document
- Ask questions about content, themes, or insights
- Get AI-powered answers with context
- Maintain conversation history

### 4. **Analytics Dashboard**
- View upload statistics
- Monitor AI usage
- Track file types and sizes
- Real-time system health

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main application interface |
| `/api/upload` | POST | Upload and process documents |
| `/api/chat` | POST | Chat with AI about documents |
| `/api/search` | POST | Search across documents |
| `/api/documents` | GET | List all uploaded documents |
| `/api/analytics` | GET | Get system analytics |
| `/api/health` | GET | Health check endpoint |
| `/api/clear` | POST | Clear all documents |

## 🏗️ Project Structure

```
document-scanner-wih-chatbot/
├── website_backend.py          # Main Flask application
├── enhanced_website.html       # Modern UI frontend
├── requirements.txt            # Python dependencies
├── .env                       # Environment variables
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose setup
├── test_groq_api.py           # API testing utility
├── clean_build/               # Clean deployment version
├── docker_build/              # Docker-specific build
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables
```bash
GROQ_API_KEY=your_groq_api_key_here    # Required: Groq API key
MAX_CONTENT_LENGTH=104857600           # Optional: Max file size (100MB)
REQUEST_TIMEOUT=30                     # Optional: API timeout
```

### Advanced Configuration
Edit `website_backend.py` to modify:
- File size limits
- Supported file types
- AI model parameters
- Logging levels

## 🚀 Performance Features

- **Efficient File Processing**: Optimized text extraction
- **Memory Management**: Smart document storage
- **Caching**: Reduced API calls with intelligent caching
- **Async Processing**: Non-blocking file operations
- **Error Recovery**: Graceful handling of failures

## 🎨 UI/UX Highlights

- **Glassmorphism Effects**: Modern frosted glass design
- **Gradient Animations**: Dynamic color transitions
- **Micro-interactions**: Smooth hover and click effects
- **Typography**: Professional Inter font family
- **Icons**: Font Awesome integration
- **Responsive**: Mobile-first design approach

## 🔒 Security Features

- **File Validation**: Strict file type checking
- **Size Limits**: Configurable upload limits
- **Input Sanitization**: XSS protection
- **Error Handling**: No sensitive data exposure
- **API Rate Limiting**: Built-in protection

## 📊 Analytics & Monitoring

- **Upload Tracking**: File count, sizes, types
- **Usage Statistics**: Search queries, chat interactions
- **Performance Metrics**: Response times, error rates
- **Health Checks**: System status monitoring
- **Logging**: Comprehensive activity logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Groq AI** for providing fast and efficient AI inference
- **Font Awesome** for beautiful icons
- **Google Fonts** for typography
- **Flask** for the robust web framework

## 📞 Support

For support, email srikrishnamishraofficial@gmail.com or create an issue on GitHub.

---

<div align="center">
  <strong>Built with ❤️ by Sri Krishna Mishra</strong><br>
  <em>Transforming document analysis with AI</em>
</div>
