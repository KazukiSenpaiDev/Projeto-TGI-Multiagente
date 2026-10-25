import subprocess
import sys
from pathlib import Path
from services.ast_service import analisar_arquivo_ast

def analisar_arquivo(caminho_arquivo: str) -> dict:
    caminho = Path(caminho_arquivo)

    if not caminho.is_file():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )

    if caminho.suffix.lower() != ".py":
        raise ValueError(
            "A análise só aceita arquivos Python (.py)."
        )

    analisadores = {
        "bandit": [sys.executable, "-m", "bandit", str(caminho)],
        "radon": [
            sys.executable, "-m", "radon", "cc",
            str(caminho), "-s"
        ],
        "pylint": [sys.executable, "-m", "pylint", str(caminho)],
    }

    resultados = {}

    for nome, comando in analisadores.items():
        try:
            processo = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=60,
                check=False,
            )

            resultados[nome] = {
                "codigo_retorno": processo.returncode,
                "saida": processo.stdout,
                "erros": processo.stderr,
            }

        except subprocess.TimeoutExpired:
            resultados[nome] = {
                "codigo_retorno": None,
                "saida": "",
                "erros": "O analisador excedeu o tempo limite de 60 segundos.",
            }

        except OSError as erro:
            resultados[nome] = {
                "codigo_retorno": None,
                "saida": "",
                "erros": f"Não foi possível executar o analisador: {erro}",
            }

    return resultados


def analisar_projeto(pasta_projeto: str) -> dict:
    pasta = Path(pasta_projeto)

    if not pasta.is_dir():
        raise NotADirectoryError(
            f"Pasta do projeto não encontrada: {pasta}"
        )

    arquivos_python = sorted(
        caminho
        for caminho in pasta.rglob("*.py")
        if caminho.is_file()
    )

    resultados = {}

    for arquivo in arquivos_python:
        caminho_relativo = arquivo.relative_to(pasta).as_posix()

        resultados[caminho_relativo] = analisar_arquivo(
            str(arquivo)
        )

        resultados[caminho_relativo]["ast"] = analisar_arquivo_ast(
            str(arquivo)
        )

    return resultados

