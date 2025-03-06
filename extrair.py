import pandas as pd
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

"""#################################################################################################################################
                                                       Extrair
#################################################################################################################################"""

# Buscar ações
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