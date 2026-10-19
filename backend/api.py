from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class promptRequest(BaseModel):
    prompt: str

@app.post("/gerar")
def gerar_projeto(dados: promptRequest):
    
    return {
        "message": "Prompt enviado com sucesso!",
        "Prompt_recebido": dados.prompt
    }   