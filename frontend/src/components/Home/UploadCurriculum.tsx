import { UploadCloud } from "lucide-react";
import { Button } from "../ui/button";

interface UploadCurriculumProps {
  onUpload?: () => void;
}

export default function UploadCurriculum({ onUpload }: UploadCurriculumProps) {
  return (
    <div role="status" className="flex w-full flex-col items-center justify-center gap-4 rounded-2xl p-12 text-center">
      <span aria-hidden="true" className="flex size-14 items-center justify-center rounded-full bg-brand-primary-tint">
        <UploadCloud className="size-6 text-brand-primary" />
      </span>
      <div>
        <h2 className="text-xl font-bold text-brand-secondary">Você ainda não enviou nenhum currículo</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Envie seu currículo ou conecte seu LinkedIn para começar
          <br />a criar versões otimizadas para vagas.
        </p>
      </div>
      <Button
        onClick={onUpload}
        className="h-9 gap-2 bg-brand-primary px-4 text-white hover:bg-brand-primary/90 lg:h-11"
      >
        <UploadCloud className="size-4" />
        <span>Enviar Currículo</span>
      </Button>
    </div>
  );
}
