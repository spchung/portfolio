'use client';
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ChatPanel from '../dash/chat-panel';
import { SidebarTrigger } from "@/components/ui/sidebar"
import { AiFillEye, AiFillEyeInvisible } from "react-icons/ai";
import DevPanel from '../dash/dev-panel';

export default function page() {
    const [devPanelIsOpen, setIsOpenDevPanel] = useState(false);
    return ( 
        <div className="flex h-full w-full">
            <div className='flex flex-col w-full'>
                <div className="w-full bg-gray-200 p-3">
                    <SidebarTrigger />
                    <button
                        className="hover:bg-white text-white font-bold py-[4px] px-[4px] rounded"
                        onClick={() => setIsOpenDevPanel(!devPanelIsOpen)}
                    >
                        { devPanelIsOpen ? <AiFillEyeInvisible className='text-gray-700'/> : <AiFillEye className='text-gray-700'/> }
                    </button>
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
