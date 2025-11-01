import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import timedelta
import openai
from dotenv import load_dotenv
import os

# ----------------------------
# 🔹 Leitura e limpeza de dados
# ----------------------------
data = pd.read_csv(r"C:\Users\joaof\Desktop\Dados-Covid-main\covid_19_data.csv")
data.dropna(inplace=True)
data.drop('SNo', axis = 1, inplace = True)
data.loc[data['Province/State'].isna() == True] == "Estado não informado"
data['ObservationDate'] = pd.to_datetime(data['ObservationDate'])
data.set_index('ObservationDate', inplace=True)

# # ----------------------------
# # 🔹 Carregar estilo
# # ----------------------------
def carregar_css(caminho_arquivo):
    with open(caminho_arquivo) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

carregar_css("estilo.css")

# # ----------------------------
# # 🔹 CHATBOT
# # ----------------------------
load_dotenv()
client = os.getenv(key="OPENAI_API_KEY")

def chatbot(mensagem, lista_dados=[]):
    lista_dados.append(
        {"role": "system", "content": f"Você é um assistente que ajuda a analisar exclusivamente dados de COVID-19 do seguinte dataset: {data}."}
    )
    lista_dados.append(
        {"role": "user", "content": mensagem}
    )
    resposta = openai.chat.completions.create(
        model = "gpt-4.1-nano",
        messages = lista_dados
    )
   
    return resposta.choices[0].message.content
    

def pergunta(pergunta):
        if pergunta and pergunta.lower() != 'sair':
            resposta = chatbot(pergunta)
            return st.sidebar.markdown(f"**Chatbot:** {resposta}")
            

# # ----------------------------
# # 🔹 Controle de telas
# # ----------------------------

if "tela" not in st.session_state:
    st.session_state.tela = "inicial"  # pode ser "inicial" ou "analises"

