import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Liga Fiuzeira 25/26", layout="wide", page_icon="⚽")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏆 Liga Fiuzeira Forever 25/26")
st.subheader("Dashboard Oficial de Gestão")

# --- LÓGICA DE PONTOS EXTRA ---
def calcular_pontos_extra(pts):
    if pts > 100: return 2
    if 75 <= pts <= 100: return 1
    if 10 <= pts <= 25: return -1
    if pts < 10: return -2
    return 0

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Painel Admin")
    uploaded_file = st.file_uploader("Ficheiro da Ronda (CSV Liga Record)", type=["csv"])
    
    st.divider()
    st.write("📌 **Regras do Campeonato:**")
    st.caption("Vitória: 2 | Empate: 1 | Derrota: 0")
    st.caption("✅ >100 pts: +2 | 75-100 pts: +1")
    st.caption("❌ 10-25 pts: -1 | <10 pts: -2")

# --- CONTEÚDO PRINCIPAL ---
if uploaded_file:
    # Ler os dados da Liga Record
    df = pd.read_csv(uploaded_file, skiprows=4)
    # Limpar espaços extra nos nomes das equipas (evita erros de cruzamento)
    df['Equipa'] = df['Equipa'].str.strip()
    
    # Calcular automaticamente os pontos extra de cada um na ronda atual
    df['Pts Extra'] = df['Pts Ronda'].apply(calcular_pontos_extra)
    
    tab1, tab2, tab3 = st.tabs(["📊 Liga Record", "⚔️ Campeonato H2H (Jogos)", "🍽️ O Jantar"])

    with tab1:
        st.markdown("### Classificação Geral (Liga Record)")
        df_geral = df.sort_values(by="Pts Total", ascending=False).reset_index(drop=True)
        df_geral.index += 1
        st.dataframe(df_geral[['Equipa', 'Treinador', 'Pts Ronda', 'Pts Extra', 'Pts Total']], use_container_width=True)

    with tab2:
        st.markdown("### ⚔️ Máquina de Resultados do Campeonato")
        st.info("Alinha aqui os confrontos desta semana. A App vai buscar as pontuações e calcula os vencedores e os bónus!")
        
        equipas_lista = df['Equipa'].tolist()
        
        # Criar a grelha de jogos interativa
        if 'jogos' not in st.session_state:
            meio = len(equipas_lista) // 2
            st.session_state['jogos'] = pd.DataFrame({
                'Equipa Casa': equipas_lista[:meio],
                'Equipa Fora': equipas_lista[meio:]
            })
        
        # Tabela onde podes escolher as equipas a partir de listas dropdown
        jogos_editados = st.data_editor(
            st.session_state['jogos'],
            column_config={
                "Equipa Casa": st.column_config.SelectboxColumn("🏠 Equipa Casa", options=equipas_lista, required=True),
                "Equipa Fora": st.column_config.SelectboxColumn("✈️ Equipa Fora", options=equipas_lista, required=True)
            },
            hide_index=True,
            use_container_width=True
        )
        
        if st.button("🔥 Calcular Resultados desta Jornada", type="primary"):
            st.markdown("---")
            st.markdown("### 🏁 Resultados Oficiais")
            resultados = []
            
            for _, row in jogos_editados.iterrows():
                casa = row['Equipa Casa']
                fora = row['Equipa Fora']
                
                # Garantir que não está a jogar contra si mesmo e que as equipas existem
                if casa and fora and casa != fora:
                    # Ir buscar os pontos feitos na ronda
                    pts_casa = df[df['Equipa'] == casa]['Pts Ronda'].values[0]
                    pts_fora = df[df['Equipa'] == fora]['Pts Ronda'].values[0]
                    
                    # Ir buscar os pontos extra calculados
                    extra_casa = df[df['Equipa'] == casa]['Pts Extra'].values[0]
                    extra_fora = df[df['Equipa'] == fora]['Pts Extra'].values[0]
                    
                    # Lógica do Jogo (2, 1, 0)
                    if pts_casa > pts_fora:
                        res_casa, res_fora = 2, 0
                    elif pts_casa < pts_fora:
                        res_casa, res_fora = 0, 2
                    else:
                        res_casa, res_fora = 1, 1
                        
                    # Pontos Finais para a tabela do campeonato (Resultado do jogo + Pts Extra)
                    total_casa = res_casa + extra_casa
                    total_fora = res_fora + extra_fora
                    
                    resultados.append({
                        "Equipa Casa": casa, 
                        "Pts Ronda (Casa)": pts_casa, 
                        "Pontos Campeonato (Casa)": f"{total_casa} pts",
                        "VS": "⚔️",
                        "Pontos Campeonato (Fora)": f"{total_fora} pts", 
                        "Pts Ronda (Fora)": pts_fora, 
                        "Equipa Fora": fora
                    })
            
            df_resultados = pd.DataFrame(resultados)
            st.dataframe(df_resultados, hide_index=True, use_container_width=True)
            st.success("Tudo calculado! Vitórias, Derrotas, Empates e Bónus aplicados com sucesso.")

    with tab3:
        st.markdown("### 🍽️ Gestão do Jantar")
        df_jantar = df.sort_values(by="Pts Total", ascending=False).reset_index(drop=True)
        meio = len(df_jantar) // 2
        
        col1, col2 = st.columns(2)
        with col1:
            st.success("👑 **Metade Superior (Comem de Graça)**")
            st.table(df_jantar.iloc[:meio][['Treinador', 'Equipa']])
        with col2:
            st.error("💸 **Metade Inferior (Abrem a Carteira)**")
            st.table(df_jantar.iloc[meio:][['Treinador', 'Equipa']])

else:
    st.info("👋 Olá! À espera do upload do ficheiro CSV da Ronda no painel lateral.")
