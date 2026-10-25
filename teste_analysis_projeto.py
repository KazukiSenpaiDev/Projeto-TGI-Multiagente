from pathlib import Path
from tempfile import TemporaryDirectory

from services.analysis_service import analisar_projeto


with TemporaryDirectory() as diretorio:
    pasta = Path(diretorio)

    (pasta / "main.py").write_text(
        'print("Olá")\n',
        encoding="utf-8",
    )

    (pasta / "utils").mkdir()

    (pasta / "utils" / "calculo.py").write_text(
        "def somar(a, b):\n    return a + b\n",
        encoding="utf-8",
    )

    (pasta / "README.md").write_text(
        "# Projeto de teste\n",
        encoding="utf-8",
    )

    resultados = analisar_projeto(str(pasta))

    assert "main.py" in resultados
    assert "utils/calculo.py" in resultados
    assert "README.md" not in resultados

    for arquivo, analises in resultados.items():
        assert set(analises.keys()) == {
            "bandit",
            "radon",
            "pylint",
        }

    print("Teste aprovado: arquivos Python analisados.")
    print("Arquivos encontrados:", list(resultados.keys()))
