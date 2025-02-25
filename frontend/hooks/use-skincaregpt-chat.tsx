import { useState, useRef, useEffect, use } from "react";
import { chatSkincareGPT } from "@/services/chat-service";
import { useRagStore } from "@/stores/use-rag-store";

export interface Message {
  role: "user" | "bot";
  content: string;
}

export function useSkincareGPTChat() {
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const [input, setInput] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const iterateContext = useRagStore((store) => store.iterateContext);
  const ragState = useRagStore((store) => store.state);
  
  useEffect(() => {
    if (!ragState.sessionId) return;
    

    
  }, [ragState.sessionId]);


  const [messages, setMessages] = useState<Message[]>([
    { role: "bot", content: `Hello! How can I help you today? - ${ragState.sessionId}` },
  ]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, newMessage]);
    setInput("");

    const botMessage: Message = { role: "bot", content: "..." };
    setMessages((prev) => [...prev, botMessage]);

    try {
      const reader = await chatSkincareGPT(input, ragState.sessionId);
      if (!reader) throw new Error("No response body");

      const decoder = new TextDecoder();
      let botResponse = "";

      while (true) {
        const { value, done } = await reader.read();
        
        // streaming response ends - call for new context snapshot
        if (done) {
          iterateContext();
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
