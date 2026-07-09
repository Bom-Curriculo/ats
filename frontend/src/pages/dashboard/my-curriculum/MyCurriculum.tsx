import Header from "@/components/MyCurriculum/Header";
import Card, { type CurriculumCardProps } from "@/components/MyCurriculum/Card";
import AddCurriculumCard from "@/components/MyCurriculum/AddCurriculumCard";
import AISuggestion from "@/components/MyCurriculum/AISuggestion";

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

export default function MyCurriculum() {
  return (
    <>
      <Header />
      <section
        aria-label="Lista de currículos"
        className="mt-6 grid grid-cols-1 gap-5 lg:grid-cols-2 xl:grid-cols-3"
      >
        {curriculums.map(({ id, ...card }) => (
          <Card key={id} {...card} />
        ))}
        <AddCurriculumCard
          isLimitReached={curriculums.length >= CURRICULUM_LIMIT}
          limit={CURRICULUM_LIMIT}
        />
      </section>
      <AISuggestion />
    </>
  );
}
