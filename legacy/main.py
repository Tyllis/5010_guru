import logging
import os
import streamlit as st
from deta import Deta
from datetime import datetime
from gpt_index import GPTSimpleVectorIndex

logging.basicConfig(format="\n%(asctime)s\n%(message)s", level=logging.INFO, force=True)

# Define functions
def get_index():
    # note
    os.environ['OPENAI_API_KEY'] = st.secrets["openai_api"]
    # llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="text-davinci-003"))
    # index = GPTSimpleVectorIndex.load_from_disk('index.json', llm_predictor=llm_predictor)
    index = GPTSimpleVectorIndex.load_from_disk('index.json')
    st.session_state.index = index


def get_answer(query_strs):
    st.session_state.text_error = ''
    st.session_state.answer = ''
    st.session_state.source = ''
    if not query_strs:
        st.session_state.text_error = "Please ask a question."
        return
    if not st.session_state.index:
        st.session_state.text_error = "Please enter a valid key first."
        return
    with text_spinner_placeholder:
        with st.spinner("Please wait while I look for an answer..."):
            try:
                response = st.session_state.index.query(query_strs.strip())
                st.session_state.answer = response.response.strip()
                st.session_state.source = response.source_nodes[0].source_text
                st.session_state.rated = False
                st.session_state.now = datetime.now()
                st.session_state.query = query_strs
            except Exception as err:
                message = f"""
                😕 Ran into unexpected error. Please seek out Master Jun for help. 
                Error message:
                {err}
                """
                st.session_state.text_error = message


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] in st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password",
            placeholder='***********',
            help="""
            Right key, you do not have. Master Jun, you must seek.
            """
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True


def get_deta():
    deta = Deta(st.secrets["deta_key"])
    st.session_state.deta_users = deta.Base("users")


def deta_insert(rating):
    st.session_state.deta_users.insert({
        "date": st.session_state.now.strftime('%Y-%m-%d'),
        "time": st.session_state.now.strftime("%H:%M:%S"),
        "question": st.session_state.query,
        "answer": st.session_state.answer,
        "rating": rating
    })
    st.session_state.rated = True

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


if check_password():
    if "text_error" not in st.session_state:
        st.session_state.text_error = ""
    if "query" not in st.session_state:
        st.session_state.query = "What is 5010.1E?"
    if "answer" not in st.session_state:
        st.session_state.answer = ""
    if "source" not in st.session_state:
        st.session_state.source = ""
    if "rated" not in st.session_state:
        st.session_state.rated = ""
    if "index" not in st.session_state:
        get_index()
    if "deta_users" not in st.session_state:
        get_deta()

    # Render Streamlit page
    st.title("5010 Guru")
    st.markdown(
        "Hello, I'm an expert in [5010.1E](https://www.transit.dot.gov/regulations-and-guidance/"
        "fta-circulars/award-management-requirements-circular-50101e), "
        "FTA's Award Management Requirements Circular.  \n\n"
        "Ask me any questions!"
    )

    query = st.text_input(label="Question:", placeholder=st.session_state.query)

    st.button(
        label="Get Answer",
        type="primary",
        on_click=get_answer,
        args=(query,),
    )

    text_spinner_placeholder = st.empty()

    if st.session_state.text_error:
        st.error(st.session_state.text_error)
        st.session_state.text_error = ''

    if st.session_state.answer:
        st.markdown("""---""")
        st.markdown(st.session_state.query)
        st.text_area(label="Answer:", value=st.session_state.answer, height=200)

        if not st.session_state.rated:
            st.markdown("""---""")
            st.markdown(
                """
                Please rate my answer. This will help Master Jun train me in the future.  \n\n
                """
            )
            col1, col2, col3, col4 = st.columns(4)
            col1.button(':disappointed:', on_click=deta_insert, args=(0,),
                        help="The answer does not make any sense.")
            col2.button(':star:', on_click=deta_insert, args=(1,),
                        help="The answer only helps a little.")
            col3.button(':star::star:', on_click=deta_insert, args=(2,),
                        help="The answer helps me some what.")
            col4.button(':star::star::star:', on_click=deta_insert, args=(3,),
                        help="WOW, the answer nails it!")

    if st.session_state.source:
        st.markdown("""---""")
        st.text_area(label="Source:", value=st.session_state.source, height=1000)