import re
from dataclasses import dataclass
from difflib import SequenceMatcher

from app.providers.base import ProvedorIA
from app.schemas.analise import (
    AnaliseDetalhada,
    EvidenciasCurriculo,
    InformacoesPrivacidade,
    ItemAnaliseRequisito,
    ResultadoAnalise,
    SolicitacaoAnalise,
    SugestoesDetalhadas,
)
from app.schemas.analise_ia import AnaliseIARequisito, RespostaAnaliseIA
from app.services.catalogo_tecnologias import CATALOGO, Tecnologia
from app.services.extrator_secoes import detectar_evidencias, extrair_secoes_curriculo, analisar_secoes_curriculo
from app.services.inventario_curriculo import extrair_inventario_curriculo
from app.services.fact_bank import construir_fact_bank, resumo_fontes
from app.services.keyword_report import construir_keyword_report
from app.services.matching_tecnico import encontrar_alias
from app.services.grupos_requisitos import construir_grupos_requisitos
from app.services.orquestrador_ia import executar_pipeline_ia
from app.services.normalizador_texto import (
    normalizar_para_comparacao,
    normalizar_texto_curriculo,
)
from app.services.normalizador_vaga import limpar_texto_vaga, normalizar_texto_vaga
from app.services.sanitizador_privacidade import sanitizar_dados_pessoais
from app.services.analise_ia_estruturada import executar_analise_ia_estruturada
from app.services.equivalencias_tecnicas import (
    NivelEvidencia,
    NivelVaga,
    detectar_nivel_vaga,
    inferencias_para,
    peso_fonte,
    status_publico,
    GRUPOS_SUBREQUISITOS,
)

# requisitos não tech q tb entram no catalogo
REQUISITOS_NAO_TECNICOS = (
    Tecnologia("Inglês avançado", "idiomas", ("ingles avancado", "advanced english")),
    Tecnologia(
        "graduação completa",
        "formacao",
        ("graduacao completa", "ensino superior completo"),
    ),
    Tecnologia("portfólio", "ferramentas", ("portfolio",)),
)


# mapeia nome da seção pra chave q a gente usa
SECOES_ESPERADAS = {
    "experiência": "experiencia_profissional",
    "formação": "educacao",
    "projetos": "projetos",
    "habilidades": "competencias_tecnicas",
}


@dataclass(frozen=True)
class PalavraChave:
    termo: str

    peso: int

    ordem: int

    grupo: str

    tecnologia: bool


def normalizar_texto(texto: str) -> str:

    return normalizar_para_comparacao(texto)


# acha a primeira ocorrencia da tecnologia pelo texto
def _ocorrencia(texto: str, aliases: tuple[str, ...]) -> re.Match[str] | None:
    return encontrar_alias(texto, aliases)


def extrair_requisitos_vaga(
    vaga_estruturada: dict[str, str | list[str]],
) -> list[PalavraChave]:
    """Extrai somente catálogo conhecido das áreas que podem influenciar o score."""

    requisitos: dict[str, PalavraChave] = {}

    grupos = (
        ("requisito_obrigatorio", 3, "requisitos_obrigatorios"),
        ("responsabilidade", 2, "responsabilidades"),
        ("diferencial", 1, "diferenciais"),
    )

    catalogo = CATALOGO + REQUISITOS_NAO_TECNICOS

    deslocamento = 0

    for grupo, peso, campo in grupos:
        valor = vaga_estruturada.get(campo, [])

        texto = normalizar_para_comparacao(
            "\n".join(valor) if isinstance(valor, list) else valor
        )

        for tecnologia in catalogo:
            match = _ocorrencia(texto, tecnologia.aliases)

            if match and tecnologia.nome not in requisitos:
                requisitos[tecnologia.nome] = PalavraChave(
                    tecnologia.nome,
                    peso,
                    deslocamento + match.start(),
                    grupo,
                    tecnologia in CATALOGO,
                )

        deslocamento += len(texto) + 1

    # Tecnologias no título também são requisitos principais
    titulo = normalizar_para_comparacao(str(vaga_estruturada.get("titulo", "")))

    for tecnologia in CATALOGO:
        match = _ocorrencia(titulo, tecnologia.aliases)

        if match and tecnologia.nome not in requisitos:
            requisitos[tecnologia.nome] = PalavraChave(
                tecnologia.nome, 3, match.start(), "requisito_obrigatorio", True
            )

    # Descrições reais frequentemente não preservam cabeçalhos ao serem copiadas.
    # O texto completo funciona como cobertura contextual de baixo peso.
    texto_completo = normalizar_para_comparacao(
        "\n".join(
            str(item)
            for valor in vaga_estruturada.values()
            for item in (valor if isinstance(valor, list) else [valor])
        )
    )
    for tecnologia in catalogo:
        match = _ocorrencia(texto_completo, tecnologia.aliases)
        if match and tecnologia.nome not in requisitos:
            requisitos[tecnologia.nome] = PalavraChave(
                tecnologia.nome,
                1,
                deslocamento + match.start(),
                "contexto",
                tecnologia in CATALOGO,
            )

    # Evita contar o requisito genérico e o específico para a mesma menção.
    if ("APIs REST" in requisitos or "APIs de IA" in requisitos) and "APIs" in requisitos:
        del requisitos["APIs"]

    # Evita matches por substring de bases que só aparecem dentro do composto.
    pares_compostos = (
        ("Spring Boot", "Spring", r"\bspring\b(?!\s+boot)"),
        ("Docker Compose", "Docker", r"\bdocker\b(?!\s+compose)"),
        ("React Native", "React", r"\breact\b(?!\s+native)"),
    )
    for composto, base, padrao_base_solto in pares_compostos:
        if composto in requisitos and base in requisitos and not re.search(padrao_base_solto, texto_completo):
            del requisitos[base]

    return sorted(requisitos.values(), key=lambda item: (-item.peso, item.ordem))


