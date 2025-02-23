"use client";
import { useSkincareGPTChat } from "@/hooks/use-skincaregpt-chat";
import { useLangChainChat } from "@/hooks/use-langchain-chat";
import ChatWindow from "@/components/chat-window";
import ChatInput from "@/components/chat-input";

const ChatPanel = () => {
  const {
    messages,
    input,
    setInput,
    sendMessage,
    messagesEndRef,
    // TODO: thread manager for langchain
  } = useLangChainChat('test-thread-id');

  return (
    <div className="flex flex-col bg-gray-100 p-4 max-w-full w-full h-full overflow-y-auto">
      <ChatWindow messages={messages} messagesEndRef={messagesEndRef} />
      <ChatInput input={input} setInput={setInput} sendMessage={sendMessage} />
    </div>
  );
};

export default ChatPanel;
