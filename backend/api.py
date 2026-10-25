from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from services.claude_service import gerar_codigo
from services.project_storage import salvar_projeto
from services.analysis_service import analisar_projeto
from services.normalization_service import normalizar_resultados_projeto

app = FastAPI()


class PromptRequest(BaseModel):
    prompt: str = Field(min_length=1)



@app.post("/gerar")
def gerar_projeto(dados: PromptRequest):
    try:
        codigo_gerado = gerar_codigo(dados.prompt)

        pasta_projeto = salvar_projeto(codigo_gerado, dados.prompt)

        resultados_brutos = analisar_projeto(str(pasta_projeto))

        resultados_analise = normalizar_resultados_projeto(
            resultados_brutos
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

    return {
        "message": "Projeto gerado e salvo com sucesso!",
        "Prompt_recebido": dados.prompt,
        "codigo_gerado": codigo_gerado,
        "pasta_projeto": str(pasta_projeto),
        "resultados_analise": resultados_analise
    }

