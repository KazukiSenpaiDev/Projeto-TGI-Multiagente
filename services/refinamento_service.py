import logging
import threading
from contextlib import contextmanager

from services.analysis_service import analisar_projeto
from services.claude_service import refinar_codigo
from services.historico_service import (
    PADRAO_ID,
    ProjetoInvalidoError,
    carregar_projeto,
)
from services.normalization_service import normalizar_resultados_projeto
from services.openai_service import auditar_projeto
from services.project_storage import (
    PASTA_PROJETOS,
    _montar_resultados_para_historico,
    _remover_caminhos_locais,
    gravar_resultado,
    obter_pasta_arquivos,
    salvar_nova_versao,
)


logger = logging.getLogger(__name__)


class RefinamentoEmAndamentoError(Exception):
    """Já existe um refinamento em andamento para este projeto."""


# Projetos com refinamento em andamento. Vale apenas para este processo
# da API: reiniciar a API libera todos os bloqueios.
_trava = threading.Lock()
_em_andamento = set()


@contextmanager
def _reservar_projeto(projeto_id: str):
    """Impede dois refinamentos simultâneos do mesmo projeto."""
    with _trava:
        if projeto_id in _em_andamento:
            raise RefinamentoEmAndamentoError(
                "Já existe um refinamento em andamento para este projeto. "
                "Aguarde a conclusão antes de solicitar outro."
            )

        _em_andamento.add(projeto_id)

    try:
        yield

    finally:
        with _trava:
            _em_andamento.discard(projeto_id)


def _resposta_sem_historico(
    origem: dict,
    novo_projeto: dict,
    numero: int,
    numero_origem: int,
    instrucoes,
    resultados: dict,
    diagnostico: dict,
) -> dict:
    """Resposta usada quando o resultado não pôde ser gravado no histórico."""
    instrucoes_limpas = (
        instrucoes.strip()
        if isinstance(instrucoes, str) and instrucoes.strip()
        else None
    )

    return {
        "message": (
            "Nova versão gerada e auditada, mas o resultado "
            "não foi gravado no histórico."
        ),
        "Prompt_recebido": origem["Prompt_recebido"],
        "codigo_gerado": novo_projeto,
        "resultados_analise": _remover_caminhos_locais(
            _montar_resultados_para_historico(resultados)
        ),
        "diagnostico": diagnostico,
        "decisao": None,
        "decisao_data_hora": None,
        "projeto_id": origem["projeto_id"],
        "numero_versao": numero,
        "versao_origem": numero_origem,
        "instrucoes": instrucoes_limpas,
        "estado": "completa",
        "aviso": (
            "O resultado desta versão não pôde ser gravado no histórico. "
            "Os arquivos foram salvos, mas esta tela não poderá ser reaberta."
        ),
        "historico_salvo": False,
    }


def _executar_refinamento(projeto_id, numero_versao, instrucoes) -> dict:

    origem = carregar_projeto(projeto_id, numero_versao)

    if origem.get("estado") != "completa" or not isinstance(
        origem.get("diagnostico"), dict
    ):
        raise ProjetoInvalidoError(
            "A versão escolhida não possui resultado completo: "
            "não é possível refiná-la."
        )

    numero_origem = origem["numero_versao"]
    pasta = PASTA_PROJETOS / projeto_id

    try:
        novo_projeto = refinar_codigo(
            origem["Prompt_recebido"],
            origem["codigo_gerado"]["arquivos"],
            origem["diagnostico"],
            instrucoes,
        )

    except ValueError as erro:
        raise RuntimeError(str(erro)) from erro

    try:
        numero = salvar_nova_versao(
            pasta,
            novo_projeto,
            numero_origem,
            instrucoes,
        )

    except ValueError as erro:
        raise RuntimeError(
            f"O Claude retornou arquivos que não puderam ser salvos: {erro}"
        ) from erro

    # A partir daqui a versão já existe no disco. Se algo falhar, ela
    # permanece como incompleta e a versão anterior continua utilizável.
    try:
        resultados = normalizar_resultados_projeto(
            analisar_projeto(str(obter_pasta_arquivos(pasta, numero)))
        )

        diagnostico = auditar_projeto(novo_projeto, resultados)

    except (RuntimeError, ValueError) as erro:
        logger.exception("Falha na análise ou na auditoria do refinamento.")

        raise RuntimeError(
            f"A versão {numero} foi gerada e salva, mas a análise ou a "
            f"auditoria não foi concluída: {erro}"
        ) from erro

    except OSError as erro:
        logger.exception("Falha na análise ou na auditoria do refinamento.")

        raise RuntimeError(
            f"A versão {numero} foi gerada e salva, mas a análise ou a "
            "auditoria não foi concluída."
        ) from erro

    try:
        gravar_resultado(pasta, resultados, diagnostico, numero)

        resposta = carregar_projeto(projeto_id, numero)

    except (OSError, TypeError, ValueError):
        logger.exception("Não foi possível gravar o resultado do refinamento.")

        return _resposta_sem_historico(
            origem,
            novo_projeto,
            numero,
            numero_origem,
            instrucoes,
            resultados,
            diagnostico,
        )

    resposta["message"] = "Nova versão gerada e salva com sucesso!"

    return resposta


def refinar_projeto(
    projeto_id: str,
    numero_versao: int = None,
    instrucoes: str = None,
) -> dict:
    """Gera, analisa e audita uma nova versão de um projeto existente.

    Levanta:
      ValueError                   - identificador inválido.
      FileNotFoundError            - projeto inexistente.
      ProjetoInvalidoError         - versão inexistente ou sem resultado completo.
      RefinamentoEmAndamentoError  - outro refinamento do projeto em andamento.
      RuntimeError                 - falha do Claude, da análise ou da auditoria.
      OSError                      - falha ao gravar a nova versão.
    """
    if not isinstance(projeto_id, str) or not PADRAO_ID.match(projeto_id):
        raise ValueError("Identificador de projeto inválido.")

    with _reservar_projeto(projeto_id):
        return _executar_refinamento(projeto_id, numero_versao, instrucoes)