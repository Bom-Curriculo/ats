import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { getUser } from "@/api/user/get-user";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { jobs } from "./jobs-data";
import {
    ArrowUpRight,
    Bell,
    Briefcase,
    Building2,
    ChevronDown,
    Clock,
    MapPin,
    Search,
    SlidersHorizontal,
    Wallet,
} from "lucide-react";

export default function JobAnalysis() {
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
                        Analisador de{" "}
                        <span className="text-brand-primary">Vagas</span>
                    </h1>

                    <p className="text-muted-foreground mt-1">
                        Encontre vagas compatíveis com o seu currículo.
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

            {/* FILTROS */}

            <div className="rounded-2xl border border-border bg-card p-6">
                <div className="flex flex-col gap-3 md:flex-row md:items-center">
                    <div className="relative flex-1">
                        <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                        <Input
                            placeholder="Buscar por cargo ou palavra-chave"
                            className="h-10 rounded-lg pl-9"
                        />
                    </div>

                    <div className="relative flex-1">
                        <MapPin className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                        <Input
                            placeholder="Localização"
                            className="h-10 rounded-lg pl-9"
                        />
                    </div>

                    <div className="relative w-full md:w-52">
                        <select
                            defaultValue="todas"
                            className="h-10 w-full appearance-none rounded-lg border border-input bg-transparent px-3 pr-8 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
                        >
                            <option value="todas">Todas as modalidades</option>
                            <option value="remoto">Remoto</option>
                            <option value="hibrido">Híbrido</option>
                            <option value="presencial">Presencial</option>
                        </select>
                        <ChevronDown className="pointer-events-none absolute right-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                    </div>

                    <button
                        type="button"
                        className="inline-flex h-10 shrink-0 items-center justify-center gap-2 rounded-lg bg-brand-primary px-6 text-sm font-medium text-white transition-colors hover:bg-brand-primary/90"
                    >
                        <SlidersHorizontal className="size-4" />
                        Filtrar
                    </button>
                </div>
            </div>

            {/* LISTA DE VAGAS */}

            <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
                {jobs.map((job) => (
                    <div
                        key={job.id}
                        className="flex flex-col justify-between rounded-2xl border border-border bg-card p-6"
                    >
                        <div>
                            <div className="flex items-start justify-between">
                                <div className="flex size-14 items-center justify-center rounded-xl bg-brand-primary-tint">
                                    <Building2 className="size-6 text-brand-primary" />
                                </div>

                                <Badge className="gap-1 border-transparent bg-brand-primary text-white">
                                    <ArrowUpRight className="size-3.5" />
                                    {job.match}% compatível
                                </Badge>
                            </div>

                            <h3 className="mt-4 text-xl font-bold">
                                {job.title}
                            </h3>
                            <p className="text-sm font-medium text-muted-foreground">
                                {job.company}
                            </p>

                            <p className="mt-3 text-sm leading-6 text-muted-foreground">
                                {job.description}
                            </p>

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
                        </div>

                        <div className="mt-6 flex items-center justify-between border-t border-border pt-4">
                            <span className="inline-flex items-center gap-1.5 text-xs text-muted-foreground">
                                <Clock className="size-3.5" />
                                Publicada em {job.postedAt}
                            </span>
                            <Link
                                to={`/job-analysis/${job.id}`}
                                className="inline-flex items-center gap-2 rounded-lg bg-brand-secondary px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90"
                            >
                                Ver Vaga
                                <ArrowUpRight className="size-4" />
                            </Link>
                        </div>
                    </div>
                ))}
            </div>

            {/* PAGINAÇÃO */}

            <div className="mt-8 flex justify-center">
                <button
                    type="button"
                    className="rounded-lg border-2 border-brand-primary px-6 py-2 text-sm font-medium text-brand-primary transition-colors hover:bg-brand-primary/10"
                >
                    Ver mais vagas recomendadas
                </button>
            </div>
        </div>
    );
}
