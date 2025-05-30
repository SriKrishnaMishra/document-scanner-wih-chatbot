// DOM Elements
const fileUpload = document.getElementById('file-upload');
const fileInfo = document.getElementById('file-info');
const processBtn = document.getElementById('process-btn');
const documentList = document.getElementById('document-list');
const welcomeScreen = document.getElementById('welcome-screen');
const documentView = document.getElementById('document-view');
const documentTitle = document.getElementById('document-title');
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const themesList = document.getElementById('themes-list');
const summaryContent = document.getElementById('summary-content');
const documentContent = document.getElementById('document-content');
const totalWords = document.getElementById('total-words');
const totalSentences = document.getElementById('total-sentences');
const identifiedThemes = document.getElementById('identified-themes');
const loadingOverlay = document.getElementById('loading-overlay');
const loadingText = document.getElementById('loading-text');
const clearDataBtn = document.getElementById('clear-data-btn');
const tabBtns = document.querySelectorAll('.tab-btn');
const tabPanes = document.querySelectorAll('.tab-pane');
const vizTabBtns = document.querySelectorAll('.viz-tab-btn');
const vizPanes = document.querySelectorAll('.viz-pane');
const questionBtns = document.querySelectorAll('.question-btn');
const searchInput = document.getElementById('search-input');
const searchBtn = document.getElementById('search-btn');

// State
let state = {
    documents: {},
    currentDocument: null,
    chatHistory: []
};

// API Base URL
const API_BASE_URL = window.location.origin;

// Initialize
async function init() {
    // Load state from localStorage if available
    const savedState = localStorage.getItem('docAIState');
    if (savedState) {
        state = JSON.parse(savedState);
    }
    
    // Load documents from server
    await loadDocuments();
    
    // Set up event listeners
    setupEventListeners();
    
    // Show welcome screen if no documents
    if (Object.keys(state.documents).length === 0) {
        welcomeScreen.style.display = 'flex';
        documentView.style.display = 'none';
    } else if (state.currentDocument) {
        await loadDocument(state.currentDocument);
    }
}

// Set up event listeners
function setupEventListeners() {
    fileUpload.addEventListener('change', handleFileUpload);
    processBtn.addEventListener('click', processDocument);
    sendBtn.addEventListener('click', sendMessage);
    searchBtn.addEventListener('click', handleSearch);
    
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });
    
    clearDataBtn.addEventListener('click', clearAllData);
    
    // Tab navigation
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            switchTab(tabId);
        });
    });
    
    // Visualization tab navigation
    vizTabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const vizId = btn.getAttribute('data-viz');
            switchVizTab(vizId);
        });
    });
    
    // Sample questions
    questionBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const question = btn.textContent;
            addMessageToChat('user', question);
            simulateResponse(question);
        });
    });
}

// Load documents from server
async function loadDocuments() {
    try {
        showLoading('Loading documents...');
        const response = await fetch(`${API_BASE_URL}/api/documents`);
        if (!response.ok) throw new Error('Failed to load documents');
        
        const docs = await response.json();
        state.documents = {};
        
        // Fetch full document for each doc
        for (const doc of docs) {
            const docResponse = await fetch(`${API_BASE_URL}/api/documents/${doc.id}`);
            if (docResponse.ok) {
                const fullDoc = await docResponse.json();
                state.documents[doc.id] = fullDoc;
            }
        }
        
        renderDocumentList();
        hideLoading();
    } catch (error) {
        console.error('Error loading documents:', error);
        hideLoading();
        alert('Failed to load documents. Please refresh the page.');
    }
}

// File Upload Handler
function handleFileUpload(e) {
    const file = e.target.files[0];
    if (file) {
        fileInfo.textContent = file.name;
        processBtn.disabled = false;
    } else {
        fileInfo.textContent = 'No file selected';
        processBtn.disabled = true;
    }
}

