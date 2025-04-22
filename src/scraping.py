from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
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
    ultimo_mes_atulizado = today
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

html_limpo = html.tostring(tree, pretty_print=True, encoding='unicode')
print(html_limpo)
hrefs = [a.get('href') for a in tree.xpath('//a[@href]')]
print("\nHREFs encontrados:")
for href in hrefs:
    print(href)