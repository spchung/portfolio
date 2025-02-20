export async function fetchChatStream(userQuery: string) {
    const response = await fetch("http://127.0.0.1:8000/api/v2/ecommerce-rag/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userQuery }),
    });
  
    if (!response.body) throw new Error("No response body");
  
    return response.body.getReader();
  }