import { AlertCircle } from "lucide-react";
import { ResumeDropzone } from "@/components/resume-upload/ResumeDropzone";
import { SelectedResumeFile } from "@/components/resume-upload/SelectedResumeFile";
import { ResumeUploadActions } from "@/components/resume-upload/ResumeUploadActions";

interface ResumeUploadStageProps {
  file: File | null;
  error: string | null;
  acceptedExtensions: string[];
  maxSizeMB: number;
  onFileSelected: (file: File) => void;
  onRemoveFile: () => void;
  onCancel: () => void;
  onContinue: () => void;
}

export function ResumeUploadStage({
  file,
  error,
  acceptedExtensions,
  maxSizeMB,
  onFileSelected,
  onRemoveFile,
  onCancel,
  onContinue,
}: ResumeUploadStageProps) {
  return (
    <div className="flex flex-1 items-center justify-center">
      <div className="w-full max-w-2xl">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-brand-secondary md:text-3xl dark:text-foreground">
            Vamos criar seu perfil
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Envie seu currículo para gerar seu perfil-mestre. Ele será a base para criar
            <br className="hidden sm:block" /> versões otimizadas para cada vaga.
          </p>
        </div>

        <div className="mt-8 space-y-4">
          {!file ? (
            <ResumeDropzone
              acceptedExtensions={acceptedExtensions}
              maxSizeMB={maxSizeMB}
              onFileSelected={onFileSelected}
            />
          ) : (
            <SelectedResumeFile file={file} onRemove={onRemoveFile} />
          )}

          {error && (
            <p role="alert" className="flex items-center gap-1.5 text-sm text-destructive">
              <AlertCircle className="size-4" />
              {error}
            </p>
          )}
        </div>

        <ResumeUploadActions disabled={!file} onContinue={onContinue} onCancel={onCancel} />
      </div>
    </div>
  );
}
