import { useQuery } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router-dom";
import { getUser } from "@/api/user/get-user";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { getJobById, jobs } from "./jobs-data";
import {
    ArrowLeft,
    ArrowUpRight,
    Bell,
    Bookmark,
    Briefcase,
    Building2,
    CheckCircle2,
    Clock,
    MapPin,
    Send,
    Share2,
    Sparkles,
    Star,
    Wallet,
    Wand2,
    X,
} from "lucide-react";

function CompatibilityRing({ value }: { value: number }) {
    const radius = 42;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (value / 100) * circumference;

    return (
        <div className="relative flex size-32 items-center justify-center">
            <svg viewBox="0 0 100 100" className="size-32 -rotate-90">
                <circle
                    cx="50"
                    cy="50"
                    r={radius}
                    fill="none"
                    stroke="var(--color-brand-primary-tint)"
                    strokeWidth="10"
                />
                <circle
                    cx="50"
                    cy="50"
                    r={radius}
                    fill="none"
                    stroke="var(--color-brand-primary)"
                    strokeWidth="10"
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                />
            </svg>
            <div className="absolute flex flex-col items-center">
                <span className="text-2xl font-bold text-brand-secondary">{value}%</span>
                <span className="text-xs text-muted-foreground">compatível</span>
            </div>
        </div>
    );
}

