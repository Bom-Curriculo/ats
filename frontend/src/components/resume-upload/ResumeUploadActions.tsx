import { Button } from "@/components/ui/button";

interface ResumeUploadActionsProps {
  disabled: boolean;
  onContinue: () => void;
  onCancel: () => void;
}

export function ResumeUploadActions({ disabled, onContinue, onCancel }: ResumeUploadActionsProps) {
  return (
    <div className="mt-8 flex items-center gap-3 ">
      <Button
        onClick={onCancel}
        className="flex-1 px-6 py-5 bg-brand-primary-tint text-brand-primary hover:bg-brand-primary-tint/80"
      >
        Cancelar
      </Button>
      <Button
        disabled={disabled}
        onClick={onContinue}
        className="flex-1 px-6 py-5 bg-brand-primary text-white hover:bg-brand-primary/80"
      >
        Salvar
      </Button>
    </div>
  );
}
