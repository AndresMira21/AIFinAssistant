document.addEventListener("DOMContentLoaded", () => {
    
    // 1. Calculator Tabs Logic
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");

    if (tabBtns.length > 0) {
        tabBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                // Remove active class from all
                tabBtns.forEach(b => b.classList.remove("active"));
                tabContents.forEach(c => c.classList.remove("active"));

                // Add active to clicked
                btn.classList.add("active");
                const targetId = btn.getAttribute("data-target");
                document.getElementById(targetId).classList.add("active");
            });
        });
    }

    // 2. Chatbot Logic
    const chatInput = document.getElementById("chat-input");
    const chatSendBtn = document.getElementById("chat-send");
    const chatHistory = document.getElementById("chat-history");

    if (chatInput && chatSendBtn && chatHistory) {
        
        const appendMessage = (text, sender) => {
            const msgDiv = document.createElement("div");
            msgDiv.classList.add("chat-msg");
            if (sender === "user") {
                msgDiv.classList.add("msg-user");
            } else {
                msgDiv.classList.add("msg-bot");
            }
            msgDiv.textContent = text;
            chatHistory.appendChild(msgDiv);
            
            // Scroll to bottom
            chatHistory.scrollTop = chatHistory.scrollHeight;
        };

        const sendMessage = async () => {
            const text = chatInput.value.trim();
            if (!text) return;

            // 1. Show user message
            appendMessage(text, "user");
            chatInput.value = "";
            chatInput.disabled = true;
            chatSendBtn.disabled = true;

            // 2. Fetch bot response
            try {
                // We assume CHAT_API_URL is available in the global scope (set in chat.html)
                const url = window.CHAT_API_URL || "/chatbot/api/";
                const response = await fetch(url, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ message: text })
                });

                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }

                const data = await response.json();
                
                if (data.error) {
                    appendMessage("Error: " + data.error, "bot");
                } else {
                    appendMessage(data.response, "bot");
                }
            } catch (error) {
                console.error("Chat error:", error);
                appendMessage("Ocurrió un error al contactar con el asistente.", "bot");
            } finally {
                chatInput.disabled = false;
                chatSendBtn.disabled = false;
                chatInput.focus();
            }
        };

        chatSendBtn.addEventListener("click", sendMessage);
        
        chatInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                sendMessage();
            }
        });
    }
});
