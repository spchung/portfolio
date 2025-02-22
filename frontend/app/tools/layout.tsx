'use client';
import { SidebarProvider } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/app-sidebar"
import { useSidebarStore } from "@/stores/use-sidebar-store"

export default function Layout({ children }: { children: React.ReactNode }) {
  const { isOpen } = useSidebarStore((state) => state.state);
  return (
    <SidebarProvider open={isOpen}>
      <AppSidebar />
      <main className='w-full'>
        {children}
      </main>
    </SidebarProvider>
  )
}