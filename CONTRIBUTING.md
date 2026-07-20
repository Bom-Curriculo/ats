# Contributing

# English

Thank you for contributing!

## How to contribute

- Fork this repository.
- Create a new branch.
- Make your changes.
- Commit them: `git add . && git commit -m "My changes" && git push origin development`
- Submit a Pull Request.

## Pull request template
*You must use this template on yout pull request:*

```md
## Contribution title

**Have you used AI to vibe code?**
Response.
**Have you used AI as a research source?**
Response.
**Have REVIEWED your code before request a review?**
Response.
**Have you tested locally?**
Response.

### Fixes:
Description of what you have fixed. You can also upload screenshots if needed.

```

## Before opening a PR

- **Backend (PHP):** run `vendor/bin/pint` before committing — it auto-fixes code style. If you don't have PHP installed, run it via Docker:
  `docker run --rm -v ${PWD}/backend:/app -w /app php:8.4-cli vendor/bin/pint`
- **Mobile (Flutter):** run `dart format .` inside `mobile/` before committing. Without Flutter installed:
  `docker run --rm -v ${PWD}/mobile:/app -w /app dart:stable dart format .`
- **Backend (API docs):** if you add, remove, or change an endpoint under `backend/app/Http/Controllers/Api/**`, update its Swagger attributes (`#[OpenApi\Attributes\...]`) and regenerate/lint the spec before committing:
  `cd backend && php artisan l5-swagger:generate && npx --yes @redocly/cli lint storage/api-docs/api-docs.json`
  This is the same check the "API docs (OpenAPI lint)" CI job runs, so catching it locally avoids a failed PR. If you don't have PHP/Node installed, run it via Docker instead:
  ```
  docker run --rm -v ${PWD}/backend:/app -w /app php:8.4-cli php artisan l5-swagger:generate
  docker run --rm -v ${PWD}/backend:/app -w /app node:22 npx --yes @redocly/cli lint storage/api-docs/api-docs.json
  ```
- **Keep your branch up to date** with `development` before opening/merging your PR — CI runs against your branch's current state, so a stale branch can show failures that were already fixed elsewhere.
- **Keep PRs focused**: don't mix formatting-only changes with bug fixes or new features in the same PR — it makes review and rollback much easier.

## Coding Style

- Keep code readable.
- Write comments when necessary.
- Follow existing project patterns.

## Reporting Bugs

Please open an Issue describing:

- Expected behavior
- Actual behavior
- Steps to reproduce

## Suggesting Features

Open an Issue with:

- Feature description
- Motivation
- Possible implementation

# Português

Obrigado por contribuir!

## Como contribuir

- Faça um Fork.
- Crie uma nova branch.
- Faça suas alterações.
- Faça o commit: `git add . && git commit -m "My changes" && git push origin development`
- Envie um Pull Request.

## Template de Pull Request
*Você deve usar este template na sua pull request:*

```md
## Título da contribuição


**Você usou IA para vibe-codar?**
Resposta.
**Você usou IA como fonte de pesquisa?**
Resposta.
**Você REVISOU seu código antes de pedir por uma review?**
Resposta.
**Você testou localmente?**
Resposta.

### O que foi feito:
Descrição do que foi feito. Você pode adicionar alguma print se necessário.

```

## Antes de abrir um PR

- **Backend (PHP):** rode `vendor/bin/pint` antes de commitar — ele corrige o estilo de código automaticamente. Se não tiver PHP instalado, rode via Docker:
  `docker run --rm -v ${PWD}/backend:/app -w /app php:8.4-cli vendor/bin/pint`
- **Mobile (Flutter):** rode `dart format .` dentro de `mobile/` antes de commitar. Sem Flutter instalado:
  `docker run --rm -v ${PWD}/mobile:/app -w /app dart:stable dart format .`
- **Backend (documentação da API):** se você adicionar, remover ou alterar um endpoint em `backend/app/Http/Controllers/Api/**`, atualize os atributos de Swagger (`#[OpenApi\Attributes\...]`) e regenere/lint a spec antes de commitar:
  `cd backend && php artisan l5-swagger:generate && npx --yes @redocly/cli lint storage/api-docs/api-docs.json`
  É a mesma checagem que o job "API docs (OpenAPI lint)" do CI roda, então pegar isso localmente evita um PR falhando. Se não tiver PHP/Node instalado, rode via Docker:
  ```
  docker run --rm -v ${PWD}/backend:/app -w /app php:8.4-cli php artisan l5-swagger:generate
  docker run --rm -v ${PWD}/backend:/app -w /app node:22 npx --yes @redocly/cli lint storage/api-docs/api-docs.json
  ```
- **Mantenha sua branch atualizada** com a `development` antes de abrir/mergear o PR — o CI roda em cima do estado atual da sua branch, então uma branch desatualizada pode mostrar falhas que já foram corrigidas em outro lugar.
- **Mantenha os PRs focados**: não misture mudanças só de formatação com correção de bug ou feature nova no mesmo PR — facilita muito a revisão e um eventual rollback.

## Padrão de código

- Código limpo.
- Comentários quando necessário.
- Siga o padrão do projeto.

## Reportando Bugs

Abra uma Issue contendo:

- Comportamento esperado
- Comportamento atual
- Como reproduzir

## Sugestões

Abra uma Issue contendo:

- Descrição
- Motivação
- Possível implementação
