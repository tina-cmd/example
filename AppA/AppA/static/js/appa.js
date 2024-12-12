let token = localStorage.getItem("token");

document.addEventListener("DOMContentLoaded", function () {
    if (token) {
        // User is already logged in
        document.getElementById("auth-section").style.display = "none";
        document.getElementById("message-section").style.display = "block";
        document.getElementById("logout-btn").style.display = "block";
        loadInbox();
    }
});

async function register() {
    const username = document.getElementById("register-username").value;
    const email = document.getElementById("register-email").value;
    const password = document.getElementById("register-password").value;

    try {
        const response = await fetch("http://127.0.0.1:8000/api/auth/register/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ username, email, password }),
        });

        if (response.ok) {
            alert("Registration successful! You can now log in.");
        } else {
            const data = await response.json();
            document.getElementById("register-error").innerText = JSON.stringify(data);
        }
    } catch (error) {
        console.error(error);
        document.getElementById("register-error").innerText = "An error occurred.";
    }
}

async function login() {
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    try {
        const response = await fetch("http://127.0.0.1:8000/api/auth/login/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ username, password }),
        });

        if (response.ok) {
            const data = await response.json();
            token = data.access;
            localStorage.setItem("token", token);

            document.getElementById("auth-section").style.display = "none";
            document.getElementById("message-section").style.display = "block";
            document.getElementById("logout-btn").style.display = "block";

            // Initial load of inbox
            await refreshInbox();

            // Set up auto-refresh every 30 seconds
            window.inboxInterval = setInterval(refreshInbox, 30000);
        } else {
            const data = await response.json();
            document.getElementById("login-error").innerText = JSON.stringify(data);
        }
    } catch (error) {
        console.error(error);
        document.getElementById("login-error").innerText = "An error occurred.";
    }
}

async function sendMessage() {
    // Declare recipientUsername and content first
    const recipientUsername = document.getElementById("recipient").value;
    const content = document.getElementById("message-content").value;

    try {
        // Ensure the recipient username is provided
        if (!recipientUsername) {
            document.getElementById("message-error").innerText = "Recipient username is required.";
            return;
        }

        // Fetch the recipient data by username
        const userResponse = await fetch(`http://127.0.0.1:8000/api/messages/users/get_by_username/?username=${recipientUsername}`, {
            headers: {
                "Authorization": `Bearer ${token}`,
            },
        });

        // If the user is not found, handle the error
        if (!userResponse.ok) {
            const userData = await userResponse.json();
            document.getElementById("message-error").innerText = userData.detail || "Recipient not found.";
            return;
        }

        // Extract the recipient ID from the response
        const userData = await userResponse.json();
        const recipientId = userData.id;

        // Send the message to the recipient
        const response = await fetch("http://127.0.0.1:8000/api/messages/send/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
            },
            body: JSON.stringify({
                recipient: recipientId,  // Pass the recipient's ID
                content,                 // Pass the message content
            }),
        });

        // Handle success or failure
        if (response.ok) {
            alert("Message sent!");
            loadInbox();  // Reload the inbox after sending the message
        } else {
            const data = await response.json();
            document.getElementById("message-error").innerText = JSON.stringify(data);
        }
    } catch (error) {
        console.error(error);
        document.getElementById("message-error").innerText = "An error occurred while sending the message.";
    }
}

async function loadInbox() {
    if (!token) {
        console.error("Token is missing or expired. Please log in again.");
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:8000/api/messages/inbox/", {
            headers: {
                "Authorization": `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }

        const messages = await response.json();
        const inboxDiv = document.getElementById('inbox');
        const noMessagesDiv = document.getElementById('no-messages');
        
        // Update message count
        updateMessageCount(messages.length);

        if (messages.length === 0) {
            inboxDiv.style.display = 'none';
            noMessagesDiv.style.display = 'flex';
        } else {
            inboxDiv.style.display = 'block';
            noMessagesDiv.style.display = 'none';
            
            inboxDiv.innerHTML = messages.map(msg => `
                <div class="message-item">
                    <div class="message-header">
                        <span class="message-sender">From: ${msg.sender_username || 'Unknown'}</span>
                        <span class="message-time">${new Date(msg.timestamp).toLocaleString()}</span>
                    </div>
                    <div class="message-content">${msg.content}</div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading inbox:', error);
    }
}

async function refreshInbox() {
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.classList.add('refreshing');
        refreshBtn.disabled = true;
    }

    try {
        await loadInbox();
    } finally {
        if (refreshBtn) {
            refreshBtn.classList.remove('refreshing');
            refreshBtn.disabled = false;
        }
    }
}

function logout() {
    if (window.inboxInterval) {
        clearInterval(window.inboxInterval);
    }
    localStorage.removeItem("token");
    token = null;
    document.getElementById("auth-section").style.display = "block";
    document.getElementById("message-section").style.display = "none";
    document.getElementById("logout-btn").style.display = "none";
    
    // Clear the inbox
    const inboxDiv = document.getElementById("inbox");
    if (inboxDiv) {
        inboxDiv.innerHTML = '';
    }
}

// Add this function to update message count
function updateMessageCount(count) {
    const messageCount = document.getElementById('message-count');
    messageCount.textContent = `${count} ${count === 1 ? 'Message' : 'Messages'}`;
}

// Check token and set up auto-refresh on page load
document.addEventListener('DOMContentLoaded', () => {
    const savedToken = localStorage.getItem("token");
    if (savedToken) {
        token = savedToken;
        document.getElementById("auth-section").style.display = "none";
        document.getElementById("message-section").style.display = "block";
        document.getElementById("logout-btn").style.display = "block";
        
        // Initial load and set up auto-refresh
        refreshInbox();
        window.inboxInterval = setInterval(refreshInbox, 30000);
    }
});
