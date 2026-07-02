import { Outlet } from "react-router-dom";
import { SidebarInset, SidebarProvider } from "../ui/sidebar";
import AppSidebar from "./app-sidebar";


export function DashboardLayout() {
  return (
    <SidebarProvider defaultOpen={true}>
      <AppSidebar />
      <SidebarInset>
        <main className="flex-1 p-6 bg-white">
          <Outlet />
        </main>
      </SidebarInset>
    </SidebarProvider>
  );
}


