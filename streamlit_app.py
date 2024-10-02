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

#============= processa dados start ==================

!pip install boto3
import pandas as pd
import boto3
import io



# Replace with your S3 bucket and file details
bucket_name = 'smartmixfarpoc'

#names excel files
perfil_lojas_file_name = 'Perfil lojas tratado.xlsx'
iqvia_med_file_name = 'IQVIA PCP_MEDICAMENTO - tratado.xlsx'
iqvia_naomed_file_name = 'IQVIA PCP_NÃO MEDICAMENTO - tratado.xlsx'
#close_up_file_name = 'Rk Produtos Mercado Close-UP - MAT 06.2024 - tratado.xlsx'
close_up_file_name = 'utcs_concatenados.csv'

#names csv files
sellout_julho_file_name = 'sellout.ft_venda_202407_202408261021.csv'
fato_pcp_file_name = 'fato_pcp_cubo_farmarcas_iqvia_202409192107.csv'
cadastro_produtos_file_name = 'cadastro_produtos_iqvia_202409192057.csv'


# Create an S3 client
s3 = boto3.client('s3',
                  aws_access_key_id= 'AKIARRDSZWDIZXKVM3OF',
                  aws_secret_access_key= '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'
                  )

# ------- reading excel files ----------
##perfil_lojas
# Download the Excel file from S3
obj = s3.get_object(Bucket=bucket_name, Key = perfil_lojas_file_name)
excel_content = obj['Body'].read()
# Read the Excel content into a Pandas DataFrame
perfil_lojas = pd.read_excel(io.BytesIO(excel_content))

##iqvia_med
# Download the Excel file from S3
obj = s3.get_object(Bucket=bucket_name, Key = iqvia_med_file_name)
excel_content = obj['Body'].read()
# Read the Excel content into a Pandas DataFrame
iqvia_med = pd.read_excel(io.BytesIO(excel_content))

##iqvia_naomed
# Download the Excel file from S3
obj = s3.get_object(Bucket=bucket_name, Key = iqvia_naomed_file_name)
excel_content = obj['Body'].read()
# Read the Excel content into a Pandas DataFrame
iqvia_naomed = pd.read_excel(io.BytesIO(excel_content))

iqvia_consolidado = pd.concat([iqvia_med, iqvia_naomed])

##close_up
# Download the Excel file from S3
#obj = s3.get_object(Bucket=bucket_name, Key = close_up_file_name)
#excel_content = obj['Body'].read()
# Read the Excel content into a Pandas DataFrame
#close_up = pd.read_excel(io.BytesIO(excel_content), sheet_name='Região')

# ------- reading csv files ----------
##close_up
# Download the CSV file from S3
obj = s3.get_object(Bucket=bucket_name, Key=close_up_file_name)
csv_content = obj['Body'].read().decode('utf-8')
# Read the CSV content into a Pandas DataFrame
close_up = pd.read_csv(io.StringIO(csv_content), sep=';')

##sellout_julho
# Download the CSV file from S3
obj = s3.get_object(Bucket=bucket_name, Key=sellout_julho_file_name)
csv_content = obj['Body'].read().decode('utf-8')
# Read the CSV content into a Pandas DataFrame
sellout_julho = pd.read_csv(io.StringIO(csv_content), sep=';')

##fato_pcp
# Download the CSV file from S3
obj = s3.get_object(Bucket=bucket_name, Key=fato_pcp_file_name)
csv_content = obj['Body'].read().decode('utf-8')
# Read the CSV content into a Pandas DataFrame
fato_pcp = pd.read_csv(io.StringIO(csv_content), sep=';')

##cadastro_produtos
# Download the CSV file from S3
obj = s3.get_object(Bucket=bucket_name, Key=cadastro_produtos_file_name)
csv_content = obj['Body'].read().decode('utf-8')
# Read the CSV content into a Pandas DataFrame
cadastro_produtos = pd.read_csv(io.StringIO(csv_content), sep=';')


cadastro_produtos['categoria_ajustada'] = cadastro_produtos.apply(lambda row: row['classe_1'] if row['nec_1'] == '98 - NOT OTC                  ' else row['nec_1'], axis=1)

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

merge_brick_categoria = fato_pcp.merge(cadastro_produtos, left_on='ean', right_on='ean', how='left')
df_brick_categoria = df_pareto_func(merge_brick_categoria, 'brick', 'categoria_ajustada', 'sum_unidade')

merge_utc_categoria = close_up.merge(cadastro_produtos, left_on='EAN', right_on='ean', how='left')
df_utc_categoria = df_pareto_func(merge_utc_categoria, 'UTC', 'categoria_ajustada', 'RK UTC (UND.)')

merge_classe_categoria = sellout_julho.merge(cadastro_produtos, left_on='cod_barras', right_on='ean', how='left')
merge_classe_categoria = merge_classe_categoria.merge(perfil_lojas, left_on='cnpj', right_on='CNPJ', how='left')
df_classe_categoria = df_pareto_func(merge_classe_categoria, 'classe social', 'categoria_ajustada', 'sum_unidade')





#====================== processa dados end ==============================
brick_input = st.selectbox('Selecione o brick:', [1032,2,3,4,5])
region_input = st.selectbox('Selecione o UTC:', [1500404000,7,8,9,10])
class_input = st.selectbox('Selecione o perfil de loja:', ['B1','B','C','D','E'])


df_brick_categoria_filtered = df_brick_categoria[df_brick_categoria['brick'] == brick_input]
df_utc_categoria_filtered = df_utc_categoria[df_utc_categoria['UTC'] == region_input]
df_classe_categoria_filtered = df_classe_categoria[df_classe_categoria['classe social'] == class_input]

merged_df = df_brick_categoria_filtered.merge(df_utc_categoria_filtered, on='ean', how='inner', suffixes=('_brick', '_utc')) \
              .merge(df_classe_categoria_filtered, on='ean', how='inner', suffixes=('_merged', '_classe'))


df_out[['pareto_classification_classe']] = merged_df[['pareto_classification'] ]
df_out = df_out[['ean', 'pareto_classification_brick', 'pareto_classification_utc', 'pareto_classification_classe'] ]





#df_example = pd.DataFrame(np.array( [[1, 2, 3, 45], [4, 5, 6, 43], [3, 6, 2, 12]] ),
#                   columns=[ 'brick', 'utc', 'perfil loja', 'quantidade'])

st.dataframe(df_out)
