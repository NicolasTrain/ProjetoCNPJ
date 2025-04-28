from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
import zipfile
import os
import shutil
from lxml import html

today = datetime.today()
last_month = today - relativedelta(months=1)
last_month = last_month.strftime('%Y-%m')
today = today.strftime('%Y-%m')
print(today)
print(last_month)

url_mes_atual = f'https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/{today}/'
url_mes_passado = f'https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/{last_month}/'

if requests.get(url_mes_atual).status_code == 200:
    ultimo_mes_atualizado = today
    url_ultimo_mes_atualizado = url_mes_atual
else: 
    ultimo_mes_atualizado = last_month
    url_ultimo_mes_atualizado = url_mes_passado

html_texto = requests.get(url_ultimo_mes_atualizado).content
tree = html.fromstring(html_texto)

for link in tree.xpath('//a[text()="Parent Directory"]'):
    link.getparent().remove(link)
for link in tree.xpath('//a[starts-with(@href, "?")]'):
    link.getparent().remove(link)

hrefs = [a.get('href') for a in tree.xpath('//a[@href]')]
print("\nHREFs encontrados:")

for href in hrefs:
    nome_arquivo_zip = href
    nome_arquivo_csv = href.replace('.zip', '.csv')

    if os.path.exists(nome_arquivo_zip) and os.path.exists(nome_arquivo_csv):
        print(f"Arquivo já baixado e descompactado, ignorando: {nome_arquivo_zip}")
        continue

    if not os.path.exists(nome_arquivo_zip):
        print(f"Baixando: {nome_arquivo_zip}")
        arquivo = requests.get(f'{url_ultimo_mes_atualizado}{href}')
        with open(nome_arquivo_zip, "wb") as file:
            for chunk in arquivo.iter_content(chunk_size=8192):
                file.write(chunk)
    else:
        print(f"ZIP já existe: {nome_arquivo_zip}")

    if not os.path.exists('tmp'):
        os.mkdir('tmp')

    try:
        with zipfile.ZipFile(nome_arquivo_zip, "r") as zip_ref:
            zip_ref.extractall('tmp')
        print(f"Arquivo Descompactado: {nome_arquivo_zip}")

        arquivos_extraidos = os.listdir('tmp')
        if arquivos_extraidos:
            arquivo_extraido = arquivos_extraidos[0]
            shutil.move(f'tmp/{arquivo_extraido}', nome_arquivo_csv)
            print(f"Arquivo convertido: {nome_arquivo_csv}")
        else:
            print(f"Nenhum arquivo extraído de: {nome_arquivo_zip}")

    except zipfile.BadZipFile:
        print(f"Erro ao descompactar: {nome_arquivo_zip} (arquivo corrompido?)")
        
    if os.path.exists('tmp'):
        shutil.rmtree('tmp')