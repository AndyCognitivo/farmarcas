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
