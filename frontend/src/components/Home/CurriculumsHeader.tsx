import { List, Plus, ListFilter } from "lucide-react";
import { Button } from "../ui/button";

export default function CurriculumsHeader() {
  return (
    <header className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
      <div>
        <h1 className="text-2xl lg:text-3xl font-bold text-[#03206E] tracking-wide">Meus Currículos</h1>
        <span className="text-sm lg:text-base text-gray-600">Gerencie e otimize suas aplicações para o mercado</span>
      </div>
      <div className="flex flex-col md:flex-row items-center gap-3">
        <div className="flex w-full items-center gap-3 md:contents">
          <div
            role="status"
            className="flex h-9 min-w-0 flex-1 items-center justify-center gap-2 rounded-lg bg-[#DCE1FF] px-2.5 text-sm font-medium whitespace-nowrap text-[#001550] md:flex-none md:px-4 lg:h-11"
          >
            <List className="size-4 shrink-0" />
            <span className="truncate">2/5 Currículos</span>
          </div>
          <Button className="h-9 lg:h-11 min-w-0 flex-1 gap-2 md:px-4 bg-[#D3E4FE] text-[#00072B] hover:bg-[#D3E4FE]/90 md:flex-none">
            <ListFilter className="size-4 shrink-0" />
            <span className="truncate">Filtrar</span>
          </Button>
        </div>
        <Button className="w-full h-9 lg:h-11 gap-2 md:px-4 bg-[#1A56DB] text-white hover:bg-[#1A56DB]/90 md:w-auto">
          <Plus className="size-4" />
          <span className="truncate">Adicionar Currículo</span>
        </Button>
      </div>
    </header>
  );
}
