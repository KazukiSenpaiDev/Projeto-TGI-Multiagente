import streamlit as st
from services.prompt_service import receber_prompt

if "prompt_enviado" not in st.session_state:
    st.session_state.prompt_enviado = None

def mostrar_interface():
    st.html("<style>textarea { resize: none !important; }</style>")


    st.title("Projeto TGI - Multiagente!!!")


    prompt = st.text_area("Digite seu prompt:", height=200, key="prompt_text_area")

    if st.button("Gerar projeto", on_click=enviar_prompt, args=(prompt,)):

        
        if st.session_state.prompt_enviado:
            resposta = st.session_state.prompt_enviado

            
            if "error" in resposta:
                st.error(resposta["error"])

            elif not isinstance(resposta, dict):
                st.error("A resposta recebida da API é inválida.")

            elif "codigo_gerado" not in resposta:
                st.error("A resposta da API não contém os arquivos gerados.")

            elif not isinstance(resposta["codigo_gerado"], dict):
                st.error("O formato dos dados gerados é inválido.")

            elif not isinstance(
                resposta["codigo_gerado"].get("arquivos"), list
            ):
                st.error("A resposta não contém uma lista válida de arquivos.")

            else:
                st.success(resposta.get("message", "Projeto gerado com sucesso!"))

                st.write("Prompt recebido pela API:")
                st.code(resposta.get("Prompt_recebido", ""))

                st.write("Arquivos gerados pelo Claude:")

                arquivos = resposta["codigo_gerado"]["arquivos"]

                if not arquivos:
                    st.warning("Nenhum arquivo foi gerado.")

                for arquivo in arquivos:
                    if (
                        not isinstance(arquivo, dict)
                        or not isinstance(arquivo.get("nome"), str)
                        or not isinstance(arquivo.get("conteudo"), str)
                    ):
                        st.warning("Um arquivo retornado possui formato inválido.")
                        continue

                    st.subheader(arquivo["nome"])
                    st.code(arquivo["conteudo"], language="python")

        else:
            st.warning("Por favor, digite um prompt antes de enviar.")



def enviar_prompt(p: str):

    if p.strip() == "":
        st.session_state.prompt_enviado = None
    else:
        resposta = receber_prompt(p)
        st.session_state.prompt_enviado = resposta
        st.session_state.prompt_text_area = ""
    