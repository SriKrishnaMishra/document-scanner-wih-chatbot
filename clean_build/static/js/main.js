// DOM Elements
const fileUpload = document.getElementById('file-upload');
const fileInfo = document.getElementById('file-info');
const processBtn = document.getElementById('process-btn');
const documentList = document.getElementById('document-list');
const welcomeScreen = document.getElementById('welcome-screen');
const documentView = document.getElementById('document-view');
const clearDataBtn = document.getElementById('clear-data-btn');

// State
let state = {
    documents: {},
    currentDocument: null
};

// Initialize
document.addEventListener('DOMContentLoaded', function() {
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
    clearDataBtn.addEventListener('click', clearAllData);
});

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
    
    // Create a simple document object
    const docId = 'doc_' + Date.now();
    const docName = file.name;
    
    // Add to state
    state.documents[docId] = {
        name: docName,
        uploadDate: new Date().toLocaleString()
    };
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
}

// Load Document
function loadDocument(docId) {
    const doc = state.documents[docId];
    if (!doc) return;
    
    // Update UI
    welcomeScreen.style.display = 'none';
    documentView.style.display = 'block';
    documentView.innerHTML = `
        <div class="document-header">
            <h2>${doc.name}</h2>
            <p>Uploaded: ${doc.uploadDate}</p>
        </div>
        <div class="document-content">
            <p>This is a simplified version of the document viewer.</p>
            <p>In a full implementation, this would display the document content and analysis.</p>
        </div>
    `;
    
    // Set current document
    state.currentDocument = docId;
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

// Clear All Data
function clearAllData() {
    if (confirm('Are you sure you want to clear all data? This action cannot be undone.')) {
        state = {
            documents: {},
            currentDocument: null
        };
        
        saveState();
        renderDocumentList();
        
        welcomeScreen.style.display = 'flex';
        documentView.style.display = 'none';
    }
}

// Save State
function saveState() {
    localStorage.setItem('docAIState', JSON.stringify(state));
}
