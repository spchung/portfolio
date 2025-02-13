"use client";
import { useChat } from "@/hooks/use-chat";
import ChatWindow from "@/components/chat-window";
import ChatInput from "@/components/chat-input";

const Chat: React.FC = () => {
  const {
    messages,
    input,
    setInput,
    metadata,
    sendMessage,
    messagesEndRef,
  } = useChat();

  return (
    <div className="flex flex-col h-screen bg-gray-100 p-4">
      <h1 className="absolute top-1 right-1 text-2xl font-semibold bg-red-400">
        Tokens: {metadata?.last_response_tokens}
        intent: {metadata?.last_query_intent}
        products: {metadata?.products[0].title}
      </h1>

      <ChatWindow messages={messages} messagesEndRef={messagesEndRef} />
      <ChatInput input={input} setInput={setInput} sendMessage={sendMessage} />
    </div>
  );
};

export default Chat;
