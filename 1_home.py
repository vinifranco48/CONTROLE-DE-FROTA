import streamlit as st
import sqlite3
import pandas as pd
from google.oauth2.service_account import Credentials
import gspread
import os

# Defina suas credenciais do Google Sheets
GOOGLE_PROJECT_ID = "atualizardados"
GOOGLE_PRIVATE_KEY_ID = "16c09e59f7872364ef46d71f09a2fe614438599f"
GOOGLE_PRIVATE_KEY = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCUbF9NxrPa4bmJ\niHU/msZL+S6CDuAVfXyxODe2xtP5egm3FypjehmzzWYXSNLAMctgT95eNLU/r6aw\nE6apC1SCu3N14/wLU4RlLzOfKPokJOsWfsqWkv3DaCFZu3TI/ktUpwdC1yosRLao\npvyOkQgsmYeftPe+g2UHjWlm0VdztJHd2L5KQckEEyiWkJjmj0erq+VX/F8icpjg\neWn7Lb6/FgZ4MVLPX2rc0j0jeeUHaf5rKsmQLHq8nOrEoM9KysLsOtsoHk0YRXZp\nYmEBqIj+OW0FPGFCole8uFUsNwO1tA5CPM5ni2pws79hYMdf2X8b0ZxIUDX6X0bf\nJNo7TJWPAgMBAAECggEAQB2Si+AOuLpysjlK4PeEurQBRbiUT2Q+dbXhx2ibkDUK\nNlfg/Uj1CmlrtRpFxDWec9P8rLhbJZBE0uIiR/r3fmPobCBYtDHXSvh5dcM3T17N\nWRHbhPEpgvycD429VMgZFY/zwIl/E9F5EGDWT+XR4KZP4otDzD4pafpJ8lrzSq0p\nONaqkZc4tCTlZdd7CEFb8UTmsgDZMySeXIWOznp0F7z/TXpZ+nsnYbq1tKqn9Tgp\nraBBBGS+SpqMbo62Q8gJHPfu0Ig8ZNuJgUQwFa08frcnLozbm65xetiLGYlTS5y5\nS4eyHFBVdfoqiyvGjXCJsBuXDXrLMSGWSb1OA+OJnQKBgQDGN4ECbhjnwHgR8n5v\nVY1zoi+M5W0HR3nJ/pUi8iOWp/mjaMIvf5NdJV6HLP4zIB0SFJmOV3dQLDPJ5V3j\nqrzN35Ase1S+zvoSITbyOuVXuWOzSlu35vXd9Pbw2po6sTPHsp5atiIhBMnKT3T3\nv/BC4INKtvd+RFlHDxQ2zsqxfQKBgQC/sOMqsCWV9Ww5kft8Fj78aTiQCHn7luan\ntWqf6h3AUN1zQXqZjKuo5uSgR6MXo2FsdJI6r8l+CHT2/rXQAlzdHkWwDLuxttwM\nEZwIRDPpRIx2pChhoKHKWgKLTh9oJkU6eSqTEhhVyyK5+BswB7pnEKdyBDTxkO7J\npjXnsrfQ+wKBgH3tnUSR9bimiqG8UZ8h1y/zhgoZZ98MBc/SsaT1+K4qIWszjsrm\nXhT7PMbcStLoQA/Qjo3j+6Uvr+dAlRmiyzhwJARehkSC8lS6TVIvIK1O1ox9XS/E\nx8cvbgMunnVTRvZEAF7Y/23CwQCK4mDTzCxwvnilLS9G9QE0Dz+SuStxAoGBAKAZ\nTKHKnJmycMFke3YX3mNSPjuN2NOYJOzNSFBnaJHG+C3a8lpscrKOpUR4kG6dtjCu\n67K4PsFUrtvbwF4KmyTSs8Fl4R18bCxoSLlevTyGVAqC8HcZggdPRfCzPuftjsRX\njodnBYwiLM7FuW9UBQsvjapceRuIwOcKOttZGM0hAoGAWCAHJAPL8IE99A5FsCy5\nEa3nSsZAwHWkAcVzX1Wm2goEQd4rAYDLVpmKTn51ABjZmPUW3rEdTc4S9cG/5TuQ\n+tIpGizoV8RzHlijgKG1Pe61s4fEzCDkN7RsnRrWm95o9WNFXM+5jAv3huWQqm22\nIviUvH8En6OsIke8O/ahTVA=\n-----END PRIVATE KEY-----\n"
GOOGLE_CLIENT_EMAIL = "atualizar-dados@atualizardados.iam.gserviceaccount.com"
GOOGLE_CLIENT_ID = "105127364991999381484"
GOOGLE_CLIENT_CERT_URL = "https://www.googleapis.com/robot/v1/metadata/x509/atualizar-dados%40atualizardados.iam.gserviceaccount.com"

