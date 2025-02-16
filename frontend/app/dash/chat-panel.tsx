
"use client";
import { useChat } from "@/hooks/use-chat";
import ChatWindow from "@/components/chat-window";
import ChatInput from "@/components/chat-input";

const ChatPanel: React.FC = () => {
  const {
    messages,
    input,
    setInput,
    metadata,
    sendMessage,
    messagesEndRef,
  } = useChat();

  return (
    <div className="flex flex-col bg-gray-100 p-4 h-full w-full">
      {/* <h1 className="absolute top-1 right-1 text-2xl font-semibold bg-red-400">
        Tokens: {metadata?.last_response_tokens}
        intent: {metadata?.last_query_intent}
      </h1> */}

      <ChatWindow messages={messages} messagesEndRef={messagesEndRef} />
      <ChatInput input={input} setInput={setInput} sendMessage={sendMessage} />
    </div>
  );
};

export default ChatPanel;