def extrair_palavras_relevantes_com_pesos(
    texto_vaga: str, limite: int = 40
) -> list[PalavraChave]:

    return extrair_requisitos_vaga(normalizar_texto_vaga(texto_vaga))[:limite]


def extrair_palavras_relevantes(texto_vaga: str, limite: int = 40) -> list[str]:

    return [
        item.termo for item in extrair_palavras_relevantes_com_pesos(texto_vaga, limite)
    ]


# pega o objeto [tecnologias] pelo nome
def _tecnologia(nome: str) -> Tecnologia:

    return next(
        item for item in CATALOGO + REQUISITOS_NAO_TECNICOS if item.nome == nome
    )


# verifica se o termo aparece no texto normalizado
def _contem(texto: str, nome: str) -> bool:

    return (
        _ocorrencia(
            normalizar_para_comparacao(normalizar_texto_curriculo(texto)),
            _tecnologia(nome).aliases,
        )
        is not None
    )


def detectar_secoes_ausentes(curriculo_texto: str) -> list[str]:

    secoes = extrair_secoes_curriculo(curriculo_texto)

    return [
        f"Seção de {nome} não identificada no currículo."
        for nome, chave in SECOES_ESPERADAS.items()
        if chave not in secoes
    ]


def comparar_curriculo_com_vaga(
    curriculo: str, secoes: dict[str, str], requisitos: list[PalavraChave]
) -> list[ItemAnaliseRequisito]:
    """Classifica cada requisito e n copia dados pessoais"""

    itens: list[ItemAnaliseRequisito] = []

    secoes_praticas_parciais = ("residencias", "projetos_academicos")
    secoes_educacionais = ("educacao", "certificacoes", "cursos")

    def contem_direto(texto: str, nome: str) -> bool:
        # Evita que uma tecnologia composta satisfaça a base por mera substring;
        # relações legítimas são avaliadas depois pelo catálogo de inferências.
        compostos = {
            "CSS": ("Tailwind CSS",),
            "Docker": ("Docker Compose",),
            "React": ("React Native",),
            "Spring": ("Spring Boot",),
        }
        limpo = texto
        for composto in compostos.get(nome, ()):
            limpo = re.sub(re.escape(composto), " ", limpo, flags=re.I)
        return _contem(limpo, nome)

    def localizar(nome: str) -> tuple[NivelEvidencia, str | None, str | None]:
        if contem_direto(secoes.get("experiencia_profissional", ""), nome):
            return NivelEvidencia.PRATICA_FORTE, "experiência profissional", None
        freela = secoes.get("freelas", "")
        if contem_direto(freela, nome):
            entrega = re.search(r"\b(entreg|cliente|contrat|publicad|deploy|implement|desenvolv|delivered|client|contract|released|built)\w*\b", normalizar_para_comparacao(freela))
            return (NivelEvidencia.PRATICA_FORTE if entrega else NivelEvidencia.RELACIONADA), "freela", None
        projeto = secoes.get("projetos", "")
        if contem_direto(projeto, nome):
            return NivelEvidencia.PRATICA_FORTE, "projeto", None
        aberto = secoes.get("open_source", "")
        if contem_direto(aberto, nome):
            contribuicao = re.search(r"\b(contribu|commit|pull request|merged|aceit|corrig|implement|maintain|fixed)\w*\b", normalizar_para_comparacao(aberto))
            return (NivelEvidencia.PRATICA_FORTE if contribuicao else NivelEvidencia.RELACIONADA), "open source", None
        if any(contem_direto(secoes.get(s, ""), nome) for s in secoes_praticas_parciais):
            fonte = "residência/laboratório prático" if contem_direto(secoes.get("residencias", ""), nome) else "projeto acadêmico"
            return NivelEvidencia.PRATICA_PARCIAL, fonte, None
        if any(contem_direto(secoes.get(s, ""), nome) for s in secoes_educacionais):
            return NivelEvidencia.EDUCACIONAL, "curso/formação", None
        for linha in curriculo.splitlines():
            linha_normalizada = normalizar_para_comparacao(linha)
            if contem_direto(linha, nome) and re.search(
                r"\b(curso|certifica|disciplina|formacao|bootcamp|treinamento)\b",
                linha_normalizada,
            ):
                return NivelEvidencia.EDUCACIONAL, "curso/formação", None
            if contem_direto(linha, nome) and re.search(
                r"\b(residencia tecnologica|laboratorio pratico|lab pratico)\b",
                linha_normalizada,
            ):
                return NivelEvidencia.PRATICA_PARCIAL, "residência/laboratório prático", None
        if contem_direto(secoes.get("competencias_tecnicas", ""), nome) or contem_direto(curriculo, nome):
            return NivelEvidencia.SKILL_SOLTA, "competências", None

        corpus = normalizar_para_comparacao(curriculo)
        for inferencia in inferencias_para(nome):
            try:
                origem_presente = _contem(curriculo, inferencia.origem)
            except StopIteration:
                origem_presente = normalizar_para_comparacao(inferencia.origem) in corpus
            contexto_ok = not inferencia.exige_contexto or any(
                termo in corpus for termo in inferencia.exige_contexto
            )
            if origem_presente and contexto_ok:
                return NivelEvidencia.RELACIONADA, inferencia.origem, inferencia.forca.value
        return NivelEvidencia.AUSENTE, None, None

    for requisito in requisitos:
        nivel_evidencia, fonte, forca = localizar(requisito.termo)
        status = status_publico(nivel_evidencia)
        evidencia = (
            f"{requisito.termo} aparece em {fonte}." if fonte and nivel_evidencia != NivelEvidencia.RELACIONADA
            else (f"{fonte} fornece evidência técnica relacionada, sem comprovar {requisito.termo} diretamente." if fonte else None)
        )
        if nivel_evidencia in {NivelEvidencia.PRATICA_FORTE, NivelEvidencia.PRATICA_PARCIAL}:
            orientacao = "Mantenha a evidência objetiva e descreva uso, entrega e resultado alcançado."
        elif nivel_evidencia == NivelEvidencia.EDUCACIONAL:
            orientacao = "Mantenha como formação/conhecimento; associe a projeto real somente se essa aplicação existiu."
        elif nivel_evidencia == NivelEvidencia.SKILL_SOLTA:
            orientacao = "Associe a habilidade a projeto ou experiência real, se possível."
        elif nivel_evidencia == NivelEvidencia.RELACIONADA:
            orientacao = f"A relação com {fonte} é indício, não comprovação direta; explicite somente se tiver vivência real."
        else:
            orientacao = f"Não inclua {requisito.termo} como experiência se não tiver usado. Pode criar projeto prático para evidenciar."

        itens.append(
            ItemAnaliseRequisito(
                item=requisito.termo,
                tipo="tecnologia" if requisito.tecnologia else "requisito",
                categoria=requisito.grupo,
                peso=requisito.peso,
                status=status,
                evidencia_no_curriculo=evidencia,
                orientacao=orientacao,
                nivel_evidencia=nivel_evidencia.value,
                fonte_evidencia=fonte,
                forca_inferencia=forca,
            )
        )

    return itens


