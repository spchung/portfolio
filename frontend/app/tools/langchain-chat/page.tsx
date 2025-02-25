"use client";
import { LangChainChatConfig, useLangChainChat } from "@/hooks/use-langchain-chat";
import ChatWindow from "@/components/chat-window";
import ChatInput from "@/components/chat-input";
import { useSidebarStore } from '@/stores/use-sidebar-store';
import { BsWindowSidebar } from "react-icons/bs";
import { Monomaniac_One } from "next/font/google";

const monomanic = Monomaniac_One({ subsets: ["latin"], weight: "400" });

const ChatPanel = () => {
  const {
    messages,
    input,
    setInput,
    sendMessage,
    messagesEndRef,
    // TODO: thread manager for langchain
  } = useLangChainChat({
    threadId: "test-thread",
    initMessage: "Hi welcome to chilli's!"
  } as LangChainChatConfig);

  const { toggle, state: sidebarState} = useSidebarStore();
  
  return (
    <>
      <div className='flex h-screen max-h-screen w-full overflow-y-auto'>
      <div className='flex flex-col w-full max-h-full'>
                <div className="w-full bg-gray-200 flex flex-row">
                    { !sidebarState.isOpen && <button
                        className="hover:bg-white text-white font-bold p-3 rounded"
                        onClick={() => toggle()}
                    >
                        <BsWindowSidebar className='text-gray-700 h-6 w-6'/>
                    </button>}
                    <h2 className={`${monomanic.className} text-2xl font-bold text-gray-700 p-3`}>Langchain Chat </h2>
                </div>
                <div className="flex flex-col bg-gray-100 p-4 max-w-full w-full h-full overflow-y-auto">
                  <ChatWindow messages={messages} messagesEndRef={messagesEndRef} />
                  <ChatInput input={input} setInput={setInput} sendMessage={sendMessage} />
                </div>
            </div>
      </div>
      
    </>
  );
};

export default ChatPanel;
