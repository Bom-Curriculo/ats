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
        <h3 className="font-bold text-brand-secondary">Limite Atingido</h3>
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
      className="flex cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed border-brand-primary/35 bg-brand-primary/5 p-8 text-center transition-colors hover:border-brand-primary hover:bg-brand-primary/15"
    >
      <span aria-hidden="true" className="flex size-12 items-center justify-center rounded-full bg-[#DCE1FF]">
        <CirclePlus className="size-5 text-brand-primary" />
      </span>
      <span className="block font-bold text-brand-secondary">Criar Novo Currículo</span>
      <span className="block text-sm text-gray-500">
        Crie uma versão otimizada
        <br />
        para uma nova vaga.
      </span>
    </button>
  );
}