# Função para autenticar e conectar ao Google Sheets
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

# Função para criar cabeçalhos na planilha, se ainda não existirem
def criar_colunas(sheet):
    colunas = [
        'Data', 'Placa', 'Modelo', 'KM', 'Nota', 'Fornecedor','Tipo de Serviço', 'Item da Nota', 'Valor','Quantidade', 'Peça', 'Observações'
    ]
    existing_headers = sheet.row_values(1)
    if not existing_headers or set(colunas) != set(existing_headers):
        sheet.insert_row(colunas, 1)
        st.success('Cabeçalhos criados na planilha!')

# Criar conexão com o banco de dados SQLite
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Função para criar a tabela de notas no SQLite, se ainda não existir
def create_sqlite_table():
    c.execute('''CREATE TABLE IF NOT EXISTS notas
                 (data TEXT, placa TEXT, modelo TEXT, km INTEGER, nota TEXT, fornecedor TEXT, 
                  tipo_servico TEXT, peca TEXT, quantidade INTEGER, valor REAL, observacoes TEXT)''')
    conn.commit()
    
# Função para criar a tabela de carros no SQLite
def create_carros_table():
    c.execute('''CREATE TABLE IF NOT EXISTS carros
                 (placa TEXT PRIMARY KEY, modelo TEXT)''')
    conn.commit()

# Função para criar a tabela de fornecedores no SQLite
def create_fornecedores_table():
    c.execute('''CREATE TABLE IF NOT EXISTS fornecedores
                 (nome TEXT PRIMARY KEY)''')
    conn.commit()

# Função para adicionar carro no SQLite
def add_carro_sqlite(placa, modelo):
    c.execute("INSERT OR IGNORE INTO carros (placa, modelo) VALUES (?, ?)", (placa, modelo))
    conn.commit()

# Função para adicionar fornecedor no SQLite
def add_fornecedor_sqlite(nome):
    c.execute("INSERT OR IGNORE INTO fornecedores (nome) VALUES (?)", (nome,))
    conn.commit()

# Função para carregar carros do SQLite
def carregar_carros():
    c.execute("SELECT placa, modelo FROM carros")
    return [{'placa': row[0], 'modelo': row[1]} for row in c.fetchall()]

# Função para carregar fornecedores do SQLite
def carregar_fornecedores():
    c.execute("SELECT nome FROM fornecedores")
    return [row[0] for row in c.fetchall()]

# Função para adicionar novo registro à tabela de notas no SQLite
def add_record_sqlite(data, placa, modelo, km, nota, fornecedor, tipo_servico, peca, quantidade, valor, observacoes):
    c.execute("INSERT INTO notas (data, placa, modelo, km, nota, fornecedor, tipo_servico, peca, quantidade, valor,  observacoes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
              (data, placa, modelo, km, nota, fornecedor, tipo_servico, peca, quantidade, valor, observacoes))
    conn.commit()


# Inicializar dados em cache
if 'carros' not in st.session_state:
    st.session_state['carros'] = []
if 'fornecedores' not in st.session_state:
    st.session_state['fornecedores'] = []
