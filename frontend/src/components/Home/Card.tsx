import { ChartSpline, Clock, Download, FileText, Trash2, Zap } from "lucide-react";

export interface CurriculumCardProps {
  fileName: string;
  matchPercentage: number;
  updatedLabel: string;
  tags: string[];
  maxVisibleTags?: number;
  onDownload?: () => void;
  onMatch?: () => void;
  onDelete?: () => void;
}

export default function Card({
  fileName,
  matchPercentage,
  updatedLabel,
  tags,
  maxVisibleTags = 3,
  onDownload,
  onMatch,
  onDelete,
}: CurriculumCardProps) {
  const visibleTags = tags.slice(0, maxVisibleTags);
  const hiddenCount = tags.length - visibleTags.length;

  return (
    <article className="flex flex-col rounded-2xl border border-gray-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md">
      <header className="flex items-start justify-between gap-3">
        <div
          aria-hidden="true"
          className="flex size-10 md:size-12 shrink-0 items-center justify-center rounded-xl bg-[#DCE1FF]"
        >
          <FileText className="size-6 text-[#03206E]" />
        </div>
        <p className="inline-flex items-center gap-1.5 rounded-full bg-[#2E7BFF] px-3 py-1.5 text-xs font-semibold text-white">
          <Zap className="size-4 fill-current" aria-hidden="true" />
          {matchPercentage}% Match
        </p>
      </header>

      <h3 className="mt-4 line-clamp-2 sm:text-lg leading-snug font-bold wrap-break-word text-[#03206E]">{fileName}</h3>

      <p className="mt-1.5 flex items-center gap-1.5 text-xs sm:text-sm text-gray-500">
        <Clock className="size-3 sm:size-4 shrink-0" aria-hidden="true" />
        <time>Atualizado {updatedLabel}</time>
      </p>

      {tags.length > 0 && (
        <ul aria-label="Tecnologias identificadas" className="mt-4 flex flex-wrap gap-2">
          {visibleTags.map((tag) => (
            <li key={tag} className="rounded-full bg-[#EFF4FF] px-3 py-1 text-xs font-medium text-[#03206E]">
              {tag}
            </li>
          ))}
          {hiddenCount > 0 && (
            <li className="rounded-full bg-[#EFF4FF] px-3 py-1 text-xs font-medium text-[#03206E]">+{hiddenCount}</li>
          )}
        </ul>
      )}

      <footer className="mt-5 grid grid-cols-3 gap-2 border-t border-gray-100 pt-4">
        <button
          type="button"
          onClick={onDownload}
          className="flex cursor-pointer flex-col items-center gap-1.5 rounded-lg py-1.5 text-xs font-medium text-gray-600 transition-colors hover:bg-gray-50 hover:text-[#2E7BFF]"
        >
          <Download className="size-5" aria-hidden="true" />
          Baixar
        </button>
        <button
          type="button"
          onClick={onMatch}
          className="flex cursor-pointer flex-col items-center gap-1.5 rounded-lg py-1.5 text-xs font-medium text-gray-600 transition-colors hover:bg-gray-50 hover:text-[#2E7BFF]"
        >
          <ChartSpline className="size-5" aria-hidden="true" />
          Match
        </button>
        <button
          type="button"
          onClick={onDelete}
          className="flex cursor-pointer flex-col items-center gap-1.5 rounded-lg py-1.5 text-xs font-medium text-gray-600 transition-colors hover:bg-red-50 hover:text-red-600"
        >
          <Trash2 className="size-5" aria-hidden="true" />
          Excluir
        </button>
      </footer>
    </article>
  );
}
