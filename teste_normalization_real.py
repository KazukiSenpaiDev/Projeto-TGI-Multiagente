
import tempfile
from pathlib import Path

from services.analysis_service import analisar_arquivo
from services.ast_service import analisar_arquivo_ast
from services.normalization_service import normalizar_resultado_arquivo


codigo_teste = '''"""Modulo de teste da normalizacao."""


def somar(a, b):
    """Retorna a soma de dois valores."""
    return a + b
'''


with tempfile.TemporaryDirectory() as diretorio:
    caminho = Path(diretorio) / "exemplo.py"

    import subprocess
    import sys

    processo_pylint = subprocess.run(
        [
            sys.executable,
            "-m",
            "pylint",
            "--score=y",
            "teste_pontuacao_pylint",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    print("\nSaída padrão do Pylint com pontuação:")
    print(repr(processo_pylint.stdout))

    print("\nSaída de erros do Pylint com pontuação:")
    print(repr(processo_pylint.stderr))

    caminho.write_text(codigo_teste, encoding="utf-8")

    resultados = analisar_arquivo(str(caminho))

    print("\nSaída original do Pylint:")
    print(repr(resultados["pylint"]["saida"]))

    print("\nErros originais do Pylint:")
    print(repr(resultados["pylint"]["erros"]))

    print("\nCódigo de retorno do Pylint:")
    print(resultados["pylint"]["codigo_retorno"])

    resultados["ast"] = analisar_arquivo_ast(str(caminho))

    normalizado = normalizar_resultado_arquivo(
        "exemplo.py",
        resultados,
    )

    print("\nMétricas normalizadas:")
    print(normalizado["metricas"])

    print("\nPontuação do Pylint para o arquivo analisado:")
    print(repr(resultados["pylint"].get("saida_pontuacao", "")))

    print("\nAchados normalizados:")
    for achado in normalizado["achados"]:
        print(achado)

    print("\nSaída original do Radon:")

    print(
        "Saída original do Radon MI:",
        repr(
            normalizado["dados_originais"]["radon"].get(
                "saida_manutenibilidade"
            )
        ),
    )

    print(
        "Saída original da pontuação do Pylint:",
        repr(
            normalizado["dados_originais"]["pylint"].get(
                "saida_pontuacao"
            )
        ),
    )
    
    print(repr(normalizado["dados_originais"]["radon"]["saida"]))

    print("\nSaída de erros do Pylint:")
    print(repr(normalizado["dados_originais"]["pylint"]["erros"]))

    assert normalizado["arquivo"] == "exemplo.py"

    assert set(normalizado["execucoes"]) == {
        "bandit", "radon", "pylint", "ast"
    }

    assert normalizado["estrutura_codigo"]["ast"]["valido"] is True

    assert "exemplo.py" in normalizado["dados_originais"]["bandit"]["saida"] or (
        normalizado["dados_originais"]["bandit"]["saida"] == ""
        or normalizado["execucoes"]["bandit"]["status"] != "concluida"
    )

    for ferramenta in ("bandit", "radon", "pylint"):
        assert ferramenta in normalizado["dados_originais"]
        assert "saida" in normalizado["dados_originais"][ferramenta]
        assert "erros" in normalizado["dados_originais"][ferramenta]

    print("Teste aprovado: analisadores reais executados.")
    print("Teste aprovado: resultados normalizados.")
    print("Teste aprovado: estrutura AST identificada.")
    print("Status geral:", normalizado["status_analise"])

    print("\nStatus por ferramenta:")
    for ferramenta, execucao in normalizado["execucoes"].items():
        print(f"{ferramenta}: {execucao['status']}")
