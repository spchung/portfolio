import { SideBarWrapper } from './sidebar-wrapper';
import { cookies } from 'next/headers'
 
export default async function Layout({ children }: { children: React.ReactNode }) {
  const cookieStore = await cookies()
  const sessionId = cookieStore.get('session_id')
  return (
    <SideBarWrapper sessionId={sessionId?.value}>
      {children}
    </SideBarWrapper>
  );
}
