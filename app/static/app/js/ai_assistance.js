
// Mở/Đóng cửa sổ chat
function toggleChatWindow() {
  const chatWindow = document.getElementById("chatWindow");
  chatWindow.style.display = chatWindow.style.display === "flex" ? "none" : "flex";
}

// Gửi tin nhắn
function sendMessage() {
  const chatInput = document.getElementById("chatInput");
  const chatBody = document.getElementById("chatBody");

  const userMessage = chatInput.value.trim();
  if (!userMessage) return;

  // Hiển thị tin nhắn người dùng
  const userDiv = document.createElement("div");
  userDiv.className = "message user";
  userDiv.textContent = userMessage;
  chatBody.appendChild(userDiv);

  // Gửi yêu cầu đến API
  fetch("/api/chat/", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      'X-CSRFToken':csrftoken,
    },
    body: `message=${encodeURIComponent(userMessage)}`,
  })
  .then(response => response.json())
  .then(data => {
    // Hiển thị phản hồi từ bot
    const botDiv = document.createElement("div");
    botDiv.className = "message bot";
    botDiv.innerHTML = data.reply || "Bot không phản hồi.";
    chatBody.appendChild(botDiv);

    // Cuộn xuống cuối
    chatBody.scrollTop = chatBody.scrollHeight;
  })
  .catch(error => {
    console.error("Error:", error);
  });

  // Xóa nội dung input
  chatInput.value = "";
}
