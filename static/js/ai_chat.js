/**
 * AI Chat JavaScript - COMPLETELY FIXED
 * All issues from Codex diagnosis resolved
 */

let currentInvestigationId = null;
let currentInvestigation = null; // ✅ Store full investigation data
let chatMessages = [];

/**
 * Load investigations into selector
 */
async function loadInvestigations() {
    try {
        const response = await fetch('/api/investigations');
        const data = await response.json();
        
        const select = document.getElementById('investigationSelect');
        select.innerHTML = '<option value="">Select an investigation...</option>';
        
        if (data.success && data.investigations.length > 0) {
            data.investigations.forEach(inv => {
                const option = document.createElement('option');
                option.value = inv.id;
                option.textContent = inv.name;
                select.appendChild(option);
            });
        } else {
            select.innerHTML = '<option value="">No investigations found. Create one first!</option>';
        }
        
        // Add change listener
        select.addEventListener('change', onInvestigationChange);
        
    } catch (error) {
        console.error('Error loading investigations:', error);
        document.getElementById('investigationSelect').innerHTML = 
            '<option value="">Error loading investigations</option>';
    }
}

/**
 * Handle investigation selection change - COMPLETELY FIXED
 */
async function onInvestigationChange(event) {
    const investigationId = event.target.value;
    
    if (!investigationId) {
        currentInvestigationId = null;
        currentInvestigation = null;
        document.getElementById('investigationInfo').textContent = '';
        clearChat();
        return;
    }
    
    currentInvestigationId = investigationId;
    
    try {
        // ✅ FIX 1: Get investigation (expecting {success, investigation})
        const invResponse = await fetch(`/api/investigations/${investigationId}`);
        const invData = await invResponse.json();
        
        console.log('Investigation data:', invData); // Debug
        
        // ✅ FIX 2: Check for success flag
        if (!invData.success) {
            throw new Error(invData.error || 'Failed to load investigation');
        }
        
        const inv = invData.investigation;
        currentInvestigation = inv;
        
        // ✅ FIX 3: Use already-loaded results instead of separate fetch
        // The investigation already has results from get_investigation_with_results
        const results = inv.results || [];
        const resultsCount = results.length;
        
        console.log('Results count:', resultsCount); // Debug
        
        // Update info display
        const info = `${resultsCount} result${resultsCount !== 1 ? 's' : ''} • Status: ${inv.status}`;
        document.getElementById('investigationInfo').textContent = info;
        
        // Clear chat and show welcome message
        clearChat();
        
        if (resultsCount > 0) {
            addMessageToUI(
                `Ready to analyze "${inv.name}"! This investigation has ${resultsCount} results. Ask me anything!`,
                'bot'
            );
        } else {
            addMessageToUI(
                `Investigation "${inv.name}" loaded, but it has no results yet. Run some OSINT tools first, then come back to chat!`,
                'bot'
            );
        }
        
    } catch (error) {
        console.error('Error loading investigation:', error);
        document.getElementById('investigationInfo').textContent = 'Error loading investigation';
        addMessageToUI('Error loading investigation. Please try again.', 'bot');
    }
}

/**
 * Send chat message - FIXED
 */
async function sendMessage() {
    const input = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const message = input.value.trim();
    
    console.log('Send clicked, message:', message); // Debug
    
    if (!message) {
        console.log('Message is empty'); // Debug
        return;
    }
    
    if (!currentInvestigationId) {
        alert('Please select an investigation first!');
        return;
    }
    
    console.log('Sending to investigation:', currentInvestigationId); // Debug
    
    // Disable input
    input.disabled = true;
    sendBtn.disabled = true;
    
    // Add user message to UI
    addMessageToUI(message, 'user');
    input.value = '';
    
    // Show typing indicator
    showTyping(true);
    
    try {
        console.log('Sending request to /ai/chat...'); // Debug
        
        const response = await fetch('/ai/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                investigation_id: currentInvestigationId,
                message: message
            })
        });
        
        console.log('Response status:', response.status); // Debug
        
        const data = await response.json();
        console.log('Response data:', data); // Debug
        
        showTyping(false);
        
        if (data.success) {
            addMessageToUI(data.response, 'bot', data.timestamp);
        } else {
            // Show user-friendly error message
            const errorMsg = data.error || 'Unknown error occurred';
            addMessageToUI(`❌ ${errorMsg}`, 'bot');
            console.error('AI Error:', data.error); // Debug
        }
        
    } catch (error) {
        console.error('Chat error:', error);
        showTyping(false);
        addMessageToUI('Sorry, I encountered an error. Please check the console for details.', 'bot');
    } finally {
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
    }
}

/**
 * Ask a predefined question
 */
function askQuestion(question) {
    if (!currentInvestigationId) {
        alert('Please select an investigation first!');
        return;
    }
    
    const input = document.getElementById('chatInput');
    input.value = question;
    sendMessage();
}

/**
 * Add message to chat UI
 */
function addMessageToUI(text, sender, timestamp = null) {
    const messagesContainer = document.getElementById('chatMessages');
    const typingIndicator = document.getElementById('typingIndicator');
    
    // Clear welcome message if exists
    const welcome = messagesContainer.querySelector('div[style*="text-align: center"]');
    if (welcome) {
        welcome.remove();
    }
    
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = `message-bubble ${sender}`;
    bubbleDiv.textContent = text;
    
    messageDiv.appendChild(bubbleDiv);
    
    if (timestamp) {
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = formatTimestamp(timestamp);
        messageDiv.appendChild(timeDiv);
    }
    
    // Insert before typing indicator
    messagesContainer.insertBefore(messageDiv, typingIndicator);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/**
 * Show/hide typing indicator
 */
function showTyping(show) {
    const indicator = document.getElementById('typingIndicator');
    if (show) {
        indicator.classList.add('active');
    } else {
        indicator.classList.remove('active');
    }
    
    // Scroll to bottom
    const messagesContainer = document.getElementById('chatMessages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/**
 * Clear chat messages
 */
function clearChat() {
    const messagesContainer = document.getElementById('chatMessages');
    messagesContainer.innerHTML = `
        <div style="text-align: center; padding: 40px; color: var(--text-tertiary);">
            <div style="font-size: 3em;">💬</div>
            <p>Select an investigation and start chatting!</p>
        </div>
        <div class="typing-indicator" id="typingIndicator">
            <div class="message-bubble bot">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
    `;
}

/**
 * Format timestamp
 */
function formatTimestamp(timestamp) {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) {
        const minutes = Math.floor(diff / 60000);
        return `${minutes} min${minutes > 1 ? 's' : ''} ago`;
    }
    if (diff < 86400000) {
        const hours = Math.floor(diff / 3600000);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    }
    return date.toLocaleString();
}

// Add Enter key support
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('chatInput');
    if (input) {
        input.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        });
    }
});