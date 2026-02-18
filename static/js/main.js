let isRecording = false;
let mediaRecorder;
let audioChunks = [];
let sessionId = null;

const voiceBtn = document.getElementById('voiceBtn');
const statusText = document.getElementById('statusText');
const chatContainer = document.getElementById('chatContainer');
const textInput = document.getElementById('textInput');
const sendBtn = document.getElementById('sendBtn');
const customerEmail = document.getElementById('customerEmail');
const orderNumber = document.getElementById('orderNumber');
const resetBtn = document.getElementById('resetBtn');
const visualizer = document.getElementById('visualizer');

voiceBtn.addEventListener('click', toggleRecording);
sendBtn.addEventListener('click', sendTextMessage);
textInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendTextMessage();
});
resetBtn.addEventListener('click', resetConversation);

window.addEventListener('load', loadAnalytics);

async function toggleRecording() {
    if (!isRecording) {
        await startRecording();
    } else {
        stopRecording();
    }
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            await processAudio(audioBlob);
        };

        mediaRecorder.start();
        isRecording = true;
        
        voiceBtn.classList.add('recording');
        statusText.textContent = 'Listening... Click again to stop';
        statusText.classList.add('recording');
        document.querySelector('.pulse-ring').classList.add('active');
        
    } catch (error) {
        console.error('Error accessing microphone:', error);
        alert('Please allow microphone access to use voice features.');
    }
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        isRecording = false;
        
        voiceBtn.classList.remove('recording');
        statusText.textContent = 'Processing your message...';
        statusText.classList.remove('recording');
        document.querySelector('.pulse-ring').classList.remove('active');
    }
}

async function processAudio(audioBlob) {
    try {
        const reader = new FileReader();
        reader.readAsDataURL(audioBlob);
        
        reader.onloadend = async () => {
            const base64Audio = reader.result.split(',')[1];
            
            const transcriptResponse = await fetch('/api/transcribe', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ audio: base64Audio })
            });
            
            const transcriptData = await transcriptResponse.json();
            
            if (transcriptData.error) {
                throw new Error(transcriptData.error);
            }
            
            const userText = transcriptData.text;
            
            addMessage(userText, 'user');
            
            const chatResponse = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: userText,
                    session_id: sessionId,
                    customer_email: customerEmail.value || null,
                    order_number: orderNumber.value || null
                })
            });
            
            const chatData = await chatResponse.json();
            
            if (chatData.error) {
                throw new Error(chatData.error);
            }
            
            sessionId = chatData.session_id;
            const botResponse = chatData.response;
            
            addMessage(botResponse, 'bot');
            
            const synthesizeResponse = await fetch('/api/synthesize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: botResponse })
            });
            
            const synthesizeData = await synthesizeResponse.json();
            
            if (synthesizeData.error) {
                throw new Error(synthesizeData.error);
            }
            
            playAudio(synthesizeData.audio);
            
            statusText.textContent = 'Click the microphone to start';
            
        };
        
    } catch (error) {
        console.error('Error processing audio:', error);
        addMessage('Sorry, there was an error processing your request.', 'bot');
        statusText.textContent = 'Error occurred. Try again.';
    }
}

async function sendTextMessage() {
    const message = textInput.value.trim();
    
    if (!message) return;
    
    textInput.value = '';
    
    addMessage(message, 'user');
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                session_id: sessionId,
                customer_email: customerEmail.value || null,
                order_number: orderNumber.value || null
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        sessionId = data.session_id;
        
        addMessageWithSources(data.response, 'bot', data.rag_sources);
        
    } catch (error) {
        console.error('Error sending message:', error);
        addMessage('Sorry, there was an error processing your request.', 'bot');
    }
}

