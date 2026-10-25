
from services.analysis_service import analisar_arquivo
from unittest.mock import patch
import subprocess
from tempfile import TemporaryDirectory
from pathlib import Path

def testar_arquivo_inexistente():
    try:
        analisar_arquivo("arquivo_que_nao_existe.py")
    except FileNotFoundError:
        print("Teste aprovado: arquivo inexistente rejeitado.")
    else:
        raise AssertionError("O arquivo inexistente foi aceito.")


def testar_extensao_invalida():
    try:
        analisar_arquivo("README.md")
    except ValueError as erro:
        assert "Python" in str(erro)
        print("Teste aprovado: extensão inválida rejeitada.")
    else:
        raise AssertionError("A extensão inválida foi aceita.")




def testar_timeout():
    with TemporaryDirectory() as diretorio:
        arquivo = Path(diretorio) / "teste.py"
        arquivo.write_text("print('teste')\n", encoding="utf-8")

        with patch(
            "services.analysis_service.subprocess.run",
            side_effect=subprocess.TimeoutExpired(
                cmd=["analisador_teste"],
                timeout=60,
            ),
        ):
            resultados = analisar_arquivo(str(arquivo))

    for nome in ("bandit", "radon", "pylint"):
        assert resultados[nome]["codigo_retorno"] is None
        assert "tempo limite" in resultados[nome]["erros"]

    print("Teste aprovado: timeout tratado nos três analisadores.")




def testar_falha_execucao():
    with TemporaryDirectory() as diretorio:
        arquivo = Path(diretorio) / "teste.py"
        arquivo.write_text("print('teste')\n", encoding="utf-8")

        with patch(
            "services.analysis_service.subprocess.run",
            side_effect=OSError("Falha simulada"),
        ):
            resultados = analisar_arquivo(str(arquivo))

    for nome in ("bandit", "radon", "pylint"):
        assert resultados[nome]["codigo_retorno"] is None
        assert "Não foi possível executar" in resultados[nome]["erros"]

    print("Teste aprovado: falha de execução tratada nos três analisadores.")




def testar_falha_de_um_analisador():
    with TemporaryDirectory() as diretorio:
        arquivo = Path(diretorio) / "teste.py"
        arquivo.write_text("print('teste')\n", encoding="utf-8")

        processo_sucesso = subprocess.CompletedProcess(
            args=["analisador_teste"],
            returncode=0,
            stdout="Análise concluída.",
            stderr="",
        )

        
        with patch(
            "services.analysis_service.subprocess.run",
            side_effect=[
                OSError("Falha simulada no Bandit"),
                processo_sucesso,  # Radon CC
                processo_sucesso,  # Radon MI
                processo_sucesso,  # Pylint JSON
                processo_sucesso,  # Pontuação do Pylint
            ],
        ):
            resultados = analisar_arquivo(str(arquivo))


    assert resultados["bandit"]["codigo_retorno"] is None
    assert "Falha simulada no Bandit" in resultados["bandit"]["erros"]

    assert resultados["radon"]["codigo_retorno"] == 0
    assert resultados["pylint"]["codigo_retorno"] == 0

    print(
        "Teste aprovado: a falha do Bandit não impediu "
        "os resultados do Radon e do Pylint."
    )


if __name__ == "__main__":
    testar_arquivo_inexistente()
    testar_extensao_invalida()
    testar_timeout()
    testar_falha_execucao()
    testar_falha_de_um_analisador()