// Process Document
async function processDocument() {
    const file = fileUpload.files[0];
    if (!file) return;
    
    showLoading('Processing document...');
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_BASE_URL}/api/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to process document');
        }
        
        const docData = await response.json();
        
        // Get full document
        const docResponse = await fetch(`${API_BASE_URL}/api/documents/${docData.id}`);
        if (!docResponse.ok) throw new Error('Failed to load document details');
        
        const fullDoc = await docResponse.json();
        state.documents[docData.id] = fullDoc;
        state.currentDocument = docData.id;
        
        // Save state
        saveState();
        
        // Update UI
        renderDocumentList();
        await loadDocument(docData.id);
        
        // Reset file upload
        fileUpload.value = '';
        fileInfo.textContent = 'No file selected';
        processBtn.disabled = true;
        
        // Show document view
        welcomeScreen.style.display = 'none';
        documentView.style.display = 'block';
        
    } catch (error) {
        console.error('Error processing document:', error);
        alert(`Error: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Process Document Text (simulated)
function processDocumentText(text, docName) {
    // Count words and sentences
    const words = text.split(/\s+/).filter(word => word.length > 0);
    const sentences = text.split(/[.!?]+/).filter(sentence => sentence.trim().length > 0);
    
    // Extract themes (simulated)
    const themes = extractThemes(text);
    
    // Generate summary (simulated)
    const summary = generateSummary(text);
    
    return {
        name: docName,
        text: text,
        words: words.length,
        sentences: sentences.length,
        themes: themes,
        summary: summary
    };
}

// Extract Themes (simulated)
function extractThemes(text) {
    // In a real app, this would use NLP to extract themes
    // Here we'll just create some random themes based on the text
    const words = text.toLowerCase().split(/\s+/).filter(word => word.length > 3);
    const uniqueWords = [...new Set(words)];
    const themes = [];
    
    // Get some random words to use as themes
    const numThemes = Math.min(5, Math.ceil(uniqueWords.length / 20));
    
    for (let i = 0; i < numThemes; i++) {
        const keywordCount = Math.floor(Math.random() * 3) + 1;
        const keywords = [];
        
        for (let j = 0; j < keywordCount; j++) {
            const randomIndex = Math.floor(Math.random() * uniqueWords.length);
            keywords.push(uniqueWords[randomIndex]);
        }
        
        // Get a random sentence as the representative content
        const sentences = text.split(/[.!?]+/).filter(sentence => sentence.trim().length > 0);
        const randomSentenceIndex = Math.floor(Math.random() * sentences.length);
        
        themes.push({
            keywords: keywords,
            representativeSentence: sentences[randomSentenceIndex].trim()
        });
    }
    
    return themes;
}

// Generate Summary (simulated)
function generateSummary(text) {
    // In a real app, this would use NLP to generate a summary
    // Here we'll just return the first few sentences
    const sentences = text.split(/[.!?]+/).filter(sentence => sentence.trim().length > 0);
    const summaryLength = Math.min(3, sentences.length);
        chatMessages.innerHTML = '';
        state.chatHistory = [];
        
        // Add welcome message
        addMessageToChat('assistant', `I've loaded "${doc.filename || 'your document'}". What would you like to know about it?`);
        
    } catch (error) {
        console.error('Error loading document:', error);
        alert(`Failed to load document: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Clear All Data
async function clearAllData() {
    if (confirm('Are you sure you want to clear all data? This cannot be undone.')) {
        try {
            showLoading('Clearing data...');
            
            // Clear server-side data (if applicable)
            // Note: In a real app, you would have an API endpoint to clear data
            
            // Clear client-side state
            state = {
                documents: {},
                currentDocument: null,
                chatHistory: []
            };
            
            saveState();
            
            // Reset UI
            documentList.innerHTML = '';
            welcomeScreen.style.display = 'flex';
            documentView.style.display = 'none';
            
            // Reset file upload
            fileUpload.value = '';
            fileInfo.textContent = 'No file selected';
            processBtn.disabled = true;
            
            // Reload the page to ensure clean state
            window.location.reload();
            
        } catch (error) {
            console.error('Error clearing data:', error);
            alert('Failed to clear data. Please try again.');
        } finally {
            hideLoading();
        }
    }
}
