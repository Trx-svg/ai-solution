document.getElementById('chatIcon').addEventListener('click', function() {
    document.getElementById('chatContainer').style.display = 'block';
    this.style.display = 'none';
});

document.getElementById('closeChat').addEventListener('click', function() {
    document.getElementById('chatContainer').style.display = 'none';
    document.getElementById('chatIcon').style.display = 'flex';
});

function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value;
    if (!message) return;

    // Add your message sending logic here
    input.value = '';
}

// Handle Enter key
document.getElementById('messageInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});