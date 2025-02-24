import { useState, useRef, useEffect } from "react";
import { chatLangChain } from "@/services/chat-service";
import { useRagStore } from "@/stores/use-rag-store";

export interface Message {
  role: "user" | "bot";
  content: string;
}

export interface LangChainChatConfig {
    threadId: string | null;
    initMessage: string;
  }

export function useLangChainChat({
    threadId='123abc',
    initMessage="Hello! How can I help you today?"
}:LangChainChatConfig) {
  const [messages, setMessages] = useState<Message[]>([
    { role: "bot", content: initMessage },
  ]);
  const [input, setInput] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, newMessage]);
    setInput("");

    const botMessage: Message = { role: "bot", content: "..." };
    setMessages((prev) => [...prev, botMessage]);

    try {
      const reader = await chatLangChain(input, threadId);
      if (!reader) throw new Error("No response body");

      const decoder = new TextDecoder();
      let botResponse = "";

      while (true) {
        const { value, done } = await reader.read();
        
        // streaming response ends - call for new context snapshot
        if (done) {
          break;
        }

        const chunk = decoder.decode(value, { stream: true });

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

  return {
    messages,
    input,
    setInput,
    sendMessage,
    messagesEndRef,
  };
}
