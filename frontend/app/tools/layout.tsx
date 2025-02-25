import { SideBarWrapper } from './sidebar-wrapper';
 
export default async function Layout({ children }: { children: React.ReactNode }) {
  return (
    <SideBarWrapper>
      {children}
    </SideBarWrapper>
  );
}
