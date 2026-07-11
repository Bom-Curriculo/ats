import { useState } from "react";
import { Header } from "@/components/Home/Header";
import ResumesHeader from "@/components/Home/ResumesHeader";
import { type ResumeCardProps } from "@/components/Home/ResumeCard";
import AISuggestion from "@/components/Home/AISuggestion";
import HomeEmptyState from "@/components/Home/HomeEmptyState";
import ResumeListSkeleton from "@/components/Home/ResumeListSkeleton";
import ResumeProcessingState from "@/components/Home/ResumeProcessingState";
import ResumeList from "@/components/Home/ResumeList";
import { ResumeUploadStage } from "@/components/resume-upload/ResumeUploadStage";
import { useResumeFile } from "@/hooks/use-resume-file";

const RESUME_LIMIT = 5;

type OnboardingStage = "empty" | "uploading" | "processing";

const resumes: (ResumeCardProps & { id: string })[] = [
  {
    id: "1",
    fileName: "Curriculo_Engenheiro_Senior.pdf",
    matchPercentage: 85,
    updatedLabel: "há 2 dias",
    tags: ["React", "Node.js", "AWS", "TypeScript", "Docker", "GraphQL"],
  },
  {
    id: "2",
    fileName: "Curriculo_Product_Designer.pdf",
    matchPercentage: 72,
    updatedLabel: "há 5 dias",
    tags: ["Figma", "UX Research"],
  },
  {
    id: "3",
    fileName: "Curriculo_Desenvolvedor_FullStack.pdf",
    matchPercentage: 91,
    updatedLabel: "há 1 dia",
    tags: ["React", "Next.js", "Node.js", "PostgreSQL", "Prisma", "Tailwind CSS"],
  },
  {
    id: "4",
    fileName: "Curriculo_Cientista_Dados.pdf",
    matchPercentage: 78,
    updatedLabel: "há 3 dias",
    tags: ["Python", "Pandas", "SQL", "Machine Learning", "TensorFlow", "Power BI"],
  },
  // {
  //   id: "5",
  //   fileName: "Curriculo_DevOps_Engineer.pdf",
  //   matchPercentage: 88,
  //   updatedLabel: "há 6 horas",
  //   tags: ["AWS", "Kubernetes", "Docker", "Terraform", "CI/CD", "Linux"],
  // },
];

export default function Home() {
  const [stage, setStage] = useState<OnboardingStage>("empty");
  const { file, error, acceptedExtensions, maxSizeMB, selectFile, removeFile } = useResumeFile();
  const showEmptyState = true;
  const isLoading = false;
  const aiSuggestion = false;

  function handleCancelUpload() {
    removeFile();
    setStage("empty");
  }

  function handleConfirmUpload() {
    // envia o curriculo para o back
    setStage("processing");
  }

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <div className="flex flex-1 flex-col p-6">
        {!showEmptyState && <ResumesHeader />}

        {isLoading ? (
          <ResumeListSkeleton />
        ) : stage === "processing" ? (
          <ResumeProcessingState />
        ) : stage === "uploading" ? (
          <ResumeUploadStage
            file={file}
            error={error}
            acceptedExtensions={acceptedExtensions}
            maxSizeMB={maxSizeMB}
            onFileSelected={selectFile}
            onRemoveFile={removeFile}
            onCancel={handleCancelUpload}
            onContinue={handleConfirmUpload}
          />
        ) : showEmptyState ? (
          <div className="flex flex-1 items-center justify-center">
            <HomeEmptyState onUpload={() => setStage("uploading")} />
          </div>
        ) : (
          <ResumeList resumes={resumes} limit={RESUME_LIMIT} />
        )}

        {aiSuggestion && <AISuggestion />}
      </div>
    </div>
  );
}
