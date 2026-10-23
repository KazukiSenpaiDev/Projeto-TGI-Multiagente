from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from services.claude_service import gerar_codigo


app = FastAPI()


class PromptRequest(BaseModel):
    prompt: str


@app.post("/gerar")
def gerar_projeto(dados: PromptRequest):
    try:
        codigo_gerado = gerar_codigo(dados.prompt)

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

    return {
        "message": "Projeto gerado com sucesso!",
        "Prompt_recebido": dados.prompt,
        "codigo_gerado": codigo_gerado
    }
