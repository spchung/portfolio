"use client"; // If using Next.js App Router
import { useState } from "react";
import { motion } from "framer-motion";

interface PanelProps extends React.HTMLProps<HTMLDivElement> {
    title: string;
    children: React.ReactNode;
    defaultOpen?: boolean;
}

const Panel = ({ title, children, defaultOpen = false }: PanelProps) => {
    const [isOpen, setIsOpen] = useState(defaultOpen);

    return (
        <div className="border rounded-xl shadow-md p-4 w-full bg-white">
            <button 
                onClick={() => setIsOpen(!isOpen)} 
                className="w-full text-left flex justify-between items-center font-semibold"
            >
                {title}
                <span>{isOpen ? "▲" : "▼"}</span>
            </button>

            {/* Animated Collapsible Section */}
            <motion.div
                initial={false}
                animate={{ height: isOpen ? "auto" : 0, opacity: isOpen ? 1 : 0 }}
                transition={{ duration: 0.3, ease: "easeInOut" }}
                className="overflow-hidden"
            >
                <div className="mt-2">{children}</div>
            </motion.div>
        </div>
    );
};

export { Panel };