def calcular_score_ats(
    itens: list[ItemAnaliseRequisito], analise_valida: bool,
    nivel_vaga: NivelVaga = NivelVaga.NAO_INFORMADO,
) -> int:

    if not analise_valida or not itens:
        return 0

    grupos: dict[str, list[ItemAnaliseRequisito]] = {}
    for item in itens:
        chave = next(
            (grupo for grupo, membros in GRUPOS_SUBREQUISITOS.items() if item.item in membros),
            item.item,
        )
        grupos.setdefault(chave, []).append(item)
    total = sum(max(item.peso for item in grupo) for grupo in grupos.values())
    pontos = sum(
        max(item.peso for item in grupo)
        * max(peso_fonte(nivel_vaga, NivelEvidencia(item.nivel_evidencia)) for item in grupo)
        for grupo in grupos.values()
    )
    score = round(pontos / total * 100)

    # se tiver poucos itens e score 100, capa em 95 pra não dar falso positivo
    return min(score, 95) if len(itens) < 5 and score == 100 else score


def detectar_possiveis_impeditivos(curriculo: str, vaga: str) -> list[str]:

    cv, descricao = (
        normalizar_para_comparacao(curriculo),
        normalizar_para_comparacao(limpar_texto_vaga(vaga)),
    )

    saida: list[str] = []

    # graduaçãp em andamento vs completa
    if re.search(
        r"graduacao completa|ensino superior completo", descricao
    ) and re.search(r"graduacao.{0,40}cursando|cursando.{0,40}graduacao", cv):
        saida.append(
            "Vaga pede graduação completa; currículo indica graduação em andamento."
        )

    # inglês tecnico vs avançado
    if (
        re.search(r"ingles avancado|advanced english", descricao)
        and "ingles tecnico" in cv
    ):
        saida.append("Vaga pede inglês avançado; currículo indica inglês técnico.")

    # lista de cidades pra bater localidade
    cidades = (
        "Manaus",
        "Recife",
        "São Paulo",
        "Rio de Janeiro",
        "Belo Horizonte",
        "Curitiba",
        "Porto Alegre",
        "Brasília",
        "Fortaleza",
        "Salvador",
    )

    # se for hibrido/presencial e cidades diferentes, alerta
    if re.search(r"\b(hibrid[oa]|presencial)\b", descricao):
        cidade_vaga = next(
            (c for c in cidades if normalizar_para_comparacao(c) in descricao), None
        )

        cidade_cv = next(
            (c for c in cidades if normalizar_para_comparacao(c) in cv), None
        )

        if cidade_vaga and cidade_cv and cidade_vaga != cidade_cv:
            saida.append(
                f"Vaga é híbrida/presencial em {cidade_vaga}; currículo indica {cidade_cv}."
            )

    return saida


