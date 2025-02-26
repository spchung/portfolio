
"use client";
import { useSkincareGPTChat } from "@/hooks/use-skincaregpt-chat";
import ChatWindow from "@/components/chat-window";
import ChatInput from "@/components/chat-input";

const ChatPanel: React.FC = () => {
  const {
    messages,
    input,
    setInput,
    sendMessage,
    messagesEndRef,
    isInitialized,
  } = useSkincareGPTChat();

  return (
    <div className="flex flex-col bg-gray-100 p-4 max-w-full w-full h-full overflow-y-auto">
      <ChatWindow messages={messages} messagesEndRef={messagesEndRef} isInitialized={isInitialized}/>
      <ChatInput input={input} setInput={setInput} sendMessage={sendMessage} />
    </div>
  );
};

export default ChatPanel;
