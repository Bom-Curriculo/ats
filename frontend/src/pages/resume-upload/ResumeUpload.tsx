import { useNavigate } from "react-router-dom";
import { AlertCircle, ArrowLeft } from "lucide-react";
import { Header } from "@/components/Home/Header";
import { ResumeDropzone } from "@/components/resume-upload/ResumeDropzone";
import { SelectedResumeFile } from "@/components/resume-upload/SelectedResumeFile";
import { ResumeUploadActions } from "@/components/resume-upload/ResumeUploadActions";
import { useResumeFile } from "@/hooks/use-resume-file";

export default function ResumeUpload() {
  const navigate = useNavigate();
  const { file, error, acceptedExtensions, maxSizeMB, selectFile, removeFile } = useResumeFile();

  function handleContinue() {
  }

  return (
    <div className="flex min-h-screen flex-col">
      <Header />

      <div className="flex flex-1 justify-center p-6">
        <div className="w-full max-w-2xl">
          <button
            onClick={() => navigate("/")}
            className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition hover:text-foreground"
          >
            <ArrowLeft className="size-4" />
            Voltar
          </button>

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
                onFileSelected={selectFile}
              />
            ) : (
              <SelectedResumeFile file={file} onRemove={removeFile} />
            )}

            {error && (
              <p role="alert" className="flex items-center gap-1.5 text-sm text-destructive">
                <AlertCircle className="size-4" />
                {error}
              </p>
            )}
          </div>

          <ResumeUploadActions disabled={!file} onContinue={handleContinue} />
        </div>
      </div>
    </div>
  );
}
