import { Link } from "react-router-dom";
import { PieChart, Pie, Cell } from "recharts";
import {
    Bell,
    CircleCheck,
    CircleUserRound,
    Download,
    Link2,
    Plus,
    Save,
    Sparkles,
    XCircle,
    Zap,
} from "lucide-react";

const profile = {
    name: "Alexandre Martins",
    location: "São Paulo, SP",
    email: "alexandre.m@email.com",
    linkedin: "linkedin.com/in/alexandre",
    summary:
        "Engenheiro de Software Sênior com mais de 8 anos de experiência em desenvolvimento Full Stack, focado em arquiteturas escaláveis e liderança técnica. Especialista em ecossistemas Cloud e otimização de performance.",
};

const experiences = [
    {
        role: "Tech Lead & Full Stack Developer",
        period: "Jan 2020 - Presente",
        company: "GlobalTech Solutions",
        description:
            "Liderança de uma equipe de 10 desenvolvedores na migração de monolito para microserviços, reduzindo o tempo de resposta da API em 45%. Implementação de pipelines CI/CD que elevaram a frequência de deploys diários.",
    },
    {
        role: "Senior Software Engineer",
        period: "Mar 2017 - Dez 2019",
        company: "Innovation Hub",
        description:
            "Desenvolvimento de aplicações reativas utilizando React e Node.js para o setor bancário.",
    },
];

const education = [
    {
        degree: "Bacharelado em Ciência da Computação",
        period: "Concluído em 2016",
        institution: "Universidade Federal de São Paulo",
    },
];

const matchedKeywords = ["CI/CD", "Microserviços", "Cloud", "Full Stack"];
const keywordScore = "8/12";
const suggestedKeywords = ["Kubernetes", "AWS", "Terraform"];

const formattingChecks = [
    { label: "Fontes padrão ATS (Manrope)", ok: true },
    { label: "Margens ideais detectadas", ok: true },
    { label: "Seção de 'Habilidades' não encontrada", ok: false },
];

const atsScore = 75;
const gaugeData = [
    { name: "Pontuação", value: atsScore },
    { name: "Restante", value: 100 - atsScore },
];
const GAUGE_COLORS = ["var(--color-brand-primary)", "var(--color-border)"];

const navItems = [
    { label: "Dashboard", to: "/dashboard" },
    { label: "Editor", to: "/editor" },
    { label: "Vagas", to: "/job-analysis" },
    { label: "Preços", to: "/" },
];

