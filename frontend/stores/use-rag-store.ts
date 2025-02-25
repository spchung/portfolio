import { create } from 'zustand';

type EcommerceRagState = {
    sessionId: string;
    iterateContextCount: number;
}

interface StoreState {
    state: EcommerceRagState;
    setSessionId: (session_id: string) => void;
    iterateContext: () => void;
}

export const useRagStore = create<StoreState>((set, get) => ({
    state: {
        sessionId: '',
        iterateContextCount: 0
    },
    setSessionId: (sessionId: string) => set((store) => ({ 
        state: { ...store.state, sessionId } 
    })),
    iterateContext: () => set((store) => ({ 
        state: { ...store.state, iterateContextCount: store.state.iterateContextCount + 1 } 
    }))
}));

