import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Liga Fiuzeira 25/26", layout="wide", page_icon="⚽")

# --- ESTILOS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🏆 Liga Fiuzeira Forever 25/26")
st.subheader("Dashboard Oficial de Gestão")

# --- FUNÇÕES DE LÓGICA ---
def calcular_pontos_extra(pts):
    if pts > 100: return 2
    if 75 <= pts <= 100: return 1
    if 10 <= pts <= 25: return -1
    if pts < 10: return -2
    return 0

# --- BARRA LATERAL (ADMIN) ---
with st.sidebar:
    st.header("⚙️ Painel Admin")
    st.info("Carrega o ficheiro CSV semanal da Liga Record.")
    uploaded_file = st.file_uploader("Ficheiro da Ronda", type=["csv"])
    
    st.divider()
    st.write("📌 **Regras Ativas:**")
    st.caption("✅ >100 pts: +2 | 75-100: +1")
    st.caption("❌ 10-25 pts: -1 | <10: -2")

# --- CONTEÚDO PRINCIPAL ---
if uploaded_file:
    # A Liga Record tem metadados nas primeiras 4 linhas
    df = pd.read_csv(uploaded_file, skiprows=4)
    
    # Limpeza e cálculos
    df['Pts Extra'] = df['Pts Ronda'].apply(calcular_pontos_extra)
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Liga Record", "⚔️ Campeonato", "🔥 Top Performance", "🍽️ Painel do Jantar"])

    with tab1:
        st.markdown("### Classificação Geral (Liga Record)")
        df_geral = df.sort_values(by="Pts Total", ascending=False).reset_index(drop=True)
        df_geral.index += 1
        st.dataframe(df_geral[['Equipa', 'Treinador', 'Pts Ronda', 'Pts Total']], use_container_width=True)

    with tab2:
        st.markdown("### Campeonato H2H (Confronto Direto)")
        st.info("Para ativar os confrontos, na próxima versão vamos carregar o Calendário fixo.")
        st.write("Resumo de Pontuação Extra desta Ronda:")
        df_extra = df[df['Pts Extra'] != 0][['Treinador', 'Equipa', 'Pts Ronda', 'Pts Extra']].sort_values(by="Pts Extra", ascending=False)
        st.table(df_extra)

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🔥 Top 5 Treinadores da Semana")
            top5 = df.sort_values(by="Pts Ronda", ascending=False).head(5)
            for i, row in top5.iterrows():
                st.success(f"**{row['Treinador']}** - {row['Pts Ronda']} pts")
        
        with col2:
            st.markdown("### 🚀 Recordes (Pontuação Alta)")
            # Simulação de Top 10 (precisará de base de dados para ser persistente em todas as rondas)
            st.write("Top 10 histórico em desenvolvimento...")

    with tab4:
        st.markdown("### 🍽️ Quem paga o jantar?")
        # Lógica: Dividir a tabela ao meio
        meio = len(df) // 2
        pagam = df_geral.iloc[meio:]
        recebem = df_geral.iloc[:meio]
        
        c1, c2 = st.columns(2)
        with c1:
            st.warning("🍷 **Os que Recebem (Primeira Metade)**")
            st.write(recebem[['Treinador', 'Equipa']])
        with c2:
            st.error("💸 **Os que PAGAM (Segunda Metade)**")
            st.write(pagam[['Treinador', 'Equipa']])
            if len(df) % 2 != 0:
                st.info(f"💡 {df_geral.iloc[meio]['Treinador']} está no meio: paga apenas o seu!")

else:
    st.info("👋 Olá! À espera do upload do ficheiro da ronda para mostrar os dados.")