def _entrada_valida(curriculo: str, vaga: str) -> tuple[bool, list[str]]:

    a, b = (
        normalizar_para_comparacao(curriculo),
        normalizar_para_comparacao(limpar_texto_vaga(vaga)),
    )

    similaridade = SequenceMatcher(None, a, b).ratio() if a and b else 0

    # se for parecido é inválidado
    if a == b or (min(len(a), len(b)) > 50 and similaridade >= 0.92):
        return False, [
            "Currículo e vaga são iguais ou muito parecidos; confirme os campos enviados."
        ]

    return True, []


def gerar_sugestoes_locais(
    itens: list[ItemAnaliseRequisito],
    evidencias: dict[str, bool],
    impeditivos: list[str],
    vaga: str,
) -> SugestoesDetalhadas:

    ajustes, lacunas, atencao, passos = [], [], list(impeditivos), []

    # habilidades ausentes, mas sem penalidade
    if not evidencias["secao_habilidades"]:
        ajustes.append(
            "Crie uma seção 'Competências Técnicas' claramente identificada; ela é fortemente recomendada para ATS tech, mas sua ausência não reprova automaticamente."
        )

    grupos_processados: set[str] = set()
    grupos = {
        "SQL": ({"SQL", "SELECT", "JOIN", "WHERE", "INSERT", "UPDATE", "DELETE"}, "SQL: consultas, JOINs, CRUD e modelagem"),
        "Git": ({"Git", "branches", "pull requests", "code review"}, "Git/versionamento: branches, pull requests e code review"),
        "Testes": ({"testes automatizados", "testes unitários", "testes de integração", "Jest", "Vitest", "Pytest", "JUnit", "PHPUnit", "Cypress", "Playwright"}, "testes automatizados: unitários, integração ou e2e"),
        "APIs": ({"APIs", "APIs REST", "Webhooks"}, "APIs REST e integrações: consumo, endpoints e webhooks"),
    }

    for item in itens:
        grupo = next((nome for nome, (membros, _) in grupos.items() if item.item in membros), None)
        rotulo = grupos[grupo][1] if grupo else item.item
        if grupo and grupo in grupos_processados:
            continue
        if grupo:
            grupos_processados.add(grupo)
        if item.status == "encontrado_sem_contexto_claro":
            ajustes.append(
                f"Detalhe melhor {rotulo}, se você já usou em projetos ou experiência."
            )

        elif item.status == "faltando":
            lacunas.append(
                f"Se não tiver experiência com {rotulo}, trate como lacuna técnica da vaga."
            )

            passos.append(
                f"Considere estudar e criar um projeto prático com {rotulo}, sem declarar experiência antes de utilizá-lo."
            )

        elif item.status == "relacionado_mas_nao_explicito":
            ajustes.append(item.orientacao)

    # sem experiência profissional é recomendado compensar com projetos etc
    if not evidencias["experiencia_profissional"]:
        passos.append(
            "Sem experiência profissional, evidencie projetos pessoais ou acadêmicos, labs, freelas, residência tecnológica e cursos práticos; isso não causa reprovação automática."
        )

    vaga_normalizada = normalizar_para_comparacao(vaga)

    if "portfolio" in vaga_normalizada and "portfólio" in [
        i.item for i in itens if i.status == "faltando"
    ]:
        passos.append(
            "Monte um portfólio com projetos reais porque esta vaga o solicita."
        )

    ajustes = list(dict.fromkeys(ajustes))
    lacunas = list(dict.fromkeys(lacunas))
    passos = list(dict.fromkeys(passos))
    alertas_honestidade = ["Não inclua tecnologias, práticas ou resultados que você não possa comprovar."]
    return SugestoesDetalhadas(
        ajustes_recomendados=ajustes,
        lacunas_tecnicas=lacunas,
        pontos_de_atencao=atencao,
        proximos_passos=passos,
        ajustes_no_curriculo=ajustes,
        lacunas_reais=lacunas,
        proximos_passos_de_estudo=passos,
        alertas_contra_inventar=alertas_honestidade,
    )


def _chave_requisito_ia(nome: str) -> str:
    chave = normalizar_para_comparacao(nome)
    equivalentes = {
        "html5": "html", "css3": "css", "api rest": "apis rest",
        "consumo de apis rest": "apis rest", "desenvolvimento de apis rest": "apis rest",
        "integracao de apis rest": "apis rest", "integracao de apis": "apis rest",
        "ingles": "ingles tecnico",
    }
    return normalizar_para_comparacao(equivalentes.get(nome, equivalentes.get(chave, chave)))


