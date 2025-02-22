'use client';
import { Monomaniac_One } from "next/font/google";
import { Calendar, Home, Inbox, Search, Settings } from "lucide-react"
import { BsWindowSidebar } from "react-icons/bs";
import { useSidebarStore } from '@/stores/use-sidebar-store';
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarTrigger,
} from "@/components/ui/sidebar"

// Menu items.
const items = [
  {
    title: "SkincareGPT",
    url: "#",
    icon: Home,
  },
  {
    title: "Hugginface Summarizer",
    url: "#",
    icon: Inbox,
  },
  {
    title: "ChatGPT Wrapper",
    url: "#",
    icon: Calendar,
  },
  {
    title: "Chat With Your Papers",
    url: "#",
    icon: Search,
  },
]


const monomanic = Monomaniac_One({ subsets: ["latin"], weight: "400" });
export function AppSidebar() {
  const { toggle } = useSidebarStore();
  return (
    <Sidebar>
      <SidebarContent >
        <SidebarGroup>
          <div className='flex items-center pl-2 pb-2'>
            <button className="hover:bg-white text-white font-boldrounded"
                onClick={() => toggle()}
            >
                <BsWindowSidebar className='text-gray-700 h-6 w-6'/>
            </button>
            <SidebarGroupLabel>Tools</SidebarGroupLabel>
          </div>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <a href={item.url}>
                      <item.icon />
                      <span>{item.title}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  )
}
