document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const personaSelect = document.getElementById('persona');
    const languageSelect = document.getElementById('language');
    const sendButton = document.getElementById('send-button');

    // --- UTILITY FUNCTIONS ---

    /**
     * Appends a message to the chat window.
     * @param {string} sender - 'user' or 'bot'
     * @param {string} text - The message text.
     * @param {string|null} imageUrl - Optional URL for an image to display.
     */
    function appendMessage(sender, text, imageUrl = null) {
        const messageWrapper = document.createElement('div');
        const messageContent = document.createElement('div');
        
        // Sanitize text before inserting
        const sanitizedText = text.replace(/</g, "&lt;").replace(/>/g, "&gt;");

        if (sender === 'user') {
            messageWrapper.className = 'flex justify-end items-start gap-3';
            messageContent.className = 'bg-blue-600 text-white p-4 rounded-lg rounded-br-none max-w-xl shadow';
            messageContent.innerHTML = `<p>${sanitizedText}</p>`;
            
            const userAvatar = document.createElement('div');
            userAvatar.className = 'bg-gray-300 text-gray-700 p-2 rounded-full h-10 w-10 flex items-center justify-center font-bold text-lg flex-shrink-0';
            userAvatar.textContent = 'You';

            messageWrapper.appendChild(messageContent);
            messageWrapper.appendChild(userAvatar);

        } else { // Bot message
            messageWrapper.className = 'flex items-start gap-3';
            messageContent.className = 'bg-gray-200 text-gray-800 p-4 rounded-lg rounded-tl-none max-w-xl shadow';
            
            let htmlContent = `<p>${sanitizedText.replace(/\n/g, '<br>')}</p>`;

            // If an image URL is provided, add it
            if (imageUrl) {
                htmlContent += `
                    <div class="mt-4 border-t border-gray-300 pt-3">
                        <img src="${imageUrl}" alt="Generated Chart" class="rounded-lg shadow-md w-full" />
                    </div>
                `;
            }
            messageContent.innerHTML = htmlContent;
            
            const botAvatar = document.createElement('div');
            botAvatar.className = 'bg-blue-500 text-white p-2 rounded-full h-10 w-10 flex items-center justify-center font-bold text-lg flex-shrink-0';
            botAvatar.textContent = 'JV';
            
            messageWrapper.appendChild(botAvatar);
            messageWrapper.appendChild(messageContent);
        }

        chatMessages.appendChild(messageWrapper);
        chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll
    }
    
    /**
     * Shows a loading indicator for the bot's response.
     */
    function showLoadingIndicator() {
        const loadingWrapper = document.createElement('div');
        loadingWrapper.id = 'loading-indicator';
        loadingWrapper.className = 'flex items-start gap-3';
        
        const botAvatar = document.createElement('div');
        botAvatar.className = 'bg-blue-500 text-white p-2 rounded-full h-10 w-10 flex items-center justify-center font-bold text-lg flex-shrink-0';
        botAvatar.textContent = 'JV';

        const loadingDots = document.createElement('div');
        loadingDots.className = 'bg-gray-200 text-gray-800 p-4 rounded-lg rounded-tl-none max-w-xl shadow flex items-center space-x-2';
        loadingDots.innerHTML = `
            <span class="block w-3 h-3 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0s;"></span>
            <span class="block w-3 h-3 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s;"></span>
            <span class="block w-3 h-3 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.4s;"></span>
        `;
        
        loadingWrapper.appendChild(botAvatar);
        loadingWrapper.appendChild(loadingDots);
        chatMessages.appendChild(loadingWrapper);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    /**
     * Removes the loading indicator.
     */
    function removeLoadingIndicator() {
        const indicator = document.getElementById('loading-indicator');
        if (indicator) {
            indicator.remove();
        }
    }


    // --- EVENT LISTENERS ---

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const prompt = userInput.value.trim();

        if (!prompt) {
            return;
        }

        // Disable form
        userInput.value = '';
        userInput.disabled = true;
        sendButton.disabled = true;

        appendMessage('user', prompt);
        showLoadingIndicator();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt: prompt,
                    persona: personaSelect.value,
                    language: languageSelect.value
                }),
            });

            removeLoadingIndicator();

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.text || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            appendMessage('bot', data.text, data.imageUrl);

        } catch (error) {
            removeLoadingIndicator();
            console.error('Error:', error);
            appendMessage('bot', `Sorry, an error occurred: ${error.message}`);
        } finally {
            // Re-enable form
            userInput.disabled = false;
            sendButton.disabled = false;
            userInput.focus();
        }
    });
});

