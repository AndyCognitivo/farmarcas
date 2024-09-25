import streamlit as st
import string


st.set_page_config(
    page_title='Password Generator',
    page_icon='🔑',
    layout='wide'
)

st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

st.title('Password Generator 🔑')
st.text('Generate a random password with the length and characters of your choice.')

st.multiselect('Selecione o brick:', [1,2,3,4,5])

st.sidebar.title('Settings')
length = st.sidebar.slider('Length', 4, 64, 8, 1)
chars = st.sidebar.multiselect('Characters', ['Letters', 'Digits', 'Punctuation'], ['Letters', 'Digits', 'Punctuation'])
