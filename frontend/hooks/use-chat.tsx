import { useState, useRef, useEffect } from "react";
import { fetchChatStream } from "@/services/chat-service";
import { Metadata } from "@/models";

export interface Message {
  role: "user" | "bot";
  content: string;
}


export function useChat() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "bot", content: "Hello! How can I help you today?" },
  ]);
  const [input, setInput] = useState<string>("");
  const [metadata, setMetadata] = useState<Metadata>();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, newMessage]);
    setInput("");

    const botMessage: Message = { role: "bot", content: "..." };
    setMessages((prev) => [...prev, botMessage]);

    try {
      const reader = await fetchChatStream(input);
      if (!reader) throw new Error("No response body");

      const decoder = new TextDecoder();
      let botResponse = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });

        if (chunk.startsWith("event: metadata")) {
          const match = chunk.match(/data: (.*)/);
          if (match) {
            const metadata = JSON.parse(match[1]);
            console.log("Metadata:", metadata);
            setMetadata(metadata);
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

  return {
    messages,
    input,
    setInput,
    metadata,
    sendMessage,
    messagesEndRef,
  };
}
