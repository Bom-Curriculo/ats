import { List, Plus, ListFilter } from "lucide-react";
import { Button } from "../ui/button";

export default function Header() {
  return (
    <header className="flex items-center justify-between gap-4 py-6">
      <div>
        <h1 className="text-3xl font-bold text-[#03206E] tracking-wide">Meus Currículos</h1>
        <span className="text-gray-600">Gerencie e otimize suas aplicações para o mercado</span>
      </div>
      <div className="flex items-center gap-3">
        <Button className="h-11 gap-2 px-4 bg-[#DCE1FF] text-[#001550] hover:bg-[#DCE1FF]/90">
          <List className="size-4" />
          2/5 Currículos
        </Button>
        <Button className="h-11 gap-2 px-4 bg-[#D3E4FE] text-[#00072B] hover:bg-[#D3E4FE]/90">
          <ListFilter className="size-4" />
          Filtrar
        </Button>
        <Button className="h-11 gap-2 px-4 bg-[#2E7BFF] text-white hover:bg-[#2E7BFF]/90">
          <Plus className="size-4" />
          Novo Currículo
        </Button>
      </div>
    </header>
  );
}