function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const label = sender === 'user' ? 'You' : 'AI Assistant';
    contentDiv.innerHTML = `<strong>${label}:</strong> ${text}`;
    
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function addMessageWithSources(text, sender, sources) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const label = sender === 'user' ? 'You' : 'AI Assistant';
    let html = `<strong>${label}:</strong> ${text}`;
    
    // Add RAG sources if available
    if (sources && sources.length > 0) {
        html += `<div class="rag-sources">
            <small>📚 Sources: ${sources.join(', ')}</small>
        </div>`;
    }
    
    contentDiv.innerHTML = html;
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function playAudio(base64Audio) {
    const audio = new Audio(`data:audio/wav;base64,${base64Audio}`);
    audio.play().catch(error => {
        console.error('Error playing audio:', error);
    });
}

async function resetConversation() {
    if (!confirm('Are you sure you want to reset the conversation?')) return;
    
    try {
        await fetch('/api/reset', { method: 'POST' });
        
        chatContainer.innerHTML = `
            <div class="chat-message bot-message">
                <div class="message-content">
                    <strong>AI Assistant:</strong> Hello! How can I help you today?
                </div>
            </div>
        `;
        
        sessionId = null;
        
        alert('Conversation reset successfully!');
        
    } catch (error) {
        console.error('Error resetting conversation:', error);
        alert('Error resetting conversation. Please try again.');
    }
}

async function loadAnalytics() {
    try {
        const response = await fetch('/api/analytics');
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        const analyticsContent = document.getElementById('analyticsContent');
        
        const html = `
            <div class="stat-grid">
                <div class="stat-card">
                    <h3>${data.summary.total_conversations || 0}</h3>
                    <p>Total Conversations</p>
                </div>
                <div class="stat-card">
                    <h3>${data.summary.unique_sessions || 0}</h3>
                    <p>Unique Sessions</p>
                </div>
                <div class="stat-card">
                    <h3>${data.summary.avg_response_length || 0}</h3>
                    <p>Avg Response Length</p>
                </div>
                <div class="stat-card">
                    <h3>${data.summary.avg_input_length || 0}</h3>
                    <p>Avg Input Length</p>
                </div>
            </div>
            
            <h4>Recent Conversations</h4>
            <div style="max-height: 200px; overflow-y: auto;">
                ${data.recent_conversations.map(conv => `
                    <div style="margin-bottom: 10px; padding: 10px; background: white; border-radius: 8px;">
                        <p><strong>User:</strong> ${conv.user_input}</p>
                        <p><strong>Bot:</strong> ${conv.bot_response}</p>
                        <p style="font-size: 0.8em; color: #999;">
                            ${new Date(conv.timestamp).toLocaleString()}
                        </p>
                    </div>
                `).join('')}
            </div>
        `;
        
        analyticsContent.innerHTML = html;
        
    } catch (error) {
        console.error('Error loading analytics:', error);
        document.getElementById('analyticsContent').innerHTML = 
            '<p style="color: red;">Error loading analytics</p>';
    }
}

setInterval(loadAnalytics, 30000);

// Document upload
document.getElementById('uploadBtn').addEventListener('click', async () => {
    const fileInput = document.getElementById('docUpload');
    const file = fileInput.files[0];
    const status = document.getElementById('uploadStatus');
    
    if (!file) {
        status.innerHTML = '<p style="color:red">Please select a file!</p>';
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    status.innerHTML = '<p>Uploading...</p>';
    
    try {
        const response = await fetch('/api/upload-doc', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.error) {
            status.innerHTML = `<p style="color:red">${data.error}</p>`;
        } else {
            status.innerHTML = `<p style="color:green">✅ ${data.message}</p>`;
        }
    } catch (error) {
        status.innerHTML = '<p style="color:red">Upload failed!</p>';
    }
});

// Reload knowledge base
document.getElementById('reloadKbBtn').addEventListener('click', async () => {
    const status = document.getElementById('uploadStatus');
    status.innerHTML = '<p>Reloading knowledge base...</p>';
    
    try {
        const response = await fetch('/api/reload-knowledge-base', {
            method: 'POST'
        });
        const data = await response.json();
        const message = data.message || 'Knowledge base reloaded successfully!';
        status.innerHTML = `<p style="color:green">✅ ${message}</p>`;
    } catch (error) {
        status.innerHTML = '<p style="color:red">Reload failed!</p>';
    }
});