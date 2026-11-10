from dotenv import load_dotenv

load_dotenv()

import logging
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from services.claude_service import gerar_codigo
from services.project_storage import (
    salvar_projeto,
    obter_pasta_arquivos,
    gravar_resultado
)
from services.analysis_service import analisar_projeto
from services.normalization_service import normalizar_resultados_projeto
from services.openai_service import auditar_projeto
from services.historico_service import (
    ProjetoInvalidoError,
    carregar_projeto,
    listar_projetos,
    registrar_decisao
)

app = FastAPI()

logger = logging.getLogger(__name__)


class PromptRequest(BaseModel):
    prompt: str = Field(min_length=1)


class DecisaoRequest(BaseModel):
    # Sem valor padrão: o campo é obrigatório, e "null" remove a decisão.
    decisao: Literal["aceito", "refinamento"] | None
    versao: int | None = None



@app.post("/gerar")
def gerar_projeto(dados: PromptRequest):
    try:
        codigo_gerado = gerar_codigo(dados.prompt)

        pasta_projeto = salvar_projeto(codigo_gerado, dados.prompt)

        resultados_brutos = analisar_projeto(
            str(obter_pasta_arquivos(pasta_projeto))
        )

        resultados_analise = normalizar_resultados_projeto(
            resultados_brutos
        )

        diagnostico = auditar_projeto(
            codigo_gerado,
            resultados_analise
        )

    except RuntimeError as erro:
        raise HTTPException(
            status_code=502,
            detail=str(erro)
        ) from erro

    except ValueError as erro:
        raise HTTPException(
            status_code=502,
            detail=str(erro)
        ) from erro

    except OSError as erro:
        raise HTTPException(
            status_code=500,
            detail="Não foi possível salvar os arquivos do projeto."
        ) from erro

    # A auditoria já foi concluída (e paga). Uma falha ao gravar o
    # histórico não deve descartar o resultado: ela é registrada no
    # terminal da API e sinalizada na resposta.
    try:
        gravar_resultado(pasta_projeto, resultados_analise, diagnostico)
        historico_salvo = True

    except (OSError, TypeError, ValueError):
        logger.exception("Não foi possível gravar o resultado no histórico.")
        historico_salvo = False

    return {
        "message": "Projeto gerado e salvo com sucesso!",
        "Prompt_recebido": dados.prompt,
        "codigo_gerado": codigo_gerado,
        "projeto_id": pasta_projeto.name,
        "numero_versao": 1,
        "resultados_analise": resultados_analise,
        "diagnostico": diagnostico,
        "historico_salvo": historico_salvo
    }


@app.get("/projetos")
def listar_historico():
    return {"projetos": listar_projetos()}


@app.get("/projetos/{projeto_id}")
def obter_projeto_historico(projeto_id: str, versao: int | None = None):
    try:
        return carregar_projeto(projeto_id, versao)

    except FileNotFoundError as erro:
        raise HTTPException(
            status_code=404,
            detail="Projeto não encontrado."
        ) from erro

    # ProjetoInvalidoError herda de ValueError, por isso vem primeiro.
    except ProjetoInvalidoError as erro:
        raise HTTPException(
            status_code=422,
            detail=str(erro)
        ) from erro

    except ValueError as erro:
        raise HTTPException(
            status_code=400,
            detail="Identificador de projeto inválido."
        ) from erro

    except OSError as erro:
        raise HTTPException(
            status_code=500,
            detail="Não foi possível ler o histórico."
        ) from erro


@app.put("/projetos/{projeto_id}/decisao")
def registrar_decisao_projeto(projeto_id: str, dados: DecisaoRequest):
    try:
        return registrar_decisao(projeto_id, dados.decisao, dados.versao)

    except FileNotFoundError as erro:
        raise HTTPException(
            status_code=404,
            detail="Projeto não encontrado."
        ) from erro

    # ProjetoInvalidoError herda de ValueError, por isso vem primeiro.
    except ProjetoInvalidoError as erro:
        raise HTTPException(
            status_code=422,
            detail=str(erro)
        ) from erro

    except ValueError as erro:
        raise HTTPException(
            status_code=400,
            detail=str(erro)
        ) from erro

    except OSError as erro:
        raise HTTPException(
            status_code=500,
            detail="Não foi possível gravar a decisão."
        ) from erro