export default function JobDetails() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { data: user } = useQuery({
        queryKey: ["user"],
        queryFn: getUser,
    });

    const job = getJobById(Number(id));

    if (!job) {
        return (
            <div className="w-full max-w-[1450px] mx-auto px-6 py-6">
                <p className="text-muted-foreground">Vaga não encontrada.</p>
                <Link to="/job-analysis" className="text-brand-primary underline">
                    Voltar para a lista de vagas
                </Link>
            </div>
        );
    }

    const similarJobs = jobs.filter((j) => j.id !== job.id).slice(0, 3);

    return (
        <div className="w-full max-w-[1450px] mx-auto px-6 py-6">
            {/* HEADER */}
            <div className="flex items-start justify-between mb-8">
                <div>
                    <button
                        type="button"
                        onClick={() => navigate("/job-analysis")}
                        className="mb-2 inline-flex items-center gap-1.5 text-sm font-medium text-brand-secondary transition-colors hover:text-brand-primary"
                    >
                        <ArrowLeft className="size-4" />
                        Voltar para vagas
                    </button>
                    <h1 className="text-4xl font-bold leading-tight">
                        Detalhes da{" "}
                        <span className="text-brand-primary">Vaga</span>
                    </h1>
                    <p className="text-muted-foreground mt-1">
                        Confira todos os detalhes e veja se essa vaga combina com você.
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
                        <span className="text-sm font-medium">{user?.name}</span>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_320px]">
                {/* COLUNA PRINCIPAL */}
                <div className="flex flex-col gap-6">
                    {/* CABEÇALHO DA VAGA */}
                    <div className="rounded-2xl border border-border bg-card p-6">
                        <div className="flex items-start justify-between">
                            <div className="flex items-center gap-4">
                                <div className="flex size-16 items-center justify-center rounded-xl bg-brand-primary-tint">
                                    <Building2 className="size-7 text-brand-primary" />
                                </div>
                                <div>
                                    <h2 className="text-2xl font-bold">{job.title}</h2>
                                    <p className="text-sm font-medium text-muted-foreground">{job.company}</p>
                                </div>
                            </div>
                            <Badge className="gap-1 border-transparent bg-brand-primary px-4 py-2 text-sm text-white">
                                <ArrowUpRight className="size-4" />
                                {job.match}% compatível
                            </Badge>
                        </div>

                        <p className="mt-4 text-sm leading-6 text-muted-foreground">{job.description}</p>

                        <div className="mt-4 flex flex-wrap gap-2">
                            <span className="inline-flex items-center gap-1.5 rounded-full bg-brand-primary-tint px-3 py-1 text-xs font-medium text-brand-secondary">
                                <MapPin className="size-3.5" />
                                {job.location}
                            </span>
                            <span className="inline-flex items-center gap-1.5 rounded-full bg-brand-primary-tint px-3 py-1 text-xs font-medium text-brand-secondary">
                                <Briefcase className="size-3.5" />
                                {job.modality}
                            </span>
                            <span className="inline-flex items-center gap-1.5 rounded-full bg-brand-primary-tint px-3 py-1 text-xs font-medium text-brand-secondary">
                                <Wallet className="size-3.5" />
                                {job.salary}
                            </span>
                        </div>

                        <div className="mt-3 flex flex-wrap gap-2">
                            {job.tags.map((tag) => (
                                <Badge key={tag} variant="secondary">
                                    {tag}
                                </Badge>
                            ))}
                        </div>

                        <div className="mt-6 grid grid-cols-3 gap-4 rounded-xl border border-border bg-brand-primary-tint/30 p-4">
                            <div>
                                <p className="text-xs text-muted-foreground">Habilidades</p>
                                <p className="text-lg font-bold text-brand-secondary">{job.matchBreakdown.skills}%</p>
                            </div>
                            <div>
                                <p className="text-xs text-muted-foreground">Experiência</p>
                                <p className="text-lg font-bold text-brand-secondary">{job.matchBreakdown.experience}%</p>
                            </div>
                            <div>
                                <p className="text-xs text-muted-foreground">Localização</p>
                                <p className="text-lg font-bold text-brand-secondary">{job.matchBreakdown.location}%</p>
                            </div>
                        </div>

                        <div className="mt-4 flex items-center gap-1.5 text-xs text-muted-foreground">
                            <Clock className="size-3.5" />
                            Publicada em {job.postedAt}
                        </div>
                    </div>

                    {/* SOBRE A VAGA */}
                    <div className="rounded-2xl border border-border bg-card p-6">
                        <h3 className="text-lg font-bold">Sobre a vaga</h3>
                        <p className="mt-3 text-sm leading-6 text-muted-foreground">{job.about}</p>

                        <h4 className="mt-6 text-sm font-bold text-brand-secondary">Responsabilidades</h4>
                        <ul className="mt-2 flex flex-col gap-2">
                            {job.responsibilities.map((item) => (
                                <li key={item} className="flex items-start gap-2 text-sm leading-6 text-muted-foreground">
                                    <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-brand-primary" />
                                    {item}
                                </li>
                            ))}
                        </ul>

                        <h4 className="mt-6 text-sm font-bold text-brand-secondary">Requisitos</h4>
                        <ul className="mt-2 flex flex-col gap-2">
                            {job.requirements.map((item) => (
                                <li key={item} className="flex items-start gap-2 text-sm leading-6 text-muted-foreground">
                                    <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-brand-primary" />
                                    {item}
                                </li>
                            ))}
                        </ul>

                        <h4 className="mt-6 text-sm font-bold text-brand-secondary">Benefícios</h4>
                        <ul className="mt-2 flex flex-col gap-2">
                            {job.benefits.map((item) => (
                                <li key={item} className="flex items-start gap-2 text-sm leading-6 text-muted-foreground">
                                    <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-brand-primary" />
                                    {item}
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>

                {/* SIDEBAR */}
                <div className="flex flex-col gap-6">
                    <div className="rounded-2xl border border-border bg-card p-6">
                        <div className="flex flex-col items-center">
                            <CompatibilityRing value={job.match} />
                            <p className="mt-3 text-center text-sm text-muted-foreground">
                                Seu currículo é altamente compatível com essa vaga.
                            </p>
                        </div>

                        <div className="mt-6 border-t border-border pt-5">
                            <div className="flex items-center gap-2">
                                <div className="flex size-8 items-center justify-center rounded-lg bg-brand-primary-tint">
                                    <Sparkles className="size-4 text-brand-primary" />
                                </div>
                                <h3 className="text-sm font-bold">Análise da IA</h3>
                            </div>

                            <p className="mt-3 text-xs leading-5 text-muted-foreground">
                                {job.aiAnalysis.summary}
                            </p>

                            <div className="mt-4">
                                <p className="text-xs font-bold uppercase tracking-wide text-success">
                                    Encontradas
                                </p>
                                <div className="mt-2 flex flex-wrap gap-1.5">
                                    {job.aiAnalysis.keywordsFound.map((keyword) => (
                                        <span
                                            key={keyword}
                                            className="inline-flex items-center gap-1 rounded-full bg-success/10 px-2.5 py-1 text-xs font-medium text-success"
                                        >
                                            <CheckCircle2 className="size-3" />
                                            {keyword}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            <div className="mt-4">
                                <p className="text-xs font-bold uppercase tracking-wide text-destructive">
                                    Faltando
                                </p>
                                <div className="mt-2 flex flex-wrap gap-1.5">
                                    {job.aiAnalysis.keywordsMissing.map((keyword) => (
                                        <span
                                            key={keyword}
                                            className="inline-flex items-center gap-1 rounded-full bg-destructive/10 px-2.5 py-1 text-xs font-medium text-destructive"
                                        >
                                            <X className="size-3" />
                                            {keyword}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="flex flex-col gap-3 rounded-2xl bg-brand-secondary p-6">
                        <button
                            type="button"
                            className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-primary px-4 py-3 text-sm font-medium text-white transition-colors hover:bg-brand-primary/90"
                        >
                            <Send className="size-4" />
                            Candidatar-se agora
                        </button>
                        <Link
                            to="/editor"
                            className="inline-flex items-center justify-center gap-2 rounded-lg border border-white/20 bg-white/10 px-4 py-3 text-sm font-medium text-white transition-colors hover:bg-white/20"
                        >
                            <Wand2 className="size-4" />
                            Otimizar meu currículo
                        </Link>
                        <div className="flex gap-3">
                            <button
                                type="button"
                                aria-label="Salvar vaga"
                                className="inline-flex flex-1 items-center justify-center gap-2 rounded-lg bg-white/10 px-4 py-2.5 text-xs font-medium text-white transition-colors hover:bg-white/20"
                            >
                                <Bookmark className="size-3.5" />
                                Salvar
                            </button>
                            <button
                                type="button"
                                aria-label="Compartilhar vaga"
                                className="inline-flex flex-1 items-center justify-center gap-2 rounded-lg bg-white/10 px-4 py-2.5 text-xs font-medium text-white transition-colors hover:bg-white/20"
                            >
                                <Share2 className="size-3.5" />
                                Compartilhar
                            </button>
                        </div>
                    </div>

                    <div className="rounded-2xl border-2 border-brand-primary/40 bg-card p-6">
                        <div className="flex items-center gap-3">
                            <div className="flex size-10 items-center justify-center rounded-lg bg-brand-primary-tint">
                                <Building2 className="size-5 text-brand-primary" />
                            </div>
                            <div>
                                <p className="text-sm font-bold">{job.company}</p>
                                <p className="text-xs text-muted-foreground">{job.companyInfo.industry}</p>
                            </div>
                        </div>
                        <div className="mt-4 flex items-center justify-between text-xs text-muted-foreground">
                            <span>{job.companyInfo.size}</span>
                            <span className="inline-flex items-center gap-1 font-medium text-brand-secondary">
                                <Star className="size-3.5 fill-brand-primary text-brand-primary" />
                                {job.companyInfo.rating}
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            {/* VAGAS SIMILARES */}
            <div className="mt-10">
                <h3 className="text-xl font-bold mb-4">Vagas Similares</h3>
                <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
                    {similarJobs.map((similar) => (
                        <Link
                            key={similar.id}
                            to={`/job-analysis/${similar.id}`}
                            className="flex flex-col gap-3 rounded-2xl border border-border bg-card p-5 transition-colors hover:border-brand-primary"
                        >
                            <div className="flex items-start justify-between">
                                <div className="flex size-10 items-center justify-center rounded-lg bg-brand-primary-tint">
                                    <Building2 className="size-5 text-brand-primary" />
                                </div>
                                <span className="inline-flex items-center gap-1 rounded-full bg-brand-primary-tint px-2.5 py-0.5 text-xs font-medium text-brand-secondary">
                                    <CheckCircle2 className="size-3.5" />
                                    {similar.match}%
                                </span>
                            </div>
                            <div>
                                <p className="text-sm font-bold">{similar.title}</p>
                                <p className="text-xs text-muted-foreground">{similar.company}</p>
                            </div>
                        </Link>
                    ))}
                </div>
            </div>
        </div>
    );
}
