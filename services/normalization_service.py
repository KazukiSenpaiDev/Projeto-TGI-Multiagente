
import json
import re
from pathlib import Path


def _extrair_json_bandit(saida: str) -> dict:
    """Interpreta a saída JSON do Bandit."""
    try:
        dados = json.loads(saida or "{}")
        if isinstance(dados, dict):
            return dados
    except (json.JSONDecodeError, TypeError):
        pass

    return {}


def _extrair_achados_bandit(saida: str) -> list:
    """Converte os resultados JSON do Bandit em achados."""
    dados = _extrair_json_bandit(saida)
    achados = []

    for resultado in dados.get("results", []):
        if not isinstance(resultado, dict):
            continue

        achados.append({
            "ferramenta": "bandit",
            "tipo": "seguranca",
            "codigo": resultado.get("test_id"),
            "severidade": resultado.get("issue_severity"),
            "descricao": resultado.get("issue_text"),
            "localizacao": {
                "linha": resultado.get("line_number"),
                "arquivo": resultado.get("filename"),
            },
        })

    return achados


def _extrair_achados_pylint(saida: str) -> list:
    """Interpreta as mensagens JSON do Pylint."""
    try:
        mensagens = json.loads(saida or "[]")
    except (json.JSONDecodeError, TypeError):
        return []

    if not isinstance(mensagens, list):
        return []

    achados = []

    for mensagem in mensagens:
        if not isinstance(mensagem, dict):
            continue

        achados.append({
            "ferramenta": "pylint",
            "tipo": mensagem.get("type"),
            "codigo": mensagem.get("message-id"),
            "severidade": mensagem.get("type"),
            "descricao": mensagem.get("message"),
            "localizacao": {
                "linha": mensagem.get("line"),
                "coluna": mensagem.get("column"),
                "arquivo": mensagem.get("path"),
                "simbolo": mensagem.get("symbol"),
            },
        })

    return achados


def _extrair_pontuacao_pylint(saida: str):
    """Extrai a pontuação final do Pylint, quando disponível."""
    padrao = r"Your code has been rated at\s+(-?\d+(?:\.\d+)?)/10"
    resultado = re.search(padrao, saida or "")

    if resultado:
        return float(resultado.group(1))

    return None



def _extrair_complexidade_radon(saida: str) -> dict:
    """Extrai nomes e complexidades da saída do Radon."""
    complexidades = {}

    padrao = (
        r"^\s*(?:[A-Z]\s+\d+:\d+\s+)?"
        r"(?P<nome>.+?)\s*-\s*"
        r"(?P<classe>[A-F])\s*"
        r"\((?P<complexidade>\d+)\)\s*$"
    )

    for linha in (saida or "").splitlines():
        resultado = re.match(padrao, linha)

        if not resultado:
            continue

        nome = resultado.group("nome").strip()
        complexidade = int(resultado.group("complexidade"))

        complexidades[nome] = complexidade

    return complexidades


def _extrair_indice_manutenibilidade_radon(saida: str):
    """Extrai o índice de manutenibilidade da saída do Radon."""
    padrao = r"-\s+[A-C]\s+\((\d+(?:\.\d+)?)\)"

    resultado = re.search(padrao, saida or "")

    if resultado:
        return float(resultado.group(1))

    return None


