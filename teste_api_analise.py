
from fastapi.testclient import TestClient
from unittest.mock import patch
from pathlib import Path

from backend.api import app


cliente = TestClient(app)


def testar_api_com_falha_de_analisador():
    codigo_falso = [
        {
            "nome": "main.py",
            "conteudo": "print('Olá, mundo!')",
        }
    ]

    resultados_falsos = {
        "main.py": {
            "bandit": {
                "codigo_retorno": None,
                "saida": "",
                "erros": "Não foi possível executar o analisador: falha simulada",
            },
            "radon": {
                "codigo_retorno": 0,
                "saida": "main.py - A (1)",
                "erros": "",
            },
            "pylint": {
                "codigo_retorno": 0,
                "saida": "Your code has been rated at 10.00/10",
                "erros": "",
            },
        }
    }

    with (
        patch("backend.api.gerar_codigo", return_value=codigo_falso),
        patch(
            "backend.api.salvar_projeto",
            return_value=Path("projetos_gerados/teste"),
        ),
        patch(
            "backend.api.analisar_projeto",
            return_value=resultados_falsos,
        ),
    ):
        resposta = cliente.post(
            "/gerar",
            json={"prompt": "Gere um programa simples em Python."},
        )

    assert resposta.status_code == 200, resposta.text

    dados = resposta.json()
    analises = dados["resultados_analise"]["main.py"]

    assert analises["bandit"]["codigo_retorno"] is None
    assert "falha simulada" in analises["bandit"]["erros"]
    assert analises["radon"]["codigo_retorno"] == 0
    assert analises["pylint"]["codigo_retorno"] == 0

    print("Teste aprovado: a API respondeu HTTP 200.")
    print("Teste aprovado: o erro do Bandit foi preservado.")
    print("Teste aprovado: os resultados do Radon e Pylint foram retornados.")


if __name__ == "__main__":
    testar_api_com_falha_de_analisador()
