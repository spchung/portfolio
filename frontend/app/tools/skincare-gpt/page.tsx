'use client';
import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ChatPanel from './chat-panel';
import { AiFillEye, AiFillEyeInvisible } from "react-icons/ai";
import { BsWindowSidebar } from "react-icons/bs";
import DevPanel from './dev-panel';
import { useRagStore } from "@/stores/use-rag-store";
import { Monomaniac_One } from "next/font/google";
import { useSidebarStore } from '@/stores/use-sidebar-store';

const monomanic = Monomaniac_One({ subsets: ["latin"], weight: "400" });

export default function page() {
    const { state, setSessionId, iterateContext } = useRagStore();
    const [devPanelIsOpen, setIsOpenDevPanel] = useState(false);
    const sideBarTriggerRef = useRef<HTMLButtonElement>(null);
    const { toggle, state: sidebarState} = useSidebarStore();
    
    if (!state.sessionId) {
        setSessionId('test');
    }

    return ( 
        <div className={`flex h-screen max-h-screen w-full overflow-y-auto`}>
            <div className='flex flex-col w-full max-h-full'>
                <div className="w-full bg-gray-200 flex flex-row">
                    { !sidebarState.isOpen && <button
                        className="hover:bg-white text-white font-bold p-3 rounded"
                        onClick={() => toggle()}
                    >
                        <BsWindowSidebar className='text-gray-700 h-6 w-6'/>
                    </button>}
                    <button
                        className="hover:bg-white text-white font-bold p-3 rounded "
                        onClick={() => setIsOpenDevPanel(!devPanelIsOpen)}
                    >
                        { devPanelIsOpen ? <AiFillEyeInvisible className='text-gray-700 h-6 w-6'/> : <AiFillEye className='text-gray-700 h-6 w-6'/> }
                    </button>
                    <h2 className={`${monomanic.className} text-2xl font-bold text-gray-700 p-3`}>SkincareGPT</h2>
                    {/* <button onClick={ () => {
                        deleteContext(state.sessionId);
                        iterateContext();
                    }}> clear context </button> */}
                    {/* <p className='p-[4px]'> Count: {state.iterateContextCount} - Session ID: {state.sessionId} </p> */}
                </div>
                <div className="flex-1 bg-gray-100 p-4 max-height-[calc(100vh-48px)] overflow-y-auto">
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
                        animate={{ width: '40%', opacity: 1 }}  // 256px equals Tailwind's w-64
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