# # ----------------------------
# # 🔹 Tela de Análises
# # ----------------------------
def tela_analises():
    st.markdown("""
        <style>
        .dashboard-button {
            position: fixed;
            top: 60px;
            left: 20px;
            z-index: 9999;
            background-color: #0d6efd;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 18px;
            font-size: 16px;
            cursor: pointer;
            transition: 0.2s;
        }
        .dashboard-button:hover {
            background-color: #084298;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <form action="#" method="get">
            <button class="dashboard-button" name="dashboard" type="submit">Dashboard</button>
        </form>
    """, unsafe_allow_html=True)

    # Detecta clique no botão
    if "dashboard" in st.query_params:
        st.session_state.tela = "inicial"
        st.query_params.clear()

    # -------------------- CONTEÚDO DA TELA --------------------
    st.title("📈 Análises & Estatísticas")
    st.markdown("---")
    # -------------------- PREPARAÇÃO --------------------
    data['Year'] = data.index.year
    data['YearShort'] = data['Year'].astype(str).str[-2:]  # Últimos 2 dígitos do ano
    data['Month'] = data.index.month


    st.header("Estatisticas Gerais do Ano")

    confirmados_ano = data.groupby('YearShort')['Confirmed'].sum().reset_index()
    fig1 = px.bar(confirmados_ano, x='YearShort', y='Confirmed',
                  color='Confirmed', color_continuous_scale='Blues',
                  title='Casos Confirmados por Ano')
    st.plotly_chart(fig1, use_container_width=True)
    st.subheader("O fato do gráfico ir acima de 8 milhoes, sabendo que esse é o tanto de pessoas no mundo, indica uma repetição de dados que pode ser justificado por pessoas, pessoas que se curaram e depois pegaram denovo")

    mortes_curados_ano = data.groupby('YearShort')[['Deaths', 'Recovered']].sum().reset_index()
    fig2 = px.bar(mortes_curados_ano, x='YearShort', y=['Deaths', 'Recovered'],
                  barmode='group', title='Mortes e Curados por Ano',
                  color_discrete_map={'Deaths': 'red', 'Recovered': 'green'})
    st.plotly_chart(fig2, use_container_width=True)
    st.subheader("O fato de o número de curados ser muito superior ao número de morto indica que o virús tem uma baixa taxa de mortalidade")

    st.header("Estatisticas Gerais dos meses")

    confirmados_mes = data.groupby(['YearShort', 'Month'])['Confirmed'].sum().reset_index()
    confirmados_mes['Label'] = confirmados_mes['Month'].astype(str) + '/' + confirmados_mes['YearShort']
    fig3 = px.bar(confirmados_mes, x='Label', y='Confirmed',
                  color='Confirmed', color_continuous_scale='Blues',
                  title='Casos Confirmados por Mês')
    st.plotly_chart(fig3, use_container_width=True)
    st.subheader("Esse gráfico demonstra que a deciminação do virus foi progessiva, tendo um crescimento quase constante")

    mortes_curados_mes = data.groupby(['YearShort', 'Month'])[['Deaths', 'Recovered']].sum().reset_index()
    mortes_curados_mes['Label'] = mortes_curados_mes['Month'].astype(str) + '/' + mortes_curados_mes['YearShort']
    fig4 = px.bar(mortes_curados_mes, x='Label', y=['Deaths', 'Recovered'],
                  barmode='group', title='Mortes e Curados por Mês',
                  color_discrete_map={'Deaths': 'red', 'Recovered': 'green'})
    st.plotly_chart(fig4, use_container_width=True)
    st.subheader("Esse gráfico mostra que a quantidade de mortes e curados também aumento progressivamente")

    media_confirmados_mes = data.groupby(['YearShort', 'Month'])['Confirmed'].mean().reset_index()
    media_confirmados_mes['Label'] = media_confirmados_mes['Month'].astype(str) + '/' + media_confirmados_mes['YearShort']
    fig5 = px.bar(media_confirmados_mes, x='Label', y='Confirmed',
                  color='Confirmed', color_continuous_scale='Blues',
                  title='Média de Casos Confirmados por Mês')
    st.plotly_chart(fig5, use_container_width=True)
    st.subheader("Esse gráfico demonstra que durante o período analisado a quantidade de casos por mês só aumentou")

    media_mortes_curados_mes = data.groupby(['YearShort', 'Month'])[['Deaths', 'Recovered']].mean().reset_index()
    media_mortes_curados_mes['Label'] = media_mortes_curados_mes['Month'].astype(str) + '/' + media_mortes_curados_mes['YearShort']
    fig6 = px.bar(media_mortes_curados_mes, x='Label', y=['Deaths', 'Recovered'],
                  barmode='group', title='Média de Mortes e Curados por Mês',
                  color_discrete_map={'Deaths': 'red', 'Recovered': 'green'})
    st.plotly_chart(fig6, use_container_width=True)
    st.subheader("Esse gráfico mostra que o números de curados e mortos ao longo dos meses em média só aumentou")

    max_confirmados_mes = data.groupby(['YearShort', 'Month'])['Confirmed'].max().reset_index()
    max_confirmados_mes['Label'] = max_confirmados_mes['Month'].astype(str) + '/' + max_confirmados_mes['YearShort']
    fig7 = px.bar(max_confirmados_mes, x='Label', y='Confirmed',
                  color='Confirmed', color_continuous_scale='Blues',
                  title='Máxima de Casos Confirmados por Mês')
    st.plotly_chart(fig7, use_container_width=True)
    st.subheader("Outro gráfico que mostra o crescimento progessivo dos casos de Covid-19")

    max_mortes_curados_mes = data.groupby(['YearShort', 'Month'])[['Deaths', 'Recovered']].max().reset_index()
    max_mortes_curados_mes['Label'] = max_mortes_curados_mes['Month'].astype(str) + '/' + max_mortes_curados_mes['YearShort']
    fig8 = px.bar(max_mortes_curados_mes, x='Label', y=['Deaths', 'Recovered'],
                  barmode='group', title='Máxima de Mortes e Curados por Mês',
                  color_discrete_map={'Deaths': 'red', 'Recovered': 'green'})
    st.plotly_chart(fig8, use_container_width=True)
    st.subheader("O fato desse gráfico ter uma alta e logo em seguida uma baixa de curados, mostrar o impacto incial das vacinas tendo aumentado o número de curados e em seguida reduzindo bruscamente o que pode indicar uma melhorar e espotânea, tendo um redução logo em seguida, o que pode indicar casos de pessoas que pegaram covid-19 antes de tomar a vacina ou que os efeitos dela demoram para fazer efeito ou pessoas que pegaram covid-19 novamente")


    st.header("Gráficos por País")
    st.subheader("Gráficos de casos confirmados")

    top10_paises_total = data.groupby('Country/Region')['Confirmed'].sum().nlargest(10).reset_index()
    fig9 = px.bar(top10_paises_total, x='Country/Region', y='Confirmed',
                  color='Confirmed', color_continuous_scale='Blues', title= "Top 10 Países com Maior Número de Casos Confirmados")
    st.plotly_chart(fig9, use_container_width=True)
    st.subheader("Esse gráfico ajudar a enteder quais países temos mais dados, no caso a grande maioria vem dos estados unidos")

    top10_paises_media = data.groupby('Country/Region')['Confirmed'].mean().nlargest(10).reset_index()
    fig10 = px.bar(top10_paises_media, x='Country/Region', y='Confirmed',
                   color='Confirmed', color_continuous_scale='Blues', title= "Top 10 Países com Maior Média de Casos Confirmados")
    st.plotly_chart(fig10, use_container_width=True)
    st.subheader("Esse gráfico mostra que apersar da maior parte dos dados dados virem do Estados unidos o Brasil e India foram os países que teveram a maior média de casos sendo dois países com saúde básica precaria além disso a India tem a segunda maior população mundial o que contribuir para sua posição no rank")

    top10_paises_max = data.groupby('Country/Region')['Confirmed'].max().nlargest(10).reset_index()
    fig11 = px.bar(top10_paises_max, x='Country/Region', y='Confirmed',
                   color='Confirmed', color_continuous_scale='Blues', title= "Top 10 Países com Maior Máxima de Casos Confirmados")
    st.plotly_chart(fig11, use_container_width=True)
    st.subheader("O fato da India ser o top 1 desse rank é devido do tamanho expressivo de sua população")
    
    st.subheader("Gráficos de mortes")
    top10_mortes_paises_total = data.groupby('Country/Region')['Deaths'].sum().nlargest(10).reset_index()
    fig12 = px.bar(top10_mortes_paises_total, x='Country/Region', y='Deaths',
                  color='Deaths', color_continuous_scale='Reds', title= "Top 10 Países com Maior Número de Mortes")
    st.plotly_chart(fig12, use_container_width=True)
    st.subheader("Algo curioso acontece nesse rank o Brasil tem uma quantidade de casos menor que a india, mas ainda sim, ele se posiciona como 2 no rank o que pode indicar um sistema de saúde inferior")

    top10_mortes_paises_media = data.groupby('Country/Region')['Deaths'].mean().nlargest(10).reset_index()
    fig13 = px.bar(top10_mortes_paises_media, x='Country/Region', y='Deaths',
                   color='Deaths', color_continuous_scale='Reds', title= "Top 10 Países com Maior Média de Mortes")
    st.plotly_chart(fig13, use_container_width=True)
    st.subheader("Outra vez o Brasil como primeiro no rank o que indicar uma taxa de mortes maior, podendo ser causada por diversos fatores, como demorar no atendimento médico ou super lotação em leitos hospitalares")
  
    top10_mortes_paises_max = data.groupby('Country/Region')['Deaths'].max().nlargest(10).reset_index()
    fig14 = px.bar(top10_mortes_paises_max, x='Country/Region', y='Deaths',
                   color='Deaths', color_continuous_scale='Reds', title= "Top 10 Países com Maior Máxima de Mortes")
    st.plotly_chart(fig14, use_container_width=True)
    st.subheader("Curiosamente o Reino Unido assume o topo do rank de mortes, mesmo no total de dados sendo a 4 menor, isso pode indicar uma alta mortalidade em um certo periodo, vale resaltar que no rank anterior a Inglaterra tava na 3 posição da Nédia outro fator que aponta para uma taxa de mortalidade alta")
    
    st.subheader("#Gráficos de Curados")
    top10_curados_paises_total = data.groupby('Country/Region')['Recovered'].sum().nlargest(10).reset_index()
    fig15 = px.bar(top10_curados_paises_total, x='Country/Region', y='Recovered',
                  color='Recovered', color_continuous_scale='Greens', title= "Top 10 Países com Maior Número de Curados")
    st.plotly_chart(fig15, use_container_width=True)
    st.subheader("Esse gráfico mostra que apersar do número de mortos mais elevado em relação aos outros da India e do Brasil também foram países que muitos se curaram naturalmente ou por causa da vacina, possivelmente pelo contato mais proximo do virús")

    top10_curados_paises_media = data.groupby('Country/Region')['Recovered'].mean().nlargest(10).reset_index()
    fig16 = px.bar(top10_curados_paises_media, x='Country/Region', y='Recovered',
                   color='Recovered', color_continuous_scale='Greens', title= "Top 10 Países com Maior Média de Curados")
    st.plotly_chart(fig16, use_container_width=True)
    st.subheader("Esse gráfico demonstra o mesmo que o gráfico anterior")
    
    st.subheader("Top 10 Países com Maior Máxima de Curados")
    top10_curados_paises_max = data.groupby('Country/Region')['Recovered'].max().nlargest(10).reset_index()
    fig17 = px.bar(top10_curados_paises_max, x='Country/Region', y='Recovered',
                   color='Recovered', color_continuous_scale='Greens', title= "Top 10 Países com Maior Máxima de Casos Confirmados")
    st.plotly_chart(fig17, use_container_width=True)
    st.subheader("O Estados Unidos surge de forma insperadamente no top 1 o que combinado com a falta dele no gráfico anterior e uma posição no top 4 muito inferior aos países superiores a ele no rank pode indicar que essa maxima aconteceu durante a época da vacinação e durante outros momentos tendo uma taxa de curados bem ineferiores")
    

    st.header("Gráficos por Estados")
    st.subheader("Gráficos de casos confirmados")

    top10_estados_total = data.groupby(['Province/State', 'Country/Region'])['Confirmed'].sum().nlargest(10).reset_index()
    top10_estados_total['Local'] = top10_estados_total['Province/State'].astype(str) + ' (' + top10_estados_total['Country/Region'] + ')'
    fig18 = px.bar(top10_estados_total, x='Local', y='Confirmed',
                   color='Confirmed', color_continuous_scale='Blues', title= "Top 10 Estados com Maior Número de Casos Confirmados")
    st.plotly_chart(fig18, use_container_width=True)
    st.subheader("Esse gráfico mostra o motivo do Estados Unidos ser o país com mais dados tendo 5 estados no top 10 ")

    top10_estados_media = data.groupby(['Province/State', 'Country/Region'])['Confirmed'].mean().nlargest(10).reset_index()
    top10_estados_media['Local'] = top10_estados_media['Province/State'].astype(str) + ' (' + top10_estados_media['Country/Region'] + ')'
    fig19 = px.bar(top10_estados_media, x='Local', y='Confirmed',
                   color='Confirmed', color_continuous_scale='Blues', title= "Top 10 Estados com Maior Média de Casos Confirmados")
    st.plotly_chart(fig19, use_container_width=True)
    st.subheader("Outra vez a India no top 1 possívelmente por causa da sua grande população")

    top10_estados_max = data.groupby(['Province/State', 'Country/Region'])['Confirmed'].max().nlargest(10).reset_index()
    top10_estados_max['Local'] = top10_estados_max['Province/State'].astype(str) + ' (' + top10_estados_max['Country/Region'] + ')'
    fig20 = px.bar(top10_estados_max, x='Local', y='Confirmed',
                   color='Confirmed', color_continuous_scale='Blues', title= "Top 10 Estados com Maior Máxima de Casos Confirmados")
    st.plotly_chart(fig20, use_container_width=True)
    st.subheader("Outro gráfico que a India continua sendo o top 1, justamente por causa de seu tamanho populacional")

    st.subheader("Gráficos de Mortes")
    top10_mortes_estados_total = data.groupby(['Province/State', 'Country/Region'])['Deaths'].sum().nlargest(10).reset_index()
    top10_mortes_estados_total['Local'] = top10_mortes_estados_total['Province/State'].astype(str) + ' (' + top10_mortes_estados_total['Country/Region'] + ')'
    fig21 = px.bar(top10_mortes_estados_total, x='Local', y='Deaths',
                   color='Deaths', color_continuous_scale='Reds', title= "Top 10 Estados com Maior Número de Mortes")
    st.plotly_chart(fig21, use_container_width=True)
    st.subheader("Curiosamente a Inglaterra aparece como top 1 nesse gráfico, mesmo que o Reino Unido não tenha tido tanta relevancia na maioria dos gráficos sobre morte em relação a países o que indica que Irlandia do norte, País de Gales e Escócia tenham tido em geral um número de mortos bem inferior o que leva para baixo a posição do reino unido naqueles rank, o que também pode explicar o insperado surgimento do reino unido no top 1 do gráfico de maximas de mortes entre os países")

    top10_mortes_estados_media = data.groupby(['Province/State', 'Country/Region'])['Deaths'].mean().nlargest(10).reset_index()
    top10_mortes_estados_media['Local'] = top10_mortes_estados_media['Province/State'].astype(str) + ' (' + top10_mortes_estados_media['Country/Region'] + ')'
    fig22 = px.bar(top10_mortes_estados_media, x='Local', y='Deaths',
                   color='Deaths', color_continuous_scale='Reds', title= "Top 10 Estados com Maior Média de Mortes")
    st.plotly_chart(fig22, use_container_width=True)
    st.subheader("Outro gráfico que mostra a alta taxa de morte da Inglaterra em relação aos estados, algo esperado considerando que a inglaterra é um país diferente de outros nesse rank que são estados, ou seja geralmente uma extenção teritorrial geralmente menor e menor população, em relação a área analisada")

    top10_mortes_estados_max = data.groupby(['Province/State', 'Country/Region'])['Deaths'].max().nlargest(10).reset_index()
    top10_mortes_estados_max['Local'] = top10_mortes_estados_max['Province/State'].astype(str) + ' (' + top10_mortes_estados_max['Country/Region'] + ')'
    fig23 = px.bar(top10_mortes_estados_max, x='Local', y='Deaths',
                   color='Deaths', color_continuous_scale='Reds', title= "Top 10 Estados com Maior Máxima de Mortes")
    st.plotly_chart(fig23, use_container_width=True)
    st.subheader("Outra vez a Inglaterra o ocupando o top 1, mas um fato enteressante a se nota nesse e nos ultimos dois gráficos é a constante aparição de varíos estados dos Estados Unidos e a constante aparição de São Paulo e Rio de Janeiro nos ranks")

    st.subheader("Gráficos de Curados")
    top10_curados_estados_total = data.groupby(['Province/State', 'Country/Region'])['Recovered'].sum().nlargest(10).reset_index()
    top10_curados_estados_total['Local'] = top10_curados_estados_total['Province/State'].astype(str) + ' (' + top10_curados_estados_total['Country/Region'] + ')'
    fig24 = px.bar(top10_curados_estados_total, x='Local', y='Recovered',
                   color='Recovered', color_continuous_scale='Greens', title= "Top 10 Estados com Maior Número de Curados")
    st.plotly_chart(fig24, use_container_width=True)
    st.subheader("Esse e os próximos dados, mostram que apersar da eliminação de dados nulos ainda existem dados com classificalções erronhas que precissam ser tratados, agora sobre o gráfico Maharashtra e São Paulo continuam no top 3, além de varias outros outros estados Indianos presentes no top, que demonstram o um pouco do motivo da India e o Brasil está respectivamente no top 1 e 2")

    top10_curados_estados_media = data.groupby(['Province/State', 'Country/Region'])['Recovered'].mean().nlargest(10).reset_index()
    top10_curados_estados_media['Local'] = top10_curados_estados_media['Province/State'].astype(str) + ' (' + top10_curados_estados_media['Country/Region'] + ')'
    fig25 = px.bar(top10_curados_estados_media, x='Local', y='Recovered',
                   color='Recovered', color_continuous_scale='Greens', title= "Top 10 Estados com Maior Média de Curados")
    st.plotly_chart(fig25, use_container_width=True)
    st.subheader("Esse gráfico reperte o quase totalmente o rank anterior com poucas diferenças")

    top10_curados_estados_max = data.groupby(['Province/State', 'Country/Region'])['Recovered'].max().nlargest(10).reset_index()
    top10_curados_estados_max['Local'] = top10_curados_estados_max['Province/State'].astype(str) + ' (' + top10_curados_estados_max['Country/Region'] + ')'
    fig26 = px.bar(top10_curados_estados_max, x='Local', y='Recovered',
                   color='Recovered', color_continuous_scale='Greens', title= "Top 10 Estados com Maior Máxima de Curados")
    st.plotly_chart(fig26, use_container_width=True)
    st.subheader("Nesse gráfico o valor Recovered assume o top um, possívelmente isso acontece por boa parte dos casos de curados nos estados unidos acabar sendo classificado erronhamente nesse valor")

    
