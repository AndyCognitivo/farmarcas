import streamlit as st
import string
import pandas as pd
import numpy as np

st.set_page_config(
    page_title='SMART MIX - FARMARCAS',
    #page_icon='🔑',
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

st.title('Smart Mix')
st.text('Gerando a melhor sugestão de estoque para o seu negócio farmaceutico.')

brick = st.multiselect('Selecione o brick:', [1,2,3,4,5])
utc = st.multiselect('Selecione o UTC:', [6,7,8,9,10])
perfil_loja = st.multiselect('Selecione o perfil de loja:', ['A','B','C','D','E'])

df_example = pd.DataFrame(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [34,65,23]]),
                   columns=['brick', 'utc', 'perfil loja', 'quantidade'])
st.dataframe(df_example)
