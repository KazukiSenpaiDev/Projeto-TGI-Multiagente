
from pathlib import Path
from tempfile import TemporaryDirectory

from services.ast_service import analisar_arquivo_ast


with TemporaryDirectory() as pasta:
    diretorio = Path(pasta)

    # Teste 1: arquivo Python válido.
    arquivo = diretorio / "exemplo.py"

    arquivo.write_text(
        """
class Calculadora:
    def somar(self, a, b):
        return a + b


async def buscar_dados(url):
    return url
""",
        encoding="utf-8",
    )

    resultado = analisar_arquivo_ast(str(arquivo))

    assert resultado["valido"] is True
    assert resultado["erro"] is None

    nomes_funcoes = {
        funcao["nome"] for funcao in resultado["funcoes"]
    }
    nomes_classes = {
        classe["nome"] for classe in resultado["classes"]
    }

    assert nomes_funcoes == {"somar", "buscar_dados"}
    assert nomes_classes == {"Calculadora"}

    print("Teste aprovado: arquivo Python válido analisado.")

    # Teste 2: arquivo inexistente.
    try:
        analisar_arquivo_ast(str(diretorio / "inexistente.py"))
        raise AssertionError("O arquivo inexistente deveria ser rejeitado.")
    except FileNotFoundError:
        print("Teste aprovado: arquivo inexistente rejeitado.")

    # Teste 3: extensão inválida.
    arquivo_txt = diretorio / "exemplo.txt"
    arquivo_txt.write_text("texto", encoding="utf-8")

    try:
        analisar_arquivo_ast(str(arquivo_txt))
        raise AssertionError("A extensão inválida deveria ser rejeitada.")
    except ValueError:
        print("Teste aprovado: extensão inválida rejeitada.")

    # Teste 4: erro de sintaxe.
    arquivo_invalido = diretorio / "invalido.py"
    arquivo_invalido.write_text(
        "def somar(a, b)\n    return a + b\n",
        encoding="utf-8",
    )

    resultado_invalido = analisar_arquivo_ast(
        str(arquivo_invalido)
    )

    assert resultado_invalido["valido"] is False
    assert resultado_invalido["erro"] is not None
    assert resultado_invalido["funcoes"] == []
    assert resultado_invalido["classes"] == []

    print("Teste aprovado: erro de sintaxe identificado.")
    print("Detalhe:", resultado_invalido["erro"])