export default function Editor() {
    return (
        <div className="min-h-screen bg-background">
            {/* TOP BAR */}
            <header className="flex items-center justify-between border-b border-border bg-background px-8 py-3">
                <div className="flex items-center gap-8">
                    <div className="flex items-center gap-1">
                        <img
                            src="/logo-dark.png"
                            alt="BomCurriculo"
                            className="h-8 w-auto dark:hidden"
                        />
                        <img
                            src="/logo.png"
                            alt="BomCurriculo"
                            className="hidden h-8 w-auto dark:block"
                        />
                        <span className="text-lg font-semibold text-brand-secondary dark:text-white">
                            Bom <span className="text-brand-primary">Currículo</span>
                        </span>
                    </div>

                    <nav className="flex items-center gap-6 text-sm font-medium text-muted-foreground">
                        {navItems.map((item) => {
                            const isActive = item.label === "Editor";
                            return (
                                <Link
                                    key={item.label}
                                    to={item.to}
                                    className={
                                        isActive
                                            ? "border-b-2 border-brand-primary pb-1 text-brand-primary"
                                            : "pb-1 hover:text-foreground"
                                    }
                                >
                                    {item.label}
                                </Link>
                            );
                        })}
                    </nav>
                </div>

                <div className="flex items-center gap-4">
                    <span className="inline-flex items-center gap-2 rounded-lg border border-border px-3 py-1.5 text-sm text-muted-foreground">
                        <Save className="size-4" />
                        Salvo automaticamente
                    </span>

                    <button
                        type="button"
                        className="inline-flex items-center gap-2 rounded-lg bg-brand-secondary px-4 py-2 text-sm font-medium text-brand-secondary-foreground hover:bg-brand-secondary/90"
                    >
                        <Download className="size-4" />
                        Exportar PDF
                    </button>

                    <button
                        type="button"
                        aria-label="Notificações"
                        className="text-muted-foreground transition-colors hover:text-foreground"
                    >
                        <Bell className="size-5" />
                    </button>

                    <button
                        type="button"
                        aria-label="Perfil"
                        className="text-muted-foreground transition-colors hover:text-foreground"
                    >
                        <CircleUserRound className="size-6" />
                    </button>
                </div>
            </header>

            {/* CONTEÚDO */}
            <div className="grid grid-cols-[1fr_380px]">
                {/* EDITOR / PREVIEW DO CURRÍCULO */}
                <section className="p-8">
                    <div className="rounded-2xl border border-border bg-card p-10">
                        <div className="text-center">
                            <h1 className="text-4xl font-bold tracking-tight text-brand-secondary">
                                {profile.name.toUpperCase()}
                            </h1>
                            <p className="mt-2 text-sm text-muted-foreground">
                                {profile.location} • {profile.email} •{" "}
                                {profile.linkedin}
                            </p>
                        </div>

                        <div className="mt-10">
                            <h2 className="text-xl font-bold text-brand-secondary">
                                Resumo Profissional
                            </h2>
                            <div className="mt-2 border-t border-border" />
                            <p className="mt-4 leading-7 text-muted-foreground">
                                {profile.summary}
                            </p>
                        </div>

                        <div className="mt-10">
                            <div className="flex items-center justify-between">
                                <h2 className="text-xl font-bold text-brand-secondary">
                                    Experiência Profissional
                                </h2>
                                <button
                                    type="button"
                                    className="inline-flex items-center gap-1 text-sm font-medium text-brand-primary hover:underline"
                                >
                                    <Plus className="size-4" />
                                    Adicionar
                                </button>
                            </div>
                            <div className="mt-2 border-t border-border" />

                            <div className="mt-6 space-y-6">
                                {experiences.map((exp) => (
                                    <div key={exp.role}>
                                        <div className="flex items-start justify-between gap-4">
                                            <h3 className="font-semibold text-brand-secondary">
                                                {exp.role}
                                            </h3>
                                            <span className="shrink-0 text-sm text-muted-foreground">
                                                {exp.period}
                                            </span>
                                        </div>
                                        <p className="text-sm font-medium text-brand-primary">
                                            {exp.company}
                                        </p>
                                        <p className="mt-2 leading-7 text-muted-foreground">
                                            {exp.description}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="mt-10">
                            <div className="flex items-center justify-between">
                                <h2 className="text-xl font-bold text-brand-secondary">
                                    Educação
                                </h2>
                                <button
                                    type="button"
                                    className="inline-flex items-center gap-1 text-sm font-medium text-brand-primary hover:underline"
                                >
                                    <Plus className="size-4" />
                                    Adicionar
                                </button>
                            </div>
                            <div className="mt-2 border-t border-border" />

                            <div className="mt-6 space-y-6">
                                {education.map((edu) => (
                                    <div key={edu.degree}>
                                        <div className="flex items-start justify-between gap-4">
                                            <h3 className="font-semibold text-brand-secondary">
                                                {edu.degree}
                                            </h3>
                                            <span className="shrink-0 text-sm text-muted-foreground">
                                                {edu.period}
                                            </span>
                                        </div>
                                        <p className="text-sm text-muted-foreground">
                                            {edu.institution}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </section>

                {/* PAINEL DE ANÁLISE ATS */}
                <aside className="flex flex-col justify-between border-l border-border bg-brand-primary/5 p-8">
                    <div>
                        <h2 className="text-xl font-bold text-brand-secondary">
                            Análise em Tempo Real
                        </h2>

                        <div className="mt-6 flex flex-col items-center">
                            <div className="relative size-[160px]">
                                <PieChart width={160} height={160}>
                                    <Pie
                                        data={gaugeData}
                                        dataKey="value"
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={58}
                                        outerRadius={72}
                                        startAngle={90}
                                        endAngle={-270}
                                        stroke="none"
                                    >
                                        {gaugeData.map((entry, index) => (
                                            <Cell key={entry.name} fill={GAUGE_COLORS[index]} />
                                        ))}
                                    </Pie>
                                </PieChart>
                                <div className="absolute inset-0 flex flex-col items-center justify-center">
                                    <span className="text-3xl font-bold text-brand-primary">
                                        {atsScore}
                                    </span>
                                    <span className="text-xs text-muted-foreground">
                                        Pontuação ATS
                                    </span>
                                </div>
                            </div>

                            <p className="mt-4 text-center text-sm text-muted-foreground">
                                Seu currículo está acima da média, mas pode melhorar a
                                densidade de palavras-chave.
                            </p>
                        </div>

                        <div className="mt-6 border-t border-border" />

                        <div className="mt-6">
                            <div className="flex items-center justify-between">
                                <span className="inline-flex items-center gap-2 text-sm font-semibold text-brand-secondary">
                                    <Link2 className="size-4" />
                                    Palavras-chave
                                </span>
                                <span className="rounded-full bg-brand-primary px-2 py-0.5 text-xs font-semibold text-brand-primary-foreground">
                                    {keywordScore}
                                </span>
                            </div>

                            <div className="mt-3 flex flex-wrap gap-2">
                                {matchedKeywords.map((keyword) => (
                                    <span
                                        key={keyword}
                                        className="inline-flex items-center gap-1 rounded-full bg-brand-primary-tint px-3 py-1 text-xs font-medium text-brand-primary"
                                    >
                                        <CircleCheck className="size-3.5" />
                                        {keyword}
                                    </span>
                                ))}
                            </div>

                            <div className="mt-4 rounded-lg border border-border p-3">
                                <p className="text-xs text-muted-foreground">
                                    Recomendadas para a vaga:
                                </p>
                                <div className="mt-2 flex flex-wrap gap-2">
                                    {suggestedKeywords.map((keyword) => (
                                        <span
                                            key={keyword}
                                            className="rounded-full bg-muted px-3 py-1 text-xs font-medium text-muted-foreground"
                                        >
                                            + {keyword}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </div>

                        <div className="mt-6 rounded-xl border-l-4 border-brand-primary bg-card p-4 shadow-sm">
                            <div className="flex items-center gap-2">
                                <Sparkles className="size-4 text-brand-primary" />
                                <h3 className="text-sm font-semibold text-brand-secondary">
                                    Dica de Impacto
                                </h3>
                            </div>
                            <p className="mt-2 text-sm text-muted-foreground italic">
                                "Sua descrição de experiência na GlobalTech é forte, mas
                                você poderia quantificar melhor seus resultados. Tente
                                adicionar métricas financeiras ou de tempo."
                            </p>
                        </div>

                        <div className="mt-6">
                            <h3 className="text-sm font-semibold text-brand-secondary">
                                Formatação
                            </h3>
                            <div className="mt-3 space-y-2">
                                {formattingChecks.map((check) => (
                                    <div
                                        key={check.label}
                                        className="flex items-center gap-2 text-sm"
                                    >
                                        {check.ok ? (
                                            <CircleCheck className="size-4 shrink-0 text-success" />
                                        ) : (
                                            <XCircle className="size-4 shrink-0 text-destructive" />
                                        )}
                                        <span
                                            className={
                                                check.ok
                                                    ? "text-muted-foreground"
                                                    : "text-destructive"
                                            }
                                        >
                                            {check.label}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    <button
                        type="button"
                        className="sticky bottom-8 mt-8 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-brand-secondary py-3 font-medium text-brand-secondary-foreground hover:bg-brand-secondary/90"
                    >
                        Otimizar com IA Agora
                        <Zap className="size-4" />
                    </button>
                </aside>
            </div>
        </div>
    );
}
