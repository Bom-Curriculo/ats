import { useEffect, useState } from "react";
import { Header } from "@/components/Home/Header";
import ResumesHeader from "@/components/Home/ResumesHeader";
import { type ResumeCardProps } from "@/components/Home/ResumeCard";
import AISuggestion from "@/components/Home/AISuggestion";
import HomeEmptyState from "@/components/Home/HomeEmptyState";
import ResumeListSkeleton from "@/components/Home/ResumeListSkeleton";
import ResumeProcessingState from "@/components/Home/ResumeProcessingState";
import ResumeList from "@/components/Home/ResumeList";
import { ResumeUploadStage } from "@/components/resume-upload/ResumeUploadStage";
import { ResumeReviewStage, type ReviewSection } from "@/components/resume-upload/ResumeReviewStage";
import { useResumeFile } from "@/hooks/use-resume-file";

const RESUME_LIMIT = 5;

type OnboardingStage = "empty" | "uploading" | "processing" | "reviewing";

// TODO: substituir pelos dados retornados pela IA/backend (Gustavo)
const reviewSections: ReviewSection[] = [
  {
    id: "experiences",
    title: "Experiências",
    items: [
      { id: "exp-1", title: "Bom Currículo", description: "De: 02/06/2025 à 02/07/2026" },
      { id: "exp-2", title: "Faculdade Uniasselvi", description: "De: 02/06/2025 à 02/07/2026" },
      { id: "exp-3", title: "WhiteHats", description: "De: 02/06/2025 à 02/07/2026" },
    ],
  },
  {
    id: "skills",
    title: "Habilidades",
    items: [
      { id: "skill-php", title: "PHP", description: "15 anos de experiência" },
      { id: "skill-laravel", title: "Laravel", description: "8 anos de experiência" },
      { id: "skill-react", title: "React", description: "5 anos de experiência" },
    ],
  },
];

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

  function handleGenerateResume(selectedItemIds: string[]) {
    // TODO: enviar os dados confirmados pro backend gerar o currículo
    console.log("Itens confirmados:", selectedItemIds);
    setStage("empty");
  }

  useEffect(() => {
    if (stage !== "processing") return;

    // TODO: substituir pela espera real da resposta da IA/backend
    const timeout = setTimeout(() => setStage("reviewing"), 2000);
    return () => clearTimeout(timeout);
  }, [stage]);

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <div className="flex flex-1 flex-col p-6">
        {!showEmptyState && <ResumesHeader />}

        {isLoading ? (
          <ResumeListSkeleton />
        ) : stage === "processing" ? (
          <ResumeProcessingState />
        ) : stage === "reviewing" ? (
          <ResumeReviewStage sections={reviewSections} onGenerate={handleGenerateResume} />
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
