export async function fetchContextSnapshot(sessionId: string) {
    if (!sessionId) throw new Error("No session ID provided");
    const response = await fetch(`http://127.0.0.1:8000/api/v1/ecommerce-rag/context-snapshot?session_id=${sessionId}`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
  
    if (!response.body) throw new Error("No response body");
    return response.json();
  }
  