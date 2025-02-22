
"use client";
import { useChat } from "@/hooks/use-chat";
import ChatWindow from "@/components/chat-window";
import ChatInput from "@/components/chat-input";

const ChatPanel: React.FC = () => {
  const {
    messages,
    input,
    setInput,
    sendMessage,
    messagesEndRef,
  } = useChat();

  return (
    <div className="flex flex-col bg-gray-100 p-4 max-w-full w-full h-full overflow-y-auto">
      <ChatWindow messages={messages} messagesEndRef={messagesEndRef} />
      <ChatInput input={input} setInput={setInput} sendMessage={sendMessage} />
    </div>
  );
};

export default ChatPanel;