def pos_validar_analise_ia(
    resposta: RespostaAnaliseIA, resultado_local: ResultadoAnalise
) -> tuple[RespostaAnaliseIA, list[str]]:
    """Concilia a opinião externa com o inventário local rastreável."""
    locais = {_chave_requisito_ia(i.item): i for i in resultado_local.analise_por_requisito}
    ajustes: list[str] = []
    requisitos: list[AnaliseIARequisito] = []
    for req in resposta.requisitos_contextuais:
        chave = _chave_requisito_ia(req.item)
        local = locais.get(chave)
        if local and req.status != local.status:
            anterior = req.status
            req = req.model_copy(update={
                "status": local.status,
                "evidencia": local.evidencia_no_curriculo,
                "justificativa": f"Classificação conciliada com evidência local: {local.nivel_evidencia}.",
            })
            rotulo = req.item
            if local.nivel_evidencia == NivelEvidencia.EDUCACIONAL.value:
                ajustes.append(f"{rotulo} rebaixado para evidência educacional")
            elif anterior == "faltando":
                ajustes.append(f"{rotulo} corrigido por evidência ou equivalência local")
            else:
                ajustes.append(f"{rotulo} conciliado com a força da evidência local")
        requisitos.append(req)
    nao_lacunas = {
        _chave_requisito_ia(req.item)
        for req in requisitos
        if req.status in {"encontrado_com_evidencia", "encontrado_sem_contexto_claro", "relacionado_mas_nao_explicito"}
    }
    lacunas = [item for item in resposta.lacunas if _chave_requisito_ia(item) not in nao_lacunas]
    ausentes = {i.item for i in resultado_local.analise_por_requisito if i.nivel_evidencia == NivelEvidencia.AUSENTE.value}
    pontos_fortes: list[str] = []
    for ponto in resposta.pontos_fortes:
        citadas = [item for item in ausentes if normalizar_para_comparacao(item) in normalizar_para_comparacao(ponto)]
        if citadas:
            ajustes.append(f"Ponto forte sem evidência removido: {', '.join(citadas)}")
        else:
            pontos_fortes.append(ponto)
    melhorias, passos = [], list(resposta.proximos_passos)
    for sugestao in resposta.sugestoes_de_melhoria:
        citadas = [item for item in ausentes if normalizar_para_comparacao(item) in normalizar_para_comparacao(sugestao)]
        if citadas and re.search(r"\b(adicione|inclua|declare|destaque|reescreva)\b", normalizar_para_comparacao(sugestao)):
            passos.append(f"Estude ou crie um projeto real com {', '.join(citadas)} antes de incluir como experiência.")
            ajustes.append(f"Sugestão sem evidência para {', '.join(citadas)} movida para próximos passos")
        else:
            melhorias.append(sugestao)
    return resposta.model_copy(update={"requisitos_contextuais": requisitos, "lacunas": lacunas,
        "pontos_fortes": pontos_fortes, "sugestoes_de_melhoria": melhorias,
        "proximos_passos": list(dict.fromkeys(passos))}), list(dict.fromkeys(ajustes))


def calcular_score_final(
    local: int, ia: int | None, confianca: int | None, ajustes: int,
    nivel: str, tem_experiencia: bool, keyword: int | None = None,
    hard_filters_ausentes: int = 0, qualidade_contexto: int | None = None,
    etapas_fallback: int = 0,
) -> tuple[int, str]:
    if ia is None or (confianca or 0) < 70:
        base = round(local * .8 + keyword * .2) if keyword is not None else local
        return base, "A IA não apresentou confiança suficiente; prevaleceram score local e cobertura ponderada de keywords."
    peso_ia = .2 if ajustes >= 3 else .35
    if (qualidade_contexto or 100) < 60:
        peso_ia = min(peso_ia, .15)
    if etapas_fallback:
        peso_ia = max(.05, peso_ia - min(.2, etapas_fallback * .07))
    peso_keyword = .2 if keyword is not None else 0
    peso_local = 1 - peso_ia - peso_keyword
    final = round(local * peso_local + ia * peso_ia + (keyword or 0) * peso_keyword)
    if local < 50 and ia > 80:
        final = min(final, 75)
    if nivel in {NivelVaga.PLENO.value, NivelVaga.SENIOR.value} and not tem_experiencia:
        final = min(final, 65)
    if hard_filters_ausentes:
        final = min(final, max(35, 75 - hard_filters_ausentes * 10))
    return final, f"Conciliação explicável: local {round(peso_local*100)}%, keywords {round(peso_keyword*100)}% e IA {round(peso_ia*100)}%; confiança {confianca}%, correções {ajustes}, etapas com fallback {etapas_fallback}, hard filters ausentes {hard_filters_ausentes}."


