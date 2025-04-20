// JavaScript to handle sending messages to the backend
document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.input-area');
    const sendButton = document.getElementById('send-btn');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');

    // Handle form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault(); // Prevent default form submission
        await sendMessage();
    });

    // Handle button click
    sendButton.addEventListener('click', async (e) => {
        e.preventDefault(); // Prevent default button behavior
        await sendMessage();
    });

    // Handle Enter key press
    userInput.addEventListener('keypress', async (e) => {
        if (e.key === 'Enter') {
            e.preventDefault(); // Prevent default Enter behavior
            await sendMessage();
        }
    });

    function addLoadingAnimation() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'loading';
        loadingDiv.innerHTML = `
            <div class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        chatBox.appendChild(loadingDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
        return loadingDiv;
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (message === "") return;

        // Add user message to chat box
        chatBox.innerHTML += `<div class="user-message"><strong>You:</strong> ${message}</div>`;
        
        // Add loading animation
        const loadingDiv = addLoadingAnimation();

        // Disable input and button while processing
        userInput.disabled = true;
        sendButton.disabled = true;

        // Send message to backend (Python/Flask)
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Remove loading animation
            loadingDiv.remove();
            
            // Format the response based on the format type
            let formattedReply = '';
            if (data.format.type === 'final_answer') {
                let formattedSources = ``;
                for (const source of data.sources) {
                    formattedSources += `<a href="${source}" target="_blank" class="source-link"><span style="text-decoration: none;"> - </span>${source}</a>`;
                }
                formattedReply = `
                    <div class="answer-content"><span class="assistant-label">Assistant: </span>${data.reply}</div>
                    ${data.format.show_sources ? `<span class="sources-label">Sources:</span><div class="sources-body">${formattedSources}</div>` : ''}
                    <div class>Is there anything else you would like to know?</div>
                `;
            } else if (data.format.type === 'clarifying_question') {
                formattedReply = `<div class="clarifying-question"><span class="assistant-label">Assistant: </span>${data.reply}</div>`;
            } else {
                formattedReply = `<div class="error-message"><span class="assistant-label">Assistant: </span>${data.reply}</div>`;
            }
            
            // Add bot response with formatted content
            chatBox.innerHTML += `<div class="bot-message">${formattedReply}</div>`;
        } catch (error) {
            console.error('Error:', error);
            // Remove loading animation
            loadingDiv.remove();
            chatBox.innerHTML += `<div class="bot-message"><strong>Assistant:</strong> Sorry, something went wrong. Please try again.</div>`;
        }

        // Clear input field and scroll to bottom
        userInput.value = '';
        userInput.disabled = false;
        sendButton.disabled = false;
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});