if 'pecas' not in st.session_state:
    st.session_state['pecas'] = ["Adesivos", "Aerofólio", "Airbag", "Alavanca de câmbio", "Alternador", "Amortecedor de direção", "Amortecedor dianteiro", "Amortecedor traseiro", "Amortecedores", "Amortecedores de capô", "Amortecedores de porta-malas", "Anéis de pistão", "Anéis de vedação", "Anel de vedação", "Antena", "Atuador da marcha lenta", "Atuador de ABS", "Atuador de corpo de borboleta", "Atuador de marcha lenta", "Bandejas de suspensão", "Barra de direção", "Barra estabilizadora", "Barras de torção", "Batentes", "Bateria", "Bico injetor", "Bicos injetores", "Bielas", "Bloco do motor", "Bobina de ignição", "Bomba d'água", "Bomba de ABS", "Bomba de alta pressão de combustível", "Bomba de combustível", "Bomba de combustível elétrica", "Bomba de direção hidráulica", "Bomba de óleo", "Bomba de vácuo", "Borrachas de vedação", "Botão do vidro elétrico", "Braço oscilante", "Braços de direção", "Bucha de bandeja", "Buchas", "Buchas de suspensão", "Buzina", "Cabeçote", "Cabo de ignição", "Cabo de vela", "Cabo do acelerador", "Cabos de velas", "Caixa de direção", "Caixa de fusíveis", "Caixa de transferência", "Câmbio (transmissão manual ou automática)", "Capô", "Cardan", "Carter", "Cárter do óleo", "Catalisador", "Central de ABS", "Central de alarme", "Central de injeção eletrônica", "Centralina (ECU)", "Centralina eletrônica", "Chave de ignição", "Chave de roda", "Chicote elétrico", "Cilindro mestre de freio", "Cilindros de roda", "Cinto de segurança", "Coletor de admissão", "Coletor de escape", "Coluna de direção", "Compressor de ar-condicionado", "Condensador de ar-condicionado", "Conjunto de cabeçote", "Conjunto de embreagem do ar-condicionado", "Conjunto de motor", "Conjunto de válvulas", "Corpo de borboleta", "Correia dentada", "Correias auxiliares", "Corrente de distribuição", "Coxins da suspensão", "Coxins do motor", "Diferencial", "Disco de embreagem", "Discos de freio", "Distribuidor", "EGR (Exhaust Gas Recirculation)", "Eixo cardan", "Eixo de comando", "Eixo de transmissão", "Eixo dianteiro", "Eixo piloto", "Eixo traseiro", "Eletroventilador", "Emblemas", "Embreagem", "Embreagem de ventilador", "Embreagem do ventilador", "Espelho retrovisor interno", "Espelhos de cortes", "Espelhos retrovisores", "Estepe", "Evaporador de ar-condicionado", "Extintor de incêndio", "Faróis", "Faróis de neblina", "Fechaduras", "Filtro de ar", "Filtro de ar-condicionado", "Filtro de cabine", "Filtro de cabine (ar-condicionado)", "Filtro de combustível", "Filtro de óleo", "Filtro secador", "Flanges", "Fluido de freio", "Forros de porta", "Freio de mão", "Fusíveis", "Fusível térmico", "Grade do para-choque", "Grade frontal", "Hidrovácuo", "Injetor de combustível", "Injetores de combustível", "Intercooler", "Interruptor de ignição", "Interruptor de luz de freio", "Interruptor de ré", "Interruptor de temperatura", "Interruptores", "Jogo de juntas", "Junta da tampa de válvulas", "Junta de cabeçote", "Junta de cárter", "Junta de vedação", "Juntas homocinéticas", "Juntas universais", "Kit de embreagem", "Kit de juntas", "Kit de juntas de motor", "Kit de vedação", "Lanternas de posição", "Lanternas traseiras", "Luz de placa", "Luzes de freio", "Luzes de ré", "Luzes indicadoras de direção", "Luzes internas", "Macaco", "Mangueira de radiador", "Mangueiras", "Mangueiras de direção hidráulica", "Mangueiras de freio", "Mangueiras de radiador", "Mangueiras de vácuo", "Módulo de ABS", "Módulo de controle de tração", "Módulo de ignição", "Módulo de injeção eletrônica", "Mola de suspensão", "Molas", "Molas helicoidais", "Molduras externas", "Motor", "Motor de arranque", "Motor do vidro elétrico", "Motores do limpador de para-brisa", "Painel de instrumentos", "Palhetas do limpador de para-brisa", "Para-barros", "Para-brisa", "Para-choques", "Parafuso de dreno do óleo", "Parafusos", "Parafusos de roda", "Pastilhas de freio Traseira", "Pastilhas de freio Dianteira", 'Pedal de embreagem',
'Pedal de freio',
'Pedal do acelerador',
'Pinças de freio',
'Pistões',
'Pivôs',
'Placa de válvulas',
'Plato de pressão',
'Pneus',
'Polia do alternador',
'Polia do virabrequim',
'Porcas',
'Porta-malas',
'Protetor de cárter',
'Radiador',
'Radiador de água',
'Radiador de óleo',
'Regulador de voltagem',
'Relé da bomba de combustível',
'Relé de bomba de combustível',
'Relé de farol',
'Relé de partida',
'Relé de ventoinha',
'Relés',
'Reservatório de expansão',
'Reservatório de fluido de direção hidráulica',
'Reservatório de fluido de freio',
'Resfriador de EGR',
'Resistor do ventilador',
'Retentor de óleo',
'Retentor de óleo do comando de válvulas',
'Retentor de óleo do virabrequim',
'Retentor de válvulas',
'Retentores',
'Retrovisores externos',
'Rodas',
'Rolamento de embreagem',
'Rolamentos',
'Rotor do distribuidor',
'Sapatas de freio',
'Semi-eixos',
'Sensor de chuva',
'Sensor de detonação',
'Sensor de estacionamento',
'Sensor de fase',
'Sensor de fluxo de ar',
'Sensor de fluxo de ar (MAF)',
'Sensor de fluxo de combustível',
'Sensor de impacto (airbag)',
'Sensor de inclinação',
'Sensor de marcha lenta',
'Sensor de nível de combustível',
'Sensor de nível de líquido de arrefecimento',
'Sensor de nível de óleo',
'Sensor de oxigênio (sonda lambda)',
'Sensor de posição do acelerador',
'Sensor de posição do acelerador (TPS)',
'Sensor de posição do comando de válvulas',
'Sensor de posição do pedal de freio',
'Sensor de posição do virabrequim',
'Sensor de pressão de admissão',
'Sensor de pressão de combustível',
'Sensor de pressão de óleo',
'Sensor de pressão do ar-condicionado',
'Sensor de pressão do coletor',
'Sensor de pressão do coletor (MAP)',
'Sensor de pressão do óleo',
'Sensor de pressão do turbo',
'Sensor de qualidade do ar',
'Sensor de rotação',
'Sensor de rotação do motor',
'Sensor de rotação do virabrequim',
'Sensor de temperatura da água',
'Sensor de temperatura do ar',
'Sensor de temperatura do ar de admissão',
'Sensor de temperatura do combustível',
'Sensor de temperatura do motor',
'Sensor de temperatura externa',
'Sensor de temperatura interna',
'Sensor de velocidade',
'Sensor de velocidade da roda (ABS)',
'Sensor MAF',
'Sensor MAP',
'Servo-freio',
'Silencioso',
'Sincronizadores'
'Soleira das portas',
'Sonda lambda',
'Suporte de motor',
'Tacômetro',
'Tambores de freio',
'Tampa da correia dentada',
'Tampa da corrente de distribuição',
'Tampa de válvulas',
'Tampa do distribuidor',
'Tampa do radiador',
'Tampa do reservatório de expansão',
'Tampa do tanque de combustível',
'Terminais de direção',
'Terminal de escapamento',
'Termostato',
'Trava elétrica',
'Triângulo de sinalização',
'Trocador de calor',
'Tubo de admissão',
'Tubo de arrefecimento',
'Tubo de combustível',
'Tubo intermediário',
'Tubulação de ar-condicionado',
'Tubulação de EGR',
'Tubulação de fluido de freio',
'Tubulação de radiador',
'Tucho (hidráulico ou mecânico)',
'Turbocompressor',
'Válvula borboleta',
'Válvula de admissão',
'Válvula de alívio',
'Válvula de controle de purga',
'Válvula de controle de vácuo',
'Válvula de escape',
'Válvula de expansão',
'Válvula EGR',
'Válvula PCV',
'Válvula reguladora de pressão de combustível',
'Válvula termostática',
'Válvulas',
'Vareta de nível de óleo',
'Varetas de óleo',
'Vela de aquecimento',
'Vela de ignição',
'Velas de ignição',
'Velocímetro',
'Ventilador interno',
'Ventilador interno (ar quente/frio)',
'Ventoinha',
'Vidro traseiro',
'Vidros laterais',
'Virabrequim',
'Volante',
'Volante do motor',
'Wastegate'
]

