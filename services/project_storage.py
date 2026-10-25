from pathlib import Path, PureWindowsPath
import uuid
import json
from datetime import datetime


PASTA_PROJETOS = Path(__file__).resolve().parent.parent / "projetos_gerados"



def salvar_projeto(projeto: dict, prompt: str) -> Path:
    arquivos = projeto.get("arquivos")

    if not isinstance(arquivos, list) or not arquivos:
        raise ValueError("O projeto não contém uma lista válida de arquivos.")

    pasta_projeto = PASTA_PROJETOS / f"projeto_{uuid.uuid4().hex}"

    arquivos_validados = []
    caminhos_vistos = set()

    for arquivo in arquivos:
        if not isinstance(arquivo, dict):
            raise ValueError("Um arquivo do projeto possui formato inválido.")

        nome = arquivo.get("nome")
        conteudo = arquivo.get("conteudo")

        if not isinstance(nome, str) or not nome.strip():
            raise ValueError("Um arquivo possui nome inválido.")

        if Path(nome).as_posix().casefold() == "registro.json":
            raise ValueError(
                "O nome 'registro.json' é reservado para o registro da geração."
            )

        if not isinstance(conteudo, str):
            raise ValueError(f"O conteúdo do arquivo '{nome}' é inválido.")

        caminho_relativo = Path(nome)
        caminho_windows = PureWindowsPath(nome)

        if (
            caminho_relativo.is_absolute()
            or caminho_windows.is_absolute()
            or ".." in caminho_relativo.parts
            or ".." in caminho_windows.parts
            or nome.strip() in {".", ".."}
        ):
            raise ValueError(f"Caminho de arquivo não permitido: {nome}")

        # Evita caminhos com separadores ou nomes ambíguos.
        partes = caminho_relativo.parts

        if not partes or any(parte in {"", ".", ".."} for parte in partes):
            raise ValueError(f"Caminho de arquivo não permitido: {nome}")

        # Impede nomes duplicados, considerando diferenças entre maiúsculas
        # e minúsculas e separadores de caminho.
        chave_caminho = caminho_relativo.as_posix().casefold()

        if chave_caminho in caminhos_vistos:
            raise ValueError(f"O projeto contém um caminho duplicado: {nome}")

        caminhos_vistos.add(chave_caminho)
        arquivos_validados.append((caminho_relativo, conteudo))

    # Impede conflitos como um arquivo "utils" e outro "utils/main.py".
    caminhos = {caminho.as_posix().casefold() for caminho, _ in arquivos_validados}

    for caminho, _ in arquivos_validados:
        partes = caminho.parts

        for indice in range(1, len(partes)):
            caminho_pai = Path(*partes[:indice]).as_posix().casefold()

            if caminho_pai in caminhos:
                raise ValueError(
                    f"Conflito de estrutura entre arquivos: {caminho_pai} e {caminho}"
                )

    pasta_projeto.mkdir(parents=True, exist_ok=False)

    try:
        for caminho_relativo, conteudo in arquivos_validados:
            destino = pasta_projeto / caminho_relativo
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(conteudo, encoding="utf-8")

        registro = {
            "id": pasta_projeto.name,
            "prompt": prompt,
            "data_hora": datetime.now().astimezone().isoformat(),
            "pasta_projeto": str(pasta_projeto)
        }

        caminho_registro = pasta_projeto / "registro.json"

        caminho_registro.write_text(
            json.dumps(registro, ensure_ascii=False, indent=4),
            encoding="utf-8"
        )

    except OSError:
        import shutil
        shutil.rmtree(pasta_projeto, ignore_errors=True)
        raise

    return pasta_projeto

