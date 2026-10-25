
import ast

codigo = """
def somar(a, b):
    resultado = a + b
    return resultado
"""

arvore = ast.parse(codigo)

for elemento in ast.walk(arvore):
    if isinstance(elemento, ast.FunctionDef):
        print("Função encontrada:", elemento.name)
        print("Parâmetros:", [
            argumento.arg
            for argumento in elemento.args.args
        ])
