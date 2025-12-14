const chatBody = document.getElementById("chatBody");
const chatInput = document.getElementById("chat-input");
const chatSend = document.getElementById("chat-send");

chatSend.addEventListener("click", sendMessage);
chatInput.addEventListener("keypress", e => {
    if (e.key === "Enter") sendMessage();
});


// ==============================
// ⭐ HÀM ADD TIN NHẮN
// ==============================
function appendMessage(text, sender) {
    if (!text || text.trim() === "") return; // ⛔ Không append tin rỗng

    const div = document.createElement("div");
    div.className = `message ${sender}`;
    div.innerHTML = text;

    chatBody.appendChild(div);
    chatBody.scrollTop = chatBody.scrollHeight;
}

// ==============================
// ⭐ GỬI TIN NHẮN BÌNH THƯỜNG
// ==============================
function sendMessage() {
    let text = chatInput.value.trim();

    // ⛔ Chặn tin nhắn quá ngắn (".", "h", " ")
    if (!text || text.length < 2) {
        chatInput.value = "";
        return;
    }

    appendMessage(text, "user"); // hiển thị KH gửi, thêm tin nhắn vào giao diện chat.
    chatInput.value = "";

    fetch("/chat/gui/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ text: text })
    })
    .then(res => res.json())
    .then(data => {

        if (data.reply && data.reply.trim() !== "") {
            appendMessage(data.reply, "bot");
        }

    });
}

// ==============================
// ⭐ GỬI TIN NHẮN KHI BẤM MENU
// ==============================
function sendOption(option) {

    appendMessage(`<div class="option-click">${option}</div>`, "user");

    fetch("/chat/gui/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ text: option, quick: true })
    })
    .then(res => res.json())
    .then(data => {

        if (data.reply && data.reply.trim() !== "") {
            appendMessage(data.reply, "bot");
        }

    });
}

function getCookie(name) {
    let cookieValue = null;
    document.cookie.split(";").forEach(cookie => {
        cookie = cookie.trim();
        if (cookie.startsWith(name + "=")) {
            cookieValue = cookie.substring(name.length + 1);
        }
    });
    return cookieValue;
}


