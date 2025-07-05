// Chat functionality
document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message-input');
    const chatForm = document.querySelector('form[action*="send_message"]');
    
    // Auto-scroll to bottom of chat
    function scrollToBottom() {
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    
    // Initial scroll to bottom
    scrollToBottom();
    
    // Focus on input
    if (messageInput) {
        messageInput.focus();
    }
    
    // Handle form submission
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            const message = messageInput.value.trim();
            if (!message) {
                e.preventDefault();
                return;
            }
            
            // Show loading state
            const submitButton = chatForm.querySelector('button[type="submit"]');
            const originalHTML = submitButton.innerHTML;
            submitButton.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"></div>';
            submitButton.disabled = true;
            
            // Add user message to chat immediately for better UX
            addMessageToChat(message, true);
            messageInput.value = '';
            scrollToBottom();
            
            // The form will submit normally, but we've improved the UX
            setTimeout(() => {
                submitButton.innerHTML = originalHTML;
                submitButton.disabled = false;
            }, 1000);
        });
    }
    
    // Handle Enter key for sending messages
    if (messageInput) {
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    }
    
    // Function to add message to chat (for immediate feedback)
    function addMessageToChat(message, isUser) {
        if (!chatMessages) return;
        
        const messageWrapper = document.createElement('div');
        messageWrapper.className = 'message-wrapper mb-3';
        
        const messageDiv = document.createElement('div');
        messageDiv.className = isUser ? 'd-flex justify-content-end' : 'd-flex';
        
        const messageContent = document.createElement('div');
        messageContent.className = isUser 
            ? 'message user-message bg-primary text-white p-3 rounded'
            : 'message bot-message bg-light text-dark p-3 rounded';
        
        if (isUser) {
            messageContent.innerHTML = `
                <p class="mb-1">${escapeHtml(message)}</p>
                <small class="text-white-50 d-block">${formatTime(new Date())}</small>
            `;
        } else {
            messageContent.innerHTML = `
                <div class="d-flex align-items-start">
                    <i data-feather="heart" class="text-primary me-2 mt-1" style="width: 16px; height: 16px;"></i>
                    <div>
                        <p class="mb-1">${escapeHtml(message)}</p>
                        <small class="text-muted">${formatTime(new Date())}</small>
                    </div>
                </div>
            `;
        }
        
        messageDiv.appendChild(messageContent);
        messageWrapper.appendChild(messageDiv);
        chatMessages.appendChild(messageWrapper);
        
        // Re-initialize feather icons
        feather.replace();
    }
    
    // Utility functions
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    function formatTime(date) {
        return date.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    }
    
    // Emotion info modal
    const emotionInfoModal = document.getElementById('emotionInfoModal');
    if (emotionInfoModal && !localStorage.getItem('emotionInfoSeen')) {
        // Show emotion info modal on first visit
        setTimeout(() => {
            const modal = new bootstrap.Modal(emotionInfoModal);
            modal.show();
            localStorage.setItem('emotionInfoSeen', 'true');
        }, 2000);
    }
    
    // Auto-resize textarea for multiline messages
    if (messageInput) {
        messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
    }
    
    // Add typing indicator (simulated)
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'message-wrapper mb-3';
        typingDiv.innerHTML = `
            <div class="d-flex">
                <div class="message bot-message bg-light text-dark p-3 rounded">
                    <div class="d-flex align-items-center">
                        <i data-feather="heart" class="text-primary me-2" style="width: 16px; height: 16px;"></i>
                        <div class="typing-dots">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        if (chatMessages) {
            chatMessages.appendChild(typingDiv);
            scrollToBottom();
            feather.replace();
        }
    }
    
    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    // Add CSS for typing animation
    const style = document.createElement('style');
    style.textContent = `
        .typing-dots {
            display: flex;
            gap: 2px;
        }
        
        .typing-dots span {
            width: 4px;
            height: 4px;
            background-color: var(--bs-secondary);
            border-radius: 50%;
            animation: typing 1.4s infinite ease-in-out;
        }
        
        .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
        .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes typing {
            0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
            40% { transform: scale(1); opacity: 1; }
        }
    `;
    document.head.appendChild(style);
});
