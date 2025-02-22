import { useState, useEffect } from "react";
import { fetchContextSnapshot } from "@/services/context-service";
import { useRagStore } from "@/stores/use-rag-store";
import { ChatContext } from "@/models";

export function useContext() {
    const [context, setContext] = useState<ChatContext>();
    const state = useRagStore(store => store.state);
    
    useEffect(() => {
        if (!state.sessionId) return;
    
        fetchContextSnapshot(state.sessionId)
        .then((data) => {
            setContext(data);
        })
        .catch((err) => console.error(err));

    }, [state.iterateContextCount]);
    
    return { context };
}