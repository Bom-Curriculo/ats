import {
  Bell,
  ChevronDown,
  LayoutDashboard,
  LogOut,
  Menu,
  Settings,
  User2,
  X,
} from "lucide-react";
import { ModeToggle } from "../mode-toggle";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getUser } from "@/api/user/get-user";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../ui/dropdown-menu";
import { Link, NavLink, useNavigate } from "react-router";
import { toast } from "sonner";
import { LogoutApi } from "@/api/auth/logout-api";
import { useState } from "react";

const NAV_LINKS = [
  { label: "Início", to: "/" },
  { label: "Dashboard", to: "/dashboard" },
  { label: "Editor", to: null },
  { label: "Vagas", to: null },
  { label: "Preços", to: null },
];

export function Header() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [openMenu, setOpenMenu] = useState(false);
  const { data: user, isLoading } = useQuery({
    queryKey: ["me"],
    queryFn: getUser,
    retry: false,
  });
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
    <header className="border-b border-gray-300 bg-gray-50 px-6 py-4 dark:border-brand-primary/30 dark:bg-brand-secondary">
      <div className="mx-auto flex max-w-8xl items-center justify-between">
        <div className="flex items-center gap-2">
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

          <h1 className="text-xl font-bold md:text-2xl">
            Bom<span className="text-brand-primary">Curriculo</span>
          </h1>
        </div>

        <nav className="hidden lg:block">
          <ul className="flex items-center gap-8 text-lg font-medium">
            {NAV_LINKS.map(({ label, to }) =>
              to ? (
                <li key={label}>
                  <NavLink
                    to={to}
                    end={to === "/"}
                    className={({ isActive }) =>
                      `transition hover:text-brand-primary ${
                        isActive ? "text-brand-primary" : ""
                      }`
                    }
                  >
                    {label}
                  </NavLink>
                </li>
              ) : (
                <li
                  key={label}
                  title="Em breve"
                  className="cursor-not-allowed text-gray-400 dark:text-gray-500"
                >
                  {label}
                </li>
              ),
            )}
          </ul>
        </nav>

        <div className="hidden items-center gap-4 lg:flex">
          {isLoading ? (
            <div className="h-10 w-24 animate-pulse rounded-xl bg-slate-200" />
          ) : user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex items-center gap-3 rounded-none border px-3 py-2 shadow-sm transition-all">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gray-200 font-semibold text-brand-primary">
                    {user.name.charAt(0).toUpperCase()}
                  </div>

                  <div className="text-left">
                    <p className="text-sm font-medium text-brand-primary">
                      {user.name}
                    </p>

                    <p className="text-xs text-gray-500">{user.email}</p>
                  </div>

                  <ChevronDown className="h-4 w-4 text-slate-400" />
                </button>
              </DropdownMenuTrigger>

              <DropdownMenuContent align="end" className="w-56 rounded-none">
                <DropdownMenuItem asChild  className="rounded-none">
                  <Link to="/config">
                    <Settings className="mr-2 h-4 w-4" />
                    Configurações
                  </Link>
                </DropdownMenuItem>

                <DropdownMenuItem asChild className="rounded-none">
                  <Link to="/dashboard">
                    <LayoutDashboard className="mr-2 h-4 w-4" />
                    Dashboard
                  </Link>
                </DropdownMenuItem>

                <DropdownMenuSeparator />

                <DropdownMenuItem
                  className="cursor-pointer text-destructive rounded-none"
                  onClick={() => logoutMutation.mutate()}
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Desconectar
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <Link
              to="/login"
              className="flex items-center gap-2 rounded-xl bg-gray-100 px-4 py-2 transition hover:bg-gray-200 dark:bg-brand-secondary/90"
            >
              <User2 className="h-5 w-5" />
              Entrar
            </Link>
          )}

          <Bell className="cursor-pointer text-gray-700 hover:text-brand-primary dark:text-gray-300" />

          <ModeToggle />
        </div>
        <button
          onClick={() => setOpenMenu(!openMenu)}
          className="rounded-lg p-2 lg:hidden"
        >
          {openMenu ? <X size={28} /> : <Menu size={28} />}
        </button>
      </div>

      <div
        className={`overflow-hidden transition-all duration-300 lg:hidden ${
          openMenu ? "max-h-125 opacity-100" : "max-h-0 opacity-0"
        }`}
      >
        <div className="mt-4 border-t pt-4">
          <nav>
            <ul className="flex flex-col gap-4 text-lg font-medium">
              {NAV_LINKS.map(({ label, to }) =>
                to ? (
                  <li key={label}>
                    <NavLink
                      to={to}
                      end={to === "/"}
                      onClick={() => setOpenMenu(false)}
                      className={({ isActive }) =>
                        `hover:text-brand-primary ${
                          isActive ? "text-brand-primary" : ""
                        }`
                      }
                    >
                      {label}
                    </NavLink>
                  </li>
                ) : (
                  <li
                    key={label}
                    title="Em breve"
                    className="cursor-not-allowed text-gray-400 dark:text-gray-500"
                  >
                    {label}
                  </li>
                ),
              )}
            </ul>
          </nav>

          <div className="mt-6 border-t pt-4">
            {user ? (
              <div className="space-y-3">
                <div className="rounded-none border p-3">
                  <p className="font-medium">{user.name}</p>
                  <p className="text-sm text-gray-500">{user.email}</p>
                </div>

                <Link to="/dashboard" className="flex items-center gap-2">
                  <LayoutDashboard size={18} />
                  Dashboard
                </Link>

                <Link to="/config" className="flex items-center gap-2">
                  <Settings size={18} />
                  Configurações
                </Link>

                <button
                  onClick={() => logoutMutation.mutate()}
                  className="flex items-center gap-2 text-destructive"
                >
                  <LogOut size={18} />
                  Desconectar
                </button>
              </div>
            ) : (
              <Link
                to="/login"
                className="flex items-center gap-2 rounded-xl border px-4 py-2"
              >
                <User2 size={18} />
                Entrar
              </Link>
            )}

            <div className="mt-6 flex items-center justify-between">
              <Bell className="cursor-pointer" />
              <ModeToggle />
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
