import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
import re

# Configurações e credenciais (mantenha essas informações seguras)
GOOGLE_PROJECT_ID = "atualizardados"
GOOGLE_PRIVATE_KEY_ID = "16c09e59f7872364ef46d71f09a2fe614438599f"
GOOGLE_PRIVATE_KEY = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCUbF9NxrPa4bmJ\niHU/msZL+S6CDuAVfXyxODe2xtP5egm3FypjehmzzWYXSNLAMctgT95eNLU/r6aw\nE6apC1SCu3N14/wLU4RlLzOfKPokJOsWfsqWkv3DaCFZu3TI/ktUpwdC1yosRLao\npvyOkQgsmYeftPe+g2UHjWlm0VdztJHd2L5KQckEEyiWkJjmj0erq+VX/F8icpjg\neWn7Lb6/FgZ4MVLPX2rc0j0jeeUHaf5rKsmQLHq8nOrEoM9KysLsOtsoHk0YRXZp\nYmEBqIj+OW0FPGFCole8uFUsNwO1tA5CPM5ni2pws79hYMdf2X8b0ZxIUDX6X0bf\nJNo7TJWPAgMBAAECggEAQB2Si+AOuLpysjlK4PeEurQBRbiUT2Q+dbXhx2ibkDUK\nNlfg/Uj1CmlrtRpFxDWec9P8rLhbJZBE0uIiR/r3fmPobCBYtDHXSvh5dcM3T17N\nWRHbhPEpgvycD429VMgZFY/zwIl/E9F5EGDWT+XR4KZP4otDzD4pafpJ8lrzSq0p\nONaqkZc4tCTlZdd7CEFb8UTmsgDZMySeXIWOznp0F7z/TXpZ+nsnYbq1tKqn9Tgp\nraBBBGS+SpqMbo62Q8gJHPfu0Ig8ZNuJgUQwFa08frcnLozbm65xetiLGYlTS5y5\nS4eyHFBVdfoqiyvGjXCJsBuXDXrLMSGWSb1OA+OJnQKBgQDGN4ECbhjnwHgR8n5v\nVY1zoi+M5W0HR3nJ/pUi8iOWp/mjaMIvf5NdJV6HLP4zIB0SFJmOV3dQLDPJ5V3j\nqrzN35Ase1S+zvoSITbyOuVXuWOzSlu35vXd9Pbw2po6sTPHsp5atiIhBMnKT3T3\nv/BC4INKtvd+RFlHDxQ2zsqxfQKBgQC/sOMqsCWV9Ww5kft8Fj78aTiQCHn7luan\ntWqf6h3AUN1zQXqZjKuo5uSgR6MXo2FsdJI6r8l+CHT2/rXQAlzdHkWwDLuxttwM\nEZwIRDPpRIx2pChhoKHKWgKLTh9oJkU6eSqTEhhVyyK5+BswB7pnEKdyBDTxkO7J\npjXnsrfQ+wKBgH3tnUSR9bimiqG8UZ8h1y/zhgoZZ98MBc/SsaT1+K4qIWszjsrm\nXhT7PMbcStLoQA/Qjo3j+6Uvr+dAlRmiyzhwJARehkSC8lS6TVIvIK1O1ox9XS/E\nx8cvbgMunnVTRvZEAF7Y/23CwQCK4mDTzCxwvnilLS9G9QE0Dz+SuStxAoGBAKAZ\nTKHKnJmycMFke3YX3mNSPjuN2NOYJOzNSFBnaJHG+C3a8lpscrKOpUR4kG6dtjCu\n67K4PsFUrtvbwF4KmyTSs8Fl4R18bCxoSLlevTyGVAqC8HcZggdPRfCzPuftjsRX\njodnBYwiLM7FuW9UBQsvjapceRuIwOcKOttZGM0hAoGAWCAHJAPL8IE99A5FsCy5\nEa3nSsZAwHWkAcVzX1Wm2goEQd4rAYDLVpmKTn51ABjZmPUW3rEdTc4S9cG/5TuQ\n+tIpGizoV8RzHlijgKG1Pe61s4fEzCDkN7RsnRrWm95o9WNFXM+5jAv3huWQqm22\nIviUvH8En6OsIke8O/ahTVA=\n-----END PRIVATE KEY-----\n"
GOOGLE_CLIENT_EMAIL = "atualizar-dados@atualizardados.iam.gserviceaccount.com"
GOOGLE_CLIENT_ID = "105127364991999381484"
GOOGLE_CLIENT_CERT_URL = "https://www.googleapis.com/robot/v1/metadata/x509/atualizar-dados%40atualizardados.iam.gserviceaccount.com"

import re
import pandas as pd
import plotly.express as px
import streamlit as st
from google.oauth2.service_account import Credentials
import gspread

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

def convert_to_float(value):
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        value = re.sub(r'[^\d,.]', '', value)
        value = value.replace(',', '.')
        if value.count('.') > 1:
            value = value.replace('.', '', value.count('.') - 1)
        try:
            return float(value)
        except ValueError:
            return None
    return None

def process_data(data):
    if not data:
        return None
    df = pd.DataFrame(data)
    if df.empty:
        return None

    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')

    df['Valor'] = df['Valor'].apply(convert_to_float)
    df['Quantidade'] = df['Quantidade'].apply(convert_to_float)

    df = df.dropna(subset=['Valor', 'Quantidade'])

    return df

