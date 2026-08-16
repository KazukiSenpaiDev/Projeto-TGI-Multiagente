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
            st.success("Prompt enviado com sucesso!")
            st.write(st.session_state.prompt_enviado)
        else:
            st.warning("Por favor, digite um prompt antes de enviar.")


def enviar_prompt(p: str):

    if p.strip() == "":
        st.session_state.prompt_enviado = None
    else:
        novo_prompt = receber_prompt(p)
        st.session_state.prompt_enviado = novo_prompt
        st.session_state.prompt_text_area = ""
    