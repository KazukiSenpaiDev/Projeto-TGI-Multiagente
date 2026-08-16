import streamlit as st


def enviar_prompt():
    st.session_state.prompt_enviado = prompt
    st.session_state.prompt_text_area = ""
    

st.html("<style>textarea { resize: none !important; }</style>")


st.title("Projeto TGI - Multiagente!!!")


prompt = st.text_area("Digite seu prompt:", height=200, key="prompt_text_area")

if st.button("Gerar projeto", on_click=enviar_prompt):
    if st.session_state.prompt_enviado == "":
        st.warning("Por favor, digite um prompt antes de enviar.")
    else:
        st.success("Prompt enviado com sucesso!")
        st.write("Prompt enviado:", st.session_state.prompt_enviado)