def analisar_curriculo(solicitacao: SolicitacaoAnalise) -> ResultadoAnalise:
    """nenhum texto é guardado, só executa pipeline"""

    curriculo_texto_original = solicitacao.curriculo_texto
    vaga_texto_original = solicitacao.vaga_texto
    curriculo_normalizado = normalizar_texto_curriculo(curriculo_texto_original)
    vaga_normalizada = normalizar_texto_curriculo(vaga_texto_original)
    sanitizacao_curriculo = sanitizar_dados_pessoais(curriculo_normalizado)
    sanitizacao_vaga = sanitizar_dados_pessoais(vaga_normalizada)
    urls_fontes = "\n".join(fonte.url for fonte in solicitacao.fontes_curriculo if fonte.url)
    sanitizacao_fontes = sanitizar_dados_pessoais(urls_fontes) if urls_fontes else None
    curriculo_texto_sanitizado = sanitizacao_curriculo.texto_sanitizado
    vaga_texto_sanitizado = sanitizacao_vaga.texto_sanitizado

    vaga = normalizar_texto_vaga(vaga_texto_sanitizado)
    nivel_detectado = detectar_nivel_vaga(vaga_texto_original)
    try:
        nivel_vaga = NivelVaga(normalizar_para_comparacao(solicitacao.nivel_vaga or "")) if solicitacao.nivel_vaga else nivel_detectado
    except ValueError:
        nivel_vaga = nivel_detectado

    parser_secoes = analisar_secoes_curriculo(curriculo_texto_sanitizado)
    secoes = parser_secoes.secoes

    inventario = extrair_inventario_curriculo(curriculo_texto_sanitizado, secoes)
    fact_bank = construir_fact_bank(secoes)

    requisitos = extrair_requisitos_vaga(vaga)
    itens = comparar_curriculo_com_vaga(curriculo_texto_sanitizado, secoes, requisitos)
    grupos_requisitos, score_agrupado, score_por_grupo = construir_grupos_requisitos(itens, nivel_vaga.value, vaga_texto_sanitizado)
    keyword_report, score_keywords, keywords_presentes, keywords_ausentes = construir_keyword_report(
        itens, vaga_texto_sanitizado, curriculo_texto_sanitizado, str(vaga.get("titulo", "")))
    analise_valida, alertas = _entrada_valida(curriculo_texto_sanitizado, vaga_texto_sanitizado)
    impeditivos = detectar_possiveis_impeditivos(curriculo_texto_sanitizado, vaga_texto_sanitizado)
    impeditivos.extend(keyword_report.alertas_hard_filters)
    evidencias_dict = detectar_evidencias(curriculo_texto_sanitizado, secoes)
    sugestoes_det = gerar_sugestoes_locais(
        itens, evidencias_dict, impeditivos, vaga_texto_sanitizado
    )

    encontrados = [
        i.item
        for i in itens
        if i.status in {"encontrado_com_evidencia", "encontrado_sem_contexto_claro"}
    ]

    faltando = [
        i.item
        for i in itens
        if i.status not in {"encontrado_com_evidencia", "encontrado_sem_contexto_claro"}
    ]

    inventario["habilidades_nao_exigidas_pela_vaga"] = [
        h
        for h in inventario["habilidades_detectadas"]
        if h not in {i.item for i in itens}
    ]

    detalhes = AnaliseDetalhada(
        requisitos_obrigatorios_encontrados=[
            i.item
            for i in itens
            if i.categoria == "requisito_obrigatorio" and i.item in encontrados
        ],
        requisitos_obrigatorios_faltando=[
            i.item
            for i in itens
            if i.categoria == "requisito_obrigatorio" and i.item in faltando
        ],
        diferenciais_encontrados=[
            i.item
            for i in itens
            if i.categoria == "diferencial" and i.item in encontrados
        ],
        diferenciais_faltando=[
            i.item for i in itens if i.categoria == "diferencial" and i.item in faltando
        ],
        tecnologias_encontradas=[
            i.item for i in itens if i.tipo == "tecnologia" and i.item in encontrados
        ],
        tecnologias_faltando=[
            i.item for i in itens if i.tipo == "tecnologia" and i.item in faltando
        ],
        possiveis_impeditivos=impeditivos,
    )

    score = score_agrupado if analise_valida else 0
    if parser_secoes.secoes_baixa_confianca and not any(
        chave in secoes for chave in ("experiencia_profissional", "projetos", "projetos_academicos", "freelas", "open_source", "residencias")
    ):
        score = min(score, 70)

    problemas = detectar_secoes_ausentes(curriculo_texto_sanitizado)
    vaga_longa_com_poucos_requisitos = len(vaga_texto_sanitizado) >= 300 and len(itens) < 3
    if vaga_longa_com_poucos_requisitos:
        alerta_extracao = "Poucos requisitos extraídos da vaga; a pontuação foi limitada por segurança."
        alertas.append(alerta_extracao)
        problemas.append(alerta_extracao)
        score = min(score, 60)

    sugestoes = (
        sugestoes_det.ajustes_recomendados
        + sugestoes_det.lacunas_tecnicas
        + sugestoes_det.pontos_de_atencao
        + sugestoes_det.proximos_passos
    )

    explicacao = "O inventário lista todas as habilidades detectadas; o matching e o score usam somente requisitos reais desta vaga, ponderados por categoria e força da evidência."

    return ResultadoAnalise(
        analise_valida=analise_valida,
        alertas_entrada=alertas,
        pontuacao_ats=score,
        palavras_chave_encontradas=encontrados,
        palavras_chave_faltando=faltando,
        inventario_curriculo=inventario,
        analise_por_requisito=itens,
        analise_detalhada=detalhes,
        evidencias=EvidenciasCurriculo(**evidencias_dict),
        problemas_detectados=problemas,
        sugestoes=sugestoes,
        sugestoes_detalhadas=sugestoes_det,
        explicacao_matching=explicacao,
        resumo_gerado=f"Análise {'válida' if analise_valida else 'inválida'}: {score}% de compatibilidade ponderada.",
        provedor_ia="sem_ia",
        modelo_ia=None,
        nivel_vaga=nivel_vaga.value,
        keyword_report=keyword_report,
        score_keyword_coverage=score_keywords,
        keywords_presentes_ponderadas=keywords_presentes,
        keywords_ausentes_ponderadas=keywords_ausentes,
        explicacao_keyword_coverage="Cobertura ponderada por categoria; hard filters geram alertas fora do score.",
        fact_bank=fact_bank,
        avaliacao_relevancia={"titulo_detectado": vaga.get("titulo", ""), "empresa": vaga.get("empresa", ""),
                              "area": vaga.get("area", ""), "nivel": nivel_vaga.value,
                              "modalidade": vaga.get("modalidade", ""), "localizacao": vaga.get("localidade", ""),
                              "aceita_sem_experiencia": bool(vaga.get("aceita_sem_experiencia"))},
        matriz_evidencia=[{"item": i.item, "fonte": i.fonte_evidencia, "nivel": i.nivel_evidencia} for i in itens],
        lacunas_priorizadas=[{"item": i.item, "peso": i.peso} for i in itens if i.status == "faltando"],
        diagnostico_ats={"score_local": score, "score_keyword_coverage": score_keywords},
        fatores_score_final={"score_local": score, "score_keyword_coverage": score_keywords},
        alertas_score_final=keyword_report.alertas_hard_filters,
        grupos_requisitos=grupos_requisitos,
        score_por_grupo=score_por_grupo,
        score_semantico_agrupado=score_agrupado,
        parser_warnings=parser_secoes.warnings,
        secoes_detectadas=[x for x in secoes if x != "outros"],
        secoes_com_baixa_confianca=parser_secoes.secoes_baixa_confianca,
        fontes_evidencia_resumo=resumo_fontes(fact_bank),
        sanitizacao_resumo={
            "dados_sensiveis_detectados": bool(sanitizacao_curriculo.itens_removidos or (sanitizacao_fontes and sanitizacao_fontes.itens_removidos)),
            "categorias_removidas": list(dict.fromkeys(sanitizacao_curriculo.categorias_removidas + (sanitizacao_fontes.categorias_removidas if sanitizacao_fontes else []))),
            "quantidade_categorias": len(set(sanitizacao_curriculo.categorias_removidas + (sanitizacao_fontes.categorias_removidas if sanitizacao_fontes else []))),
            "links_detectados_por_tipo": {chave: sanitizacao_curriculo.links_detectados_por_tipo.get(chave, 0) + (sanitizacao_fontes.links_detectados_por_tipo.get(chave, 0) if sanitizacao_fontes else 0)
                                          for chave in set(sanitizacao_curriculo.links_detectados_por_tipo) | set(sanitizacao_fontes.links_detectados_por_tipo if sanitizacao_fontes else {})},
            "observacao_segura": "Valores sensíveis foram substituídos antes da análise externa e não são retornados.",
        },
        score_final_recomendado=score,
        explicacao_score_final="Sem análise externa válida, o score final recomendado é igual à pontuação ATS local.",
    )


