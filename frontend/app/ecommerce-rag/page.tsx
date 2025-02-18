'use client';
import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ChatPanel from './chat-panel';
import { SidebarTrigger } from "@/components/ui/sidebar"
import { AiFillEye, AiFillEyeInvisible, AiOutlineBars } from "react-icons/ai";
import DevPanel from './dev-panel';
import { useRagStore } from "@/stores/use-rag-store";
import { deleteContext } from '@/services/context-service';

export default function page() {
    const { state, setSessionId, iterateContext } = useRagStore();
    const [devPanelIsOpen, setIsOpenDevPanel] = useState(false);
    const sideBarTriggerRef = useRef<HTMLButtonElement>(null);
    
    if (!state.sessionId) {
        setSessionId('test');
    }

    return ( 
        <div className="flex h-full w-full">
            <div className='flex flex-col w-full'>
                <div className="w-full bg-gray-200 flex">
                    <SidebarTrigger ref={sideBarTriggerRef} className='hidden'/>
                    <button
                        className="hover:bg-white text-white font-bold p-3 rounded"
                        onClick={() => sideBarTriggerRef.current?.click()}
                    >
                        <AiOutlineBars className='text-gray-700'/>
                    </button>
                    <button
                        className="hover:bg-white text-white font-bold p-3 rounded"
                        onClick={() => setIsOpenDevPanel(!devPanelIsOpen)}
                    >
                        { devPanelIsOpen ? <AiFillEyeInvisible className='text-gray-700'/> : <AiFillEye className='text-gray-700'/> }
                    </button>
                    <button onClick={ () => {
                        deleteContext(state.sessionId);
                        iterateContext();
                    }}> clear context </button>
                    <p className='p-[4px]'> Count: {state.iterateContextCount} - Session ID: {state.sessionId} </p>
                </div>
                <div className="flex-1 bg-gray-100 p-4">
                    <ChatPanel />
                </div>
            </div>
            {/* Right Panel */}
            <AnimatePresence>
                {devPanelIsOpen && (
                    <motion.div
                        key="right-panel"
                        className="bg-gray-200 p-4 overflow-hidden"
                        initial={{ width: 0, opacity: 0 }}
                        animate={{ width: '60%', opacity: 1 }}  // 256px equals Tailwind's w-64
                        exit={{ width: 0, opacity: 0 }}
                        transition={{ duration: 0.5 }}
                    >
                        <DevPanel />
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
