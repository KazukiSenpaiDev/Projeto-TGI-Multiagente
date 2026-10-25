import json
import anthropic
from pathlib import PurePath, PureWindowsPath
from dotenv import load_dotenv

load_dotenv()

cliente = anthropic.Anthropic()



def gerar_codigo(prompt: str) -> dict:
    try:
        resposta = cliente.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=16384,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Você é uma IA Desenvolvedora de software. "
                        "Gere um projeto com base no pedido do usuário. "
                        "Retorne exclusivamente um JSON válido, sem Markdown "
                        "ou explicações fora do JSON. "
                        "O JSON deve conter uma chave 'arquivos', cujo valor "
                        "seja uma lista de objetos. "
                        "Cada objeto deve conter as chaves 'nome' e 'conteudo'. "
                        "A chave 'nome' deve conter o nome do arquivo. "
                        "A chave 'conteudo' deve conter o código-fonte completo "
                        "desse arquivo, como uma string. "
                        "Não coloque explicações dentro do código. "
                        "Inclua todos os arquivos necessários para a solução."
                        "\n\n"
                        f"Pedido do usuário:\n{prompt}"
                    ),
                }
            ],
        )
        

    except anthropic.AuthenticationError as erro:
        raise RuntimeError(
            "Falha na autenticação com a API do Claude. "
            "Verifique a configuração da chave."
        ) from erro

    except anthropic.RateLimitError as erro:
        raise RuntimeError(
            "Limite de requisições ou créditos da API atingido."
        ) from erro

    except anthropic.APITimeoutError as erro:
        raise RuntimeError(
            "A solicitação à API do Claude excedeu o tempo limite."
        ) from erro

    except anthropic.APIConnectionError as erro:
        raise RuntimeError(
            "Não foi possível conectar à API do Claude."
        ) from erro

    except anthropic.APIStatusError as erro:
        raise RuntimeError(
            "A API do Claude retornou um erro ao processar a solicitação."
        ) from erro

    if resposta.stop_reason == "max_tokens":
        raise ValueError(
        "A resposta do Claude atingiu o limite de tokens "
        "e pode estar incompleta. Tente um projeto menor."
    )

    textos = [
        bloco.text
        for bloco in resposta.content
        if bloco.type == "text"
    ]

    conteudo = "\n".join(textos)

    try:
        projeto = json.loads(conteudo)

    except json.JSONDecodeError as erro:
        raise ValueError(
            "O Claude retornou uma resposta que não é um JSON válido."
        ) from erro

    if not isinstance(projeto, dict):
        raise ValueError("A resposta deve ser um objeto JSON.")

    arquivos = projeto.get("arquivos")

    if not isinstance(arquivos, list) or not arquivos:
        raise ValueError(
            "A resposta deve conter uma lista de arquivos."
        )

    for arquivo in arquivos:
        if not isinstance(arquivo, dict):
            raise ValueError("Cada arquivo deve ser um objeto JSON.")

        nome = arquivo.get("nome")
        codigo = arquivo.get("conteudo")

        if not isinstance(nome, str) or not nome.strip():
            raise ValueError("Cada arquivo deve possuir um nome válido.")

        caminho = PurePath(nome)
        caminho_windows = PureWindowsPath(nome)

        if (
            caminho.is_absolute()
            or caminho_windows.is_absolute()
            or ".." in caminho.parts
            or ".." in caminho_windows.parts
        ):
            raise ValueError(
                f"O nome do arquivo '{nome}' não é permitido."
            )

        if not isinstance(codigo, str) or not codigo.strip():
            raise ValueError(
                f"O arquivo '{nome}' não possui código válido."
            )

    return projeto

