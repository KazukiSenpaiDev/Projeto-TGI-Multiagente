
import requests

API_URL = "http://127.0.0.1:8000/gerar"


def receber_prompt(prompt):
    try:
        resposta = requests.post(
            API_URL,
            json={"prompt": prompt},
            timeout=10
        )

        resposta.raise_for_status()

        return resposta.json()

    except requests.exceptions.Timeout:
        return {"error": "A API demorou muito para responder."}

    except requests.exceptions.ConnectionError:
        return {"error": "Não foi possível conectar à API."}

    except requests.exceptions.HTTPError:
        return {"error": "A API retornou um erro ao processar o prompt."}

    except requests.exceptions.RequestException:
        return {"error": "Ocorreu um erro na comunicação com a API."}

    except ValueError:
        return {"error": "A API retornou uma resposta inválida."}
