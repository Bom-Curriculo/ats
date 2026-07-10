import { Button } from "@/components/ui/button";

interface ResumeUploadActionsProps {
  disabled: boolean;
  onContinue: () => void;
}

export function ResumeUploadActions({ disabled, onContinue }: ResumeUploadActionsProps) {
  return (
    <div className="mt-8 flex flex-col items-center gap-3">
      <Button
        disabled={disabled}
        onClick={onContinue}
        className="h-9 w-full gap-2 bg-brand-primary px-4 text-white hover:bg-brand-primary/90 lg:h-11"
      >
        Continuar
      </Button>
    </div>
  );
}
