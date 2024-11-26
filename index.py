import streamlit as st
import pandas as pd

# Título do aplicativo
st.title("Análise Básica de Arquivo CSV")

# Nome do arquivo CSV
file_name = "disney_plus_titles.csv"

try:
    # Ler o arquivo CSV
    df = pd.read_csv(file_name)

    # Exibir informações básicas
    st.subheader("Prévia dos Dados")
    st.dataframe(df.head())

    st.subheader("Informações Básicas")
    st.write("Número de linhas:", df.shape[0])
    st.write("Número de colunas:", df.shape[1])
    st.write("Colunas presentes:", list(df.columns))

    st.subheader("Resumo Estatístico")
    st.write(df.describe())

except FileNotFoundError:
    st.error(f"O arquivo `{file_name}` não foi encontrado. Certifique-se de que ele está na mesma pasta do projeto.")
except Exception as e:
    st.error(f"Ocorreu um erro ao ler o arquivo: {e}")
