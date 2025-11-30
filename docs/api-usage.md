# Quivr API Usage Guide for External Brain Querying

This guide explains how to use the Quivr API to query a brain externally. It covers authentication, required endpoints, and provides example code.

## Authentication

The Quivr API uses Bearer token authentication. There are two ways to authenticate:

1. **API Key**: Create an API key through the Quivr web interface (Settings > Quivr API Key) and use it as a Bearer token.
2. **JWT Token**: Obtain a JWT token by logging in through the authentication endpoints.

For external API usage, the API key method is recommended as it's simpler and doesn't expire as quickly.

### Using the API Key

Include the API key in the `Authorization` header of your requests:

```
Authorization: Bearer YOUR_API_KEY
```

## Required Endpoints

To query a brain externally, you'll need to use the following endpoints:

### 1. Create a Chat

Before querying a brain, you need to create a chat:

```
POST /chat
```

Request body:
```json
{
  "name": "External API Chat",
  "brain_id": "YOUR_BRAIN_ID"
}
```

Response:
```json
{
  "chat_id": "CHAT_ID",
  "name": "External API Chat"
}
```

### 2. Query the Brain

Once you have a chat, you can query the brain using one of these endpoints:

#### Standard Query (Non-streaming)

```
POST /chat/{chat_id}/question?brain_id=YOUR_BRAIN_ID
```

Request body:
```json
{
  "question": "Your question here"
}
```

Response:
```json
{
  "answer": "The answer to your question",
  "message_id": "MESSAGE_ID",
  "chat_id": "CHAT_ID"
}
```

#### Streaming Query

```
POST /chat/{chat_id}/question/stream?brain_id=YOUR_BRAIN_ID
```

Request body:
```json
{
  "question": "Your question here"
}
```

Response: A streaming response with chunks of the answer.

## Example Usage

Here's a Python example demonstrating how to query a brain externally:

```python
# pip install requests  # Uncomment and run this if you don't have requests installed
import requests

# Configuration
API_URL = "https://your-quivr-instance.com"  # Replace with your Quivr instance URL
API_KEY = "your_api_key"  # Replace with your API key
BRAIN_ID = "your_brain_id"  # Replace with your brain ID

# Headers for authentication
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Step 1: Create a chat
create_chat_response = requests.post(
    f"{API_URL}/chat",
    headers=headers,
    json={
        "name": "External API Chat",
        "brain_id": BRAIN_ID
    }
)

if create_chat_response.status_code != 200:
    print(f"Error creating chat: {create_chat_response.text}")
    exit(1)

chat_data = create_chat_response.json()
chat_id = chat_data["chat_id"]
print(f"Created chat with ID: {chat_id}")

# Step 2: Query the brain
question = "What is the capital of France?"
query_response = requests.post(
    f"{API_URL}/chat/{chat_id}/question?brain_id={BRAIN_ID}",
    headers=headers,
    json={
        "question": question
    }
)

if query_response.status_code != 200:
    print(f"Error querying brain: {query_response.text}")
    exit(1)

answer_data = query_response.json()
print(f"Question: {question}")
print(f"Answer: {answer_data['answer']}")
```

## Streaming Example

For streaming responses, you can use this Python example:

```python
# pip install requests  # Uncomment and run this if you don't have requests installed
import requests

# Configuration
API_URL = "https://your-quivr-instance.com"  # Replace with your Quivr instance URL
API_KEY = "your_api_key"  # Replace with your API key
BRAIN_ID = "your_brain_id"  # Replace with your brain ID

# Headers for authentication
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Step 1: Create a chat
create_chat_response = requests.post(
    f"{API_URL}/chat",
    headers=headers,
    json={
        "name": "External API Chat",
        "brain_id": BRAIN_ID
    }
)

if create_chat_response.status_code != 200:
    print(f"Error creating chat: {create_chat_response.text}")
    exit(1)

chat_data = create_chat_response.json()
chat_id = chat_data["chat_id"]
print(f"Created chat with ID: {chat_id}")

# Step 2: Query the brain with streaming
question = "What is the capital of France?"
with requests.post(
    f"{API_URL}/chat/{chat_id}/question/stream?brain_id={BRAIN_ID}",
    headers=headers,
    json={
        "question": question
    },
    stream=True
) as response:
    print(f"Question: {question}")
    print("Answer: ", end="", flush=True)
    
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            print(chunk.decode('utf-8'), end="", flush=True)
    
    print()  # Final newline
```

## How to Get Your Brain ID

To use the Quivr API, you need to know the ID of the brain you want to query. Here's how to get it:

### Method 1: Using the API

You can retrieve all your brains and their IDs by making a GET request to the `/brains/` endpoint:

```python
import requests

API_URL = "https://your-quivr-instance.com"  # Replace with your Quivr instance URL
API_KEY = "your_api_key"  # Replace with your API key

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

response = requests.get(f"{API_URL}/brains/", headers=headers)
brains = response.json().get("brains", [])

for brain in brains:
    print(f"Brain ID: {brain['id']}")
    print(f"Name: {brain['name']}")
    print("-" * 30)
```

### Method 2: Using the Web Interface

1. Log in to your Quivr web interface
2. Navigate to your list of brains
3. Select the brain you want to use
4. The brain ID is typically visible in the URL when viewing a specific brain (e.g., `https://your-quivr-instance.com/brain/{brain_id}`)

## JavaScript Streaming Example for Web UI Chat

To create a web UI chat interface that uses the Quivr API's streaming functionality, you can use the following JavaScript example. This example demonstrates how to handle streaming responses and display them in real-time.

### Basic JavaScript Implementation

```javascript
// Configuration
const API_URL = "https://your-quivr-instance.com";  // Replace with your Quivr instance URL
const API_KEY = "your_api_key";  // Replace with your API key
const BRAIN_ID = "your_brain_id";  // Replace with your brain ID

// Headers for authentication
const headers = {
  "Authorization": `Bearer ${API_KEY}`,
  "Content-Type": "application/json"
};

// Step 1: Create a chat session
async function createChat() {
  try {
    const response = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({
        name: "Web UI Streaming Chat",
        brain_id: BRAIN_ID
      })
    });
    
    if (!response.ok) {
      throw new Error(`Error creating chat: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.chat_id;
  } catch (error) {
    console.error("Failed to create chat:", error);
    throw error;
  }
}

// Step 2: Stream a question using Fetch API
async function streamQuestion(chatId, question) {
  try {
    // Make the streaming request
    const response = await fetch(`${API_URL}/chat/${chatId}/question/stream?brain_id=${BRAIN_ID}`, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({ question }),
    });
    
    if (!response.ok) {
      throw new Error(`Error: ${response.status} ${response.statusText}`);
    }
    
    // Get the reader from the response body stream
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let result = '';
    
    // Function to process the stream chunks
    async function processStream() {
      try {
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) {
            console.log("Stream complete");
            break;
          }
          
          // Decode the chunk and append to result
          const chunk = decoder.decode(value, { stream: true });
          result += chunk;
          
          // Update the UI with the latest chunk
          document.getElementById('response-container').textContent = result;
        }
      } catch (error) {
        console.error("Error reading stream:", error);
      }
    }
    
    // Start processing the stream
    await processStream();
    return result;
  } catch (error) {
    console.error("Stream request failed:", error);
    throw error;
  }
}

// Main function to handle the chat
async function handleChat() {
  try {
    // Create a chat session
    const chatId = await createChat();
    
    // Get the question from the input field
    const question = document.getElementById('question-input').value;
    
    // Stream the question and display the response
    await streamQuestion(chatId, question);
  } catch (error) {
    console.error("Chat handling failed:", error);
  }
}
```

### Integrating into a Web UI Chat Interface

To integrate the streaming functionality into a web UI chat interface, you need to:

1. **Create a chat container** to display messages
2. **Add a typing indicator** to show when the assistant is generating a response
3. **Update the UI in real-time** as chunks of the response are received

Here's a simplified example of how to structure your HTML:

```html
<div id="chat-container">
  <!-- Messages will appear here -->
</div>

<div class="input-group">
  <input type="text" id="question-input" placeholder="Ask something...">
  <button id="submit-button" onclick="handleChat()">Send</button>
</div>

<div id="response-container"></div>
```

And here's how to update the UI with each chunk:

```javascript
// Function to add a message to the chat container
function addMessageToChat(message, isUser = false) {
  const chatContainer = document.getElementById('chat-container');
  const messageElement = document.createElement('div');
  messageElement.className = isUser ? 'user-message' : 'assistant-message';
  messageElement.textContent = message;
  chatContainer.appendChild(messageElement);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Modified streamQuestion function to update the UI
async function streamQuestion(chatId, question) {
  // Add the user's question to the chat
  addMessageToChat(question, true);
  
  // Create a message element for the assistant's response
  const chatContainer = document.getElementById('chat-container');
  const responseElement = document.createElement('div');
  responseElement.className = 'assistant-message';
  responseElement.id = 'streaming-response';
  chatContainer.appendChild(responseElement);
  
  try {
    const response = await fetch(`${API_URL}/chat/${chatId}/question/stream?brain_id=${BRAIN_ID}`, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({ question }),
    });
    
    if (!response.ok) {
      throw new Error(`Error: ${response.status} ${response.statusText}`);
    }
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let result = '';
    
    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        break;
      }
      
      const chunk = decoder.decode(value, { stream: true });
      result += chunk;
      
      // Update the streaming response element
      document.getElementById('streaming-response').textContent = result;
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    return result;
  } catch (error) {
    console.error("Stream request failed:", error);
    document.getElementById('streaming-response').textContent = `Error: ${error.message}`;
    throw error;
  }
}
```

### Complete Example

For a complete working example with styling, error handling, and a fully functional chat interface, see the `streaming_demo.html` file in the `testing` directory. This example demonstrates:

1. Creating a chat session
2. Sending questions to the Quivr API
3. Displaying streaming responses in real-time
4. Handling errors and providing user feedback
5. Maintaining chat history

## Notes

1. API keys are valid for the current year only, as per the API key service implementation.
2. For production use, consider implementing proper error handling and retries.
3. The Quivr API documentation is available at `/docs` when running the Quivr instance.
4. When implementing a streaming interface, make sure to handle network errors and reconnection gracefully.
5. The streaming endpoint returns plain text chunks, not JSON, so you need to handle the response accordingly.