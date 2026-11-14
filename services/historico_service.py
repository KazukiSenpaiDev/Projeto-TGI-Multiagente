import json
import re
from datetime import datetime
from pathlib import Path

from services.project_storage import (
    FORMATO_VERSAO,
    PASTA_PROJETOS,
    PASTA_VERSOES,
    _gravar_json,
    obter_pasta_arquivos,
)


# Aceita apenas o formato gerado pela aplicação. Isso impede que um
# identificador como "../../algo" seja usado para ler fora da pasta.
PADRAO_ID = re.compile(r"^projeto_[0-9a-f]{32}$")

TAMANHO_RESUMO_PROMPT = 120

DECISOES_VALIDAS = ("aceito", "refinamento")


class ProjetoInvalidoError(ValueError):
    """O projeto existe no histórico, mas não pode ser usado."""


def _ler_json(caminho: Path) -> dict:
    """Lê um arquivo JSON que deve conter um objeto."""
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))

    except FileNotFoundError as erro:
        raise ProjetoInvalidoError(
            f"O arquivo {caminho.name} não foi encontrado."
        ) from erro

    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as erro:
        raise ProjetoInvalidoError(
            f"Não foi possível ler o arquivo {caminho.name}."
        ) from erro

    if not isinstance(dados, dict):
        raise ProjetoInvalidoError(
            f"O arquivo {caminho.name} tem um formato inesperado."
        )

    return dados


def _verificar_formato(registro: dict) -> str:
    """Classifica o registro como 'ok', 'antigo' ou 'desconhecido'."""
    if "formato_versao" not in registro:
        return "antigo"

    formato = registro["formato_versao"]

    if (
        not isinstance(formato, int)
        or isinstance(formato, bool)
        or formato < 1
        or formato > FORMATO_VERSAO
    ):
        return "desconhecido"

    return "ok"


def _obter_versoes(registro: dict) -> list:
    """Retorna as versões do registro que possuem um número válido."""
    versoes = registro.get("versoes")

    if not isinstance(versoes, list):
        return []

    return [
        versao
        for versao in versoes
        if (
            isinstance(versao, dict)
            and isinstance(versao.get("numero"), int)
            and not isinstance(versao.get("numero"), bool)
        )
    ]


def _versao_padrao(versoes: list) -> dict:
    """Versão exibida por padrão: a completa mais recente.

    Se nenhuma estiver completa, a mais recente. Assim, um refinamento
    em andamento (ou que falhou) não esconde a última versão utilizável.
    """
    completas = [
        versao
        for versao in versoes
        if versao.get("estado") == "completa"
    ]

    return max(completas or versoes, key=lambda versao: versao["numero"])


def _resumir_versoes(versoes: list) -> list:
    """Resumo de cada versão, em ordem crescente, para o seletor de versões."""
    resumo = []

    for versao in sorted(versoes, key=lambda item: item["numero"]):

        origem = versao.get("origem")
        status = versao.get("status_auditoria")
        data_hora = versao.get("data_hora")

        resumo.append({
            "numero": versao["numero"],
            "estado": (
                "completa"
                if versao.get("estado") == "completa"
                else "incompleta"
            ),
            "status_auditoria": status if isinstance(status, str) else None,
            "origem": (
                origem
                if isinstance(origem, int) and not isinstance(origem, bool)
                else None
            ),
            "data_hora": data_hora if isinstance(data_hora, str) else None,
        })

    return resumo

