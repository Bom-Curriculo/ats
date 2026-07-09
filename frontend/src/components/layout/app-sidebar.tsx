import {
  ChartColumnBigIcon,
  CircleQuestionMarkIcon,
  FileText,
  HomeIcon,
  LayoutDashboard,
  LogOut,
  Plus,
  SettingsIcon,
} from "lucide-react";

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenu,
} from "../ui/sidebar";
import { Button } from "../ui/button";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { LogoutApi } from "@/api/auth/logout-api";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";

const items = [
  {
    title: "Visão Geral",
    url: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "Meus Curriculos",
    url: "/my-curriculum",
    icon: FileText,
  },
  {
    title: "Analisador de Vagas",
    url: "/job-analysis",
    icon: ChartColumnBigIcon,
  },
  {
    title: "Configurações",
    url: "/settings",
    icon: SettingsIcon,
  },
  {
    title: "Voltar ao site",
    url: "/",
    icon: HomeIcon,
  },
];

export default function AppSidebar() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const logoutMutation = useMutation({
    mutationFn: LogoutApi,
    onSuccess: () => {
      queryClient.removeQueries({
        queryKey: ["me"],
      });
      toast.success("Logout!");
      navigate("/login");
    },
    onError: () => {
      toast.error("Erro ao sair da conta");
    },
  });

  return (
    <Sidebar collapsible="icon">
      <SidebarContent className="border-b border-solid border-sidebar-border">
        <div className="border-b border-sidebar-border ">
          <div className="p-4 ">
            <div className="flex gap-1">
              <img
                src="/logo-dark.png"
                alt="BomCurriculo"
                className="h-10 w-auto dark:hidden"
              />

              <img
                src="/logo.png"
                alt="BomCurriculo"
                className="hidden h-10 w-auto dark:block"
              />
              <h1 className="text-brand-secondary dark:text-white flex items-center text-xl gap-1 font-semibold">
                Bom<span className="text-brand-primary"> Currículo</span>
              </h1>
            </div>
            <span className="text-muted-foreground text-sm">Otimização ATS</span>
          </div>
        </div>

        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    asChild
                    className="py-4 hover:bg-brand-secondary dark:hover:bg-brand-primary "
                  >
                    <a
                      href={item.url}
                      className="flex items-center gap-3  hover:text-white "
                    >
                      <item.icon className={"w-5! h-5!"} />
                      <span>{item.title}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <footer className="p-4">
        <div className="flex flex-col gap-2">
          <Button className="bg-brand-secondary dark:bg-brand-primary p-6 hover:bg-brand-secondary">
            {/** Tds os botoes aqui criar o component */} <Plus /> Novo
            Currículo
          </Button>
          <div className="flex gap-1 items-center">
            <CircleQuestionMarkIcon size={16} /> <h1>Ajuda</h1>
          </div>
          <div className="flex gap-1 items-center">
            <Button  onClick={() => logoutMutation.mutate()} className="text-destructive bg-transparent hover:bg-transparent">
              <LogOut/> Desconectar
            </Button>
          </div>
        </div>
      </footer>
    </Sidebar>
  );
}
