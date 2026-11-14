import json

from services.project_storage import (
    _montar_resultados_para_historico,
    _remover_caminhos_locais,
)


# Limite para o texto de erro de uma ferramenta que falhou.
LIMITE_ERRO = 2000

# Esclarecimentos fixos enviados ao auditor junto com os dados. Eles
# evitam que a ausência das saídas brutas, ou o código de retorno das
# ferramentas, seja interpretada como limitação ou como falha.
NOTAS_DA_ENTRADA = [
    "Todas as mensagens do Pylint e todos os alertas do Bandit de cada "
    "arquivo estão na lista 'achados' (campo 'ferramenta'). As métricas "
    "do Radon e a pontuação do Pylint estão em 'metricas'. As saídas "
    "brutas das ferramentas não foram enviadas porque estão integralmente "
    "representadas nesses campos: a ausência delas não é uma limitação "
    "da análise.",

    "O 'codigo_retorno' do Pylint é uma máscara de bits: 1 fatal, 2 erro, "
    "4 aviso, 8 refatoração, 16 convenção e 32 erro de uso da ferramenta. "
    "Os bits de 1 a 16 apenas indicam que mensagens desse tipo foram "
    "emitidas (e elas já estão em 'achados'); por exemplo, 16 significa "
    "somente mensagens de convenção. Não indicam falha de execução nem "
    "mensagens omitidas.",

    "O 'codigo_retorno' do Bandit é 1 quando ele encontrou alertas e 0 "
    "quando não encontrou; não indica falha. A conclusão de cada "
    "ferramenta é indicada por 'status' em 'execucoes'. Falhas aparecem "
    "com outro status e, quando disponível, em 'erros_execucao'.",
]


def preparar_resultados_para_auditoria(resultados_analise: dict) -> dict:
    """Cria a cópia dos resultados que será enviada ao auditor.

    - Remove "dados_originais" (saídas brutas, duplicadas e com caminhos).
    - Troca o caminho de cada achado pelo nome relativo do arquivo.
    - Mantém o texto de erro apenas das ferramentas que não concluíram,
      para que o auditor saiba por que a execução falhou.

    O objeto recebido não é alterado.
    """
    limpos = _montar_resultados_para_historico(resultados_analise)

    for nome_arquivo, resultado in resultados_analise.items():

        if not isinstance(resultado, dict):
            continue

        execucoes = resultado.get("execucoes")
        originais = resultado.get("dados_originais")

        if not isinstance(execucoes, dict) or not isinstance(originais, dict):
            continue

        erros = {}

        for ferramenta, execucao in execucoes.items():

            if (
                not isinstance(execucao, dict)
                or execucao.get("status") == "concluida"
            ):
                continue

            bruto = originais.get(ferramenta)
            texto = bruto.get("erros") if isinstance(bruto, dict) else None

            if isinstance(texto, str) and texto.strip():
                erros[ferramenta] = texto[:LIMITE_ERRO]

        if erros and isinstance(limpos.get(nome_arquivo), dict):
            limpos[nome_arquivo]["erros_execucao"] = erros

    return _remover_caminhos_locais(limpos)


def montar_entrada_auditoria(
    codigo_gerado: dict,
    resultados_analise: dict,
    incluir_notas: bool = True,
) -> str:
    """Monta o texto JSON compacto enviado ao auditor.

    incluir_notas: acrescenta os esclarecimentos fixos de NOTAS_DA_ENTRADA.
    """
    entrada = {}

    if incluir_notas:
        entrada["notas_da_entrada"] = NOTAS_DA_ENTRADA

    entrada["codigo_gerado"] = codigo_gerado
    entrada["resultados_analise"] = preparar_resultados_para_auditoria(
        resultados_analise
    )

    return json.dumps(
        entrada,
        ensure_ascii=False,
        separators=(",", ":")
    )