import ast
from pathlib import Path


def analisar_arquivo_ast(caminho_arquivo: str) -> dict:
    caminho = Path(caminho_arquivo)

    if not caminho.is_file():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )

    if caminho.suffix.lower() != ".py":
        raise ValueError(
            "A análise só aceita arquivos Python (.py)."
        )

    try:
        codigo = caminho.read_text(encoding="utf-8")
        arvore = ast.parse(codigo, filename=str(caminho))

    except SyntaxError as erro:
        return {
            "valido": False,
            "erro": (
                f"Erro de sintaxe na linha {erro.lineno}: "
                f"{erro.msg}"
            ),
            "funcoes": [],
            "classes": [],
        }

    funcoes = []
    classes = []

    for elemento in ast.walk(arvore):
        if isinstance(elemento, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funcoes.append({
                "nome": elemento.name,
                "linha": elemento.lineno,
                "parametros": [
                    argumento.arg
                    for argumento in elemento.args.args
                ],
            })

        elif isinstance(elemento, ast.ClassDef):
            classes.append({
                "nome": elemento.name,
                "linha": elemento.lineno,
            })

    return {
        "valido": True,
        "erro": None,
        "funcoes": funcoes,
        "classes": classes,
    }