async def analisar_curriculo_com_ia(
    solicitacao: SolicitacaoAnalise,
    provedor: ProvedorIA,
    propagar_erro_provider: bool = False,
) -> ResultadoAnalise:

    # roda primeiro
    resultado = analisar_curriculo(solicitacao)

    curriculo_sanitizado = sanitizar_dados_pessoais(solicitacao.curriculo_texto)
    vaga_sanitizada = sanitizar_dados_pessoais(solicitacao.vaga_texto)
    itens = list(dict.fromkeys(curriculo_sanitizado.itens_removidos + vaga_sanitizada.itens_removidos))

    segura = solicitacao.model_copy(
        update={

            "curriculo_texto": curriculo_sanitizado.texto_sanitizado,
            "vaga_texto": vaga_sanitizada.texto_sanitizado,
            "fontes_curriculo": [],
        }
    )



    pipeline_ia = None
    try:
        respostas_tarefa = getattr(provedor, "respostas_por_tarefa", None)
        suporta_pipeline = respostas_tarefa is None or bool(respostas_tarefa)
        if suporta_pipeline:
            pipeline_ia, analise_ia = await executar_pipeline_ia(segura, resultado, provedor)
            if len(pipeline_ia.etapas_com_fallback) >= 3:
                analise_ia = await executar_analise_ia_estruturada(segura, resultado, provedor)
        else:
            analise_ia = await executar_analise_ia_estruturada(segura, resultado, provedor)
    except Exception:


        if propagar_erro_provider:
            raise

        analise_ia = None

    if analise_ia is None:
        return resultado.model_copy(
            update={
                "fallback_local_usado": True,
                "score_final_recomendado": resultado.pontuacao_ats,
                "explicacao_score_final": "A IA falhou ou retornou schema inválido; foi mantida a pontuação ATS local.",
                "privacidade": InformacoesPrivacidade(
                    dados_sensiveis_detectados=bool(itens),
                    itens_removidos_antes_ia=itens,
                    texto_enviado_para_ia_foi_sanitizado=True,
                ),
            }
        )

    analise_ia, ajustes_validacao = pos_validar_analise_ia(analise_ia, resultado)
    candidatas = analise_ia.sugestoes_de_melhoria + analise_ia.proximos_passos
    sugestoes_ia: list[str] = []
    vistas: set[str] = set()
    for sugestao in candidatas:
        chave = re.sub(r"\b(select|join|where|insert|update|delete|branches?|pull requests?|code review)\b", "grupo", normalizar_para_comparacao(sugestao))
        if chave not in vistas:
            vistas.add(chave)
            sugestoes_ia.append(sugestao)
        if len(sugestoes_ia) == 10:
            break
    score_final, explicacao_final = calcular_score_final(
        resultado.pontuacao_ats,
        analise_ia.score_sugerido_ia,
        analise_ia.confianca,
        len(ajustes_validacao),
        resultado.nivel_vaga,
        bool(resultado.evidencias and resultado.evidencias.experiencia_profissional),
        resultado.score_keyword_coverage,
        len(resultado.keyword_report.alertas_hard_filters) if resultado.keyword_report else 0,
        analise_ia.qualidade_contexto_ia,
        len(pipeline_ia.etapas_com_fallback) if pipeline_ia else 0,
    )

    # merge do resultado local com que foi gerado pela IA
    return resultado.model_copy(
        update={
            "resumo_gerado": analise_ia.resumo_contextual,
            "sugestoes": sugestoes_ia or resultado.sugestoes,
            "provedor_ia": provedor.nome,
            "modelo_ia": provedor.modelo,
            "analise_ia": analise_ia,
            "score_sugerido_ia": analise_ia.score_sugerido_ia,
            "justificativa_score_ia": analise_ia.justificativa_score_ia,
            "confianca_ia": analise_ia.confianca,
            "fallback_local_usado": False,
            "validacao_ia_aplicada": True,
            "ajustes_validacao_ia": ajustes_validacao,
            "score_final_recomendado": score_final,
            "explicacao_score_final": explicacao_final,
            "requisitos_contextuais": analise_ia.requisitos_contextuais,
            "lacunas_contextuais": analise_ia.lacunas,
            "proximos_passos": analise_ia.proximos_passos,
            "alertas_contra_inventar": analise_ia.alertas_contra_inventar,
            "papel_ia": analise_ia.papel_ia or ["avaliadora contextual", "auditora de lacunas", "revisora anti-alucinação"],
            "qualidade_contexto_ia": analise_ia.qualidade_contexto_ia,
            "avaliacao_relevancia": analise_ia.avaliacao_relevancia or resultado.avaliacao_relevancia,
            "matriz_evidencia": analise_ia.matriz_evidencia or resultado.matriz_evidencia,
            "lacunas_priorizadas": analise_ia.lacunas_priorizadas or resultado.lacunas_priorizadas,
            "sugestoes_de_reescrita_seguras": analise_ia.sugestoes_de_reescrita_seguras,
            "diagnostico_ats": analise_ia.diagnostico_ats or resultado.diagnostico_ats,
            "score_contextual_ia": analise_ia.score_contextual_ia,
            "fatores_score_final": {"score_local": resultado.pontuacao_ats, "score_keywords": resultado.score_keyword_coverage or 0,
                "score_ia": analise_ia.score_sugerido_ia or 0, "confianca_ia": analise_ia.confianca,
                "correcoes_ia": len(ajustes_validacao), "etapas_com_fallback": len(pipeline_ia.etapas_com_fallback) if pipeline_ia else 0},
            "pipeline_ia": pipeline_ia,
            "etapas_ia_executadas": pipeline_ia.etapas_executadas if pipeline_ia else [],
            "etapas_ia_com_fallback": pipeline_ia.etapas_com_fallback if pipeline_ia else [],
            "evidencias_relevantes_para_vaga": pipeline_ia.evidencias_relevantes if pipeline_ia else [],
            "classificacao_vaga_ia": pipeline_ia.classificacao_vaga if pipeline_ia else None,
            "avaliacao_contextual_requisitos": pipeline_ia.avaliacao_requisitos if pipeline_ia else [],
            "confianca_pipeline_ia": pipeline_ia.confianca_pipeline if pipeline_ia else None,
            "erros_pipeline_ia_sanitizados": [x["mensagem_segura"] for x in pipeline_ia.detalhes_fallback] if pipeline_ia else [],
            "detalhes_fallback_pipeline": pipeline_ia.detalhes_fallback if pipeline_ia else [],
            "privacidade": InformacoesPrivacidade(
                dados_sensiveis_detectados=bool(itens),
                itens_removidos_antes_ia=itens,
                texto_enviado_para_ia_foi_sanitizado=True,
            ),
        }
    )