if 'servico' not in st.session_state:
    st.session_state['servico'] = ['Troca de óleo e filtro',
'Alinhamento e balanceamento',
'Revisão dos freios',
'Troca de pneus',
'Troca de filtro de ar',
'Verificação e troca de fluídos',
'Revisão elétrica',
'Troca de correia dentada',
'Troca de velas de ignição',
'Revisão de suspensão',
'Limpeza ou substituição do filtro de combustível',
'Lavagem e polimento',
'Alinhamento dos faróis',
'Inspeção do sistema de ar-condicionado',
'Substituição de palhetas do para-brisa',
'Revisão da embreagem',
'Troca do filtro de cabine (ar-condicionado)',
'Troca de correias auxiliares',
'Ajuste da folga das válvulas',
'Substituição de rolamentos',
'Verificação e recarga do gás do ar-condicionado',
'Verificação e substituição de terminais de direção',
'Revisão do sistema de escapamento',
'Limpeza dos bicos injetores',
'Troca do líquido de arrefecimento',
'Verificação da bomba d’água',
'Troca de junta do cabeçote',
'Calibração dos pneus',
'Descarbonização do motor',
'Substituição do sensor de oxigênio (sonda lambda)',
'Revisão do sistema de transmissão',
'Revisão do sistema de direção hidráulica',
'Verificação de vazamentos de óleo e fluídos',
'Troca de coxins do motor e câmbio',
'Substituição de lâmpadas externas e internas',
'Regulagem do motor',
'Inspeção de juntas homocinéticas',
'Verificação e troca de fusíveis',
'Limpeza do radiador',
'Inspeção do sistema de segurança',
'Verificação e ajuste dos retrovisores',
'Substituição de batentes e buchas da suspensão',
'Troca de bateria',
'Troca de filtros do óleo e combustível',
'Substituição do filtro do ar-condicionado',
'Reparo de vidros e para-brisa',
'Limpeza de carpetes e estofados',
'Inspeção dos sistemas eletrônicos',
'Reparos na lataria e pintura',
'Revisão e substituição de amortecedores',
'Revisão do sistema de ignição',
'Troca de velas',
'Troca de cabos de velas',
'Troca de bobina de ignição',
'Inspeção do sistema de freios ABS',
'Troca do fluido da direção hidráulica',
'Limpeza do sistema de admissão',
'Reparo do alternador',
'Substituição de correias',
'Troca de tensor da correia dentada',
'Revisão do sistema de injeção eletrônica',
'Limpeza de corpo de borboleta',
'Troca de sensor de temperatura',
'Inspeção de coxins de motor e câmbio',
'Troca do filtro de óleo',
'Revisão do sistema de arrefecimento',
'Troca do termostato',
'Revisão do sistema de ar quente',
'Reparo da ventoinha',
'Troca do sensor de pressão do óleo',
'Troca de junta de cabeçote',
'Reparo de trincas no para-brisa'
'Inspeção dos cilindros de roda',
'Inspeção do servo-freio',
'Revisão do sistema de iluminação',
'Substituição de lâmpadas',
'Reparo de chicote elétrico',
'Substituição de fusíveis',
'Troca de relé',
'Revisão do sistema de alarme',
'Troca de reservatório de expansão',
'Reparo de painel de instrumentos'
'Revisão de cintos de segurança',
'Inspeção de airbags',
'Reparo de motor de vidro elétrico',
'Troca de botões e interruptores',
'Substituição de buzina',
'Reparo do sistema de som',
'Substituição de chicotes e conectores',
'Verificação do sistema de carregamento',
'Troca de bateria',
'Reparo de trincas no bloco do motor',
'Inspeção do sistema de escapamento',
'Reparo de cabeçote',
'Troca de tuchos',
'Substituição de juntas e retentores',
'Reparo de motor de partida',
'Revisão do sistema de aquecimento dos bancos',
'Revisão do sistema de teto solar',
'Substituição de sensores de estacionamento'
]
if 'nota_atual' not in st.session_state:
    st.session_state['nota_atual'] = None  # Inicializar o número da nota atual
