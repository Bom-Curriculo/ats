import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

const data = [
    { day: "SEG", value: 20 },
    { day: "TER", value: 35 },
    { day: "QUA", value: 50 },
    { day: "QUI", value: 30 },
    { day: "SEX", value: 40 },
    { day: "SAB", value: 25 },
    { day: "DOM", value: 45 },
]

export function ApplicationProgress() {
    return (
        <div className="bg-white rounded-xl shadow p-6 flex flex-col h-full">
            <h3 className="text-lg font-semibold mb-4">Progresso de Aplicações</h3>
            
            <ResponsiveContainer width="100%" height={250}>
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="day" />
                    <YAxis />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: "#fff",
                            border: "1px solid #e5e7eb",
                            borderRadius: "8px"
                        }}
                    />
                    <Bar dataKey="value" fill="#2e7bff" radius={[8, 8, 0, 0]} />
                </BarChart>
            </ResponsiveContainer>
        </div>
    )
}
