import requests

BASE_URL = "http://127.0.0.1:8000"
API_URL = f"{BASE_URL}/gerar"

# O refinamento faz geração, análise e auditoria numa só chamada.
TIMEOUT_REFINAMENTO = 300


def receber_prompt(prompt):
    try:
        resposta = requests.post(
            API_URL,
            json={"prompt": prompt},
            timeout=120,
        )

        resposta.raise_for_status()

        try:
            return resposta.json()
        except ValueError:
            return {
                "error": "A API retornou uma resposta inválida."
            }

    except requests.exceptions.Timeout:
        return {"error": "A API demorou muito para responder."}

    except requests.exceptions.ConnectionError:
        return {"error": "Não foi possível conectar à API."}

    except requests.exceptions.HTTPError:
        return {
            "error": "A API retornou um erro ao processar o prompt."
        }

    except requests.exceptions.RequestException:
        return {
            "error": "Ocorreu um erro na comunicação com a API."
        }


# ============================================================
# HISTÓRICO
# ============================================================

def _extrair_detalhe(resposta, padrao):
    """Lê a mensagem de erro enviada pela API, quando ela existe."""
    try:
        detalhe = resposta.json().get("detail")
    except (ValueError, AttributeError):
        return padrao

    return detalhe if isinstance(detalhe, str) else padrao


def _chamar_historico(
    metodo,
    caminho,
    parametros=None,
    corpo=None,
    timeout=30,
    erro_padrao="A API retornou um erro ao consultar o histórico.",
    mensagem_timeout="A API demorou muito para responder.",
):
    try:
        resposta = requests.request(
            metodo,
            f"{BASE_URL}{caminho}",
            params=parametros,
            json=corpo,
            timeout=timeout,
        )

        if not resposta.ok:
            return {"error": _extrair_detalhe(resposta, erro_padrao)}

        try:
            return resposta.json()
        except ValueError:
            return {
                "error": "A API retornou uma resposta inválida."
            }

    except requests.exceptions.Timeout:
        return {"error": mensagem_timeout}

    except requests.exceptions.ConnectionError:
        return {"error": "Não foi possível conectar à API."}

    except requests.exceptions.RequestException:
        return {
            "error": "Ocorreu um erro na comunicação com a API."
        }


def listar_projetos_historico():
    """Devolve {"projetos": [...]} ou {"error": "..."}."""
    return _chamar_historico("GET", "/projetos")


def carregar_projeto_historico(projeto_id, numero_versao=None):
    """Devolve o projeto no formato do dashboard ou {"error": "..."}."""
    parametros = (
        {"versao": numero_versao}
        if numero_versao is not None
        else None
    )

    return _chamar_historico(
        "GET",
        f"/projetos/{projeto_id}",
        parametros=parametros
    )


def registrar_decisao_historico(projeto_id, decisao, numero_versao=None):
    """Grava a decisão do usuário. decisao: "aceito", "refinamento" ou None.

    Devolve os dados da decisão gravada ou {"error": "..."}.
    """
    corpo = {"decisao": decisao}

    if numero_versao is not None:
        corpo["versao"] = numero_versao

    return _chamar_historico(
        "PUT",
        f"/projetos/{projeto_id}/decisao",
        corpo=corpo
    )


def refinar_projeto_historico(projeto_id, numero_versao=None, instrucoes=None):
    """Pede uma nova versão do projeto. Devolve a versão ou {"error": "..."}."""
    corpo = {}

    if numero_versao is not None:
        corpo["versao"] = numero_versao

    if isinstance(instrucoes, str) and instrucoes.strip():
        corpo["instrucoes"] = instrucoes

    return _chamar_historico(
        "POST",
        f"/projetos/{projeto_id}/refinar",
        corpo=corpo,
        timeout=TIMEOUT_REFINAMENTO,
        erro_padrao="A API retornou um erro ao refinar o projeto.",
        mensagem_timeout=(
            "O refinamento demorou mais que o esperado e pode ainda estar "
            "em andamento na API. Aguarde alguns minutos e consulte a "
            "lista de projetos anteriores."
        ),
    )