def _resumir_projeto(pasta: Path) -> dict:
    """Cria o resumo de um projeto para a lista, sem nunca levantar erro."""
    resumo = {
        "id": pasta.name,
        "prompt_resumo": "",
        "data_hora": None,
        "estado": "invalido",
        "status_auditoria": None,
        "numero_versao": None,
        "total_versoes": 0,
        "aviso": None,
    }

    try:
        registro = _ler_json(pasta / "registro.json")

    except ProjetoInvalidoError as erro:
        resumo["aviso"] = str(erro)
        return resumo

    prompt = registro.get("prompt")

    if isinstance(prompt, str):
        resumo["prompt_resumo"] = (
            prompt[:TAMANHO_RESUMO_PROMPT] + "…"
            if len(prompt) > TAMANHO_RESUMO_PROMPT
            else prompt
        )

    data_hora = registro.get("data_hora")

    if isinstance(data_hora, str):
        resumo["data_hora"] = data_hora

    formato = _verificar_formato(registro)

    if formato == "antigo":
        resumo["estado"] = "formato_antigo"
        resumo["aviso"] = (
            "Projeto criado antes do histórico. "
            "Apenas o prompt está disponível."
        )
        return resumo

    if formato == "desconhecido":
        resumo["estado"] = "formato_desconhecido"
        resumo["aviso"] = (
            "Este projeto usa um formato de registro que esta versão "
            "da aplicação não reconhece."
        )
        return resumo

    versoes = _obter_versoes(registro)
    resumo["total_versoes"] = len(versoes)

    if not versoes:
        resumo["aviso"] = "O registro do projeto não possui versões."
        return resumo

    padrao = _versao_padrao(versoes)
    resumo["numero_versao"] = padrao["numero"]

    if padrao.get("estado") == "completa":
        resumo["estado"] = "completa"
        resumo["status_auditoria"] = padrao.get("status_auditoria")
    else:
        resumo["estado"] = "incompleta"
        resumo["aviso"] = (
            "A análise ou a auditoria desta versão não foi concluída."
        )

    return resumo


def listar_projetos() -> list:
    """Lista os projetos salvos, do mais recente para o mais antigo."""
    if not PASTA_PROJETOS.is_dir():
        return []

    projetos = [
        _resumir_projeto(pasta)
        for pasta in PASTA_PROJETOS.iterdir()
        if pasta.is_dir() and PADRAO_ID.match(pasta.name)
    ]

    projetos.sort(key=lambda projeto: projeto["data_hora"] or "", reverse=True)

    return projetos


def _ler_arquivos(pasta_arquivos: Path) -> list:
    """Lê o código gerado de uma versão."""
    if not pasta_arquivos.is_dir():
        raise ProjetoInvalidoError(
            "A pasta de arquivos desta versão não foi encontrada."
        )

    arquivos = []

    try:
        for caminho in sorted(pasta_arquivos.rglob("*")):
            if caminho.is_symlink() or not caminho.is_file():
                continue

            arquivos.append({
                "nome": caminho.relative_to(pasta_arquivos).as_posix(),
                "conteudo": caminho.read_text(
                    encoding="utf-8",
                    errors="replace"
                ),
            })

    except OSError as erro:
        raise ProjetoInvalidoError(
            "Não foi possível ler os arquivos desta versão."
        ) from erro

    return arquivos


def _abrir_registro(projeto_id: str):
    """Valida o identificador e lê o registro de um projeto utilizável.

    Levanta:
      ValueError            - identificador inválido.
      FileNotFoundError     - projeto inexistente.
      ProjetoInvalidoError  - projeto que não pode ser usado.

    Retorna (pasta, registro, versoes).
    """
    if not isinstance(projeto_id, str) or not PADRAO_ID.match(projeto_id):
        raise ValueError("Identificador de projeto inválido.")

    pasta = PASTA_PROJETOS / projeto_id

    if not pasta.is_dir():
        raise FileNotFoundError("Projeto não encontrado.")

    registro = _ler_json(pasta / "registro.json")

    formato = _verificar_formato(registro)

    if formato == "antigo":
        raise ProjetoInvalidoError(
            "Projeto criado antes do histórico: não há resultados salvos."
        )

    if formato == "desconhecido":
        raise ProjetoInvalidoError(
            "Este projeto usa um formato de registro não reconhecido."
        )

    versoes = _obter_versoes(registro)

    if not versoes:
        raise ProjetoInvalidoError(
            "O registro do projeto não possui versões."
        )

    return pasta, registro, versoes


def _selecionar_versao(versoes: list, numero_versao):
    """Escolhe a versão pedida ou, se nenhuma for pedida, a padrão."""
    if numero_versao is None:
        return _versao_padrao(versoes)

    entrada = next(
        (
            versao
            for versao in versoes
            if versao["numero"] == numero_versao
        ),
        None
    )

    if entrada is None:
        raise ProjetoInvalidoError(
            f"A versão {numero_versao} não existe neste projeto."
        )

    return entrada


