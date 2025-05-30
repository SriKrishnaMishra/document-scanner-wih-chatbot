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

// State
let state = {
    documents: {},
    currentDocument: null,
    chatHistory: []
};

// Initialize
function init() {
    // Load state from localStorage if available
    const savedState = localStorage.getItem('docAIState');
    if (savedState) {
        state = JSON.parse(savedState);
        renderDocumentList();
        
        if (state.currentDocument) {
            loadDocument(state.currentDocument);
        }
    }
    
    // Event listeners
    fileUpload.addEventListener('change', handleFileUpload);
    processBtn.addEventListener('click', processDocument);
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
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
function processDocument() {
    const file = fileUpload.files[0];
    if (!file) return;
    
    showLoading('Processing document...');
    
    // Simulate document processing
    setTimeout(() => {
        const docId = 'doc_' + Date.now();
        const docName = file.name;
        
        // Create a FileReader to read the file content
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const text = e.target.result;
            
            // Process the document (in a real app, this would be done by the backend)
            const processedDoc = processDocumentText(text, docName);
            
            // Add to state
            state.documents[docId] = processedDoc;
            state.currentDocument = docId;
            
            // Save state
            saveState();
            
            // Update UI
            renderDocumentList();
            loadDocument(docId);
            
            // Reset file upload
            fileUpload.value = '';
            fileInfo.textContent = 'No file selected';
            processBtn.disabled = true;
            
            hideLoading();
        };
        
        reader.readAsText(file);
    }, 2000);
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
    
    return sentences.slice(0, summaryLength).join('. ') + '.';
}

// Load Document
function loadDocument(docId) {
    const doc = state.documents[docId];
    if (!doc) return;
    
    // Update UI
    welcomeScreen.style.display = 'none';
    documentView.style.display = 'block';
    documentTitle.textContent = doc.name;
    
    // Update stats
    totalWords.textContent = doc.words;
    totalSentences.textContent = doc.sentences;
    identifiedThemes.textContent = doc.themes.length;
    
    // Update themes list
    themesList.innerHTML = '';
    doc.themes.forEach((theme, index) => {
        const themeEl = document.createElement('div');
        themeEl.className = 'theme-item';
        themeEl.innerHTML = `
            <h4>Theme ${index + 1}: ${theme.keywords.join(', ')}</h4>
            <p><strong>Representative Content:</strong> ${theme.representativeSentence}</p>
        `;
        themesList.appendChild(themeEl);
    });
    
    // Update summary
    summaryContent.textContent = doc.summary;
    
    // Update document content
    documentContent.textContent = doc.text;
    
    // Reset chat
    chatMessages.innerHTML = `
        <div class="message system">
            <div class="message-content">
                <p>Hello! I'm your document assistant. Ask me anything about "${doc.name}".</p>
            </div>
        </div>
    `;
    
    // Create visualizations
    createWordFrequencyChart(doc);
    createThemeNetworkChart(doc);
    
    // Set current document
    state.currentDocument = docId;
    state.chatHistory = [];
    saveState();
    
    // Highlight the document in the list
    const docItems = documentList.querySelectorAll('li');
    docItems.forEach(item => {
        if (item.getAttribute('data-id') === docId) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}

// Send Message
function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;
    
    addMessageToChat('user', message);
    chatInput.value = '';
    
    // Simulate response
    simulateResponse(message);
}

// Add Message to Chat
function addMessageToChat(role, content) {
    const messageEl = document.createElement('div');
    messageEl.className = `message ${role}`;
    messageEl.innerHTML = `
        <div class="message-content">
            <p>${content}</p>
        </div>
    `;
    chatMessages.appendChild(messageEl);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Add to chat history
    state.chatHistory.push({ role, content });
    saveState();
}

// Simulate Response
function simulateResponse(question) {
    const doc = state.documents[state.currentDocument];
    if (!doc) return;
    
    // Show typing indicator
    const typingEl = document.createElement('div');
    typingEl.className = 'message assistant typing';
    typingEl.innerHTML = `
        <div class="message-content">
            <p>Thinking...</p>
        </div>
    `;
    chatMessages.appendChild(typingEl);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Simulate thinking time
    setTimeout(() => {
        // Remove typing indicator
        chatMessages.removeChild(typingEl);
        
        // Generate response based on question
        let response = '';
        
        if (question.toLowerCase().includes('summary') || question.toLowerCase().includes('summarize')) {
            response = `Here's a summary of the document: ${doc.summary}`;
        } else if (question.toLowerCase().includes('theme') || question.toLowerCase().includes('topic')) {
            response = `The main themes in this document are: ${doc.themes.map((theme, i) => `Theme ${i+1}: ${theme.keywords.join(', ')}`).join('; ')}`;
        } else if (question.toLowerCase().includes('important') || question.toLowerCase().includes('key point')) {
            const randomTheme = doc.themes[Math.floor(Math.random() * doc.themes.length)];
            response = `One of the key points in the document is: ${randomTheme.representativeSentence}`;
        } else {
            // Default response
            response = `Based on the document, I found the following information that might be relevant to your question: ${doc.themes[0].representativeSentence}`;
        }
        
        // Add response to chat
        addMessageToChat('assistant', response);
    }, 1500);
}

// Create Word Frequency Chart
function createWordFrequencyChart(doc) {
    const canvas = document.getElementById('word-freq-chart');
    
    // Clear previous chart if it exists
    if (window.wordFreqChart) {
        window.wordFreqChart.destroy();
    }
    
    // Get word frequencies
    const words = doc.text.toLowerCase().split(/\s+/).filter(word => word.length > 3);
    const wordFreq = {};
    
    words.forEach(word => {
        wordFreq[word] = (wordFreq[word] || 0) + 1;
    });
    
    // Sort by frequency
    const sortedWords = Object.entries(wordFreq)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);
    
    // Create chart
    window.wordFreqChart = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: sortedWords.map(item => item[0]),
            datasets: [{
                label: 'Word Frequency',
                data: sortedWords.map(item => item[1]),
                backgroundColor: '#4a6bff',
                borderColor: '#3a5bef',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Create Theme Network Chart
function createThemeNetworkChart(doc) {
    const canvas = document.getElementById('theme-network-chart');
    
    // Clear previous chart if it exists
    if (window.themeNetworkChart) {
        window.themeNetworkChart.destroy();
    }
    
    // Create a simple network visualization
    window.themeNetworkChart = new Chart(canvas, {
        type: 'bubble',
        data: {
            datasets: doc.themes.map((theme, i) => ({
                label: `Theme ${i+1}`,
                data: [{
                    x: Math.random() * 100,
                    y: Math.random() * 100,
                    r: (theme.keywords.length * 10) + 10
                }],
                backgroundColor: `hsl(${i * 360 / doc.themes.length}, 70%, 60%)`,
            }))
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const theme = doc.themes[context.datasetIndex];
                            return `${context.dataset.label}: ${theme.keywords.join(', ')}`;
                        }
                    }
                }
            }
        }
    });
}

