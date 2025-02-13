import React from "react";
import { Message } from "@/hooks/use-chat";

interface ChatWindowProps {
  messages: Message[];
  messagesEndRef: React.RefObject<HTMLDivElement | null>;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ messages, messagesEndRef }) => {
  return (
    <div className="flex-1 overflow-y-auto space-y-2 p-4 bg-white rounded-lg shadow-md">
      {messages.map((msg, index) => (
        <div
          key={index}
          className={`p-3 rounded-lg max-w-xs ${
            msg.role === "user"
              ? "bg-blue-500 text-white ml-auto"
              : "bg-gray-200 text-gray-900"
          }`}
        >
          {msg.content}
        </div>
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatWindow;
