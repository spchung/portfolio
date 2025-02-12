'use client';
import { useState, useRef, useEffect } from "react";

const endpoint = process.env.NEXT_PUBLIC_API_URL

export default function Chat() {
  const [messages, setMessages] = useState([
    { role: "bot", content: "Hello! How can I help you today?" },
  ]);
  const [input, setInput] = useState("");
  const [tokenCount, setTokenCount] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, newMessage]);
    setInput("");
    
    // request chat
    const botMessage = { role: "bot", content: "..." };
    setMessages((prev) => [...prev, botMessage]);

    try {
        const response = await fetch("http://127.0.0.1:8000/api/v1/ecommerce-rag/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: input }),
        });
  
        if (!response.body) throw new Error("No response body");
  
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let botResponse = "";
  
        while (true) {
          // parse incoming chunks
          const { value, done } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          console.log(chunk);
          if (chunk.startsWith("event: metadata")) {
            
            console.log(chunk);

            const match = chunk.match(/data: (.*)/);
            if (match) {
              const metadata = JSON.parse(match[1]);
              setTokenCount(metadata.tokens_used);
            }
            continue;
          }
          
          botResponse += chunk;
  
          setMessages((prev) =>
            prev.map((msg, index) =>
              index === prev.length - 1 ? { ...msg, content: botResponse } : msg
            )
          );
        }
      } catch (error) {
        console.error("Error receiving stream:", error);
      }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-col h-screen bg-gray-100 p-4">
      <h1 className="absolute top-1 right-1 text-2xl font-semibold bg-red-400">MetaData: {tokenCount}</h1>
      <div className="flex-1 overflow-y-auto space-y-2 p-4 bg-white rounded-lg shadow-md">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`p-3 rounded-lg max-w-xs ${
              msg.role === "user" ? 
                "bg-blue-500 text-white ml-auto" : 
                "bg-gray-200 text-gray-900"
            }`}
          >
            {msg.content}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="mt-4 flex">
        <input
          type="text"
          className="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Type a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button
          className="ml-2 bg-blue-500 text-white p-2 rounded-lg hover:bg-blue-600"
          onClick={sendMessage}
        >
          Send
        </button>
      </div>
    </div>
  );
}