if 'macro' not in st.session_state:
    st.session_state['macro'] = [
        'Manutenção Preventiva',
        'Manutenção Corretiva',
        'Manutenção Preditiva',
        'Manutenção Detectiva',
        'Manutenção Proativa',
        'Reparação',
        'Substituição de Peças',
        'Inspeção',
        'Lubrificação',
        'Ajustes',
        'Alinhamento e Balanceamento',
        'Troca de Fluídos',
        'Teste de Diagnóstico',
        'Limpeza e Conservação',
        'Atualização de Software'

    ]
# Função para adicionar carro
def adicionar_carro():
    placa_carro = st.text_input('Placa do Carro')
    nome_modelo = st.text_input('Nome do Modelo')
    if st.button('Adicionar Carro'):
        if not any(carro['placa'] == placa_carro for carro in st.session_state['carros']):
            st.session_state['carros'].append({'placa': placa_carro, 'modelo': nome_modelo})
            add_carro_sqlite(placa_carro, nome_modelo)
            st.success(f'Carro {nome_modelo} ({placa_carro}) adicionado!')
        else:
            st.warning('Este carro já está cadastrado.')

# Função para adicionar fornecedor
def adicionar_fornecedor():
    nome_fornecedor = st.text_input('Nome do Fornecedor')
    if st.button('Adicionar Fornecedor'):
        if nome_fornecedor not in st.session_state['fornecedores']:
            st.session_state['fornecedores'].append(nome_fornecedor)
            add_fornecedor_sqlite(nome_fornecedor)
            st.success(f'Fornecedor {nome_fornecedor} adicionado!')
        else:
            st.warning('Este fornecedor já está cadastrado.')

