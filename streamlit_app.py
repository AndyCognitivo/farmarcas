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

# ============================ processa dados ============================
import pandas as pd

from google.colab import drive
drive.mount('/content/drive')

# exemplo
#perfil_lojas = pd.read_excel("/content/drive/MyDrive/dados_farmarcas/Perfillojas_Farmarcas.xlsx")

#cnpj, classe social
perfil_lojas = pd.read_excel("/content/drive/MyDrive/dados_farmarcas/Perfil lojas tratado.xlsx")
#iqvia: brick, ean, qtde
iqvia_med = pd.read_excel("/content/drive/MyDrive/dados_farmarcas/IQVIA PCP_MEDICAMENTO - tratado.xlsx")
iqvia_naomed = pd.read_excel("/content/drive/MyDrive/dados_farmarcas/IQVIA PCP_NÃO MEDICAMENTO - tratado.xlsx")
iqvia_consolidado = pd.concat([iqvia_med, iqvia_naomed])
#cnpj, ean, qtde
sellout_julho = pd.read_csv("/content/drive/MyDrive/dados_farmarcas/sellout.ft_venda_202407_202408261021.csv",sep=';')
fato_pcp = pd.read_csv("/content/drive/MyDrive/dados_farmarcas/fato_pcp_cubo_farmarcas_iqvia_202409192107.csv",sep=';')
cadastro_produtos = pd.read_csv("/content/drive/MyDrive/dados_farmarcas/cadastro_produtos_iqvia_202409192057.csv", sep = ';')

merge_fato_cadastro = fato_pcp.merge(cadastro_produtos, left_on='ean', right_on='ean', how='left')
merge_fato_cadastro['categoria_ajustada'] = merge_fato_cadastro.apply(lambda row: row['classe_1'] if row['nec_1'] == '98 - NOT OTC                  ' else row['nec_1'], axis=1)

# Coluna pareto
def pareto_classification(row):
  if row['cumulative_percentage'] <= 50:
    return 'A'
  elif row['cumulative_percentage'] <= 80:
    return 'B'
  else:
    return 'C'

def df_pareto_func(df, col1, col2, col_unid):
  # Group by 'brick', 'categoria ajustada', and 'ean' and sum 'sum_unidade'
  pareto_out = df.groupby([col1, col2, 'ean'])[col_unid].sum().reset_index()
  # Sort values by 'brick', 'categoria ajustada', and 'sum_unidade' in descending order
  pareto_out = pareto_out.sort_values(by=[col1, col2, col_unid], ascending=[True, True, False])
  # Calculate the cumulative sum of 'sum_unidade' for each 'brick' and 'categoria ajustada'
  pareto_out['cumulative_sum'] = pareto_out.groupby([col1, col2])[col_unid].cumsum()
  # Calculate the cumulative percentage for each 'brick' and 'categoria ajustada'
  pareto_out['cumulative_percentage'] = (pareto_out['cumulative_sum'] / pareto_out.groupby([col1, col2])[col_unid].transform('sum')) * 100
  pareto_out['pareto_classification'] = pareto_out.apply(pareto_classification, axis=1)
  return pareto_out

df = df_pareto_func(merge_fato_cadastro, 'brick', 'categoria_ajustada', 'sum_unidade')
#df.head()


# ========================================================================








#df_example = pd.DataFrame(np.array( [[1, 2, 3, 45], [4, 5, 6, 43], [3, 6, 2, 12]] ),
#                   columns=[ 'brick', 'utc', 'perfil loja', 'quantidade'])

st.dataframe(df)
