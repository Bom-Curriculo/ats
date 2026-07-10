import { Header } from "@/components/Home/Header";
import CurriculumsHeader from "@/components/Home/CurriculumsHeader";
import Card, { type CurriculumCardProps } from "@/components/Home/Card";
import AddCurriculumCard from "@/components/Home/AddCurriculumCard";
import AISuggestion from "@/components/Home/AISuggestion";
import { Skeleton } from "@/components/ui/skeleton";
import UploadCurriculum from "@/components/Home/UploadCurriculum";

const CURRICULUM_LIMIT = 5;

const curriculums: (CurriculumCardProps & { id: string })[] = [
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
  const showEmptyState = true;
  const isLoading = false;
  const aiSuggestion = false;

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <div className="flex flex-1 flex-col p-6">
        {!showEmptyState && <CurriculumsHeader />}

        {isLoading ? (
          <section className="mt-6 grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
            {Array.from({ length: 3 }).map((_, index) => (
              <Skeleton key={index} className="h-48 rounded-2xl" />
            ))}
          </section>
        ) : showEmptyState ? (
          <div className="flex flex-1 items-center justify-center">
            <UploadCurriculum />
          </div>
        ) : (
          <section
            aria-label="Lista de currículos"
            className="mt-6 grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3"
          >
            {curriculums.map(({ id, ...card }) => (
              <Card key={id} {...card} />
            ))}
            <AddCurriculumCard isLimitReached={curriculums.length >= CURRICULUM_LIMIT} limit={CURRICULUM_LIMIT} />
          </section>
        )}

        {aiSuggestion && <AISuggestion />}
      </div>
    </div>
  );
}