def normalizar_resultado_arquivo(
    nome_arquivo: str,
    resultados_originais: dict,
) -> dict:
    """Organiza e preserva os resultados das ferramentas."""

    achados = []

    metricas = {
        "radon": {
            "complexidade_ciclomatica": {},
            "indice_manutenibilidade": None,
        },
        "pylint": {
            "pontuacao": None,
        },
    }

    ast_padrao = {
        "valido": None,
        "erro": "Resultado da AST não disponível.",
        "funcoes": [],
        "classes": [],
    }

    resultado_ast = resultados_originais.get("ast", ast_padrao)

    estrutura_codigo = {
        "ast": resultado_ast,
    }

    execucoes = {}
    dados_originais = {}

    for ferramenta in ("bandit", "radon", "pylint"):
        resultado = resultados_originais.get(ferramenta)

        if not isinstance(resultado, dict):
            execucoes[ferramenta] = {
                "status": "resultado_invalido",
                "codigo_retorno": None,
            }
            dados_originais[ferramenta] = {
                "saida": "",
                "erros": "Resultado ausente ou inválido.",
            }
            continue

        codigo_retorno = resultado.get("codigo_retorno")
        saida = resultado.get("saida", "")
        erros = resultado.get("erros", "")

        if codigo_retorno is None:
            status = (
                "timeout"
                if "tempo limite" in str(erros).lower()
                else "falha"
            )
        else:
            status = "concluida"

        execucoes[ferramenta] = {
            "status": status,
            "codigo_retorno": codigo_retorno,
        }

        dados_originais[ferramenta] = {
            "saida": saida,
            "erros": erros,
        }

        if ferramenta == "radon":
            dados_originais[ferramenta]["saida_manutenibilidade"] = (
                resultado.get("saida_manutenibilidade", "")
            )
            dados_originais[ferramenta]["erros_manutenibilidade"] = (
                resultado.get("erros_manutenibilidade", "")
            )

        elif ferramenta == "pylint":
            dados_originais[ferramenta]["saida_pontuacao"] = (
                resultado.get("saida_pontuacao", "")
            )

        
        if status != "concluida":
            continue

        if ferramenta == "bandit":
            dados_json = _extrair_json_bandit(saida)

            if not isinstance(dados_json.get("results"), list):
                execucoes[ferramenta]["status"] = (
                    "resultado_invalido"
                )
                continue

        elif ferramenta == "pylint":
            try:
                dados_json = json.loads(saida or "[]")
            except (json.JSONDecodeError, TypeError):
                dados_json = None

            if not isinstance(dados_json, list):
                execucoes[ferramenta]["status"] = (
                    "resultado_invalido"
                )
                continue

        elif ferramenta == "radon":
            if not isinstance(saida, str):
                execucoes[ferramenta]["status"] = (
                    "resultado_invalido"
                )
                continue


        if ferramenta == "bandit":
            if isinstance(saida, str):
                achados.extend(_extrair_achados_bandit(saida))

        elif ferramenta == "radon":
            if isinstance(saida, str):
                metricas["radon"]["complexidade_ciclomatica"] = (
                    _extrair_complexidade_radon(saida)
                )

                saida_manutenibilidade = resultado.get(
                    "saida_manutenibilidade", ""
                )

                metricas["radon"]["indice_manutenibilidade"] = (
                    _extrair_indice_manutenibilidade_radon(
                        saida_manutenibilidade
                    )
                )

        elif ferramenta == "pylint":
            if isinstance(saida, str):
                achados.extend(_extrair_achados_pylint(saida))
                metricas["pylint"]["pontuacao"] = (
                    _extrair_pontuacao_pylint(
                        resultado.get("saida_pontuacao", "")
                    )
                )

    if resultado_ast.get("valido") is False:
        achados.append({
            "ferramenta": "ast",
            "tipo": "sintaxe",
            "codigo": "ERRO_SINTAXE",
            "severidade": None,
            "descricao": resultado_ast.get(
                "erro", "Erro de sintaxe não especificado."
            ),
            "localizacao": {},
        })

    status_ast = (
        "concluida"
        if resultado_ast.get("valido") is not None
        else "resultado_invalido"
    )

    execucoes["ast"] = {"status": status_ast}

    status_analise = (
        "concluida"
        if all(
            execucoes[ferramenta]["status"] == "concluida"
            for ferramenta in ("bandit", "radon", "pylint")
        ) and status_ast == "concluida"
        else "parcial"
    )

    return {
        "arquivo": Path(nome_arquivo).as_posix(),
        "status_analise": status_analise,
        "achados": achados,
        "metricas": metricas,
        "estrutura_codigo": estrutura_codigo,
        "execucoes": execucoes,
        "dados_originais": dados_originais,
    }


def normalizar_resultados_projeto(resultados_originais: dict) -> dict:
    """Normaliza os resultados de análise de todos os arquivos do projeto."""
    resultados_normalizados = {}

    for nome_arquivo, resultados_arquivo in resultados_originais.items():
        if not isinstance(resultados_arquivo, dict):
            resultados_normalizados[nome_arquivo] = {
                "arquivo": Path(nome_arquivo).as_posix(),
                "status_analise": "parcial",
                "achados": [],
                "metricas": {
                    "radon": {
                        "complexidade_ciclomatica": {},
                        "indice_manutenibilidade": None,
                    },
                    "pylint": {"pontuacao": None},
                },
                "estrutura_codigo": {
                    "ast": {
                        "valido": None,
                        "erro": "Resultado da AST não disponível.",
                        "funcoes": [],
                        "classes": [],
                    }
                },
                "execucoes": {},
                "dados_originais": {},
            }
            continue

        resultados_normalizados[nome_arquivo] = normalizar_resultado_arquivo(
            nome_arquivo,
            resultados_arquivo,
        )

    return resultados_normalizados
