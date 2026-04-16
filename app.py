import streamlit as st
import pandas as pd
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Liga Fiuzeira 25/26", layout="wide", page_icon="⚽")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏆 Liga Fiuzeira Forever 25/26")

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
    st.info("Passo 1: Carrega a Jornada da Liga Record")
    uploaded_file = st.file_uploader("Ficheiro da Ronda (CSV)", type=["csv"])
    
    st.divider()
    st.write("📌 **Regras H2H:**")
    st.caption("Vitória: 2 | Empate: 1 | Derrota: 0")
    st.caption("Bónus: >100 (+2) | 75-100 (+1)")
    st.caption("Penalização: 10-25 (-1) | <10 (-2)")

# --- CONTEÚDO PRINCIPAL ---
if uploaded_file:
    # Ler os dados da Liga Record da semana
    try:
        df = pd.read_csv(uploaded_file, skiprows=4)
        df['Equipa'] = df['Equipa'].str.strip()
        df['Pts Extra'] = df['Pts Ronda'].apply(calcular_pontos_extra)
    except Exception as e:
        st.error(f"Erro ao ler o ficheiro da Liga Record. Confirma se é o ficheiro correto. Erro: {e}")
        st.stop()
    
    tab1, tab2, tab3, tab4 = st.tabs(["⚔️ 1. Resultados da Jornada", "🏆 2. Classificação Campeonato", "📊 3. Liga Record", "🍽️ 4. O Jantar"])

    with tab1:
        st.markdown("### ⚔️ Máquina de Resultados")
        
        if os.path.exists("calendario.csv") and os.path.exists("historico_campeonato.csv"):
            df_cal = pd.read_csv("calendario.csv")
            df_hist = pd.read_csv("historico_campeonato.csv")
            
            # Limpar espaços para garantir que os nomes cruzam bem
            df_cal['Equipa Casa'] = df_cal['Equipa Casa'].str.strip()
            df_cal['Equipa Fora'] = df_cal['Equipa Fora'].str.strip()
            df_hist['Equipa'] = df_hist['Equipa'].str.strip()
            
            jornadas_disponiveis = sorted(df_cal['Jornada_Camp'].unique())
            jornada_selecionada = st.selectbox("👉 Seleciona a Jornada do Campeonato que estamos a jogar:", jornadas_disponiveis)
            
            if st.button("🔥 Calcular Resultados e Atualizar Tabela", type="primary"):
                st.markdown("---")
                jogos_jornada = df_cal[df_cal['Jornada_Camp'] == jornada_selecionada]
                resultados = []
                
                # Dicionário para guardar os pontos ganhos nesta jornada
                pontos_ganhos = {}
                
                for _, row in jogos_jornada.iterrows():
                    casa = row['Equipa Casa']
                    fora = row['Equipa Fora']
                    
                    try:
                        pts_casa = df[df['Equipa'] == casa]['Pts Ronda'].values[0]
                        pts_fora = df[df['Equipa'] == fora]['Pts Ronda'].values[0]
                        extra_casa = df[df['Equipa'] == casa]['Pts Extra'].values[0]
                        extra_fora = df[df['Equipa'] == fora]['Pts Extra'].values[0]
                        
                        # Vitória (2), Empate (1), Derrota (0)
                        if pts_casa > pts_fora:
                            res_casa, res_fora = 2, 0
                        elif pts_casa < pts_fora:
                            res_casa, res_fora = 0, 2
                        else:
                            res_casa, res_fora = 1, 1
                            
                        # Somar com os pontos extra
                        total_casa = res_casa + extra_casa
                        total_fora = res_fora + extra_fora
                        
                        pontos_ganhos[casa] = total_casa
                        pontos_ganhos[fora] = total_fora
                        
                        resultados.append({
                            "Equipa Casa": casa, 
                            "Pts (Liga)": pts_casa, 
                            "Bónus": extra_casa,
                            "🏆 Pts Ganho": total_casa,
                            "VS": "⚔️",
                            "🏆 Pts Ganho ": total_fora, 
                            "Bónus ": extra_fora,
                            "Pts (Liga) ": pts_fora, 
                            "Equipa Fora": fora
                        })
                    except Exception as e:
                        st.error(f"⚠️ Erro ao encontrar equipas. Confirma se os nomes '{casa}' e '{fora}' no calendario.csv estão iguais aos da Liga Record.")
                
                if resultados:
                    st.dataframe(pd.DataFrame(resultados), hide_index=True, use_container_width=True)
                    st.success("Resultados processados! Vai à Tab '2. Classificação Campeonato' ver a tabela atualizada.")
                    
                    # Atualizar Histórico na memória
                    df_novo_hist = df_hist.copy()
                    for equipa, pts in pontos_ganhos.items():
                        if equipa in df_novo_hist['Equipa'].values:
                            df_novo_hist.loc[df_novo_hist['Equipa'] == equipa, 'Pts_Campeonato'] += pts
                            df_novo_hist.loc[df_novo_hist['Equipa'] == equip
