let token = localStorage.getItem("token");

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
            // Show success message
            document.getElementById("register-error").style.color = "var(--success-color)";
            document.getElementById("register-error").innerText = "Registration successful! Please login.";
            
            // Clear registration form
            document.getElementById("register-username").value = "";
            document.getElementById("register-email").value = "";
            document.getElementById("register-password").value = "";
            
            // Switch to login tab after successful registration
            setTimeout(() => {
                showTab('login');
            }, 1500);
        } else {
            const data = await response.json();
            document.getElementById("register-error").innerText = JSON.stringify(data);
        }
    } catch (error) {
        console.error(error);
        document.getElementById("register-error").innerText = "An error occurred during registration.";
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

            document.getElementById("auth-section").style.opacity = "0";
            setTimeout(() => {
                document.getElementById("auth-section").style.display = "none";
                document.getElementById("message-section").style.display = "block";
                setTimeout(() => {
                    document.getElementById("message-section").style.opacity = "1";
                }, 50);
            }, 300);
        } else {
            const data = await response.json();
            document.getElementById("login-error").innerText = JSON.stringify(data);
        }
    } catch (error) {
        console.error(error);
        document.getElementById("login-error").innerText = "An error occurred during login.";
    }
}

async function sendMessage() {
    const recipientUsername = document.getElementById("recipient").value;
    const content = document.getElementById("message-content").value;

    try {
        // First, verify the recipient exists
        const userResponse = await fetch(`http://127.0.0.1:8000/api/auth/users/get_by_username/?username=${recipientUsername}`, {
            headers: { 
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
        });

        if (!userResponse.ok) {
            document.getElementById("message-error").innerText = "Recipient not found.";
            return;
        }

        const userData = await userResponse.json();
        const recipientId = userData.id;

        // Then send the message
        const response = await fetch("http://127.0.0.1:8000/api/messages/send/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
            },
            body: JSON.stringify({
                recipient: recipientId,
                content: content
            }),
        });

        if (response.ok) {
            // Clear form and show success message
            document.getElementById("recipient").value = "";
            document.getElementById("message-content").value = "";
            document.getElementById("message-error").style.color = "var(--success-color)";
            document.getElementById("message-error").innerText = "Message sent successfully!";
            
            // Reset character count
            document.querySelector('.char-count').textContent = "0/500";
            
            // Clear success message after 3 seconds
            setTimeout(() => {
                document.getElementById("message-error").innerText = "";
            }, 3000);
        } else {
            const data = await response.json();
            document.getElementById("message-error").innerText = JSON.stringify(data);
        }
    } catch (error) {
        console.error(error);
        document.getElementById("message-error").innerText = "An error occurred while sending the message.";
    }
}

function logout() {
    localStorage.removeItem("token");
    token = null;
    
    // Reset forms
    document.getElementById("login-username").value = "";
    document.getElementById("login-password").value = "";
    document.getElementById("recipient").value = "";
    document.getElementById("message-content").value = "";
    document.querySelector('.char-count').textContent = "0/500";
    
    // Show auth section and hide message section with animation
    document.getElementById("message-section").style.opacity = "0";
    setTimeout(() => {
        document.getElementById("message-section").style.display = "none";
        document.getElementById("auth-section").style.display = "block";
        document.getElementById("auth-section").style.opacity = "1";
    }, 300);
}

// Check token on page load
document.addEventListener('DOMContentLoaded', () => {
    if (token) {
        document.getElementById("auth-section").style.display = "none";
        document.getElementById("message-section").style.display = "block";
        document.getElementById("message-section").style.opacity = "1";
    }
});
