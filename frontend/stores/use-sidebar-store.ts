import { create } from 'zustand';

type SidebarStoreState = {
    isOpen: boolean;
}

interface StoreState {
    state: SidebarStoreState
    toggle: () => void;
}

export const useSidebarStore = create<StoreState>((set, get) => ({
    state: {
        isOpen: true
    },
    toggle: () => set((store) => ({ 
        state: { ...store.state, isOpen: !store.state.isOpen } 
    }))
}));
