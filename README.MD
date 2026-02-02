
# Google Maps Scraper

Este projeto é um **scraper desenvolvido em Python** para coletar informações de estabelecimentos diretamente do **Google Maps**.

Ele é capaz de extrair dados como:

* Endereço
* Tipo de estabelecimento
* Avaliação em estrelas
* Quantidade de avaliações

Os dados podem ser utilizados para **análises, relatórios ou automações**.

---

## Tecnologias Utilizadas

O projeto foi construído utilizando:

* **Python 3.13+**
* **Selenium** — Automação do navegador
* **webdriver-manager** — Gerenciamento automático do ChromeDriver
* **tqdm** — Barra de progresso no terminal
* **pandas** — Manipulação de dados
* **openpyxl** — Exportação de planilhas Excel

---

## Instalação

### 1️Clone o repositório

```bash
git clone https://github.com/seu-usuario/googlemaps-scraper.git
cd googlemaps-scraper
```

---

### 2️Instale as dependências

Abra o **Prompt de Comando (CMD)** ou terminal dentro da pasta do projeto e execute:

```bash
pip install selenium webdriver-manager tqdm openpyxl pandas
```

---

## Configuração

Antes de executar o scraper, abra o arquivo:

```
config.py
```

Verifique principalmente esta configuração:

```python
HEADLESS = True
```

### O que significa?

| Valor   | Comportamento                                  |
| ------- | ---------------------------------------------- |
| `True`  | Executa sem abrir o navegador (modo invisível) |
| `False` | Executa abrindo o navegador normalmente        |

**Atenção:**
No modo **headless**, o Google Maps pode não carregar todas as informações corretamente.
Para capturar **100% dos dados visíveis**, recomenda-se usar:

```python
HEADLESS = False
```

---

## Como Executar

Depois de instalar tudo e configurar:

```bash
python main.py
```

O script irá:

1. Abrir o Google Maps
2. Pesquisar os tipos de estabelecimentos definidos em SEARCHS_DIC
3. Coletar as informações
4. Salvar os dados em arquivo JSON
5. Converter dados do arquivo JSON para o excel

---

## Possíveis Melhorias Futuras

* Capturar dados em headless

