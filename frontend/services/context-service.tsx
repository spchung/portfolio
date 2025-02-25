export async function fetchContextSnapshot(sessionId: string) {
    if (!sessionId) throw new Error("No session ID provided");
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v2/skincare-gpt/context-snapshot?session_id=${sessionId}`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
    });

    if (response.status === 404) return null;

    if (!response.body) throw new Error("No response body");
    return response.json();
}

export async function deleteContext(sessionId: string) {
    if (!sessionId) throw new Error("No session ID provided");
    const response = await fetch(`http://127.0.0.1:8000/api/v1/ecommerce-rag/clear-context-snapshot?session_id=${sessionId}`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
    });
    return response.json();
}

export function getNewSessionId() {
    return fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v2/skincare-gpt/register-new-session`, {
        method: "GET",
        credentials: "include",
    }).then((response) => response.json());
}