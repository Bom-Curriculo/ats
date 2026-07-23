import { FileText, X } from "lucide-react";

interface SelectedResumeFileProps {
  file: File;
  onRemove: () => void;
}

function formatFileSize(bytes: number) {
  return bytes < 1024 * 1024
    ? `${Math.max(1, Math.round(bytes / 1024))} KB`
    : `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function SelectedResumeFile({ file, onRemove }: SelectedResumeFileProps) {
  return (
    <div className="flex items-center gap-3 rounded-2xl border border-border bg-card p-4">
      <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-brand-primary-tint">
        <FileText className="size-5 text-brand-primary" />
      </span>
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium">{file.name}</p>
        <p className="text-sm text-muted-foreground">{formatFileSize(file.size)}</p>
      </div>
      <button
        onClick={onRemove}
        aria-label="Remover arquivo"
        className="rounded-lg cursor-pointer p-2 text-muted-foreground transition hover:bg-muted hover:text-foreground"
      >
        <X className="size-4" />
      </button>
    </div>
  );
}
