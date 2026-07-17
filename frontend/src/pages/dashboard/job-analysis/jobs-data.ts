export type Job = {
    id: number;
    company: string;
    title: string;
    match: number;
    description: string;
    location: string;
    modality: string;
    salary: string;
    tags: string[];
    postedAt: string;
    matchBreakdown: {
        skills: number;
        experience: number;
        location: number;
    };
    about: string;
    responsibilities: string[];
    requirements: string[];
    benefits: string[];
    companyInfo: {
        industry: string;
        size: string;
        rating: number;
    };
    aiAnalysis: {
        summary: string;
        keywordsFound: string[];
        keywordsMissing: string[];
    };
};

export const jobs: Job[] = [
    {
        id: 1,
        company: "Nubank",
        title: "Product Designer Pleno",
        match: 92,
        description:
            "Buscamos um Product Designer para atuar em squads multidisciplinares, criando experiências centradas no usuário para produtos financeiros.",
        location: "São Paulo, SP",
        modality: "Remoto",
        salary: "R$ 8.000 - 12.000",
        tags: ["UX", "UI", "Figma"],
        postedAt: "12/03/2025 às 14:32",
        matchBreakdown: { skills: 95, experience: 88, location: 100 },
        about:
            "O time de Design do Nubank trabalha de forma multidisciplinar com pesquisa, produto e engenharia para construir experiências financeiras simples e acessíveis para milhões de clientes. Você fará parte de um squad responsável por um dos principais produtos da plataforma.",
        responsibilities: [
            "Conduzir pesquisas com usuários para embasar decisões de design",
            "Criar wireframes, protótipos e fluxos de alta fidelidade no Figma",
            "Colaborar diretamente com PMs e engenheiros na definição de soluções",
            "Manter e evoluir o design system da plataforma",
        ],
        requirements: [
            "Experiência prévia como Product Designer ou UX/UI Designer",
            "Domínio de Figma e ferramentas de prototipação",
            "Conhecimento em pesquisa com usuários e testes de usabilidade",
            "Boa comunicação e capacidade de trabalhar em squads multidisciplinares",
        ],
        benefits: [
            "Plano de saúde e odontológico",
            "Vale refeição e alimentação flexível",
            "Auxílio home office",
            "Horário flexível",
        ],
        companyInfo: { industry: "Serviços Financeiros", size: "5.000+ funcionários", rating: 4.6 },
        aiAnalysis: {
            summary:
                "Seu currículo cobre a maior parte das habilidades pedidas na vaga. Adicionar as palavras-chave faltantes pode aumentar ainda mais sua compatibilidade.",
            keywordsFound: ["Figma", "UX Research", "Prototipação", "Design System", "Trabalho em squad"],
            keywordsMissing: ["Testes A/B", "Design Ops", "Acessibilidade (WCAG)"],
        },
    },
    {
        id: 2,
        company: "iFood",
        title: "Analista de Marketing Digital",
        match: 81,
        description:
            "Vaga para profissional de marketing com foco em performance, gestão de campanhas e análise de métricas de aquisição.",
        location: "Osasco, SP",
        modality: "Híbrido",
        salary: "R$ 5.500 - 7.000",
        tags: ["MKT", "SEO", "Ads"],
        postedAt: "08/03/2025 às 09:15",
        matchBreakdown: { skills: 78, experience: 82, location: 90 },
        about:
            "O time de Marketing de Performance do iFood busca profissionais analíticos e criativos para escalar as campanhas de aquisição e retenção de usuários em todo o Brasil.",
        responsibilities: [
            "Planejar e executar campanhas de mídia paga (Google Ads, Meta Ads)",
            "Monitorar métricas de performance e otimizar o funil de aquisição",
            "Elaborar relatórios de resultados para stakeholders",
            "Testar novas estratégias de SEO e conteúdo",
        ],
        requirements: [
            "Experiência com gestão de campanhas de mídia paga",
            "Conhecimento em SEO e ferramentas de analytics",
            "Perfil analítico e orientado a dados",
            "Excel avançado",
        ],
        benefits: [
            "Vale refeição e alimentação",
            "Plano de saúde",
            "Gympass",
            "Day off no aniversário",
        ],
        companyInfo: { industry: "Tecnologia / Delivery", size: "5.000+ funcionários", rating: 4.3 },
        aiAnalysis: {
            summary:
                "Seu currículo tem boa aderência a marketing de performance, mas faltam algumas ferramentas específicas citadas na vaga.",
            keywordsFound: ["Google Ads", "Meta Ads", "Gestão de campanhas", "Análise de métricas"],
            keywordsMissing: ["SEO técnico", "Google Analytics 4", "Power BI"],
        },
    },
    {
        id: 3,
        company: "Stone",
        title: "UX Designer Sênior",
        match: 88,
        description:
            "Procuramos um UX Designer sênior para liderar pesquisas com usuários e desenhar fluxos de produtos de pagamento.",
        location: "Rio de Janeiro, RJ",
        modality: "Remoto",
        salary: "R$ 11.000 - 15.000",
        tags: ["UX Research", "Figma"],
        postedAt: "05/03/2025 às 18:47",
        matchBreakdown: { skills: 90, experience: 85, location: 100 },
        about:
            "A Stone busca um UX Designer sênior para liderar iniciativas de pesquisa e desenho de fluxos em produtos de pagamento, atuando lado a lado com times de produto e negócio.",
        responsibilities: [
            "Liderar pesquisas qualitativas e quantitativas com usuários",
            "Definir fluxos de ponta a ponta para produtos de pagamento",
            "Mentorar designers pleno e júnior do time",
            "Apresentar decisões de design para liderança",
        ],
        requirements: [
            "Experiência sênior em UX Research e UX Design",
            "Vivência em produtos financeiros ou de pagamento",
            "Domínio de Figma e ferramentas de pesquisa",
            "Inglês intermediário",
        ],
        benefits: [
            "Plano de saúde e odontológico",
            "Vale refeição e alimentação",
            "Auxílio home office",
            "Participação nos lucros",
        ],
        companyInfo: { industry: "Serviços Financeiros", size: "5.000+ funcionários", rating: 4.4 },
        aiAnalysis: {
            summary:
                "Seu perfil sênior em UX combina muito bem com a vaga. Reforçar vivência em produtos de pagamento pode elevar ainda mais o match.",
            keywordsFound: ["UX Research", "Figma", "Fluxos de produto", "Mentoria"],
            keywordsMissing: ["Produtos de pagamento", "Inglês avançado"],
        },
    },
    {
        id: 4,
        company: "Magalu",
        title: "Coordenador(a) de Marketing",
        match: 74,
        description:
            "Oportunidade para liderar a equipe de marketing de conteúdo, definindo estratégias de branding e comunicação.",
        location: "Franca, SP",
        modality: "Presencial",
        salary: "R$ 9.000 - 13.000",
        tags: ["Branding", "Gestão"],
        postedAt: "10/03/2025 às 11:20",
        matchBreakdown: { skills: 70, experience: 76, location: 75 },
        about:
            "O Magalu busca um(a) Coordenador(a) de Marketing para liderar a equipe responsável pela estratégia de conteúdo e branding da marca, atuando em conjunto com áreas comerciais.",
        responsibilities: [
            "Liderar a equipe de marketing de conteúdo",
            "Definir e acompanhar a estratégia de branding da marca",
            "Alinhar ações de comunicação com áreas comerciais",
            "Gerenciar orçamento e fornecedores de marketing",
        ],
        requirements: [
            "Experiência em coordenação de equipes de marketing",
            "Vivência com branding e estratégia de comunicação",
            "Boa capacidade de gestão de pessoas",
            "Disponibilidade para trabalho presencial",
        ],
        benefits: [
            "Vale refeição e alimentação",
            "Plano de saúde",
            "Desconto em compras",
            "Plano de carreira estruturado",
        ],
        companyInfo: { industry: "Varejo", size: "10.000+ funcionários", rating: 4.1 },
        aiAnalysis: {
            summary:
                "Seu currículo atende parte dos requisitos de gestão, mas faltam palavras-chave de branding e liderança de equipe presentes na vaga.",
            keywordsFound: ["Marketing de conteúdo", "Gestão de orçamento", "Comunicação"],
            keywordsMissing: ["Branding", "Liderança de equipe", "Trabalho presencial"],
        },
    },
];

export function getJobById(id: number) {
    return jobs.find((job) => job.id === id);
}
