import { PieChart, Pie, Cell } from "recharts";

const data = [
  { name: "Otimizado", value: 75 },
  { name: "Pendente", value: 25 },
];

const COLORS = ["#2e7bff", "#e5e7eb"]; // espelha --color-brand-primary e --color-chart-grid (index.css)

export function OptimizationChart() {
  return (
    <div className="flex flex-col items-center">
      <div className="relative w-[180px] h-[180px]">
  <PieChart width={180} height={180}>
    <Pie
      data={data}
      dataKey="value"
      cx="50%"
      cy="50%"
      innerRadius={55}
      outerRadius={80}
    >
      {data.map((_, index) => (
        <Cell key={index} fill={COLORS[index]} />
      ))}
    </Pie>
  </PieChart>

  <div className="absolute inset-0 flex flex-col items-center justify-center">
    <span className="text-4xl font-bold text-brand-primary">
      75%
    </span>

    <span className="text-sm text-muted-foreground">
      ATS SCORE
    </span>
  </div>

      </div>

    </div>
  );
}