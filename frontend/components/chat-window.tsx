import React from "react";
import { Message } from "@/hooks/use-skincaregpt-chat";

interface ChatWindowProps {
  messages: Message[];
  messagesEndRef: React.RefObject<HTMLDivElement | null>;
  isInitialized: boolean;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ messages, messagesEndRef, isInitialized }) => {

  if (!isInitialized) {
    return (
      <div className="flex-1 overflow-y-auto space-y-2 p-4 bg-white rounded-lg shadow-md">
        <div className="flex justify-start">
          <div className="p-3 rounded-lg w-fit bg-gray-200 text-gray-900 max-w-xl">
            Loading...
          </div>
        </div>
        <div/>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto space-y-2 p-4 bg-white rounded-lg shadow-md">
      {messages.map((msg, index) => (
        <div
          key={index}
          className={`flex ${
            msg.role === "user" ? "justify-end" : "justify-start"
          }`}
        >
          <div
            className={`p-3 rounded-lg w-fit ${
              msg.role === "user"
                ? "bg-blue-500 text-white max-w-sm"
                : "bg-gray-200 text-gray-900 max-w-xl"
            }`}
          >
            {msg.content}
          </div>
        </div>
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatWindow;