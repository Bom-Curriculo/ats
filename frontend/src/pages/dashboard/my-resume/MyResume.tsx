import ResumesHeader from "@/components/Home/ResumesHeader";
import ResumeList from "@/components/Home/ResumeList";
import ResumeListSkeleton from "@/components/Home/ResumeListSkeleton";
import HomeEmptyState from "@/components/Home/HomeEmptyState";
import AISuggestion from "@/components/Home/AISuggestion";
import { type ResumeCardProps } from "@/components/Home/ResumeCard";

const RESUME_LIMIT = 5;

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
];

export default function MyResume() {
  const isLoading = false;
  const hasResumes = resumes.length > 0;

  return (
    <div className="flex flex-1 flex-col">
      <ResumesHeader />

      {isLoading ? (
        <ResumeListSkeleton />
      ) : hasResumes ? (
        <>
          <ResumeList resumes={resumes} limit={RESUME_LIMIT} />
          <AISuggestion />
        </>
      ) : (
        <div className="flex flex-1 items-center justify-center">
          <HomeEmptyState />
        </div>
      )}
    </div>
  );
}
