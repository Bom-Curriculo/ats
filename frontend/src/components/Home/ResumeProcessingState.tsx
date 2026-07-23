import { Loader2 } from "lucide-react";

export default function ResumeProcessingState() {
  return (
    <div className="flex flex-1 items-center justify-center">
      <div role="status" className="flex w-full max-w-md flex-col items-center gap-4 rounded-2xl p-12 text-center">
        <span aria-hidden="true" className="flex size-14 items-center justify-center rounded-full bg-brand-primary-tint">
          <Loader2 className="size-6 animate-spin text-brand-primary" />
        </span>
        <div>
          <h2 className="text-xl font-bold text-brand-secondary">Nossa IA está analisando seu currículo</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Iremos te notificar assim que terminar.
          </p>
        </div>
      </div>
    </div>
  );
}