def carregar_projeto(projeto_id: str, numero_versao: int = None) -> dict:
    """Carrega uma versão de um projeto no formato usado pelo dashboard.

    Sem número de versão, carrega a versão completa mais recente.

    Levanta:
      ValueError            - identificador inválido.
      FileNotFoundError     - projeto inexistente.
      ProjetoInvalidoError  - projeto ou versão que não pode ser carregado.
    """
    pasta, registro, versoes = _abrir_registro(projeto_id)

    entrada = _selecionar_versao(versoes, numero_versao)

    numero = entrada["numero"]

    arquivos = _ler_arquivos(obter_pasta_arquivos(pasta, numero))

    prompt = registro.get("prompt")

    versao_origem = entrada.get("origem")
    instrucoes = entrada.get("instrucoes")

    resposta = {
        "message": "Projeto carregado do histórico.",
        "Prompt_recebido": prompt if isinstance(prompt, str) else "",
        "codigo_gerado": {"arquivos": arquivos},
        "resultados_analise": None,
        "diagnostico": None,
        "decisao": None,
        "decisao_data_hora": None,
        "projeto_id": projeto_id,
        "numero_versao": numero,
        "versao_origem": (
            versao_origem
            if isinstance(versao_origem, int)
            and not isinstance(versao_origem, bool)
            else None
        ),
        "instrucoes": instrucoes if isinstance(instrucoes, str) else None,
        "versoes": _resumir_versoes(versoes),
        "estado": "incompleta",
        "aviso": None,
    }

    if entrada.get("estado") != "completa":
        resposta["aviso"] = (
            "A análise ou a auditoria desta versão não foi concluída."
        )
        return resposta

    try:
        resultado = _ler_json(
            pasta / PASTA_VERSOES / f"v{numero}" / "resultado.json"
        )

    except ProjetoInvalidoError as erro:
        resposta["aviso"] = f"O resultado desta versão não pôde ser lido. {erro}"
        return resposta

    resultados_analise = resultado.get("resultados_analise")
    diagnostico = resultado.get("diagnostico")

    if not isinstance(resultados_analise, dict) or not isinstance(
        diagnostico, dict
    ):
        resposta["aviso"] = (
            "O resultado desta versão está incompleto ou em formato inesperado."
        )
        return resposta

    resposta["resultados_analise"] = resultados_analise
    resposta["diagnostico"] = diagnostico
    resposta["estado"] = "completa"

    decisao_salva = resultado.get("decisao")

    if (
        isinstance(decisao_salva, dict)
        and decisao_salva.get("valor") in DECISOES_VALIDAS
    ):
        resposta["decisao"] = decisao_salva["valor"]

        data_hora = decisao_salva.get("data_hora")

        if isinstance(data_hora, str):
            resposta["decisao_data_hora"] = data_hora

    return resposta


def registrar_decisao(
    projeto_id: str,
    decisao,
    numero_versao: int = None,
) -> dict:
    """Grava a decisão do usuário no resultado de uma versão.

    decisao: "aceito", "refinamento" ou None (remove a decisão).

    Levanta:
      ValueError            - identificador ou decisão inválidos.
      FileNotFoundError     - projeto inexistente.
      ProjetoInvalidoError  - versão sem resultado completo ou ilegível.
      OSError               - falha ao gravar o arquivo.
    """
    if decisao is not None and decisao not in DECISOES_VALIDAS:
        raise ValueError("Decisão inválida.")

    pasta, _, versoes = _abrir_registro(projeto_id)

    entrada = _selecionar_versao(versoes, numero_versao)

    numero = entrada["numero"]

    if entrada.get("estado") != "completa":
        raise ProjetoInvalidoError(
            "Esta versão não possui resultado completo: "
            "a decisão não pode ser registrada."
        )

    caminho_resultado = pasta / PASTA_VERSOES / f"v{numero}" / "resultado.json"

    # Se o arquivo estiver corrompido, o erro acontece aqui,
    # antes de qualquer gravação, e o arquivo não é sobrescrito.
    resultado = _ler_json(caminho_resultado)

    data_hora = datetime.now().astimezone().isoformat()

    resultado["decisao"] = (
        None
        if decisao is None
        else {"valor": decisao, "data_hora": data_hora}
    )

    _gravar_json(caminho_resultado, resultado)

    return {
        "projeto_id": projeto_id,
        "numero_versao": numero,
        "decisao": decisao,
        "data_hora": None if decisao is None else data_hora,
    }