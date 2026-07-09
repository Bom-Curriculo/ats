import { useQuery } from "@tanstack/react-query";
import { getUser } from "@/api/user/get-user";
import { ApplicationProgress } from "../../../components/ui/ApplicationProgress";
import { OptimizationChart } from "../../../components/ui/OptimizationChart";
import { Link } from "react-router-dom";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";

export default function GeneralView() {
    const { data: user } = useQuery({
        queryKey: ["user"],
        queryFn: getUser,
    });

    return (
        <div className="w-full max-w-[1450px] mx-auto px-6 py-6">

            {/* HEADER */}

            <div className="flex items-start justify-between mb-8">
                <div>
                    <h1 className="text-4xl font-bold leading-tight">
                        Bem-vindo,{" "}
                        <span className="text-brand-primary">
                            {user?.name}
                        </span>
                    </h1>

                    <p className="text-gray-500 mt-1">
                        Seus currículos otimizados em um só lugar.
                    </p>
                </div>

                <div className="flex items-center gap-3 rounded-full border border-brand-primary/20 bg-brand-primary/5 px-3 py-1.5">
                    <Avatar className="size-8">
                        <AvatarFallback className="size-full bg-brand-primary text-white text-xs font-semibold">
                            {user?.name?.[0]}
                        </AvatarFallback>
                    </Avatar>

                    <span className="text-sm font-medium">
                        {user?.name}
                    </span>
                </div>
            </div>

            {/* PRIMEIRA LINHA */}

            <section className="grid grid-cols-[2.2fr_340px] gap-6">

                {/* PERFORMANCE */}

                <div className="rounded-2xl border border-gray-200 bg-white p-6">
                    <div className="flex gap-8">
                        <div className="flex-shrink-0">
                            <OptimizationChart />
                        </div>
                        <div className="flex flex-col flex-1">
                            <p className="text-sm text-gray-500">
                                Melhor que 92% dos candidatos
                            </p>
                            <h2 className="text-3xl font-bold mt-1">
                                Performance Geral
                            </h2>
                            <p className="mt-4 text-gray-600 leading-7">
                                Sua pontuação média de otimização está excelente.
                                Foque em adicionar palavras-chave específicas para
                                as vagas de Product Designer para atingir a nota máxima.
                            </p>

                            <div className="flex gap-2 mt-6">
                                <Badge variant="outline">
                                    Keywords
                                </Badge>
                                <Badge variant="outline">
                                    Formatação
                                </Badge>
                            </div>
                        </div>
                    </div>

                </div>

                {/* IA */}

                <div className="rounded-2xl border border-l-4 border-brand-primary bg-brand-primary/5 p-6">
                    <div className="flex items-center gap-3 mb-6">
                        ⭐
                        <h3 className="font-bold text-lg">
                            Dicas da IA
                        </h3>
                    </div>
                    <div className="space-y-5">
                        <div className="flex gap-3">
                            <div className="w-2 h-2 rounded-full bg-brand-primary mt-2" />
                            <p className="text-sm text-gray-700">
                                Inclua métricas quantitativas na seção de experiências para aumentar o score em até 15%.
                            </p>
                        </div>
                        <div className="flex gap-3">
                            <div className="w-2 h-2 rounded-full bg-brand-primary mt-2" />
                            <p className="text-sm text-gray-700">
                                A skill "Agile Methodology" é recorrente nas vagas que você analisou.
                            </p>
                        </div>
                    </div>
                    <button className="mt-8 w-full rounded-lg border-2 border-brand-primary py-2 font-medium text-brand-primary hover:bg-brand-primary/15">
                        Otimizar agora
                    </button>
                </div>
            </section>

            {/* TÍTULO */}

            <div className="flex justify-between items-center mt-10 mb-4">
                <h2 className="text-3xl font-bold">
                    Meus Currículos
                </h2>
                <Link
                    to="/my-curriculum"
                    className="text-brand-primary text-sm font-medium hover:underline"
                >
                    Ver todos
                </Link>
            </div>

            {/* SEGUNDA LINHA */}

            <section className="grid grid-cols-[1fr_1fr_340px] gap-6">
                <div className="rounded-2xl border border-gray-200 bg-white p-6 min-h-[290px]">
                    teste1
                </div>
                <div className="rounded-2xl border border-gray-200 bg-white p-6 min-h-[290px]">
                    teste2
                </div>
                <ApplicationProgress />
            </section>
        </div>
    );
}