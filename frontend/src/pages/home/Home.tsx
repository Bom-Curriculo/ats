import { useNavigate } from "react-router-dom";
import { Header } from "@/components/Home/Header";
import ResumesHeader from "@/components/Home/ResumesHeader";
import ResumeCard, { type ResumeCardProps } from "@/components/Home/ResumeCard";
import AddResumeCard from "@/components/Home/AddResumeCard";
import AISuggestion from "@/components/Home/AISuggestion";
import { Skeleton } from "@/components/ui/skeleton";
import HomeEmptyState from "@/components/Home/HomeEmptyState";

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
  const navigate = useNavigate();
  const showEmptyState = true;
  const isLoading = false;
  const aiSuggestion = false;

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <div className="flex flex-1 flex-col p-6">
        {!showEmptyState && <ResumesHeader />}

        {isLoading ? (
          <section className="mt-6 grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
            {Array.from({ length: 3 }).map((_, index) => (
              <Skeleton key={index} className="h-48 rounded-2xl" />
            ))}
          </section>
        ) : showEmptyState ? (
          <div className="flex flex-1 items-center justify-center">
            <HomeEmptyState onUpload={() => navigate("/resume-upload")} />
          </div>
        ) : (
          <section
            aria-label="Lista de currículos"
            className="mt-6 grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3"
          >
            {resumes.map(({ id, ...card }) => (
              <ResumeCard key={id} {...card} />
            ))}
            <AddResumeCard isLimitReached={resumes.length >= RESUME_LIMIT} limit={RESUME_LIMIT} />
          </section>
        )}

        {aiSuggestion && <AISuggestion />}
      </div>
    </div>
  );
}
