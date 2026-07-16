import { useQuery } from "@tanstack/react-query";
import { getUser } from "@/api/user/get-user";
import { ApplicationProgress } from "../../../components/ui/ApplicationProgress";
import { OptimizationChart } from "../../../components/ui/OptimizationChart";
import { Link } from "react-router-dom";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import {
    Bell,
    CircleCheck,
    FileText,
    MapPin,
    MoreVertical,
    Sparkles,
} from "lucide-react";

const resumes = [
    {
        id: 1,
        name: "Curriculo_ProductDesigner_v2.pdf",
        score: 92,
        updatedAt: "Atualizado há 2 dias",
        tags: ["UX", "UI"],
    },
    {
        id: 2,
        name: "Curriculo_MarketingDigital.pdf",
        score: 78,
        updatedAt: "Atualizado há 1 semana",
        tags: ["MKT"],
    },
];

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

                    <p className="text-muted-foreground mt-1">
                        Seus currículos otimizados em um só lugar.
                    </p>
                </div>

                <div className="flex items-center gap-4">
                    <button
                        type="button"
                        aria-label="Notificações"
                        className="text-brand-secondary transition-colors hover:text-brand-primary"
                    >
                        <Bell className="size-6" />
                    </button>

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
            </div>

            {/* PRIMEIRA LINHA */}

            <section className="grid grid-cols-[2.2fr_340px] gap-6">

                {/* PERFORMANCE */}

                <div className="rounded-2xl border border-border bg-card p-6">
                    <div className="flex gap-8">
                        <div className="flex-shrink-0">
                            <OptimizationChart />
                        </div>
                        <div className="flex flex-col flex-1">
                            <div className="flex flex-wrap items-center gap-2">
                                <Badge className="border-transparent bg-brand-primary text-white">
                                    MÉDIA GLOBAL
                                </Badge>
                                <p className="text-sm text-muted-foreground">
                                    Melhor que 92% dos candidatos
                                </p>
                            </div>
                            <h2 className="text-3xl font-bold mt-2">
                                Performance Geral
                            </h2>
                            <p className="mt-4 text-muted-foreground leading-7">
                                Sua pontuação média de otimização está excelente.
                                Foque em adicionar palavras-chave específicas para
                                as vagas de Product Designer para atingir a nota máxima.
                            </p>

                            <div className="flex gap-2 mt-6">
                                <span className="inline-flex items-center gap-1.5 rounded-full bg-brand-primary/15 px-3 py-1 text-sm font-medium text-brand-primary">
                                    <CircleCheck className="size-4" /> Keywords
                                </span>
                                <span className="inline-flex items-center gap-1.5 rounded-full bg-brand-primary/15 px-3 py-1 text-sm font-medium text-brand-primary">
                                    <CircleCheck className="size-4" /> Formatação
                                </span>
                            </div>
                        </div>
                    </div>

                </div>

                {/* IA */}

                <div className="rounded-2xl border border-l-4 border-brand-primary bg-brand-primary/5 p-6">
                    <div className="flex items-center gap-2 mb-6">
                        <Sparkles className="size-5 text-brand-primary" />
                        <h3 className="font-bold text-lg">
                            Dicas da IA
                        </h3>
                    </div>
                    <div className="space-y-5">
                        <div className="flex gap-3">
                            <MapPin className="size-4 shrink-0 text-brand-primary mt-0.5" />
                            <p className="text-sm text-muted-foreground">
                                Inclua métricas quantitativas na seção de experiências para aumentar o score em até 15%.
                            </p>
                        </div>
                        <div className="flex gap-3">
                            <MapPin className="size-4 shrink-0 text-brand-primary mt-0.5" />
                            <p className="text-sm text-muted-foreground">
                                A skill "Agile Methodology" é recorrente nas vagas que você analisou.
                            </p>
                        </div>
                    </div>
                    <button className="mt-8 w-full rounded-lg border-2 border-brand-primary py-2 font-medium text-brand-primary hover:bg-brand-primary/15">
                        Otimizar agora
                    </button>
                </div>
            </section>

            {/* SEGUNDA LINHA */}

            <section className="grid grid-cols-[1fr_340px] gap-6 mt-10 items-start">
                <div>
                    {/* TÍTULO */}
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-3xl font-bold">
                            Meus Currículos
                        </h2>
                        <Link
                            to="/my-resume"
                            className="text-brand-primary text-sm font-medium hover:underline"
                        >
                            Ver todos
                        </Link>
                    </div>

                    {/* CARDS */}
                    <div className="grid grid-cols-2 gap-6">
                        {resumes.map((resume) => (
                            <div
                                key={resume.id}
                                className="flex flex-col justify-between rounded-2xl border border-border bg-card p-6 min-h-[290px]"
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex size-12 items-center justify-center rounded-lg bg-brand-primary/10">
                                        <FileText className="size-6 text-brand-primary" />
                                    </div>
                                    <div className="text-right">
                                        <span className="block text-2xl font-bold">
                                            {resume.score}
                                        </span>
                                        <span className="text-xs font-medium text-muted-foreground">
                                            ATS SCORE
                                        </span>
                                    </div>
                                </div>

                                <div className="mt-4">
                                    <h3 className="font-semibold break-all">
                                        {resume.name}
                                    </h3>
                                    <p className="mt-1 text-sm text-muted-foreground">
                                        {resume.updatedAt}
                                    </p>
                                </div>

                                <div className="mt-4 flex items-center justify-between">
                                    <div className="flex gap-2">
                                        {resume.tags.map((tag) => (
                                            <Badge key={tag} variant="secondary">
                                                {tag}
                                            </Badge>
                                        ))}
                                    </div>
                                    <button
                                        type="button"
                                        aria-label="Mais opções"
                                        className="text-muted-foreground hover:text-foreground"
                                    >
                                        <MoreVertical className="size-5" />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <ApplicationProgress />
            </section>
        </div>
    );
}