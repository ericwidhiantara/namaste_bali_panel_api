let selectedUser = null;
let userLoginId = null;
const userListElement = document.getElementById("userList");
const chatMessagesElement = document.getElementById("chatMessages");
const loggedInUserInfoElement = document.getElementById("loggedInUserInfo");

let messageSocket = null;

const messageInput = document.getElementById("messageInput");

messageInput.addEventListener("keypress", function (event) {
  if (event.key === "Enter") {
    sendMessage();
  }
});

async function fetchUsers() {
  try {
    const response = await fetch("http://localhost:8000/users", {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
      },
    });
    const users = await response.json();
    renderUserList(users);
    const onlineSocket = new WebSocket("ws://localhost:8000/ws/" + userLoginId);
    onlineSocket.onopen = function (event) {
      console.log(userLoginId + " Online WebSocket connected.");
      const online = {
        user_id: userLoginId, // Assuming sender_id is available
      };
      // Send message through message WebSocket connection
      onlineSocket.send(JSON.stringify(online));
      // Clear input field after sending message
    };

    onlineSocket.onmessage = function (event) {
      // Handle online status updates
      const data = JSON.parse(event.data);
      console.log("ini on message online data", data);
      data.forEach((user) => {
        console.log(user, "is online");
        updateOnlineStatus(user, true);
      });
    };
  } catch (error) {
    console.error("Error fetching users:", error);
  }
}

function renderUserList(users) {
  userListElement.innerHTML = "";
  users.forEach((user) => {
    if (user.id != userLoginId) {
      const userElement = document.createElement("li");
      userElement.classList.add("person");
      userElement.setAttribute("data-chat", user.id);

      const imgElement = document.createElement("img");
      imgElement.src = "https://via.placeholder.com/50x50";
      imgElement.alt = "";
      userElement.appendChild(imgElement);

      const nameElement = document.createElement("span");
      nameElement.classList.add("name");
      nameElement.textContent = user.username;
      userElement.appendChild(nameElement);

      const timeElement = document.createElement("span");
      timeElement.classList.add("time");
      timeElement.textContent = "2:09 PM"; // Assuming you want a static time for now
      userElement.appendChild(timeElement);

      const previewElement = document.createElement("span");
      previewElement.classList.add("preview");
      previewElement.textContent = "I was wondering..."; // Sample preview text
      userElement.appendChild(previewElement);

      userElement.onclick = () => selectUser(user, userElement);

      userListElement.appendChild(userElement);
    }
  });
}

async function fetchUserMessages(selectedUserId) {
  try {
    const response = await fetch(
      `http://localhost:8000/messages?sender_id=${userLoginId}&recipient_id=${selectedUserId}`
      , {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
      },
    }
    );
    const messages = await response.json();
    renderUserMessages(messages);
  } catch (error) {
    console.error("Error fetching user messages:", error);
  }
}

function renderUserMessages(messages) {
  chatMessagesElement.innerHTML = ""; // Clear previous messages

  const messagesElement = document.getElementById("chatMessages");

  messages.forEach((message) => {
    const messageElement = document.createElement("div");
    // messageElement.classList.add("message");

    if (message.sender.id === userLoginId) {
      messageElement.classList.add("bubble", "me");
      messageElement.textContent = message.message;
      //   messageElement.appendChild(bubbleElement);
    } else {
      messageElement.classList.add("bubble", "you");
      messageElement.textContent = `${message.message}`;
    }

    messagesElement.appendChild(messageElement);
  });
}

function selectUser(user, userElement) {
  if (selectedUser) {
    selectedUserElement.classList.remove("active");
  }
  selectedUser = user;
  selectedUserElement = userElement;
  selectedUserElement.classList.add("active");
  renderChatInterface();
}

function closeWebSocket() {
  if (messageSocket && messageSocket.readyState === WebSocket.OPEN) {
    messageSocket.close();
  }
}

function renderChatInterface() {
  recipientQuerySelector = document.getElementById("recipient");
  //   chatMessagesElement.innerHTML = `<h3>Chat with ${selectedUser.username}</h3>`;
  recipientQuerySelector.innerHTML = `<span>To: <span class='name'>${selectedUser.username}</span></span>`;

  // Close existing WebSocket connection if any
  closeWebSocket();

  messageSocket = new WebSocket(
    "ws://localhost:8000/join/" + userLoginId + "/" + selectedUser.id
  );

  // Set event handler for when the WebSocket connection is opened
  messageSocket.onopen = function (event) {
    console.log("Message WebSocket connected.");
    // Additional logic can be added here if needed
  };

  // Set event handler for incoming messages
  messageSocket.onmessage = function (event) {
    const messageBox = document.getElementById("chatMessages");
    const message = JSON.parse(event.data);

    if (
      message.sender.id === userLoginId ||
      message.recipient.id === userLoginId
    ) {
      console.log("message ", message);
      const messageElement = document.createElement("div");

      // Get the selected sender's ID from the dropdown menu
      const selectedSenderId = userLoginId;
      displayMessage(
        message.sender.id === selectedSenderId,
        `${message.message}`
      );

      // Append the message element to the message box
      messageBox.appendChild(messageElement);

      // Scroll to the bottom of the message box
      messageBox.scrollTop = messageBox.scrollHeight;
    }
  };

  // Set event handler for WebSocket errors
  messageSocket.onerror = function (event) {
    console.error("WebSocket error:", event);
  };

  // Log a message to indicate that the chat with the selected user is opened
  console.log("Opened chat with user:", selectedUser.username);
  fetchUserMessages(selectedUser.id); // Fetch messages for the selected user
}

function sendMessage() {
  const messageInput = document.getElementById("messageInput");
  const message = messageInput.value.trim();
  if (message === "") return;
  // Assuming you have a WebSocket connection established
  // and the `selectedUser` is set
  // Send the message with the format: recipient_id:message_content
  const formattedMessage = `${selectedUser.id}:${message}`;
  // Send the message over WebSocket
  // Construct message object
  const messageData = {
    sender_id: userLoginId, // Assuming sender_id is available
    recipient_id: selectedUser.id,
    message: message,
  };
  // Send message through message WebSocket connection
  messageSocket.send(JSON.stringify(messageData));
  // For the demo, we'll just display it in the chatMessagesElement
  // displayMessage(`You: ${message}`);
  messageInput.value = "";
}

function displayMessage(isSender, message) {
  const messageElement = document.createElement("div");
  messageElement.textContent = message;
  messageElement.classList.add("bubble"); // Add a class for styling
  if (isSender) {
    messageElement.classList.add("me");
  } else {
    messageElement.classList.add("you");
  }

  chatMessagesElement.appendChild(messageElement);
  // Scroll to the bottom of the chat messages
  chatMessagesElement.scrollTop = chatMessagesElement.scrollHeight;
}

// Fetch users when the page loads
window.onload = () => {
  fetchUsers();
  const accessToken = localStorage.getItem("accessToken");
  if (accessToken) {
    const decodedToken = parseJwt(accessToken);
    const userName = decodedToken.user.username;
    userLoginId = decodedToken.user.id;
    loggedInUserInfoElement.textContent = `Logged in as: ${userName}`;
  }
};

// Function to parse JWT token
function parseJwt(token) {
  const base64Url = token.split(".")[1];
  const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
  const jsonPayload = decodeURIComponent(
    atob(base64)
      .split("")
      .map((c) => {
        return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
      })
      .join("")
  );

  return JSON.parse(jsonPayload);
}