chat_input = st.sidebar.text_input("Tire sua dúvida aqui (digite 'sair' para encerrar):", key="input_chatbot")


# # ----------------------------
# # 🔹 Tela Inicial (Dashboard principal)
# # ----------------------------
def tela_inicial():

    st.header("📊 Histórico de Casos de COVID-19")

    st.sidebar.header("Opções de Filtro")

    # Botão para mudar de tela
    if st.sidebar.button("Análises & Estatísticas"):
        st.session_state.tela = "analises"
        st.rerun()

    # Filtro de País
    paises = sorted(data['Country/Region'].dropna().unique())
    pais_selecionado = st.sidebar.selectbox("Selecione o País:", options=["Todos"] + list(paises))

    # Filtro de Estado
    if pais_selecionado != "Todos":
        estados = sorted(data[data['Country/Region'] == pais_selecionado]['Province/State'].dropna().unique())
    else:
        estados = sorted(data['Province/State'].dropna().unique())

    estado_selecionado = st.sidebar.selectbox("Selecione o Estado/Província:", options=["Todos"] + list(estados))

    # Filtro de tipo de dado
    lista_acoes = st.sidebar.multiselect(
        "O que você quer ver?",
        ["Confirmed", "Deaths", "Recovered"],
        default=["Confirmed", "Deaths", "Recovered"]
    )

    # Aplicar filtros
    dados_filtrados = data.copy()

    if pais_selecionado != "Todos":
        dados_filtrados = dados_filtrados[dados_filtrados["Country/Region"] == pais_selecionado]
    if estado_selecionado != "Todos":
        dados_filtrados = dados_filtrados[dados_filtrados["Province/State"] == estado_selecionado]

    inicial = dados_filtrados.index.min().date()
    final = dados_filtrados.index.max().date()
    intervalo_data = st.sidebar.slider(
        "Período de Análise",
        min_value=inicial,
        max_value=final,
        value=(inicial, final),
        step=timedelta(days=15)
    )

    dados_filtrados = dados_filtrados.loc[intervalo_data[0]:intervalo_data[1]]

          # Campo de pergunta para o chatbot



    # ======================= GRÁFICO E INFORMAÇÕES ===========================
    if not lista_acoes:
        st.warning("Selecione ao menos um tipo de dado para visualizar.")
    else:
        col1, col2 = st.columns([3, 1])  # gráfico maior, caixa menor
        with col1:
            fig = px.line(
                dados_filtrados,
                x=dados_filtrados.index,
                y=lista_acoes,
                title=f"Casos ao Longo do Tempo ({pais_selecionado} - {estado_selecionado})"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### 🧾 Informações do Dataset")
            st.markdown(f"**Total de Linhas:** {len(dados_filtrados)}")

            # Criar a caixa com borda e colunas dentro
            colunas_html = "<div style='border: 1px solid #ccc; border-radius: 8px; padding: 10px; background-color: #363636;'>"
            colunas_html += "<b>Colunas Presentes:</b><br>"
            for col in dados_filtrados.columns:
                colunas_html += f"▪️ {col}<br>"
            colunas_html += "</div>"

            st.markdown(colunas_html, unsafe_allow_html=True)

    # ======================= TABELA ===========================
    st.subheader("📋 Dados Filtrados")
    st.dataframe(dados_filtrados.reset_index(), use_container_width=True)



# ----------------------------
# 🔹 Exibir tela atual
# ----------------------------
if st.session_state.tela == "inicial":
    tela_inicial()
elif st.session_state.tela == "analises":
    tela_analises()

   
pergunta(chat_input)
