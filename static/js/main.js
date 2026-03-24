console.log("IAMath Chatbot Loaded - v2.1");

// GLOBAL STATE
let currentSessionId = null;

// INITIALIZATION
document.addEventListener("DOMContentLoaded", () => {
    // 1. Calculator Tabs Logic
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");

    if (tabBtns.length > 0) {
        tabBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                tabBtns.forEach(b => b.classList.remove("active"));
                tabContents.forEach(c => c.classList.remove("active"));
                btn.classList.add("active");
                const targetId = btn.getAttribute("data-target");
                const content = document.getElementById(targetId);
                if (content) content.classList.add("active");
            });
        });
    }

    // 2. Chatbot Sidebar & Inputs
    const newChatBtn = document.getElementById("new-chat-btn");
    if (newChatBtn) newChatBtn.addEventListener("click", startNewChat);

    const chatSendBtn = document.getElementById("chat-send");
    if (chatSendBtn) chatSendBtn.addEventListener("click", sendMessage);

    const chatInput = document.getElementById("chat-input");
    if (chatInput) {
        chatInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") sendMessage();
        });
    }

    // Initialize existing session clicks
    document.querySelectorAll(".session-item").forEach(item => {
        const sid = item.dataset.id;
        item.addEventListener("click", () => loadChatHistory(sid));
    });
});

// GLOBAL FUNCTIONS
async function loadChatHistory(sessionId) {
    const chatHistory = document.getElementById("chat-history");
    const currentChatTitle = document.getElementById("current-chat-title");
    if (!chatHistory || !currentChatTitle) return;

    try {
        const response = await fetch(`/chatbot/api/history/${sessionId}/`);
        const data = await response.json();
        if (data.history) {
            chatHistory.innerHTML = "";
            data.history.forEach(msg => appendMessage(msg.content, msg.role));
            currentSessionId = sessionId;
            currentChatTitle.textContent = data.title;
            
            // UI Update
            document.querySelectorAll(".session-item").forEach(i => i.classList.remove("active"));
            const activeItem = document.querySelector(`.session-item[data-id="${sessionId}"]`);
            if (activeItem) activeItem.classList.add("active");
        }
    } catch (err) {
        console.error("Error loading history:", err);
    }
}

async function deleteSession(sessionId) {
    if (!confirm("¿Eliminar este chat permanentemente?")) return;
    try {
        const response = await fetch(`/chatbot/api/delete/${sessionId}/`, { method: "POST" });
        const data = await response.json();
        if (data.status === "success") {
            const item = document.querySelector(`.session-item[data-id="${sessionId}"]`);
            if (item) item.remove();
            
            if (currentSessionId == sessionId) {
                location.reload(); 
            }
        }
    } catch (err) {
        console.error("Error deleting session:", err);
    }
}

function startNewChat() {
    const chatHistory = document.getElementById("chat-history");
    const currentChatTitle = document.getElementById("current-chat-title");
    currentSessionId = null;
    if (chatHistory) {
        chatHistory.innerHTML = `
            <div class="chat-msg msg-bot">
                ¡Nueva sesión iniciada! ¿En qué puedo ayudarte hoy?
            </div>
        `;
    }
    if (currentChatTitle) currentChatTitle.textContent = "Nuevo Chat";
    document.querySelectorAll(".session-item").forEach(i => i.classList.remove("active"));
}

function appendMessage(text, sender) {
    const chatHistory = document.getElementById("chat-history");
    if (!chatHistory) return;
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("chat-msg");
    msgDiv.classList.add(sender === "user" ? "msg-user" : "msg-bot");
    msgDiv.textContent = text;
    chatHistory.appendChild(msgDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

async function sendMessage() {
    const chatInput = document.getElementById("chat-input");
    const chatSendBtn = document.getElementById("chat-send");
    const sessionList = document.getElementById("session-list");
    const currentChatTitle = document.getElementById("current-chat-title");

    if (!chatInput || !chatSendBtn) return;

    const text = chatInput.value.trim();
    if (!text) return;

    appendMessage(text, "user");
    chatInput.value = "";
    chatInput.disabled = true;
    chatSendBtn.disabled = true;

    try {
        const response = await fetch("/chatbot/api/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text, session_id: currentSessionId })
        });

        const data = await response.json();
        if (data.error) {
            appendMessage("Error: " + data.error, "bot");
        } else {
            appendMessage(data.response, "bot");
            
            if (!currentSessionId) {
                currentSessionId = data.session_id;
                if (currentChatTitle) currentChatTitle.textContent = data.session_title;
                
                if (sessionList) {
                    const newItem = document.createElement("div");
                    newItem.className = "session-item active";
                    newItem.dataset.id = data.session_id;
                    newItem.innerHTML = `
                        <span class="session-title">${data.session_title}</span>
                        <button class="delete-session" onclick="event.stopPropagation(); deleteSession(${data.session_id})">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6L18 20a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"></path><path d="M10 11L10 17"></path><path d="M14 11L14 17"></path><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"></path></svg>
                        </button>
                    `;
                    newItem.addEventListener("click", () => loadChatHistory(data.session_id));
                    sessionList.prepend(newItem);
                }
            }
        }
    } catch (error) {
        console.error("Chat error:", error);
        appendMessage("Ocurrió un error al contactar con el asistente.", "bot");
    } finally {
        chatInput.disabled = false;
        chatSendBtn.disabled = false;
        chatInput.focus();
    }
}
