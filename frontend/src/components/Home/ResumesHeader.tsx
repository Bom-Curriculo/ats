import { List, Plus, ListFilter } from "lucide-react";
import { Button } from "../ui/button";

interface ResumesHeaderProps {
  count?: number;
  limit?: number;
  onFilter?: () => void;
  onAdd?: () => void;
}

export default function ResumesHeader({ count = 2, limit = 5, onFilter, onAdd }: ResumesHeaderProps) {
  const isLimitReached = count >= limit;

  return (
    <header className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
      <div>
        <h1 className="text-2xl lg:text-3xl font-bold text-brand-secondary tracking-wide">Meus Currículos</h1>
        <span className="text-sm lg:text-base text-muted-foreground">Gerencie e otimize suas aplicações para o mercado</span>
      </div>
      <div className="flex flex-col md:flex-row items-center gap-3">
        <div className="flex w-full items-center gap-3 md:contents">
          <div
            role="status"
            className="flex h-9 min-w-0 flex-1 items-center justify-center gap-2 rounded-lg bg-brand-primary-tint px-2.5 text-sm font-medium whitespace-nowrap text-brand-secondary md:flex-none md:px-4 lg:h-11"
          >
            <List className="size-4 shrink-0" />
            <span className="truncate">
              {count}/{limit} Currículos
            </span>
          </div>
          <Button
            onClick={onFilter}
            className="h-9 lg:h-11 min-w-0 flex-1 gap-2 md:px-4 bg-brand-primary-tint text-brand-secondary hover:bg-brand-primary-tint/90 md:flex-none"
          >
            <ListFilter className="size-4 shrink-0" />
            <span className="truncate">Filtrar</span>
          </Button>
        </div>
        <Button
          type="button"
          onClick={onAdd}
          disabled={isLimitReached}
          title={isLimitReached ? "Limite de currículos atingido" : undefined}
          className="w-full h-9 lg:h-11 gap-2 md:px-4 bg-brand-primary text-white hover:bg-brand-primary/90 md:w-auto disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:bg-brand-primary"
        >
          <Plus className="size-4" />
          <span className="truncate">Adicionar Currículo</span>
        </Button>
      </div>
    </header>
  );
}
