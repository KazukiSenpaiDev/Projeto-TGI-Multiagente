
import streamlit as st
from services.prompt_service import receber_prompt
import html


# ============================================================
# CONFIGURAÇÃO INICIAL
# ============================================================

def configurar_pagina():

    st.set_page_config(
        page_title="TGI Multiagente | Dashboard",
        page_icon="🧩",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    st.markdown(
        """
        <style>

        /* ================================================== */
        /* ESTRUTURA GERAL                                    */
        /* ================================================== */

        .stApp {
            background-color: #0B0F17;
            color: #E5E7EB;
        }

        .block-container {
            max-width: 100%;
            padding: 2rem 3.5rem 4rem 3.5rem;
        }

        header[data-testid="stHeader"] {
            background-color: transparent;
        }

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        /* ================================================== */
        /* CABEÇALHO                                          */
        /* ================================================== */

        .app-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-bottom: 25px;
            margin-bottom: 30px;
            border-bottom: 1px solid #252D3A;
        }

        .brand-area {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .brand-icon {
            width: 52px;
            height: 52px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 13px;
            background: #172D4B;
            font-size: 27px;
        }

        .brand-title {
            font-size: 25px;
            font-weight: 750;
            color: #F8FAFC;
            letter-spacing: -0.5px;
        }

        .brand-description {
            font-size: 13px;
            color: #94A3B8;
            margin-top: 3px;
        }

        .system-status {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #94A3B8;
            font-size: 12px;
            background: #141B26;
            border: 1px solid #273449;
            border-radius: 20px;
            padding: 8px 13px;
        }

        .status-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #22C55E;
        }

        /* ================================================== */
        /* TÍTULOS E SEÇÕES                                   */
        /* ================================================== */

        .section-heading {
            font-size: 19px;
            font-weight: 700;
            color: #F1F5F9;
            margin-bottom: 5px;
        }

        .section-description {
            font-size: 13px;
            color: #94A3B8;
            margin-bottom: 18px;
        }

        .section-number {
            color: #60A5FA;
            font-size: 12px;
            font-weight: 700;
            margin-bottom: 7px;
            letter-spacing: 1px;
        }

        /* ================================================== */
        /* PAINÉIS                                            */
        /* ================================================== */

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #111823;
            border: 1px solid #273449;
            border-radius: 13px;
        }

        /* ================================================== */
        /* CAMPO DE TEXTO                                     */
        /* ================================================== */

        .stTextArea textarea {
            background-color: #0D131D !important;
            color: #E5E7EB !important;
            border: 1px solid #303D50 !important;
            border-radius: 9px !important;
            font-size: 14px !important;
            line-height: 1.6 !important;
        }

        .stTextArea textarea:focus {
            border-color: #3B82F6 !important;
            box-shadow: 0 0 0 1px #3B82F6 !important;
        }

        /* ================================================== */
        /* BOTÕES                                             */
        /* ================================================== */

        .stButton button {
            border-radius: 8px;
            min-height: 42px;
            font-weight: 650;
            transition: 0.2s ease;
        }

        .stButton button[kind="primary"] {
            background-color: #2563EB;
            border: 1px solid #3B82F6;
            color: white;
        }

        .stButton button[kind="primary"]:hover {
            background-color: #1D4ED8;
            border-color: #60A5FA;
        }

        /* ================================================== */
        /* CARTÕES DE INDICADORES                             */
        /* ================================================== */

        .metric-card {
            background: #111823;
            border: 1px solid #273449;
            border-radius: 12px;
            padding: 19px 20px;
            min-height: 125px;
            border-top: 2px solid #334155;
        }

        .metric-label {
            color: #94A3B8;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 15px;
        }

        .metric-value {
            color: #F8FAFC;
            font-size: 27px;
            font-weight: 750;
            letter-spacing: -0.5px;
        }

        .metric-description {
            color: #64748B;
            font-size: 11px;
            margin-top: 7px;
        }

        /* ================================================== */
        /* GRÁFICOS                                           */
        /* ================================================== */

        [data-testid="stVegaLiteChart"] {
            background: #111823;
            border: 1px solid #273449;
            border-radius: 12px;
            padding: 0;
            width: 100%;
            overflow: hidden;
            box-sizing: border-box;
        }

        /* ================================================== */
        /* EXPLORADOR DE ARQUIVOS                             */
        /* ================================================== */

        .file-list-title {
            color: #60A5FA;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }

        .st-key-arquivo_selecionado [role="radiogroup"] {
            gap: 4px;
        }

        .st-key-arquivo_selecionado label {
            width: 100%;
            padding: 8px 10px;
            border-radius: 8px;
            transition: 0.15s ease;
        }

        .st-key-arquivo_selecionado label:hover {
            background: #1A2433;
        }

        .st-key-arquivo_selecionado label:has(input:checked) {
            background: #172D4B;
        }

        .code-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            padding-bottom: 10px;
            margin-bottom: 6px;
            border-bottom: 1px solid #273449;
        }

        .code-file-name {
            color: #F1F5F9;
            font-size: 14px;
            font-weight: 650;
        }

        .code-meta {
            color: #64748B;
            font-size: 11px;
        }

        [data-testid="stCode"],
        [data-testid="stCode"] pre {
            background: #0D131D !important;
            border-radius: 9px;
        }


        /* ================================================== */
        /* RESPONSIVIDADE                                     */
        /* ================================================== */

        @media (max-width: 900px) {

            .block-container {
                padding: 1.5rem 1rem 3rem 1rem;
            }

            .app-header {
                align-items: flex-start;
                flex-direction: column;
                gap: 15px;
            }

            .brand-title {
                font-size: 21px;
            }

        }

        </style>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# CABEÇALHO
# ============================================================

def mostrar_cabecalho():

    st.html("""
        <div class="app-header">

            <div class="brand-area">

                <div class="brand-icon">🧩</div>

                <div>
                    <div class="brand-title">
                        TGI Multiagente
                    </div>

                    <div class="brand-description">
                        Plataforma de geração, análise e diagnóstico
                        inteligente de software
                    </div>
                </div>

            </div>

            <div class="system-status">
                <span class="status-dot"></span>
                Sistema de análise multiagente
            </div>

        </div>
    """)


# ============================================================
# INDICADORES
# ============================================================

def mostrar_cartao(titulo, valor, descricao, cor="#334155"):

    titulo = html.escape(str(titulo))
    valor = html.escape(str(valor))
    descricao = html.escape(str(descricao))
    cor = html.escape(str(cor))

    st.html(
        f"""
        <div class="metric-card" style="border-top-color: {cor};">

            <div class="metric-label">
                {titulo}
            </div>

            <div class="metric-value">
                {valor}
            </div>

            <div class="metric-description">
                {descricao}
            </div>

        </div>
        """
    )


def contar_ferramentas_concluidas(resultados_analise: dict):

    ferramentas = ("bandit", "radon", "pylint", "ast")

    if not isinstance(resultados_analise, dict) or not resultados_analise:
        return None

    total_concluidas = 0

    for ferramenta in ferramentas:

        ferramenta_concluida = True

        for resultado_arquivo in resultados_analise.values():

            if not isinstance(resultado_arquivo, dict):
                ferramenta_concluida = False
                break

            execucoes = resultado_arquivo.get("execucoes")

            if not isinstance(execucoes, dict):
                ferramenta_concluida = False
                break

            resultado_ferramenta = execucoes.get(ferramenta)

            if (
                not isinstance(resultado_ferramenta, dict)
                or resultado_ferramenta.get("status") != "concluida"
            ):
                ferramenta_concluida = False
                break

        if ferramenta_concluida:
            total_concluidas += 1

    return total_concluidas


def mostrar_visao_geral(resposta: dict, arquivos: list):

    diagnostico = resposta.get("diagnostico")
    resultados_analise = resposta.get("resultados_analise")

    status_legivel = {
        "aprovado": "Aprovado",
        "aprovado_com_ressalvas": "Com ressalvas",
        "reprovado": "Reprovado",
        "inconclusivo": "Inconclusivo"
    }

    status = "Indisponível"

    if isinstance(diagnostico, dict):
        status = status_legivel.get(
            diagnostico.get("status"),
            "Indisponível"
        )

    quantidade_arquivos = sum(
        1
        for arquivo in arquivos
        if (
            isinstance(arquivo, dict)
            and isinstance(arquivo.get("nome"), str)
            and isinstance(arquivo.get("conteudo"), str)
        )
    )

    quantidade_problemas = "Indisponível"

    if isinstance(diagnostico, dict):

        problemas = diagnostico.get("problemas_identificados")

        if isinstance(problemas, list):
            quantidade_problemas = len(problemas)

    ferramentas = contar_ferramentas_concluidas(
        resultados_analise
    )

    ferramentas_valor = (
        f"{ferramentas}/4"
        if ferramentas is not None
        else "Indisponível"
    )

    cores_status = {
        "Aprovado": "#22C55E",
        "Com ressalvas": "#EAB308",
        "Reprovado": "#EF4444",
        "Inconclusivo": "#64748B"
    }

    st.markdown(
        """
        <div class="section-number">01 / VISÃO GERAL</div>
        <div class="section-heading">Resumo da análise</div>
        <div class="section-description">
            Indicadores gerais do projeto gerado e auditado.
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        mostrar_cartao(
            "STATUS DA AUDITORIA",
            status,
            "Resultado da avaliação da IA",
            cores_status.get(status, "#64748B")
        )

    with col2:
        mostrar_cartao(
            "ARQUIVOS GERADOS",
            quantidade_arquivos,
            "Arquivos produzidos pelo gerador",
            "#3B82F6"
        )

    with col3:
        mostrar_cartao(
            "PROBLEMAS IDENTIFICADOS",
            quantidade_problemas,
            "Registros do diagnóstico da IA",
            "#F59E0B"
        )

    with col4:
        mostrar_cartao(
            "FERRAMENTAS CONCLUÍDAS",
            ferramentas_valor,
            "Bandit, Radon, Pylint e AST",
            "#8B5CF6"
        )

    if isinstance(diagnostico, dict):
        mostrar_graficos(diagnostico)


# ============================================================
# GRÁFICOS
# ============================================================

def mostrar_graficos(diagnostico: dict):

    st.markdown(
        """
        <div class="section-number">02 / ANÁLISE</div>
        <div class="section-heading">Distribuição dos problemas</div>
        <div class="section-description">
            Classificação dos problemas identificados pela IA Auditora.
        </div>
        """,
        unsafe_allow_html=True
    )

    problemas = diagnostico.get("problemas_identificados")

    if not isinstance(problemas, list):
        st.warning("Os dados dos problemas não estão disponíveis.")
        return

    if not problemas:
        st.info(
            "A IA Auditora não identificou problemas para apresentar nos gráficos."
        )
        return

    severidades = {
        "critica": ("Crítica", "#DC2626"),
        "alta": ("Alta", "#EA5808"),
        "media": ("Média", "#EAB308"),
        "baixa": ("Baixa", "#3B82F6"),
        "informativa": ("Informativa", "#64748B")
    }

    origens = {
        "bandit": "Bandit",
        "pylint": "Pylint",
        "radon": "Radon",
        "ast": "AST",
        "ia_auditora": "IA Auditora"
    }

    contagem_severidades = {
        chave: 0 for chave in severidades
    }

    contagem_origens = {
        chave: 0 for chave in origens
    }

    for problema in problemas:

        if not isinstance(problema, dict):
            continue

        severidade = problema.get("severidade")
        origem = problema.get("origem")

        if severidade in contagem_severidades:
            contagem_severidades[severidade] += 1

        if origem in contagem_origens:
            contagem_origens[origem] += 1

    dados_severidade = [
        {
            "severidade": severidades[chave][0],
            "quantidade": quantidade
        }
        for chave, quantidade in contagem_severidades.items()
        if quantidade > 0
    ]

    dados_origem = [
        {
            "origem": origens[chave],
            "quantidade": quantidade
        }
        for chave, quantidade in contagem_origens.items()
        if quantidade > 0
    ]

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("**Problemas por severidade**")

        if dados_severidade:

            cores = [
                severidades[chave][1]
                for chave, quantidade in contagem_severidades.items()
                if quantidade > 0
            ]

            grafico_rosca = {
                "background": "#111823",
                "padding": {
                    "left": 12,
                    "right": 12,
                    "top": 12,
                    "bottom": 12
                },
                "mark": {
                    "type": "arc",
                    "innerRadius": 75,
                    "outerRadius": 125
                },
                "encoding": {
                    "theta": {
                        "field": "quantidade",
                        "type": "quantitative"
                    },
                    "color": {
                        "field": "severidade",
                        "type": "nominal",
                        "scale": {
                            "domain": [
                                item["severidade"]
                                for item in dados_severidade
                            ],
                            "range": cores
                        },
                        "legend": {
                            "title": "Severidade",
                            "titleFontSize": 15,
                            "labelFontSize": 14,
                            "symbolSize": 180,
                            "rowPadding": 8
                        }
                    },
                    "tooltip": [
                        {
                            "field": "severidade",
                            "type": "nominal",
                            "title": "Severidade"
                        },
                        {
                            "field": "quantidade",
                            "type": "quantitative",
                            "title": "Problemas"
                        }
                    ]
                },
                "view": {
                    "stroke": None
                }
            }

            st.vega_lite_chart(
                dados_severidade,
                grafico_rosca,
                use_container_width=True
            )

        else:
            st.info("Não há severidades válidas para apresentar.")

    with col2:

        st.markdown("**Problemas por origem**")

        if dados_origem:

            grafico_barras = {
                "background": "#111823",
                "padding": {
                    "left": 12,
                    "right": 12,
                    "top": 12,
                    "bottom": 12
                },
                "mark": {
                    "type": "bar",
                    "cornerRadiusEnd": 5,
                    "size": 75
                },
                "encoding": {
                    "x": {
                        "field": "origem",
                        "type": "nominal",
                        "sort": ["Bandit", "Radon", "Pylint", "IA Auditora"],
                        "axis": {
                            "title": None,
                            "labelAngle": 0
                        }
                    },
                    "y": {
                        "field": "quantidade",
                        "type": "quantitative",
                        "axis": {
                            "title": "Quantidade de problemas",
                            "tickMinStep": 1
                        }
                    },
                    "color": {
                        "value": "#3B82F6"
                    },
                    "tooltip": [
                        {
                            "field": "origem",
                            "type": "nominal",
                            "title": "Origem"
                        },
                        {
                            "field": "quantidade",
                            "type": "quantitative",
                            "title": "Problemas"
                        }
                    ]
                },
                "view": {
                    "stroke": None
                }
            }

            st.vega_lite_chart(
                dados_origem,
                grafico_barras,
                use_container_width=True
            )

        else:
            st.info("Não há origens válidas para apresentar.")


# ============================================================
# EXPLORADOR DE ARQUIVOS
# ============================================================

EXTENSOES_LINGUAGEM = {
    ".py": "python",
    ".json": "json",
    ".md": "markdown",
    ".txt": "text",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".html": "html",
    ".css": "css",
    ".js": "javascript"
}


def obter_linguagem(nome_arquivo: str):

    if "." not in nome_arquivo:
        return "text"

    extensao = "." + nome_arquivo.rsplit(".", 1)[-1].lower()

    return EXTENSOES_LINGUAGEM.get(extensao, "text")

ICONES_ARQUIVO = {
    ".py": "🐍",
    ".json": "📋",
    ".md": "📝",
    ".txt": "📄"
}


def obter_icone(nome_arquivo: str):

    if "." not in nome_arquivo:
        return "📄"

    extensao = "." + nome_arquivo.rsplit(".", 1)[-1].lower()

    return ICONES_ARQUIVO.get(extensao, "📄")


def mostrar_explorador_arquivos(arquivos: list):

    st.markdown(
        """
        <div class="section-number">03 / ARQUIVOS</div>
        <div class="section-heading">Arquivos gerados</div>
        <div class="section-description">
            Selecione um arquivo para consultar o código gerado.
        </div>
        """,
        unsafe_allow_html=True
    )

    arquivos_validos = [
        arquivo
        for arquivo in arquivos
        if (
            isinstance(arquivo, dict)
            and isinstance(arquivo.get("nome"), str)
            and isinstance(arquivo.get("conteudo"), str)
        )
    ]

    if not arquivos_validos:
        st.info("Não há arquivos válidos para apresentar.")
        return

    conteudos = {
        arquivo["nome"]: arquivo["conteudo"]
        for arquivo in arquivos_validos
    }

    nomes = list(conteudos)

    col_lista, col_codigo = st.columns([1, 3])

    with col_lista:

        with st.container(border=True):

            st.markdown(
                f'<div class="file-list-title">'
                f'ARQUIVOS · {len(nomes)}</div>',
                unsafe_allow_html=True
            )

            nome_selecionado = st.radio(
                "Arquivos gerados",
                nomes,
                key="arquivo_selecionado",
                label_visibility="collapsed",
                format_func=lambda nome: f"{obter_icone(nome)}  {nome}"
            )

    with col_codigo:

        conteudo = conteudos[nome_selecionado]
        total_linhas = len(conteudo.splitlines())
        linguagem = obter_linguagem(nome_selecionado)

        with st.container(border=True):

            st.html(
                f"""
                <div class="code-header">

                    <span class="code-file-name">
                        {obter_icone(nome_selecionado)}
                        {html.escape(nome_selecionado)}
                    </span>

                    <span class="code-meta">
                        {html.escape(linguagem.upper())}
                        · {total_linhas} linhas
                        · somente leitura
                    </span>

                </div>
                """
            )

            st.code(
                conteudo,
                language=linguagem,
                line_numbers=True,
                height=500
            )

# ============================================================
# RESULTADOS DAS FERRAMENTAS
# ============================================================

def obter_achados(resultado: dict, ferramenta: str):

    achados = resultado.get("achados")

    if not isinstance(achados, list):
        return []

    return [
        achado
        for achado in achados
        if (
            isinstance(achado, dict)
            and achado.get("ferramenta") == ferramenta
        )
    ]


def obter_linha(achado: dict):

    localizacao = achado.get("localizacao")

    if isinstance(localizacao, dict):
        return localizacao.get("linha")

    return None


def ordenar_por_linha(achados: list):

    return sorted(
        achados,
        key=lambda achado: (
            obter_linha(achado) is None,
            obter_linha(achado) or 0
        )
    )


def classificar_complexidade(valor):

    if not isinstance(valor, (int, float)):
        return "—"

    for limite, grau in ((5, "A"), (10, "B"), (20, "C"), (30, "D"), (40, "E")):
        if valor <= limite:
            return grau

    return "F"


def mostrar_status_execucao(resultado: dict, ferramenta: str):

    execucoes = resultado.get("execucoes")

    execucao = (
        execucoes.get(ferramenta)
        if isinstance(execucoes, dict)
        else None
    )

    if not isinstance(execucao, dict):
        st.warning("Não há informações de execução para esta ferramenta.")
        return False

    status = execucao.get("status")
    codigo_retorno = execucao.get("codigo_retorno")

    if status != "concluida":
        st.error(
            f"A execução não foi concluída (status: {status}). "
            "Os dados abaixo podem estar incompletos."
        )
        return False

    texto = "Execução concluída"

    if codigo_retorno is not None:
        texto += f" · código de retorno {codigo_retorno}"

    st.caption(texto)

    return True


def mostrar_aba_bandit(resultado: dict):

    concluida = mostrar_status_execucao(resultado, "bandit")

    achados = ordenar_por_linha(obter_achados(resultado, "bandit"))

    if not achados:

        if concluida:
            st.info(
                "O Bandit não reportou alertas neste arquivo. "
                "Isso não garante a ausência de vulnerabilidades."
            )

        return

    st.dataframe(
        [
            {
                "Linha": obter_linha(achado),
                "Código": achado.get("codigo"),
                "Severidade": achado.get("severidade"),
                "Confiança": achado.get("confianca"),
                "Descrição": achado.get("descricao")
            }
            for achado in achados
        ],
        hide_index=True,
        width="stretch"
    )


def mostrar_aba_radon(resultado: dict):

    mostrar_status_execucao(resultado, "radon")

    metricas = resultado.get("metricas")

    radon = (
        metricas.get("radon")
        if isinstance(metricas, dict)
        else None
    )

    if not isinstance(radon, dict):
        st.info("Não há métricas do Radon para este arquivo.")
        return

    indice = radon.get("indice_manutenibilidade")

    if indice is not None:
        st.metric("Índice de manutenibilidade", indice)
        st.caption("Escala de 0 a 100. Quanto maior, mais fácil de manter.")

    complexidade = radon.get("complexidade_ciclomatica")

    if not isinstance(complexidade, dict) or not complexidade:
        st.info("O Radon não reportou complexidade por função.")
        return

    st.dataframe(
        [
            {
                "Função": nome,
                "Complexidade": valor,
                "Grau": classificar_complexidade(valor)
            }
            for nome, valor in sorted(
                complexidade.items(),
                key=lambda item: item[1],
                reverse=True
            )
        ],
        hide_index=True,
        width="stretch"
    )

    st.caption(
        "Grau calculado pela interface com a escala padrão do Radon: "
        "A (1–5), B (6–10), C (11–20), D (21–30), E (31–40) e F (41+)."
    )


def mostrar_aba_pylint(resultado: dict):

    concluida = mostrar_status_execucao(resultado, "pylint")

    metricas = resultado.get("metricas")

    pylint = (
        metricas.get("pylint")
        if isinstance(metricas, dict)
        else None
    )

    if isinstance(pylint, dict) and pylint.get("pontuacao") is not None:
        st.metric("Pontuação", f"{pylint['pontuacao']}/10")

    achados = ordenar_por_linha(obter_achados(resultado, "pylint"))

    if not achados:

        if concluida:
            st.info("O Pylint não reportou mensagens neste arquivo.")

        return

    contagem_tipos = {}

    for achado in achados:
        tipo = achado.get("tipo") or "indefinido"
        contagem_tipos[tipo] = contagem_tipos.get(tipo, 0) + 1

    st.caption(
        "Por tipo: "
        + " · ".join(
            f"{tipo} {quantidade}"
            for tipo, quantidade in contagem_tipos.items()
        )
    )

    st.dataframe(
        [
            {
                "Linha": obter_linha(achado),
                "Código": achado.get("codigo"),
                "Tipo": achado.get("tipo"),
                "Símbolo": (
                    achado["localizacao"].get("simbolo")
                    if isinstance(achado.get("localizacao"), dict)
                    else None
                ),
                "Descrição": achado.get("descricao")
            }
            for achado in achados
        ],
        hide_index=True,
        width="stretch"
    )


def mostrar_aba_ast(resultado: dict):

    mostrar_status_execucao(resultado, "ast")

    estrutura = resultado.get("estrutura_codigo")

    info_ast = (
        estrutura.get("ast")
        if isinstance(estrutura, dict)
        else None
    )

    if not isinstance(info_ast, dict):
        st.info("Não há dados da AST para este arquivo.")
        return

    valido = info_ast.get("valido")

    if valido is True:
        st.success("Sintaxe válida: a árvore sintática foi construída.")

    elif valido is False:
        st.error(f"Erro de sintaxe: {info_ast.get('erro')}")

    funcoes = info_ast.get("funcoes")

    if isinstance(funcoes, list) and funcoes:

        st.dataframe(
            [
                {
                    "Função": funcao.get("nome"),
                    "Linha": funcao.get("linha"),
                    "Nº de parâmetros": len(funcao.get("parametros") or []),
                    "Parâmetros": ", ".join(
                        str(parametro)
                        for parametro in (funcao.get("parametros") or [])
                    )
                }
                for funcao in funcoes
                if isinstance(funcao, dict)
            ],
            hide_index=True,
            width="stretch"
        )

    else:
        st.info("Nenhuma função identificada neste arquivo.")

    classes = info_ast.get("classes")

    if isinstance(classes, list) and classes:
        st.caption(f"Classes identificadas: {len(classes)}")
        st.dataframe(classes, hide_index=True, width="stretch")
    else:
        st.caption("Classes identificadas: 0")


def mostrar_resultados_ferramentas(resultados_analise):

    st.markdown(
        """
        <div class="section-number">04 / FERRAMENTAS</div>
        <div class="section-heading">Resultados das ferramentas</div>
        <div class="section-description">
            Saída de cada ferramenta de análise estática, por arquivo.
            As escalas de severidade são próprias de cada ferramenta.
        </div>
        """,
        unsafe_allow_html=True
    )

    if not isinstance(resultados_analise, dict) or not resultados_analise:
        st.info("Não há resultados de análise para apresentar.")
        return

    def rotulo(chave):

        resultado = resultados_analise[chave]

        if isinstance(resultado, dict) and isinstance(
            resultado.get("arquivo"), str
        ):
            return resultado["arquivo"]

        return str(chave)

    with st.container(border=True):

        chave = st.selectbox(
            "Arquivo analisado",
            list(resultados_analise),
            key="ferramentas_arquivo",
            format_func=rotulo
        )

        resultado = resultados_analise[chave]

        if not isinstance(resultado, dict):
            st.warning("O resultado deste arquivo está em formato inválido.")
            return

        st.caption(
            "Um código de retorno diferente de zero não indica falha: "
            "Bandit e Pylint o usam para sinalizar que encontraram problemas."
        )

        aba_bandit, aba_radon, aba_pylint, aba_ast = st.tabs(
            [
                "Bandit · segurança",
                "Radon · complexidade",
                "Pylint · qualidade",
                "AST · estrutura"
            ]
        )

        with aba_bandit:
            mostrar_aba_bandit(resultado)

        with aba_radon:
            mostrar_aba_radon(resultado)

        with aba_pylint:
            mostrar_aba_pylint(resultado)

        with aba_ast:
            mostrar_aba_ast(resultado)


# ============================================================
# DIAGNÓSTICO DA IA AUDITORA
# ============================================================

SEVERIDADES_DIAGNOSTICO = {
    "critica": (0, "🔴", "Crítica"),
    "alta": (1, "🟠", "Alta"),
    "media": (2, "🟡", "Média"),
    "baixa": (3, "🔵", "Baixa"),
    "informativa": (4, "⚪", "Informativa")
}

ROTULOS_ORIGEM = {
    "bandit": "Bandit",
    "pylint": "Pylint",
    "radon": "Radon",
    "ast": "AST",
    "ia_auditora": "IA Auditora"
}

STATUS_DIAGNOSTICO = {
    "aprovado": ("Aprovado", "#22C55E"),
    "aprovado_com_ressalvas": ("Aprovado com ressalvas", "#EAB308"),
    "reprovado": ("Reprovado", "#EF4444"),
    "inconclusivo": ("Inconclusivo", "#64748B")
}


def formatar_local(arquivo, linha):

    if not isinstance(arquivo, str) or not arquivo.strip():
        return "Projeto em geral"

    if isinstance(linha, int):
        return f"{arquivo}:{linha}"

    return f"{arquivo} (sem linha)"


def texto_ou_traco(valor):

    if isinstance(valor, str) and valor.strip():
        return valor

    return "—"


def chave_ordenacao_problema(problema: dict):

    ordem = SEVERIDADES_DIAGNOSTICO.get(
        problema.get("severidade"), (99,)
    )[0]

    arquivo = problema.get("arquivo")
    linha = problema.get("linha")

    return (
        ordem,
        arquivo if isinstance(arquivo, str) else "",
        not isinstance(linha, int),
        linha if isinstance(linha, int) else 0
    )


def mostrar_aba_problemas(problemas):

    problemas_validos = [
        problema
        for problema in (problemas if isinstance(problemas, list) else [])
        if isinstance(problema, dict)
    ]

    if not problemas_validos:
        st.info("A IA Auditora não registrou problemas.")
        return

    st.caption(
        "Ordenados por severidade. Abra cada item para ver a evidência."
    )

    for problema in sorted(problemas_validos, key=chave_ordenacao_problema):

        _, icone, rotulo = SEVERIDADES_DIAGNOSTICO.get(
            problema.get("severidade"),
            (99, "⚫", "Não classificada")
        )

        local = formatar_local(
            problema.get("arquivo"),
            problema.get("linha")
        )

        categoria = texto_ou_traco(problema.get("categoria"))

        with st.expander(f"{icone} {rotulo} · {local} · {categoria}"):

            st.markdown(texto_ou_traco(problema.get("descricao")))

            origem = problema.get("origem")

            if origem == "ia_auditora":
                st.caption("Origem: interpretação da IA Auditora.")

            elif origem in ROTULOS_ORIGEM:
                st.caption(
                    f"Origem: achado da ferramenta {ROTULOS_ORIGEM[origem]} "
                    "(citado pela IA Auditora)."
                )

            else:
                st.caption("Origem: não informada.")

            st.markdown("**Evidência**")

            st.code(
                texto_ou_traco(problema.get("evidencia")),
                language="text",
                wrap_lines=True
            )


def mostrar_aba_melhorias(melhorias):

    melhorias_validas = [
        melhoria
        for melhoria in (melhorias if isinstance(melhorias, list) else [])
        if isinstance(melhoria, dict)
    ]

    if not melhorias_validas:
        st.info("A IA Auditora não registrou melhorias sugeridas.")
        return

    st.caption(
        "Recomendações da IA Auditora. Avalie cada uma criticamente "
        "antes de aplicar: uma sugestão não é, por si só, uma solução segura."
    )

    for melhoria in melhorias_validas:

        aspecto = texto_ou_traco(melhoria.get("aspecto_relacionado"))
        arquivo = melhoria.get("arquivo")

        local = (
            arquivo
            if isinstance(arquivo, str) and arquivo.strip()
            else "Geral"
        )

        with st.expander(f"{aspecto} · {local}"):

            st.markdown("**Recomendação**")
            st.markdown(texto_ou_traco(melhoria.get("recomendacao")))

            st.markdown("**Justificativa**")
            st.markdown(texto_ou_traco(melhoria.get("justificativa")))


def mostrar_aba_pontos_positivos(pontos):

    pontos_validos = [
        ponto
        for ponto in (pontos if isinstance(pontos, list) else [])
        if isinstance(ponto, str) and ponto.strip()
    ]

    if not pontos_validos:
        st.info("A IA Auditora não registrou pontos positivos.")
        return

    for ponto in pontos_validos:
        st.markdown(f"- {ponto}")


def mostrar_aba_limitacoes(limitacoes):

    limitacoes_validas = [
        limitacao
        for limitacao in (
            limitacoes if isinstance(limitacoes, list) else []
        )
        if isinstance(limitacao, dict)
    ]

    if not limitacoes_validas:
        st.info("A IA Auditora não registrou limitações da análise.")
        return

    st.caption(
        "O que esta análise não consegue garantir. "
        "A ausência de alertas não significa ausência de problemas."
    )

    for limitacao in limitacoes_validas:

        ferramenta = texto_ou_traco(limitacao.get("ferramenta"))
        arquivo = limitacao.get("arquivo")

        local = (
            arquivo
            if isinstance(arquivo, str) and arquivo.strip()
            else "geral"
        )

        st.markdown(f"**{ferramenta}** · {local}")
        st.markdown(texto_ou_traco(limitacao.get("motivo")))
        st.divider()


def mostrar_diagnostico_completo(diagnostico):

    st.markdown(
        """
        <div class="section-number">05 / DIAGNÓSTICO</div>
        <div class="section-heading">Diagnóstico da IA Auditora</div>
        <div class="section-description">
            Avaliação completa do projeto, com problemas, evidências,
            recomendações e limitações da análise.
        </div>
        """,
        unsafe_allow_html=True
    )

    if not isinstance(diagnostico, dict):
        st.info("O diagnóstico da IA Auditora não está disponível.")
        return

    status_texto, status_cor = STATUS_DIAGNOSTICO.get(
        diagnostico.get("status"),
        ("Indisponível", "#64748B")
    )

    problemas = diagnostico.get("problemas_identificados")
    melhorias = diagnostico.get("melhorias_sugeridas")
    pontos = diagnostico.get("pontos_positivos")
    limitacoes = diagnostico.get("limitacoes_analise")

    with st.container(border=True):

        st.html(
            f"""
            <span style="
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                border: 1px solid {html.escape(status_cor)};
                color: {html.escape(status_cor)};
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.5px;
            ">
                {html.escape(status_texto.upper())}
            </span>
            """
        )

        st.markdown(texto_ou_traco(diagnostico.get("resumo")))

    def contar(itens):
        return len(itens) if isinstance(itens, list) else 0

    aba_problemas, aba_melhorias, aba_pontos, aba_limitacoes = st.tabs(
        [
            f"Problemas ({contar(problemas)})",
            f"Melhorias ({contar(melhorias)})",
            f"Pontos positivos ({contar(pontos)})",
            f"Limitações ({contar(limitacoes)})"
        ]
    )

    with aba_problemas:
        mostrar_aba_problemas(problemas)

    with aba_melhorias:
        mostrar_aba_melhorias(melhorias)

    with aba_pontos:
        mostrar_aba_pontos_positivos(pontos)

    with aba_limitacoes:
        mostrar_aba_limitacoes(limitacoes)


# ============================================================
# DECISÃO HUMANA (HITL)
# ============================================================

def registrar_decisao(decisao: str):

    st.session_state.decisao_hitl = decisao
    st.session_state.pop("confirmar_novo_projeto", None)


def limpar_decisao():

    st.session_state.pop("decisao_hitl", None)
    st.session_state.pop("confirmar_novo_projeto", None)


def pedir_confirmacao_novo_projeto():

    st.session_state.confirmar_novo_projeto = True


def cancelar_novo_projeto():

    st.session_state.pop("confirmar_novo_projeto", None)


def iniciar_novo_projeto():

    st.session_state.pop("prompt_enviado", None)
    st.session_state.pop("decisao_hitl", None)
    st.session_state.pop("confirmar_novo_projeto", None)


def mostrar_novo_projeto(decisao):

    st.divider()

    if st.session_state.get("confirmar_novo_projeto"):

        st.warning(
            "O resultado atual sairá da tela. Os arquivos gerados continuam "
            "salvos na pasta projetos_gerados, mas esta tela de resultados "
            "não poderá ser recuperada até a fase do histórico. "
            "Deseja continuar?"
        )

        col1, col2, _ = st.columns([1, 1, 3])

        with col1:
            st.button(
                "Sim, descartar",
                type="primary",
                use_container_width=True,
                on_click=iniciar_novo_projeto,
                key="hitl_confirmar_novo"
            )

        with col2:
            st.button(
                "Cancelar",
                use_container_width=True,
                on_click=cancelar_novo_projeto,
                key="hitl_cancelar_novo"
            )

    else:

        if decisao == "aceito":
            acao = iniciar_novo_projeto
        else:
            acao = pedir_confirmacao_novo_projeto

        st.button(
            "Novo projeto",
            on_click=acao,
            key="hitl_novo_projeto"
        )


def mostrar_decisao_hitl(diagnostico):

    st.markdown(
        """
        <div class="section-number">06 / DECISÃO</div>
        <div class="section-heading">Decisão do usuário</div>
        <div class="section-description">
            A decisão final é sua: aceite o resultado ou solicite
            uma nova versão com base no diagnóstico.
        </div>
        """,
        unsafe_allow_html=True
    )

    status = (
        diagnostico.get("status")
        if isinstance(diagnostico, dict)
        else None
    )

    decisao = st.session_state.get("decisao_hitl")

    with st.container(border=True):

        if decisao == "aceito":

            st.success("Você aceitou o resultado deste projeto.")

            st.caption(
                "Nenhum arquivo foi exportado e a decisão ainda não "
                "é salva no histórico (funcionalidades de fases futuras)."
            )

            st.button(
                "Alterar decisão",
                on_click=limpar_decisao,
                key="hitl_alterar_aceito"
            )

        elif decisao == "refinamento":

            st.info(
                "Você solicitou o refinamento deste projeto. "
                "A geração de uma nova versão ainda não está disponível: "
                "será implementada na fase de refinamento."
            )

            st.caption(
                "Nenhuma nova geração foi iniciada e a decisão ainda "
                "não é salva no histórico."
            )

            st.button(
                "Alterar decisão",
                on_click=limpar_decisao,
                key="hitl_alterar_refinamento"
            )

        else:

            if status == "reprovado":
                st.warning(
                    "A IA Auditora reprovou este projeto. "
                    "Revise os problemas do diagnóstico antes de decidir."
                )

            elif status == "inconclusivo":
                st.warning(
                    "A auditoria foi inconclusiva. "
                    "Revise as limitações do diagnóstico antes de decidir."
                )

            col1, col2, _ = st.columns([1, 1, 3])

            with col1:
                st.button(
                    "Aceitar resultado",
                    type="primary",
                    use_container_width=True,
                    on_click=registrar_decisao,
                    args=("aceito",),
                    key="hitl_aceitar"
                )

            with col2:
                st.button(
                    "Solicitar refinamento",
                    use_container_width=True,
                    on_click=registrar_decisao,
                    args=("refinamento",),
                    key="hitl_refinar"
                )

        mostrar_novo_projeto(decisao)


# ============================================================
# GERAÇÃO DO PROJETO
# ============================================================

def projeto_gerado_valido(resposta):

    if not isinstance(resposta, dict) or "error" in resposta:
        return False

    codigo_gerado = resposta.get("codigo_gerado")

    return (
        isinstance(codigo_gerado, dict)
        and isinstance(codigo_gerado.get("arquivos"), list)
    )


def mostrar_area_geracao():

    resposta_atual = st.session_state.get("prompt_enviado")

    if projeto_gerado_valido(resposta_atual):

        st.caption(
            "Projeto gerado. Para iniciar outro, use o botão "
            "**Novo projeto** na seção 06 / DECISÃO, ao final da página."
        )

        return resposta_atual

    st.markdown(
        """
        <div class="section-number">GERAÇÃO</div>
        <div class="section-heading">Novo projeto</div>
        <div class="section-description">
            Descreva o software que deseja desenvolver.
            Os agentes irão gerar e analisar o código automaticamente.
        </div>
        """,
        unsafe_allow_html=True
    )

    geracao_concluida = False

    with st.container(border=True):

        prompt = st.text_area(
            "Descrição do projeto",
            height=145,
            key="prompt_text_area",
            placeholder=(
                "Exemplo: Crie um sistema de cadastro de produtos em Python, "
                "com funcionalidades de inclusão, consulta, atualização e exclusão."
            )
        )

        col1, col2 = st.columns([1, 5])

        with col1:

            gerar = st.button(
                "Gerar projeto",
                type="primary",
                use_container_width=True
            )

        if gerar:

            if not prompt.strip():

                st.warning("Digite uma descrição antes de gerar o projeto.")

            else:

                with st.spinner(
                    "Os agentes estão gerando, analisando e auditando o projeto..."
                ):

                    try:
                        resposta = receber_prompt(prompt)

                        st.session_state.prompt_enviado = resposta
                        st.session_state.pop("decisao_hitl", None)
                        st.session_state.pop("confirmar_novo_projeto", None)

                        geracao_concluida = True

                    except Exception:
                        st.session_state.prompt_enviado = None
                        st.session_state.pop("decisao_hitl", None)
                        st.session_state.pop("confirmar_novo_projeto", None)
                        st.error(
                            "Não foi possível concluir a comunicação com a API."
                        )

    if geracao_concluida:
        st.rerun()

    return st.session_state.get("prompt_enviado")


# ============================================================
# RESULTADO DA GERAÇÃO
# ============================================================

def mostrar_resultado(resposta):

    if not isinstance(resposta, dict):
        st.error("A resposta recebida da API é inválida.")
        return

    if "error" in resposta:
        st.error(resposta["error"])
        return

    codigo_gerado = resposta.get("codigo_gerado")

    if not isinstance(codigo_gerado, dict):
        st.error("A resposta da API não contém os arquivos gerados.")
        return

    arquivos = codigo_gerado.get("arquivos")

    if not isinstance(arquivos, list):
        st.error("A resposta não contém uma lista válida de arquivos.")
        return

    st.success(
        resposta.get("message", "Projeto gerado com sucesso!")
    )

    with st.expander("Visualizar descrição enviada"):

        st.code(
            resposta.get("Prompt_recebido", ""),
            language="text"
        )

    mostrar_visao_geral(resposta, arquivos)

    mostrar_explorador_arquivos(arquivos)

    mostrar_resultados_ferramentas(resposta.get("resultados_analise"))

    mostrar_diagnostico_completo(resposta.get("diagnostico"))

    mostrar_decisao_hitl(resposta.get("diagnostico"))


# ============================================================
# INTERFACE PRINCIPAL
# ============================================================

def mostrar_interface():

    configurar_pagina()

    mostrar_cabecalho()

    resposta = mostrar_area_geracao()

    if resposta is not None:

        st.divider()

        mostrar_resultado(resposta)
