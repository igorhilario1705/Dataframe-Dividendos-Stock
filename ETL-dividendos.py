import pandas as pd
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from datetime import datetime

data_atual = datetime.now().date()

"""#################################################################################################################################
                                                       Extrair
#################################################################################################################################"""

# Lista de ações
url = "https://www.fundamentus.com.br/resultado.php"
html = urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"})).read()
soup = BeautifulSoup(html, 'html.parser')

table = soup.find('table')
headers = [th.get_text() for th in table.find_all('th')]
rows = [[td.get_text().strip() for td in row.find_all('td')] for row in table.find_all('tr')[1:]]

lista_acao = pd.DataFrame(rows, columns=headers)[['Papel', 'Liq.2meses']]
lista_acao['Liq.2meses'] = lista_acao['Liq.2meses'].str.replace('.', '').str.replace(',', '.').astype(float)
lista_acao = lista_acao[lista_acao["Liq.2meses"] >= 1000000] # Minimo de negociações
lista_acao = lista_acao.drop(["Liq.2meses"], axis=1)
lista_acao = lista_acao['Papel'].tolist()
print("1. Lista de ações encontrada!")

"""
# Lista de ações
lista_acao = ['BBAS3','WEGE3','CMIG4','SAPR4','BBSE3','CPLE3','PETR4','ITSA4','TAEE11','EGIE3']
print("1. Lista de ações encontrada!")
"""

# ==================================================================================================================

headers = {"User-Agent": "Mozilla/5.0"}

df_dividendos_bruto = {}

for acao in lista_acao:
    try:
        url = f"https://www.fundamentus.com.br/proventos.php?papel={acao}&tipo=2"
        html = urlopen(Request(url, headers=headers)).read()
        soup = BeautifulSoup(html, 'html.parser')
        tabela = soup.find('table')
        if tabela:
            rows = [[td.get_text(strip=True) for td in row.find_all('td')] for row in tabela.find_all('tr')]
            if rows:
                columns = [th.get_text(strip=True) for th in tabela.find_all('th')]
                df_dividendos_bruto[acao] = pd.DataFrame(rows, columns=columns)
    
    except Exception:
        continue 

"""#################################################################################################################################
                                                       Transformar
#################################################################################################################################"""

df_dividendos = df_dividendos_bruto

for acao, df in df_dividendos.items():
    df['Papel'] = acao  # Adiciona a coluna 'Papel' com o nome da ação
    df = df.dropna().drop(columns=['Por quantas ações'], errors='ignore')

    # Tratamento da coluna "Data"
    if "Data" in df.columns:
        datas = df["Data"].str.split("/", expand=True)
        if datas.shape[1] == 3:
            df[['Dia_com', 'Mes_com', 'Ano_com']] = datas  # Se houver 3 partes, adiciona as colunas separadas
        df = df.drop(columns=['Data'], errors='ignore')

    # Tratamento da coluna "Data de Pagamento"
    if "Data de Pagamento" in df.columns:
        datas_pag = df["Data de Pagamento"].str.split("/", expand=True)
        if datas_pag.shape[1] == 3:
            df[['Dia_pag', 'Mes_pag', 'Ano_pag']] = datas_pag
        df = df.drop(columns=['Data de Pagamento'], errors='ignore')
    df_dividendos[acao] = df

df_dividendos = pd.concat(df_dividendos.values(), ignore_index=True)

# =========================================================================================================

df_dividendos['Tipo'] = 'Proventos'

for coluna in ['Dia_com', 'Mes_com', 'Mes_pag', 'Ano_com', 'Ano_pag']:
    df_dividendos[coluna] = df_dividendos[coluna].fillna(0).astype(int)

df_dividendos = df_dividendos[df_dividendos['Ano_pag'] != 0]

if "Valor" in df_dividendos.columns:
    df_dividendos["Valor"] = df_dividendos["Valor"].astype(str).str.replace(",", ".").astype(float)

# =========================================================================================================

# Aplicando a coluna 'Status'
def verificar_status(row):
    data_com = datetime(row['Ano_com'], row['Mes_com'], row['Dia_com']).date()
    if data_com >= data_atual:
        return 'Oportunidade de receber dividendos'
    else:
        return ''

df_dividendos['Status'] = df_dividendos.apply(verificar_status, axis=1)

# =========================================================================================================

# Preço teto método bazin de 6% de dividendos.

# Filtra os últimos 12 meses
df_ultimos_12m = df_dividendos[
    (df_dividendos['Ano_pag'] * 12 + df_dividendos['Mes_pag']) >= (data_atual.year * 12 + data_atual.month - 12)]

# Soma dos dividendos dos últimos 12 meses por "Papel"
dividendo_12m_por_papel = df_ultimos_12m.groupby("Papel")["Valor"].sum()

# Dividir por 6% os últimos 12 meses.
dividendo_12m_por_papel = (dividendo_12m_por_papel / 0.06).round(2)

df_dividendos["Preço_Teto_Bazin"] = df_dividendos["Papel"].map(dividendo_12m_por_papel).fillna(0)

# =========================================================================================================

# Verificar consistência dos dividendos
def verificar_consistencia(df):
    anos_analise = set(range(2021, 2025))
    df['Dividendos_consistente?'] = df.groupby('Papel')['Ano_pag'].transform(
        lambda x: 'Sim' if anos_analise.issubset(set(x)) and all(df[(df['Papel'] == x.iloc[0]) & (df['Ano_pag'].isin(anos_analise))]['Valor'].gt(0)) else 'Não')
    return df

df_dividendos = verificar_consistencia(df_dividendos)

print("2. Tratamento realizado!")

"""#################################################################################################################################
                                                       Carregar
#################################################################################################################################"""

df_dividendos.to_csv('df_dividendos.csv', index=False, encoding='utf-8-sig', sep=';', decimal=',')

print("3. Exportação de planilha realizada!")

print(df_dividendos)