def registrar_nota(sheet):
    if not st.session_state.get('carros'):
        st.warning("Nenhum carro cadastrado. Por favor, adicione carros primeiro.")
        return
    if not st.session_state.get('fornecedores'):
        st.warning("Nenhum fornecedor cadastrado. Por favor, adicione fornecedores primeiro.")
        return

    # Inicializar 'nota_atual' se não existir ou se for None
    if 'nota_atual' not in st.session_state or st.session_state['nota_atual'] is None:
        st.session_state['nota_atual'] = {'numero_nota': '', 'itens': []}

    # Informações gerais da nota
    placa_carro = st.selectbox('Selecione a Placa do Carro', [carro['placa'] for carro in st.session_state['carros']])
    modelo_carro = next(carro['modelo'] for carro in st.session_state['carros'] if carro['placa'] == placa_carro)
    fornecedor = st.selectbox('Selecione o Fornecedor', st.session_state['fornecedores'])
    data = st.date_input('Data')
    km = st.number_input('Quilometragem', min_value=0)

    # Número da nota
    if not st.session_state['nota_atual']['numero_nota']:
        st.session_state['nota_atual']['numero_nota'] = st.text_input('Número da Nota')
    else:
        st.text(f"Número da Nota: {st.session_state['nota_atual']['numero_nota']}")

    # Formulário para adicionar itens à nota
    with st.form(key='registro_item_form'):
        col1, col2 = st.columns(2)
        with col1:
            macro = st.selectbox("Escolha macro", st.session_state['macro'])
            servico = st.selectbox('Escolha o Serviço', st.session_state['servico'])
        with col2:
            peca = st.selectbox('Escolha uma peça', st.session_state['pecas'])
            quantidade = st.number_input('Quantidade', min_value=1, value=1)
        
        # Criando três colunas para centralizar o campo de valor
        col_left, col_center, col_right = st.columns([1, 2, 1])
        with col_center:
            valor = st.number_input('Valor do Item', min_value=0.0)
    
        observacoes = st.text_area('Observações')
        
        adicionar_item_button = st.form_submit_button('Adicionar Item à Nota')

        if adicionar_item_button:
            novo_item = {
                'data': data.strftime('%Y-%m-%d'),
                'placa': placa_carro,
                'modelo': modelo_carro,
                'km': km,
                'nota': st.session_state['nota_atual']['numero_nota'],
                'fornecedor': fornecedor,
                'tipo_servico': macro,
                'peca': peca,
                'quantidade': quantidade,
                'valor': valor,
                'observacoes': observacoes
            }
            st.session_state['nota_atual']['itens'].append(novo_item)
            add_record_sqlite(**novo_item)
            adicionar_registro(sheet, novo_item)
            st.success('Item adicionado à nota com sucesso!')

    # Exibir itens da nota atual
    if st.session_state['nota_atual']['itens']:
        st.subheader("Itens na nota atual:")
        for idx, item in enumerate(st.session_state['nota_atual']['itens'], 1):
            st.text(f"{idx}. {item['peca']} - Quantidade: {item['quantidade']} - Valor: R${item['valor']:.2f}")

    if st.button('Finalizar Nota'):
        if st.session_state['nota_atual']['itens']:
            st.subheader('Resumo da Nota')
            total = sum(item['quantidade'] * item['valor'] for item in st.session_state['nota_atual']['itens'])
            st.write(f"Total da Nota: R$ {total:.2f}")
            
            st.session_state['nota_atual'] = {'numero_nota': '', 'itens': []}
            st.success('Nota finalizada!')
        else:
            st.warning('Não há itens na nota atual para finalizar.')
        
        st.rerun()  

