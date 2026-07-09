import { CirclePlus, Lock } from "lucide-react";

interface AddCurriculumCardProps {
  isLimitReached: boolean;
  limit?: number;
  onCreate?: () => void;
}

export default function AddCurriculumCard({
  isLimitReached,
  limit = 5,
  onCreate,
}: AddCurriculumCardProps) {
  if (isLimitReached) {
    return (
      <article
        role="status"
        className="flex flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed border-gray-300 bg-gray-50 p-8 text-center"
      >
        <div aria-hidden="true" className="flex size-12 items-center justify-center rounded-full bg-gray-200">
          <Lock className="size-5 text-gray-500" />
        </div>
        <h3 className="font-bold text-[#03206E]">Limite Atingido</h3>
        <p className="text-sm text-gray-500">
          Você atingiu o limite de {limit} currículos.
          <br />
          Exclua um currículo para liberar espaço.
        </p>
      </article>
    );
  }

  return (
    <button
      type="button"
      onClick={onCreate}
      className="flex cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed border-[#B9C6FF] bg-[#F5F7FF] p-8 text-center transition-colors hover:border-[#2E7BFF] hover:bg-[#EEF1FF]"
    >
      <span aria-hidden="true" className="flex size-12 items-center justify-center rounded-full bg-[#DCE1FF]">
        <CirclePlus className="size-5 text-[#2E7BFF]" />
      </span>
      <span className="block font-bold text-[#03206E]">Criar Novo Currículo</span>
      <span className="block text-sm text-gray-500">
        Crie uma versão otimizada
        <br />
        para uma nova vaga.
      </span>
    </button>
  );
}
