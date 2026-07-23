import { Link } from "react-router-dom";

const FOOTER_LINKS = [
  { label: "Sobre", href: "/#sobre" },
  { label: "Termos de Uso", href: "/termo" },
  { label: "Privacidade", href: "/termos" },
  { label: "Contato", href: "/#contato" },
];

export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="bg-brand-secondary text-white">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-6 py-8 md:flex-row">
        <Link to="/" className="flex items-center gap-2">
          <img src="/logo.png" alt="BomCurrículo" className="h-9 w-auto" />

          <span className="text-lg font-bold">
            Bom<span className="text-brand-primary">Currículo</span>
          </span>
        </Link>

        <nav>
          <ul className="flex flex-wrap items-center justify-center gap-6">
            {FOOTER_LINKS.map((link) => (
              <li key={link.label}>
                <Link
                  to={link.href}
                  className="text-sm text-white/60 hover:text-white"
                >
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        <p className="text-sm text-white/50">
          © {year} BomCurrículo. ATS Inteligente. Resultados Reais.
        </p>
      </div>
    </footer>
  );
}
