"""
Análise de Desempenho Acadêmico
Projeto Final Python
Faculdade FAFIRE - Pós de BI, BA e Big Data aplicados a négocios
Aluno Igor Luiz Oliveira da Silva
"""

# ============================
# IMPORTAÇÃO DAS BIBLIOTECAS
# ============================
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ============================
# CONFIGURAÇÃO DA PÁGINA
# ============================
st.set_page_config(
    page_title="Análise de Desempenho Acadêmico",
    page_icon="📊",
    layout="wide"
)

# ============================
# TÍTULO E DESCRIÇÃO
# ============================
st.title("📊 Análise de Desempenho Acadêmico")
st.markdown("---")
st.markdown("""
Dashboard de análise de dados educacionais de alunos em diferentes cursos e disciplinas.
""")

# ============================
# CARREGAMENTO DOS DADOS
# ============================
@st.cache_data
def carregar_dados():
    """
    Carrega e realiza o tratamento inicial dos dados
    """
    # Lê o arquivo CSV
    df = pd.read_csv('alunos_notas_frequencia.csv')
    return df

# Carrega os dados
df = carregar_dados()

# ============================
# TRATAMENTO DE DADOS
# ============================
st.header("🔧 Tratamento de Dados")

# Exibe informações básicas do dataset
with st.expander("📋 Informações do Dataset"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Registros", len(df))
    with col2:
        st.metric("Total de Colunas", len(df.columns))
    with col3:
        st.metric("Cursos Diferentes", df['curso'].nunique())
    
    st.subheader("Primeiras linhas:")
    st.dataframe(df.head())

# Padronização das colunas numéricas
# Converte colunas de notas para numérico (tratando vírgulas como separador decimal)
cols_notas = ['nota_1', 'nota_2', 'nota_final']
for col in cols_notas:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Cria coluna de média das notas
df['media_notas'] = df[['nota_1', 'nota_2']].mean(axis=1)

# Cria coluna indicando se foi reprovado por falta
df['reprovado_por_falta'] = df['faltas'] > 15

# Padroniza textos das colunas curso e status
df['curso'] = df['curso'].str.upper().str.strip()
df['status'] = df['status'].str.capitalize()

# Converte nota_final e faltas para numérico (tratando vírgulas)
df['nota_final'] = pd.to_numeric(df['nota_final'].astype(str).str.replace(',', '.'), errors='coerce')
df['faltas'] = pd.to_numeric(df['faltas'], errors='coerce')

# Função para calcular o status baseado nas regras
def calcular_status(row):
    """
    Calcula o status do aluno baseado em:
    - Faltas >= 20: Trancado
    - Nota final >= 7: Aprovado
    - Caso contrário: Reprovado
    """
    if row['faltas'] >= 20:
        return 'Trancado'
    elif row['nota_final'] >= 7:
        return 'Aprovado'
    else:
        return 'Reprovado'

# Aplica a função para criar coluna de status calculado
df['status_calculado'] = df.apply(calcular_status, axis=1)

# Exibe estatísticas descritivas
with st.expander("📊 Estatísticas Descritivas"):
    st.dataframe(df[['nota_1', 'nota_2', 'nota_final', 'faltas']].describe())

st.markdown("---")

# ============================
# FILTRO INTERATIVO
# ============================
st.header("🔍 Filtros")

# Cria o filtro de disciplina
disciplinas = ['Todas'] + sorted(df['disciplina'].unique().tolist())
disciplina_selecionada = st.selectbox(
    "📚 Selecione uma disciplina para filtrar os gráficos:",
    disciplinas,
    help="Escolha uma disciplina específica ou 'Todas' para ver todos os dados"
)

# Aplica o filtro nos dados
if disciplina_selecionada == 'Todas':
    df_filtrado = df.copy()
    texto_filtro = "Todas as Disciplinas"
else:
    df_filtrado = df[df['disciplina'] == disciplina_selecionada].copy()
    texto_filtro = f"Disciplina: {disciplina_selecionada}"

# Exibe informações sobre o filtro aplicado
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total de Alunos (Filtrado)", len(df_filtrado))
with col2:
    st.metric("Disciplina Selecionada", disciplina_selecionada)
with col3:
    taxa_aprovacao = (df_filtrado['status_calculado'] == 'Aprovado').sum() / len(df_filtrado) * 100 if len(df_filtrado) > 0 else 0
    st.metric("Taxa de Aprovação", f"{taxa_aprovacao:.1f}%")

st.markdown("---")

# ============================
# GRÁFICOS E VISUALIZAÇÕES
# ============================
st.header(f"📈 Visualizações - {texto_filtro}")

# Verifica se há dados após o filtro
if len(df_filtrado) == 0:
    st.warning("⚠️ Não há dados para a disciplina selecionada.")
else:
    # ============================
    # GRÁFICO 1: Quantidade de alunos por status
    # ============================
    st.subheader("1️⃣ Quantidade de Alunos por Status")

    # Cria a figura
    fig1, ax1 = plt.subplots(figsize=(6, 4))

    # Cria o gráfico countplot
    sns.countplot(data=df_filtrado, x='status_calculado', ax=ax1, palette='Set2')

    # Configurações do gráfico
    ax1.set_title(f'Quantidade de alunos por status\n{texto_filtro}', fontsize=14, weight='bold')
    ax1.set_xlabel('Status', fontsize=12)
    ax1.set_ylabel('Quantidade de alunos', fontsize=12)

    # Adiciona os valores em cima das barras
    for container in ax1.containers:
        ax1.bar_label(container, fontsize=10, weight='bold')

    # Exibe o gráfico no Streamlit
    st.pyplot(fig1)

    # Adiciona métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        aprovados = (df_filtrado['status_calculado'] == 'Aprovado').sum()
        st.metric("Aprovados", aprovados)
    with col2:
        reprovados = (df_filtrado['status_calculado'] == 'Reprovado').sum()
        st.metric("Reprovados", reprovados)
    with col3:
        trancados = (df_filtrado['status_calculado'] == 'Trancado').sum()
        st.metric("Trancados", trancados)

    st.markdown("---")

    # ============================
    # GRÁFICO 2: Relação entre faltas e nota final
    # ============================
    st.subheader("2️⃣ Relação entre Número de Faltas e Nota Final")

    # Cria a figura
    fig2, ax2 = plt.subplots(figsize=(7, 5))

    # Cria o scatterplot
    sns.scatterplot(
        data=df_filtrado,
        x='faltas',
        y='nota_final',
        alpha=0.6,
        ax=ax2,
        color='steelblue',
        s=50
    )

    # Configurações do gráfico
    ax2.set_title(f'Relação entre número de faltas e nota final\n{texto_filtro}', fontsize=14, weight='bold')
    ax2.set_xlabel('Número de faltas', fontsize=12)
    ax2.set_ylabel('Nota final', fontsize=12)
    ax2.grid(True, alpha=0.3)

    # Exibe o gráfico no Streamlit
    st.pyplot(fig2)

    # Adiciona análise de correlação
    if len(df_filtrado) > 1:
        correlacao = df_filtrado[['faltas', 'nota_final']].corr().iloc[0, 1]
        st.info(f"📊 Correlação entre faltas e nota final: **{correlacao:.3f}**")

    st.markdown("---")

    # ============================
    # GRÁFICO 3: Boxplot de nota final por status
    # ============================
    st.subheader("3️⃣ Distribuição da Nota Final por Status")

    # Cria a figura
    fig3, ax3 = plt.subplots(figsize=(8, 5))

    # Cria o boxplot
    sns.boxplot(
        data=df_filtrado,
        x='status_calculado',
        y='nota_final',
        ax=ax3,
        palette='pastel'
    )

    # Configurações do gráfico
    ax3.set_title(f'Distribuição da Nota Final por Status\n{texto_filtro}', fontsize=14, weight='bold')
    ax3.set_xlabel('Status do Aluno', fontsize=12)
    ax3.set_ylabel('Nota Final', fontsize=12)

    # Exibe o gráfico no Streamlit
    st.pyplot(fig3)

    # Adiciona estatísticas
    st.subheader("Estatísticas por Status:")
    col1, col2, col3 = st.columns(3)

    for idx, status in enumerate(['Aprovado', 'Reprovado', 'Trancado']):
        notas = df_filtrado[df_filtrado['status_calculado'] == status]['nota_final']
        with [col1, col2, col3][idx]:
            st.markdown(f"**{status}**")
            if len(notas) > 0:
                st.metric("Média", f"{notas.mean():.2f}")
                st.metric("Mediana", f"{notas.median():.2f}")
                st.metric("Qtd. Alunos", len(notas))
            else:
                st.metric("Sem dados", "-")

    st.markdown("---")

# ============================
# ANÁLISES ADICIONAIS
# ============================
st.header("📊 Análises Adicionais")

# Média de notas por disciplina (usando dados completos, não filtrados)
st.subheader("Média de Notas Finais por Disciplina")
media_disciplina = df.groupby('disciplina')['nota_final'].mean().sort_values(ascending=False)

# Cria um dataframe formatado
df_media = pd.DataFrame({
    'Disciplina': media_disciplina.index,
    'Média': media_disciplina.values.round(2)
})

st.dataframe(df_media, hide_index=True)

st.markdown("---")

# Tabela de dados filtrados
st.subheader("📋 Dados Filtrados")
st.dataframe(df_filtrado)

# Download dos dados filtrados
st.download_button(
    label="📥 Baixar dados filtrados (CSV)",
    data=df_filtrado.to_csv(index=False).encode('utf-8'),
    file_name=f'dados_{disciplina_selecionada.replace(" ", "_").lower()}.csv',
    mime='text/csv',
)

# ============================
# RODAPÉ
# ============================
st.markdown("---")
st.markdown("""
**Projeto Final Python - Análise de Desempenho Acadêmico**  
Dashboard desenvolvido com Streamlit | Filtros interativos por disciplina
""")