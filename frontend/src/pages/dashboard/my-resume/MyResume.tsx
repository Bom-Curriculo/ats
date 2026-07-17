import { useState } from "react";
import { toast } from "sonner";

import ResumesHeader from "@/components/Home/ResumesHeader";
import ResumeList from "@/components/Home/ResumeList";
import ResumeListSkeleton from "@/components/Home/ResumeListSkeleton";
import HomeEmptyState from "@/components/Home/HomeEmptyState";
import AISuggestion from "@/components/Home/AISuggestion";
import DeleteResumeDialog from "@/components/Home/DeleteResumeDialog";
import { type ResumeCardProps } from "@/components/Home/ResumeCard";

const RESUME_LIMIT = 5;

type Resume = ResumeCardProps & { id: string };

const initialResumes: Resume[] = [
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
];

export default function MyResume() {
  const isLoading = false;
  const [resumes, setResumes] = useState<Resume[]>(initialResumes);
  const [resumeToDelete, setResumeToDelete] = useState<Resume | null>(null);

  const hasResumes = resumes.length > 0;

  function handleRequestDelete(id: string) {
    const resume = resumes.find((item) => item.id === id) ?? null;
    setResumeToDelete(resume);
  }

  function handleConfirmDelete() {
    if (!resumeToDelete) return;

    setResumes((prev) => prev.filter((resume) => resume.id !== resumeToDelete.id));
    toast.success("Currículo excluído com sucesso.");
    setResumeToDelete(null);
  }

  return (
    <div className="flex flex-1 flex-col">
      <ResumesHeader count={resumes.length} limit={RESUME_LIMIT} />

      {isLoading ? (
        <ResumeListSkeleton />
      ) : hasResumes ? (
        <>
          <ResumeList resumes={resumes} limit={RESUME_LIMIT} onDeleteResume={handleRequestDelete} />
          <AISuggestion />
        </>
      ) : (
        <div className="flex flex-1 items-center justify-center">
          <HomeEmptyState />
        </div>
      )}

      <DeleteResumeDialog
        open={resumeToDelete !== null}
        fileName={resumeToDelete?.fileName}
        onOpenChange={(open) => !open && setResumeToDelete(null)}
        onConfirm={handleConfirmDelete}
      />
    </div>
  );
}
