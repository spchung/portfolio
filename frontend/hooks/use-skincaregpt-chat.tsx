import { useState, useRef, useEffect, use } from "react";
import { chatSkincareGPT } from "@/services/chat-service";
import { useRagStore } from "@/stores/use-rag-store";
import { fetchContextSnapshot } from "@/services/context-service";
import { History } from "@/models";

export interface Message {
    role: "user" | "bot";
    content: string;
}

export function useSkincareGPTChat() {
    const [input, setInput] = useState<string>("");
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const iterateContext = useRagStore((store) => store.iterateContext);
    const sessionId = useRagStore((store) => store.state.sessionId);
    const [messages, setMessages] = useState<Message[]>([]);
    const [isInitialized, setIsInitialized] = useState<boolean>(false);

    useEffect(() => {
        if(isInitialized || sessionId === '') return;

        const initChatHistory = async () => {
            if (sessionId) {
                try {

                    // get context snapshot
                    const response = await fetchContextSnapshot(sessionId);
                    const chatHistory = response.history as History[];
                    
                    if (history.length > 0) {
                        let messages = [{ role: "bot", content: `Hello! How can I help you today?` }];
                        chatHistory.forEach((history) => {
                            messages.push({ role: "user", content: history.user_query });
                            messages.push({ role: "bot", content: history.response });
                        });
                        setMessages(messages as Message[]);
                    } 
                    else {
                        setMessages([
                            { role: "bot", content: `Hello! How can I help you today? = ${sessionId}` },
                        ]);
                    }
                }
                catch(error){
                    console.error("Error loading previous messages:", error);
                    setMessages([
                        { role: "bot", content: `Hello! How can I help you today?` },
                    ]);
                }
            }
            else {
                setMessages([
                    { role: "bot", content: `Hello! How can I help you today?` },
                ]);
            }
            setIsInitialized(true);
        }

        initChatHistory();
    }, [sessionId]);


    const sendMessage = async () => {
        if (!input.trim()) return;

        const newMessage: Message = { role: "user", content: input };
        setMessages((prev) => [...prev, newMessage]);
        setInput("");

        const botMessage: Message = { role: "bot", content: "..." };
        setMessages((prev) => [...prev, botMessage]);

        try {
            const reader = await chatSkincareGPT(input, sessionId || "");
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
        isInitialized,
    };
}