def create_dashboard(df):
    gastos_por_mes = df.groupby(df['Data'].dt.to_period('M'))['Valor'].sum().reset_index()
    gastos_por_mes['Data'] = gastos_por_mes['Data'].dt.to_timestamp()
    fig1 = px.line(gastos_por_mes, x='Data', y='Valor', title='Gastos por Mês')
    fig1.update_layout(xaxis_title='Mês', yaxis_title='Valor Total (R$)')

    def create_pie_chart(data, period=None):
        if period:
            title = f'Gastos por Tipo de Serviço - {period}'
            filtered_data = data[data['Data'].dt.to_period('M') == period]
        else:
            title = 'Gastos por Tipo de Serviço - Todas as Datas'
            filtered_data = data
        gastos_por_servico = filtered_data.groupby('Tipo de Serviço')['Valor'].sum().reset_index()
        return px.pie(gastos_por_servico, values='Valor', names='Tipo de Serviço', title=title)

    def create_bar_chart(data, period=None):
        if period:
            title = f'Gastos por Carro - {period}'
            filtered_data = data[data['Data'].dt.to_period('M') == period]
        else:
            title = 'Gastos por Carro - Todas as Datas'
            filtered_data = data
        gastos_por_carro = filtered_data.groupby('Placa')['Valor'].sum().reset_index()
        return px.bar(gastos_por_carro, x='Placa', y='Valor', title=title)

    fig4 = px.box(df, y='Valor', title='Distribuição dos Gastos')
    fig4.update_layout(yaxis_title='Valor (R$)')

    return fig1, create_pie_chart, create_bar_chart, fig4

def update_sheet_values(sheet, cell_range, values):
    values_str = [[f"{value:.2f}".replace(',', '.') for value in row] for row in values]
    sheet.update(cell_range, values_str)

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

        st.subheader('Selecione o intervalo de datas')
        col1, col2, col3 = st.columns(3)
        with col1:
            min_date = df['Data'].min().date()
            max_date = df['Data'].max().date()
            start_date = st.date_input('Data inicial', min_date)
        with col2:
            end_date = st.date_input('Data final', max_date)
        with col3:
            all_dates = st.checkbox('Todas as datas', value=True)

        if all_dates:
            filtered_df = df
        else:
            filtered_df = df[(df['Data'].dt.date >= start_date) & (df['Data'].dt.date <= end_date)]

        fig1, create_pie_chart, create_bar_chart, fig4 = create_dashboard(filtered_df)

        st.plotly_chart(fig1, use_container_width=True)

        months = filtered_df['Data'].dt.to_period('M').unique()
        month_options = ['Todas as datas'] + list(months)
        selected_month = st.selectbox('Selecione o mês para os gráficos de pizza e barras', options=month_options)

        if selected_month == 'Todas as datas':
            fig2 = create_pie_chart(filtered_df)
            fig3 = create_bar_chart(filtered_df)
        else:
            fig2 = create_pie_chart(filtered_df, selected_month)
            fig3 = create_bar_chart(filtered_df, selected_month)

        st.plotly_chart(fig2, use_container_width=True)
        st.plotly_chart(fig3, use_container_width=True)

        st.plotly_chart(fig4, use_container_width=True)

        st.subheader('Estatísticas Gerais')
        col1, col2, col3 = st.columns(3)
        with col1:
            total_gasto = (filtered_df['Valor'] * filtered_df['Quantidade']).sum()
            st.metric("Total gasto", f"R$ {total_gasto:.2f}")
        with col2:
            num_notas = filtered_df['Nota'].nunique()
            st.metric("Número de notas", f"{num_notas}")
        with col3:
            gasto_medio = total_gasto / num_notas if num_notas > 0 else 0
            st.metric("Gasto médio por nota", f"R$ {gasto_medio:.2f}")

        st.subheader('Top 5 Notas Mais Caras')
        top_5_notas = filtered_df.groupby('Nota').agg({'Valor': 'sum'}).nlargest(5, 'Valor').reset_index()
        st.table(top_5_notas)

        st.subheader('Filtros')
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_car = st.selectbox('Selecione um veículo', options=['Todos'] + list(filtered_df['Placa'].unique()))
        with col2:
            selected_service = st.selectbox('Selecione um tipo de serviço', options=['Todos'] + list(filtered_df['Tipo de Serviço'].unique()))
        with col3:
            selected_nota = st.selectbox('Selecione uma nota', options=['Todas'] + list(filtered_df['Nota'].unique()))

        if selected_car != 'Todos':
            filtered_df = filtered_df[filtered_df['Placa'] == selected_car]
        if selected_service != 'Todos':
            filtered_df = filtered_df[filtered_df['Tipo de Serviço'] == selected_service]
        if selected_nota != 'Todas':
            filtered_df = filtered_df[filtered_df['Nota'] == selected_nota]

        st.subheader('Dados Filtrados')
        st.dataframe(filtered_df)

        if selected_nota != 'Todas':
            st.subheader(f'Detalhes da Nota {selected_nota}')
            nota_df = filtered_df[filtered_df['Nota'] == selected_nota]

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Valor Total", f"R$ {nota_df['Valor'].sum():.2f}")
            with col2:
                st.metric("Quantidade de Itens", f"{nota_df['Quantidade'].sum()}")
            with col3:
                st.metric("Data", nota_df['Data'].iloc[0].strftime('%d/%m/%Y'))

            fig_nota = px.bar(nota_df, x='Tipo de Serviço', y='Valor', title=f'Itens da Nota {selected_nota}')
            st.plotly_chart(fig_nota, use_container_width=True)

            st.subheader(f'Itens da Nota {selected_nota}')
            st.table(nota_df[['Tipo de Serviço', 'Quantidade', 'Valor']])

    else:
        st.error('Não foi possível conectar à planilha.')

if __name__ == "__main__":
    show_dashboard()
