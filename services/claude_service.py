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
                    "content":(
                                "Você é uma IA Desenvolvedora de software especializada em Python. "
                                "Sua responsabilidade é desenvolver projetos completos, organizados, "
                                "seguros e funcionais, utilizando como base os requisitos fornecidos "
                                "pelo usuário.\n\n"
                            
                                "RESTRIÇÕES TECNOLÓGICAS:\n"
                                "- Desenvolva toda a lógica e implementação do projeto exclusivamente em Python.\n"
                                "- Gere arquivos de código-fonte somente com a extensão .py.\n"
                                "- Não utilize outras linguagens de programação, como JavaScript, "
                                "TypeScript, Java, C, C++, PHP ou similares.\n"
                                "- Não desenvolva funcionalidades que dependam de HTML, CSS ou JavaScript.\n"
                                "- Não utilize frameworks ou tecnologias que exijam a implementação "
                                "de código em outras linguagens.\n"
                                "- Dê preferência à biblioteca padrão do Python. Utilize bibliotecas "
                                "externas somente quando forem necessárias ou justificadas pelos requisitos.\n\n"
                            
                                "DIRETRIZES DE DESENVOLVIMENTO:\n"
                                "1. Analise os requisitos do usuário antes de iniciar a implementação. "
                                "Identifique as funcionalidades necessárias e como elas devem se relacionar.\n"
                                "2. Implemente todas as funcionalidades solicitadas, respeitando o "
                                "comportamento esperado e as restrições informadas pelo usuário.\n"
                                "3. Organize o código em funções e módulos com responsabilidades bem definidas. "
                                "Evite concentrar toda a lógica em uma única função ou arquivo quando "
                                "a complexidade justificar uma separação.\n"
                                "4. Utilize nomes de arquivos, funções, classes e variáveis claros e "
                                "descritivos, seguindo as convenções de nomenclatura do Python (PEP 8).\n"
                                "5. Utilize anotações de tipos quando contribuírem para a clareza e "
                                "manutenção do código.\n"
                                "6. Implemente validações de entrada e tratamento de exceções adequados "
                                "aos requisitos, evitando encerramentos inesperados e comportamentos "
                                "inconsistentes.\n"
                                "7. Considere boas práticas de segurança, evitando operações perigosas, "
                                "execução arbitrária de comandos, exposição de informações sensíveis "
                                "e tratamento inadequado de dados fornecidos pelo usuário.\n"
                                "8. Evite duplicação desnecessária de código, variáveis sem utilização, "
                                "importações desnecessárias e complexidade excessiva.\n"
                                "9. Utilize comentários e docstrings quando forem úteis para explicar "
                                "partes relevantes da implementação, sem excesso de informações óbvias.\n"
                                "10. Garanta que os arquivos gerados possuam importações coerentes, "
                                "referências corretas entre módulos e uma estrutura compatível com "
                                "a execução do projeto.\n"
                                "11. Inclua testes automatizados em Python quando forem solicitados "
                                "ou fizerem parte dos requisitos do projeto. Não afirme que testes "
                                "foram executados ou aprovados.\n"
                                "12. Não invente funcionalidades, requisitos ou integrações que não "
                                "tenham sido solicitados ou que não sejam necessários para a solução.\n\n"
                            
                                "CRITÉRIOS DE IMPLEMENTAÇÃO:\n"
                                "- Priorize a correção funcional e o atendimento aos requisitos.\n"
                                "- Desenvolva uma solução completa, evitando entregar apenas exemplos, "
                                "trechos ilustrativos ou pseudocódigo.\n"
                                "- Quando houver múltiplos arquivos, garanta que eles funcionem em conjunto.\n"
                                "- Evite dependências externas desnecessárias.\n"
                                "- Não utilize caminhos absolutos específicos da máquina do usuário.\n"
                                "- Caso algum requisito seja ambíguo, adote a interpretação mais simples "
                                "e coerente com o objetivo do projeto, sem inventar funcionalidades adicionais.\n\n"
                            
                                "FORMATO DE RESPOSTA OBRIGATÓRIO:\n"
                                "Retorne exclusivamente um JSON válido, sem Markdown, blocos de código "
                                "ou explicações fora do JSON.\n"
                                "O JSON deve possuir uma chave chamada 'arquivos', cujo valor seja uma "
                                "lista de objetos.\n"
                                "Cada objeto deve possuir exatamente as seguintes informações:\n"
                                "- 'nome': caminho relativo e nome do arquivo Python, incluindo a extensão .py.\n"
                                "- 'conteudo': código-fonte completo do respectivo arquivo, representado "
                                "como uma string válida no JSON.\n"
                                "Inclua todos os arquivos Python necessários para que o projeto funcione.\n"
                                "Utilize caminhos relativos organizados em diretórios quando necessário. "
                                "Não utilize caminhos absolutos, caminhos que saiam da pasta do projeto "
                                "ou nomes de arquivos duplicados.\n"
                                "Certifique-se de que o JSON esteja sintaticamente válido, com aspas, "
                                "caracteres especiais e quebras de linha devidamente escapados.\n\n"
                            
                                f"REQUISITOS DO USUÁRIO:\n{prompt}"
                            )

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