# Função para adicionar novo registro à planilha
def adicionar_registro(sheet, registro):
    try:
        # Converter o dicionário em uma lista de valores na ordem correta
        valores = [
            registro['data'],
            registro['placa'],
            registro['modelo'],
            registro['km'],
            registro['nota'],
            registro['fornecedor'],
            registro['tipo_servico'],
            registro['peca'],  # Este campo corresponde a 'Item da Nota'
            registro['valor'],
            registro['quantidade'],
            registro['peca'],  # Repetindo 'peca' para a coluna 'Peça'
            registro['observacoes']
        ]
        sheet.append_row(valores)
    except Exception as e:
        st.error(f"Erro ao adicionar registro na planilha: {e}")

# Interface do app
st.title('Cadastro de Notas de Serviço para Carros')

sheet = connect_to_gsheet('Controle_Frota')
if sheet:
    criar_colunas(sheet)
    create_sqlite_table()
    create_carros_table()
    create_fornecedores_table()

    st.sidebar.header('Menu')
    opcao = st.sidebar.selectbox('Escolha uma opção', ['Adicionar Carro', 'Adicionar Fornecedor', 'Registrar Nota'])

    if opcao == 'Adicionar Carro':
        adicionar_carro()
    elif opcao == 'Adicionar Fornecedor':
        adicionar_fornecedor()
    elif opcao == 'Registrar Nota':
        registrar_nota(sheet)
else:
    st.error('Não foi possível conectar à planilha. Verifique suas credenciais e tente novamente.')
