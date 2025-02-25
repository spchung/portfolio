import { ChatServicesEnum } from "@/enum";

export async function chatSkincareGPT(userQuery: string, sessionId: string) {
    const response = await fetch("http://127.0.0.1:8000/api/v2/skincare-gpt/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userQuery , session_id: sessionId}),
    });

    if (!response.body) throw new Error("No response body");

    return response.body.getReader();
}

// tools/langchain-chat.tsx
export async function chatLangChain(userQuery: string, threadId: string | null) {
    let url = "http://127.0.0.1:8000/api/v2/llm/langchain-chat";
    if (threadId) {
        url += `?thread_id=${threadId}`;
    }
    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userQuery }),
    });

    if (!response.body) throw new Error("No response body");

    return response.body.getReader();
}

