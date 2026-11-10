from pathlib import Path, PureWindowsPath
import copy
import json
import shutil
import uuid
from datetime import datetime


PASTA_PROJETOS = Path(__file__).resolve().parent.parent / "projetos_gerados"

FORMATO_VERSAO = 1
PASTA_VERSOES = "versoes"


def obter_pasta_arquivos(pasta_projeto: Path, numero_versao: int = 1) -> Path:
    """Retorna a pasta onde ficam os arquivos gerados de uma versão."""
    return (
        Path(pasta_projeto)
        / PASTA_VERSOES
        / f"v{numero_versao}"
        / "arquivos"
    )


def _gravar_json(caminho: Path, dados: dict) -> None:
    """Grava um JSON de forma segura.

    Escreve primeiro em um arquivo temporário e só depois o renomeia,
    para que uma falha no meio não deixe o arquivo final corrompido.
    """
    temporario = caminho.with_name(caminho.name + ".tmp")

    temporario.write_text(
        json.dumps(dados, ensure_ascii=False, indent=4),
        encoding="utf-8"
    )

    temporario.replace(caminho)


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
        pasta_arquivos = obter_pasta_arquivos(pasta_projeto, 1)
        pasta_arquivos.mkdir(parents=True, exist_ok=False)

        for caminho_relativo, conteudo in arquivos_validados:
            destino = pasta_arquivos / caminho_relativo
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(conteudo, encoding="utf-8")

        data_hora = datetime.now().astimezone().isoformat()

        registro = {
            "formato_versao": FORMATO_VERSAO,
            "id": pasta_projeto.name,
            "prompt": prompt,
            "data_hora": data_hora,
            "versoes": [
                {
                    "numero": 1,
                    "data_hora": data_hora,
                    "estado": "arquivos_salvos",
                    "pasta_arquivos": pasta_arquivos
                    .relative_to(pasta_projeto)
                    .as_posix()
                }
            ]
        }

        _gravar_json(pasta_projeto / "registro.json", registro)

    except OSError:
        shutil.rmtree(pasta_projeto, ignore_errors=True)
        raise

    return pasta_projeto


# ============================================================
# RESULTADO DA VERSÃO (ferramentas + diagnóstico)
# ============================================================

def _montar_resultados_para_historico(resultados_analise: dict) -> dict:
    """Cria uma cópia limpa dos resultados para o histórico.

    - Remove "dados_originais" (saídas brutas, com caminhos locais).
    - Troca o caminho de cada achado pelo nome relativo do arquivo.
    O objeto recebido não é alterado.
    """
    resultados_limpos = {}

    for nome_arquivo, resultado in resultados_analise.items():
        if not isinstance(resultado, dict):
            resultados_limpos[nome_arquivo] = resultado
            continue

        copia = copy.deepcopy(resultado)
        copia.pop("dados_originais", None)

        achados = copia.get("achados")

        if isinstance(achados, list):
            for achado in achados:
                if not isinstance(achado, dict):
                    continue

                localizacao = achado.get("localizacao")

                if isinstance(localizacao, dict) and "arquivo" in localizacao:
                    localizacao["arquivo"] = nome_arquivo

        resultados_limpos[nome_arquivo] = copia

    return resultados_limpos


def _remover_caminhos_locais(valor):
    """Rede de segurança: troca a raiz do projeto, onde ainda aparecer."""
    raiz = str(PASTA_PROJETOS.parent)
    variantes = {raiz, raiz.replace("\\", "/")}

    if isinstance(valor, str):
        for variante in variantes:
            valor = valor.replace(variante, "<projeto>")
        return valor

    if isinstance(valor, list):
        return [_remover_caminhos_locais(item) for item in valor]

    if isinstance(valor, dict):
        return {
            chave: _remover_caminhos_locais(item)
            for chave, item in valor.items()
        }

    return valor


def gravar_resultado(
    pasta_projeto: Path,
    resultados_analise: dict,
    diagnostico: dict,
    numero_versao: int = 1,
) -> Path:
    """Grava o resultado de uma versão e marca a versão como completa."""
    pasta_projeto = Path(pasta_projeto)
    pasta_versao = pasta_projeto / PASTA_VERSOES / f"v{numero_versao}"
    caminho_registro = pasta_projeto / "registro.json"

    if not pasta_versao.is_dir():
        raise FileNotFoundError(
            f"Pasta da versão {numero_versao} não encontrada."
        )

    # Lê e valida o registro antes de gravar qualquer coisa,
    # para não deixar o histórico em um estado inconsistente.
    registro = json.loads(caminho_registro.read_text(encoding="utf-8"))

    entrada_versao = next(
        (
            versao
            for versao in registro.get("versoes", [])
            if isinstance(versao, dict) and versao.get("numero") == numero_versao
        ),
        None
    )

    if entrada_versao is None:
        raise ValueError(
            f"A versão {numero_versao} não existe no registro do projeto."
        )

    resultado = _remover_caminhos_locais({
        "formato_versao": FORMATO_VERSAO,
        "numero_versao": numero_versao,
        "data_hora": datetime.now().astimezone().isoformat(),
        "resultados_analise": _montar_resultados_para_historico(
            resultados_analise
        ),
        "diagnostico": diagnostico,
        "decisao": None,
    })

    caminho_resultado = pasta_versao / "resultado.json"

    _gravar_json(caminho_resultado, resultado)

    entrada_versao["estado"] = "completa"
    entrada_versao["status_auditoria"] = (
        diagnostico.get("status") if isinstance(diagnostico, dict) else None
    )
    entrada_versao["arquivo_resultado"] = (
        caminho_resultado.relative_to(pasta_projeto).as_posix()
    )

    _gravar_json(caminho_registro, registro)

    return caminho_resultado