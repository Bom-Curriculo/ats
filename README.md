# Bom Currículo - ATS Resume Builder

https://bomcurriculo.tech

## UNDER CONSTRUCTION - EM CONSTRUÇÃO

Build ATS-friendly resumes using AI.

## 🐳 Rodando com Docker

O projeto é orquestrado via Docker Compose, com ambientes separados de
desenvolvimento e produção.

```bash
# 1. Configure as variáveis da raiz (credenciais do RabbitMQ, portas, etc.)
cp .env.example .env

# Desenvolvimento (hot reload, portas expostas)
./run-dev.sh                 # sobe tudo em foreground
./run-dev.sh -d              # em background
./run-dev.sh logs -f backend # ver logs de um serviço
./run-dev.sh down            # derruba o ambiente

# Produção (imagens auto-contidas, frontend buildado e servido por nginx)
./run-prod.sh                # build + up -d
./run-prod.sh down
```

**Serviços e portas (dev):**

| Serviço  | URL / Porta                | Descrição                          |
|----------|----------------------------|------------------------------------|
| frontend | http://localhost:5173      | Vite dev server (HMR)              |
| backend  | http://localhost:8080/api  | API Laravel (via nginx + php-fpm)  |
| bot      | http://localhost:8000      | API do bot (Quart/ASGI)            |
| rabbitmq | http://localhost:15672     | Painel de gerenciamento            |
| redis    | localhost:6379             | Cache / filas                      |

Como funciona a separação:

- **Dev** — `docker-compose.yml` + `docker-compose.dev.yml`: código montado por
  bind-mount, dependências instaladas em runtime, hot reload em todos os serviços.
- **Prod** — `docker-compose.yml` + `docker-compose.prod.yml`: tudo embutido nas
  imagens (multi-stage), sem bind-mount, `restart: always`.

# English

## About

ATS Resume Builder is an open-source project that generates professional resumes optimized for Applicant Tracking Systems (ATS).

The system can use multiple optional sources of information, including:

- Current resume
- LinkedIn Profile (PDF export)
- GitHub profile
- Portfolio
- Personal information
- Target job description

The user does not need to provide every source. The only requirement is enough information to generate a resume.

## Features

- LinkedIn profile analysis
- GitHub profile analysis
- Portfolio analysis
- Job description matching
- ATS-friendly resume generation
- Resume optimization

## Screen prototype

An initial interface prototype was also developed in Figma to validate the user experience, feature organization, and the platform's main flow before final implementation.

The screen is still evolving, but it already represents the first visual proposal of the user dashboard, including:

- ATS score overview;
- General resume performance indicator;
- AI-powered optimization tips;
- List of uploaded resumes;
- Application progress tracking;
- Sidebar menu with access to the platform’s main areas.


> **Note:** the design is still under development and may be adjusted as the product evolves.

![Project screens preview](./docs/assets/figma-preview.png)

## Roadmap

- [ ] Resume generation
- [ ] LinkedIn PDF parser
- [ ] GitHub integration
- [ ] Portfolio analysis
- [ ] Job matching
- [ ] Multiple templates
- [ ] Export to PDF
- [ ] Export to DOCX

## Contributing

Contributions are welcome!

Please read CONTRIBUTING.md before submitting a Pull Request.

## License

This project is licensed under the MIT License.

# Português

## Sobre

ATS Resume Builder é um projeto open source para geração de currículos profissionais otimizados para sistemas ATS.

O sistema pode utilizar diversas fontes opcionais de informação:

- Currículo atual
- Perfil do LinkedIn (PDF)
- Perfil do GitHub
- Portfólio
- Informações pessoais
- Vaga desejada

O usuário não precisa fornecer todas essas informações. Basta enviar dados suficientes para gerar um currículo.

## Funcionalidades

- Análise do LinkedIn
- Análise do GitHub
- Análise de portfólio
- Compatibilidade com vagas
- Geração de currículo ATS
- Otimização de currículo

## Protótipo das telas

Também foi desenvolvido um protótipo inicial da interface no Figma, com o objetivo de validar a experiência do usuário, a organização das funcionalidades e o fluxo principal da plataforma antes da implementação final.

A tela ainda está em evolução, mas já representa a primeira proposta visual do dashboard do usuário, incluindo:

- Visão geral da pontuação ATS;
- Indicador de performance geral dos currículos;
- Dicas de otimização com IA;
- Lista de currículos cadastrados;
- Acompanhamento do progresso de aplicações;
- Menu lateral com acesso às principais áreas da plataforma.

> **Observação:** o design ainda está em desenvolvimento e poderá ser ajustado conforme a evolução do produto.

![Prévia das telas do projeto](./docs/assets/figma-preview.png)


## Roadmap

- [ ] Geração de currículo
- [ ] Leitor de PDF do LinkedIn
- [ ] Integração com GitHub
- [ ] Análise de portfólio
- [ ] Correspondência de vagas
- [ ] Múltiplos modelos
- [ ] Exportação para PDF
- [ ] Exportação para DOCX

## Como contribuir

Leia o arquivo CONTRIBUTING.md.

## Licença

MIT License.