
from services.normalization_service import normalizar_resultados_projeto

from services.normalization_service import (
    normalizar_resultado_arquivo,
)


def criar_resultados():
    """Cria resultados simulados para os testes."""
    return {
        "bandit": {
            "codigo_retorno": 0,
            "saida": '{"results": []}',
            "erros": "",
        },
        "radon": {
            "codigo_retorno": 0,
            "saida": "main.py\n    somar - A (1)\n",
            "erros": "",
        },
        "pylint": {
            "codigo_retorno": 0,
            "saida": "[]",
            "erros": "",
            "saida_pontuacao": "Your code has been rated at 10.00/10",
        },
        "ast": {
            "valido": True,
            "erro": None,
            "funcoes": [],
            "classes": [],
        },
    }


# TESTE 1: falha de execução do Bandit
resultados = criar_resultados()

resultados["bandit"] = {
    "codigo_retorno": None,
    "saida": "",
    "erros": "Não foi possível executar o analisador.",
}

resultado = normalizar_resultado_arquivo("main.py", resultados)

assert resultado["execucoes"]["bandit"]["status"] == "falha"
assert resultado["execucoes"]["radon"]["status"] == "concluida"
assert resultado["execucoes"]["pylint"]["status"] == "concluida"
assert resultado["dados_originais"]["bandit"]["erros"] == (
    "Não foi possível executar o analisador."
)

print("Teste aprovado: falha de execução tratada.")


# TESTE 2: saída JSON inválida do Bandit
resultados = criar_resultados()
resultados["bandit"]["saida"] = "Isto não é um JSON válido."

resultado = normalizar_resultado_arquivo("main.py", resultados)

assert resultado["achados"] == []
assert resultado["dados_originais"]["bandit"]["saida"] == (
    "Isto não é um JSON válido."
)
assert (
    resultado["execucoes"]["bandit"]["status"]
    == "resultado_invalido"
)
assert resultado["status_analise"] == "parcial"

print("Teste aprovado: saída inválida identificada.")
print("Teste aprovado: análise parcial identificada.")

# TESTE 3: AST indisponível
resultados = criar_resultados()
del resultados["ast"]

resultado = normalizar_resultado_arquivo("main.py", resultados)

assert resultado["execucoes"]["ast"]["status"] == "resultado_invalido"
assert resultado["status_analise"] == "parcial"
assert resultado["estrutura_codigo"]["ast"]["valido"] is None

print("Teste aprovado: AST indisponível identificada.")
print("Teste aprovado: análise parcial identificada.")


# TESTE 4: uma saída inválida não impede os demais analisadores

resultados = criar_resultados()

resultados["bandit"]["saida"] = "JSON inválido"

resultado = normalizar_resultado_arquivo("main.py", resultados)

assert (
    resultado["execucoes"]["bandit"]["status"]
    == "resultado_invalido"
)

assert (
    resultado["execucoes"]["radon"]["status"]
    == "concluida"
)

assert (
    resultado["execucoes"]["pylint"]["status"]
    == "concluida"
)

assert (
    resultado["metricas"]["radon"]["complexidade_ciclomatica"]["somar"]
    == 1
)

assert resultado["metricas"]["pylint"]["pontuacao"] == 10.0

assert resultado["status_analise"] == "parcial"

print("Teste aprovado: falha isolada do Bandit.")
print("Teste aprovado: métricas do Radon preservadas.")
print("Teste aprovado: pontuação do Pylint preservada.")


def testar_normalizacao_multiplos_arquivos():
    resultados_originais = {
        "main.py": {
            "bandit": {
                "codigo_retorno": 0,
                "saida": '{"results": []}',
                "erros": "",
            },
            "radon": {
                "codigo_retorno": 0,
                "saida": "main.py\n    F 1:0 somar - A (1)\n",
                "erros": "",
                "saida_manutenibilidade": "main.py - A (85.00)\n",
                "erros_manutenibilidade": "",
            },
            "pylint": {
                "codigo_retorno": 0,
                "saida": "[]",
                "erros": "",
                "saida_pontuacao": "Your code has been rated at 10.00/10",
            },
            "ast": {
                "valido": True,
                "erro": None,
                "funcoes": [{"nome": "somar", "linha": 1, "parametros": ["a", "b"]}],
                "classes": [],
            },
        },
        "utils.py": {
            "bandit": {
                "codigo_retorno": 0,
                "saida": '{"results": []}',
                "erros": "",
            },
            "radon": {
                "codigo_retorno": 0,
                "saida": "utils.py\n    F 1:0 multiplicar - A (1)\n",
                "erros": "",
                "saida_manutenibilidade": "utils.py - A (90.00)\n",
                "erros_manutenibilidade": "",
            },
            "pylint": {
                "codigo_retorno": 0,
                "saida": "[]",
                "erros": "",
                "saida_pontuacao": "Your code has been rated at 9.00/10",
            },
            "ast": {
                "valido": True,
                "erro": None,
                "funcoes": [{"nome": "multiplicar", "linha": 1, "parametros": ["a", "b"]}],
                "classes": [],
            },
        },
    }

    resultados = normalizar_resultados_projeto(resultados_originais)

    assert set(resultados.keys()) == {"main.py", "utils.py"}
    assert resultados["main.py"]["arquivo"] == "main.py"
    assert resultados["utils.py"]["arquivo"] == "utils.py"

    assert resultados["main.py"]["metricas"]["radon"]["indice_manutenibilidade"] == 85.0
    assert resultados["utils.py"]["metricas"]["radon"]["indice_manutenibilidade"] == 90.0

    assert resultados["main.py"]["metricas"]["pylint"]["pontuacao"] == 10.0
    assert resultados["utils.py"]["metricas"]["pylint"]["pontuacao"] == 9.0

    assert resultados["main.py"]["estrutura_codigo"]["ast"]["funcoes"][0]["nome"] == "somar"
    assert resultados["utils.py"]["estrutura_codigo"]["ast"]["funcoes"][0]["nome"] == "multiplicar"

    print("Teste aprovado: múltiplos arquivos normalizados separadamente.")
    
testar_normalizacao_multiplos_arquivos()

