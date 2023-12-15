import logging
import streamlit as st
import utilities as util

logging.basicConfig(format="\n%(asctime)s\n%(message)s", level=logging.INFO, force=True)

# Configure Streamlit page and state
st.set_page_config(page_title="5010 Guru")
tooltip_style = """
<style>
div[data-baseweb="tooltip"] {
  width: 300px;
}
</style>
"""
st.markdown(tooltip_style, unsafe_allow_html=True)

if util.check_password(st.session_state, st.secrets):

    # initialize state
    if "text_error" not in st.session_state:
        st.session_state.text_error = ""
    if "query" not in st.session_state:
        st.session_state.query = "What is Circular 5010.1E?"
    if "answer" not in st.session_state:
        st.session_state.answer = ""
    if "source" not in st.session_state:
        st.session_state.source = ""
    if "content" not in st.session_state:
        st.session_state.content = ""
    if "database" not in st.session_state:
        util.get_database(st.session_state, st.secrets)
    if "llm" not in st.session_state:
        util.get_llm(st.session_state, st.secrets)

    # Render Streamlit page
    st.title("5010 Guru")
    st.markdown(
        "Hello, I'm an expert in FTA's Circular 5010.1E, as well as various other [FTA circulars]"
        "(https://www.transit.dot.gov/regulations-and-programs/fta-circulars/circulars). \n\n"
        "Feel free to ask me any questions!"
    )

    # with st.form('form'):
    query = st.text_area(label="Question:", placeholder=st.session_state.query)
    st.button(
        'Get Answer',
        type='primary',
        on_click=util.get_answer,
        args=(st.session_state, query)
    )

    if st.session_state.text_error:
        st.error(st.session_state.text_error)
        st.session_state.text_error = ''

    if st.session_state.answer:
        st.markdown("""---""")
        st.write(st.session_state.query)
        st.text_area(label="Answer:", value=st.session_state.answer, height=200)
        st.text_area(label="Source:", value=st.session_state.source, height=500)
        st.text_area(label="Content:", value=st.session_state.content, height=500)
