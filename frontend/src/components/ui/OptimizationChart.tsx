import { PieChart, Pie, Cell } from "recharts";
import { Badge } from "././badge";

const data = [
  { name: "Otimizado", value: 75 },
  { name: "Pendente", value: 25 },
];

const COLORS = ["#3b82f6", "#e5e7eb"];

export function OptimizationChart() {
  return (
    <div className="flex flex-col items-center">

      <Badge className="mb-4 bg-blue-600 text-white">
        MÉDIA GLOBAL
      </Badge>

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
    <span className="text-4xl font-bold text-blue-700">
      75%
    </span>

    <span className="text-sm text-gray-500">
      ATS SCORE
    </span>
  </div>

      </div>

    </div>
  );
}