import Header from "@/components/MyCurriculum/Header";
import Card, { type CurriculumCardProps } from "@/components/MyCurriculum/Card";

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
      </section>
    </>
  );
}
