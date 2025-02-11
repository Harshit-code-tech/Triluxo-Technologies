document.addEventListener("DOMContentLoaded", function() {
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const toggleDarkModeButton = document.getElementById("toggle-dark-mode");

    window.sendMessage = function() {
        const message = userInput.value.trim();
        if (message === "") return;

        // Append user message
        appendMessage("user", message);
        userInput.value = "";

        // Send message to Flask API
        fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            appendMessage("bot", data.response);
        })
        .catch(error => {
            appendMessage("bot", "Error: Unable to reach chatbot.");
            console.error("Error:", error);
        });
    };

    userInput.addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    toggleDarkModeButton.addEventListener("click", function() {
        document.body.classList.toggle("dark-mode");
        document.querySelector(".chat-container").classList.toggle("dark-mode");
    });

    function appendMessage(sender, text) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", sender);

        // Split text into paragraphs for better formatting
        const paragraphs = text.split("\n").filter(p => p.trim() !== "");
        paragraphs.forEach(paragraph => {
            const p = document.createElement("p");
            p.textContent = paragraph;
            messageDiv.appendChild(p);
        });

        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});