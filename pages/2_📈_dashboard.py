import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials

# Configurações e credenciais (mantenha essas informações seguras)
GOOGLE_PROJECT_ID = "atualizardados"
GOOGLE_PRIVATE_KEY_ID = "16c09e59f7872364ef46d71f09a2fe614438599f"
GOOGLE_PRIVATE_KEY = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
GOOGLE_CLIENT_EMAIL = "atualizar-dados@atualizardados.iam.gserviceaccount.com"
GOOGLE_CLIENT_ID = "105127364991999381484"
GOOGLE_CLIENT_CERT_URL = "https://www.googleapis.com/robot/v1/metadata/x509/atualizar-dados%40atualizardados.iam.gserviceaccount.com"

@st.cache_resource
def connect_to_gsheet(sheet_name):
    credentials_info = {
        "type": "service_account",
        "project_id": GOOGLE_PROJECT_ID,
        "private_key_id": GOOGLE_PRIVATE_KEY_ID,
        "private_key": GOOGLE_PRIVATE_KEY,
        "client_email": GOOGLE_CLIENT_EMAIL,
        "client_id": GOOGLE_CLIENT_ID,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": GOOGLE_CLIENT_CERT_URL,
    }
    credentials = Credentials.from_service_account_info(credentials_info, scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    client = gspread.authorize(credentials)

    try:
        sheet = client.open(sheet_name).sheet1
        return sheet
    except Exception as e:
        st.error(f"Erro ao acessar a planilha: {e}")
        return None

def get_sheet_data(sheet):
    return sheet.get_all_records()

def process_data(data):
    if not data:
        return None
    df = pd.DataFrame(data)
    if df.empty:
        return None
    df['Data'] = pd.to_datetime(df['Data'])
    df['Valor'] = pd.to_numeric(df['Valor'])
    df['Quantidade'] = pd.to_numeric(df['Quantidade'])
    return df

def create_dashboard(df):
    gastos_por_mes = df.groupby(df['Data'].dt.to_period('M'))['Valor'].sum().reset_index()
    gastos_por_mes['Data'] = gastos_por_mes['Data'].dt.to_timestamp()
    fig1 = px.line(gastos_por_mes, x='Data', y='Valor', title='Gastos por Mês')
    fig1.update_layout(xaxis_title='Mês', yaxis_title='Valor Total (R$)')

    def create_pie_chart(data, month):
        gastos_por_servico = data[data['Data'].dt.to_period('M') == month].groupby('Tipo de Serviço')['Valor'].sum().reset_index()
        return px.pie(gastos_por_servico, values='Valor', names='Tipo de Serviço', title=f'Gastos por Tipo de Serviço - {month}')

    def create_bar_chart(data, month):
        gastos_por_carro = data[data['Data'].dt.to_period('M') == month].groupby('Placa')['Valor'].sum().reset_index()
        return px.bar(gastos_por_carro, x='Placa', y='Valor', title=f'Gastos por Carro - {month}')

    fig4 = px.box(df, y='Valor', title='Distribuição dos Gastos')
    fig4.update_layout(yaxis_title='Valor (R$)')

    return fig1, create_pie_chart, create_bar_chart, fig4

def show_dashboard():
    st.title('Dashboard de Gastos com Veículos')

    sheet = connect_to_gsheet('Controle_Frota')
    if sheet:
        data = get_sheet_data(sheet)
        df = process_data(data)

        if df is None or df.empty:
            st.warning("Não há dados disponíveis na planilha. Por favor, verifique se a planilha contém informações.")
            return

        num_notas = df['Nota'].nunique()

        fig1, create_pie_chart, create_bar_chart, fig4 = create_dashboard(df)

        st.plotly_chart(fig1, use_container_width=True)

        months = df['Data'].dt.to_period('M').unique()
        selected_month = st.selectbox('Selecione o mês para os gráficos de pizza e barras', options=months)

        fig2 = create_pie_chart(df, selected_month)
        st.plotly_chart(fig2, use_container_width=True)

        fig3 = create_bar_chart(df, selected_month)
        st.plotly_chart(fig3, use_container_width=True)

        st.plotly_chart(fig4, use_container_width=True)

        st.subheader('Estatísticas Gerais')
        col1, col2, col3 = st.columns(3)
        with col1:
            total_gasto = (df['Valor'] * df['Quantidade']).sum()
            st.metric("Total gasto", f"R$ {total_gasto:.2f}")
        with col2:
            st.metric("Número de notas", f"{num_notas}")
        with col3:
            gasto_medio = total_gasto / num_notas if num_notas > 0 else 0
            st.metric("Gasto médio por nota", f"R$ {gasto_medio:.2f}")

        st.subheader('Top 5 Notas Mais Caras')
        top_5_notas = df.groupby('Nota').agg({'Valor': 'sum'}).nlargest(5, 'Valor').reset_index()
        st.table(top_5_notas)

        st.subheader('Filtros')
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_car = st.selectbox('Selecione um veículo', options=['Todos'] + list(df['Placa'].unique()))
        with col2:
            selected_service = st.selectbox('Selecione um tipo de serviço', options=['Todos'] + list(df['Tipo de Serviço'].unique()))
        with col3:
            selected_nota = st.selectbox('Selecione uma nota', options=['Todas'] + list(df['Nota'].unique()))

        filtered_df = df
        if selected_car != 'Todos':
            filtered_df = filtered_df[filtered_df['Placa'] == selected_car]
        if selected_service != 'Todos':
            filtered_df = filtered_df[filtered_df['Tipo de Serviço'] == selected_service]
        if selected_nota != 'Todas':
            filtered_df = filtered_df[filtered_df['Nota'] == selected_nota]

        st.subheader('Dados Filtrados')
        st.dataframe(filtered_df)

        # Adicionar visualizações específicas para a nota selecionada
        if selected_nota != 'Todas':
            st.subheader(f'Detalhes da Nota {selected_nota}')
            nota_df = df[df['Nota'] == selected_nota]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Valor Total", f"R$ {nota_df['Valor'].sum():.2f}")
            with col2:
                st.metric("Quantidade de Itens", f"{nota_df['Quantidade'].sum()}")
            with col3:
                st.metric("Data", nota_df['Data'].iloc[0].strftime('%d/%m/%Y'))

            # Gráfico de barras para itens da nota
            fig_nota = px.bar(nota_df, x='Tipo de Serviço', y='Valor', title=f'Itens da Nota {selected_nota}')
            st.plotly_chart(fig_nota, use_container_width=True)

            # Tabela detalhada dos itens da nota
            st.subheader(f'Itens da Nota {selected_nota}')
            st.table(nota_df[['Tipo de Serviço', 'Quantidade', 'Valor']])

    else:
        st.error('Não foi possível conectar à planilha.')

if __name__ == "__main__":
    show_dashboard()