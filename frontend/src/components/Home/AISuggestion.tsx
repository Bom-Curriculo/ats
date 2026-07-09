import { Bot } from "lucide-react";
import { Button } from "../ui/button";

interface AISuggestionProps {
  role?: string;
  keyword?: string;
  scoreIncrease?: number;
  onOptimize?: () => void;
}

export default function AISuggestion({
  role = "Engenheiro",
  keyword = "Kubernetes",
  scoreIncrease = 15,
  onOptimize,
}: AISuggestionProps) {
  return (
    <aside
      aria-label="Sugestão da IA"
      className="mt-6 flex flex-col lg:flex-row lg:items-center gap-4 border-l-4 border-[#1A56DB] bg-[#DCE1FF] p-5 sm:p-6"
    >
      <div className="flex items-start md:items-center justify-center gap-4 sm:flex-1">
        <span
          aria-hidden="true"
          className="hidden sm:flex size-10 lg:size-12 shrink-0 items-center justify-center rounded-full bg-[#1A56DB] text-white"
        >
          <Bot className="size-5 lg:size-7" />
        </span>
        <div>
          <h3 className="font-bold text-sm lg:text-base text-[#03206E]">Dica da IA para o seu currículo de {role}</h3>
          <p className="mt-1 text-xs lg:text-sm text-gray-600">
            Identificamos que a palavra-chave "{keyword}" está em alta para as vagas que você analisa. Adicione
            experiências relacionadas para aumentar seu ATS score em até {scoreIncrease}%.
          </p>
        </div>
      </div>
      <Button
        type="button"
        onClick={onOptimize}
        className="h-9 lg:h-11 shrink-0 rounded-lg bg-[#03206E] px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#03206E]/90 "
      >
        Otimizar agora
      </Button>
    </aside>
  );
}