// Switch Tab
function switchTab(tabId) {
    tabBtns.forEach(btn => {
        if (btn.getAttribute('data-tab') === tabId) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    tabPanes.forEach(pane => {
        if (pane.id === `${tabId}-tab`) {
            pane.classList.add('active');
        } else {
            pane.classList.remove('active');
        }
    });
}

// Switch Visualization Tab
function switchVizTab(vizId) {
    vizTabBtns.forEach(btn => {
        if (btn.getAttribute('data-viz') === vizId) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    vizPanes.forEach(pane => {
        if (pane.id === `${vizId}-viz`) {
            pane.classList.add('active');
        } else {
            pane.classList.remove('active');
        }
    });
}

// Render Document List
function renderDocumentList() {
    documentList.innerHTML = '';
    
    Object.entries(state.documents).forEach(([id, doc]) => {
        const li = document.createElement('li');
        li.textContent = doc.name;
        li.setAttribute('data-id', id);
        
        if (id === state.currentDocument) {
            li.classList.add('active');
        }
        
        li.addEventListener('click', () => loadDocument(id));
        documentList.appendChild(li);
    });
}

// Show Loading Overlay
function showLoading(text) {
    loadingText.textContent = text || 'Loading...';
    loadingOverlay.style.display = 'flex';
}

// Hide Loading Overlay
function hideLoading() {
    loadingOverlay.style.display = 'none';
}

// Clear All Data
function clearAllData() {
    if (confirm('Are you sure you want to clear all data? This action cannot be undone.')) {
        state = {
            documents: {},
            currentDocument: null,
            chatHistory: []
        };
        
        saveState();
        renderDocumentList();
        
        welcomeScreen.style.display = 'flex';
        documentView.style.display = 'none';
    }
}

// Save State to localStorage
function saveState() {
    localStorage.setItem('docAIState', JSON.stringify(state));
}

// Initialize the app
document.addEventListener('DOMContentLoaded', init);
