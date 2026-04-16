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
    df = pd.read_csv(uploaded_file, skiprows=4)
    df['Equipa'] = df['Equipa'].str.strip()
    df['Pts Extra'] = df['Pts Ronda'].apply(calcular_pontos_extra)
    
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
                            "Pts": pts_casa, 
                            "Bónus": extra_casa,
                            "🏆 Pts Camp": total_casa,
                            "VS": "⚔️",
                            "🏆 Pts Camp ": total_fora, 
                            "Bónus ": extra_fora,
                            "Pts ": pts_fora, 
                            "Equipa Fora": fora
                        })
                    except Exception as e:
                        st.error(f"⚠️ Erro ao encontrar equipas. Confirma se os nomes no calendario.csv estão iguais aos da Liga Record. Erro: {e}")
                
                if resultados:
                    st.dataframe(pd.DataFrame(resultados), hide_index=True, use_container_width=True)
                    st.success("Resultados processados! Vai à Tab '2. Classificação Campeonato' ver a tabela atualizada.")
                    
                    # Atualizar Histórico na memória
                    df_novo_hist = df_hist.copy()
                    for equipa, pts in pontos_ganhos.items():
                        if equipa in df_novo_hist['Equipa'].values:
                            df_novo_hist.loc[df_novo_hist['Equipa'] == equipa, 'Pts_Campeonato'] += pts
                            df_novo_hist.loc[df_novo_hist['Equipa'] == equipa, 'Jogos'] += 1
                    
                    # Guardar em State para a Tab 2 usar
                    st.session_state['novo_hist'] = df_novo_hist
                    st.session_state['calculo_feito'] = True
                    
        else:
            st.warning("⚠️ Faltam os ficheiros 'calendario.csv' e 'historico_campeonato.csv' no GitHub.")

    with tab2:
        st.markdown("### 🏆 Classificação do Campeonato (H2H)")
        
        if 'calculo_feito' in st.session_state and st.session_state['calculo_feito']:
            df_atualizado = st.session_state['novo_hist'].sort_values(by="Pts_Campeonato", ascending=False).reset_index(drop=True)
            df_atualizado.index += 1
            st.dataframe(df_atualizado, use_container_width=True)
            
            st.markdown("---")
            st.info("⬇️ **Passo Final da Semana:** Faz download deste ficheiro atualizado e arrasta-o para o teu GitHub (substituindo o antigo) para guardares estes resultados para a próxima jornada!")
            
            # Botão de Download do novo histórico
            csv = df_atualizado.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descarregar historico_campeonato.csv atualizado",
                data=csv,
                file_name='historico_campeonato.csv',
                mime='text/csv',
            )
        else:
            st.write("Calcula os resultados na Tab 1 para veres a classificação atualizada.")
            if os.path.exists("historico_campeonato.csv"):
                st.write("Classificação Atual (Antes de calcular a jornada):")
                df_hist_view = pd.read_csv("historico_campeonato.csv").sort_values(by="Pts_Campeonato", ascending=False).reset_index(drop=True)
                df_hist_view.index += 1
                st.dataframe(df_hist_view)

    with tab3:
        st.markdown("### Classificação Geral (Liga Record)")
        df_geral = df.sort_values(by="Pts Total", ascending=False).reset_index(drop=True)
        df_geral.index += 1
        st.dataframe(df_geral[['Equipa', 'Treinador', 'Pts Ronda', 'Pts Extra', 'Pts Total']], use_container_width=True)

    with tab4:
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
    st.info("👋 Bem-vindo ao painel da Liga! À espera do upload do ficheiro CSV da Ronda...")
