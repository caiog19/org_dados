import streamlit as st
import pandas as pd
import plotly.express as px

# Função de carregamento e processamento de dados com cache
@st.cache_data
def load_data():
    df = pd.read_csv('disney_plus_titles.csv')
    
    # Converter 'date_added' para datetime
    if 'date_added' in df.columns:
        df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    
    # Preencher valores ausentes em colunas importantes
    df['director'].fillna('Unknown', inplace=True)
    df['cast'].fillna('Unknown', inplace=True)
    df['country'].fillna('Unknown', inplace=True)
    df['rating'].fillna('Unknown', inplace=True)
    
    return df

# Função de filtragem de dados com cache
@st.cache_data
def filter_data(df, content_type, country, start_date, end_date, director):
    filtered = df
    if content_type:
        filtered = filtered[filtered['type'].isin(content_type)]
    if country:
        filtered = filtered[filtered['country'].isin(country)]
    if start_date and end_date:
        filtered = filtered[
            (filtered['date_added'] >= pd.to_datetime(start_date)) &
            (filtered['date_added'] <= pd.to_datetime(end_date))
        ]
    if director:
        filtered = filtered[filtered['director'].str.contains(director, case=False, na=False)]
    return filtered

def main():
    st.set_page_config(
        page_title="Dashboard: Disney+ Titles",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    st.title("Dashboard: Disney+ Titles")
    st.markdown("Explore o catálogo da Disney+ de forma interativa, filtrando por tipo de conteúdo, país e outros critérios.")
    
    # Carregar os dados
    df = load_data()
    
    # Filtros principais na barra lateral
    st.sidebar.header("Filtros")
    content_type = st.sidebar.multiselect(
        "Escolha o Tipo de Conteúdo", 
        options=df['type'].dropna().unique(),
        default=df['type'].dropna().unique()  # Seleção padrão de todos os tipos
    )
    country = st.sidebar.multiselect(
        "Escolha o(s) País(es)", 
        options=df['country'].dropna().unique(),
    )
    
    # Filtro por Data de Adição
    if 'date_added' in df.columns:
        min_date = df['date_added'].min()
        max_date = df['date_added'].max()
        start_date, end_date = st.sidebar.date_input(
            "Selecione o Intervalo de Datas Adicionadas",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
    else:
        start_date, end_date = None, None
    
    # Busca por Diretor
    director_search = st.sidebar.text_input("Buscar por Diretor")
    
    # Aplicar filtros
    filtered_df = filter_data(df, content_type, country, start_date, end_date, director_search)
    
    # Navegação por Abas
    tabs = st.tabs(["Visão Geral", "Análises Específicas", "Detalhes do Título"])
    
    with tabs[0]:
        st.write("### Dados Gerais")
        st.dataframe(filtered_df.head())
        
        # KPIs
        total_titles = len(filtered_df)
        unique_directors = filtered_df['director'].nunique()
        unique_countries = filtered_df['country'].nunique()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Títulos", total_titles)
        col2.metric("Diretores Únicos", unique_directors)
        col3.metric("Países Únicos", unique_countries)
        
        # Gráfico de Distribuição por Tipo
        type_distribution = filtered_df['type'].value_counts().reset_index()
        type_distribution.columns = ['Type', 'Count']
        fig_type = px.pie(
            type_distribution, 
            names='Type', 
            values='Count', 
            title='Distribuição por Tipo de Conteúdo'
        )
        st.plotly_chart(fig_type, use_container_width=True)
    
    with tabs[1]:
        st.write("### Análise de Padrões")
        
        # Gráfico de Distribuição de Lançamentos por Ano
        release_years = filtered_df['release_year'].value_counts().reset_index()
        release_years.columns = ['Release Year', 'Count']
        release_years = release_years.sort_values('Release Year')
        
        fig_release = px.bar(
            release_years, 
            x='Release Year', 
            y='Count', 
            title='Distribuição de Lançamentos por Ano',
            labels={'Release Year': 'Ano de Lançamento', 'Count': 'Quantidade'}
        )
        st.plotly_chart(fig_release, use_container_width=True)
        
        # Top Países
        top_countries = filtered_df['country'].value_counts().head(10).reset_index()
        top_countries.columns = ['Country', 'Count']
        
        fig_countries = px.bar(
            top_countries, 
            x='Country', 
            y='Count', 
            title='Top 10 Países com Mais Títulos',
            labels={'Country': 'País', 'Count': 'Quantidade'}
        )
        st.plotly_chart(fig_countries, use_container_width=True)
    
    with tabs[2]:
        st.write("### Detalhes de Títulos")
        if not filtered_df.empty:
            selected_title = st.selectbox(
                "Selecione um Título para Ver Detalhes", 
                options=filtered_df['title'].dropna().unique()
            )
            if selected_title:
                title_details = filtered_df[filtered_df['title'] == selected_title].iloc[0]
                st.write(f"**Título:** {title_details['title']}")
                st.write(f"**Tipo:** {title_details['type']}")
                st.write(f"**Diretor:** {title_details['director']}")
                st.write(f"**Elenco:** {title_details['cast']}")
                st.write(f"**País:** {title_details['country']}")
                st.write(f"**Data de Adição:** {title_details['date_added'].strftime('%Y-%m-%d') if pd.notnull(title_details['date_added']) else 'N/A'}")
                st.write(f"**Ano de Lançamento:** {title_details['release_year']}")
                st.write(f"**Duração:** {title_details['duration']}")
                st.write(f"**Gênero(s):** {title_details['listed_in']}")
                st.write(f"**Descrição:** {title_details['description']}")
        else:
            st.info("Nenhum título disponível com os filtros aplicados.")
    
    # Botão de Download de Dados Filtrados
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')
    
    csv_data = convert_df_to_csv(filtered_df)
    
    st.download_button(
        label="Download dos Dados Filtrados",
        data=csv_data,
        file_name='disney_plus_titles_filtered.csv',
        mime='text/csv',
    )
    
if __name__ == "__main__":
    main()
