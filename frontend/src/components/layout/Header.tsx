import { Link } from "react-router-dom";

export function Header() {
  return (
    <header className="border-b border-border bg-background px-6 py-3">
      <div className="mx-auto flex max-w-7xl items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <img src="/logo-dark.png" alt="BomCurrículo" className="h-9 w-auto dark:hidden" />
          <img src="/logo.png" alt="BomCurrículo" className="hidden h-9 w-auto dark:block" />

          <span className="text-lg font-bold text-foreground">
            Bom<span className="text-brand-primary">Currículo</span>
          </span>
        </Link>

        <div className="flex items-center gap-6">
          <Link
            to="/#ajuda"
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            Ajuda
          </Link>

          <Link
            to="/login"
            className="rounded-lg bg-brand-secondary px-4 py-2 text-sm font-medium text-white hover:bg-brand-secondary/90"
          >
            Entrar
          </Link>
        </div>
      </div>
    </header>
  );
}
