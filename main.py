#%%
#IMPORTS DO SELENIUM E WEBDRIVER
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


#IMPORTS DO ARQUIVO DE CONFIGURAÇÂO E IMPORTS DE FUNÇOES AUXILIARES
import config
import utils
import time
import re
from log import log
import traceback
import logging
from tqdm import tqdm

#%%
#CLASSE QUE REALIZA SCRAPPER NO SITE
class Scrapper:
    def __init__(self):
        self.driver = None #INSTANCIA DO NAVEGADOR CHROME QUE O SELENIUM MANIPULA
        self.base_url = config.BASE_URL #URL BASE QUE DESEJA ACESSAR
        self.scroll_page = config.SCROLL_PAGE #SE DESEJA REALIZAR SCROLL
        self.scroll_total = config.SCROLL_TOTAL #QUANTIDADE DE SCROLLS NA PAGINA
        self.__private_driver_options(config.HEADLESS) #DEFININDO SE O BOT SERA EM HEADLESS
        self.branchs_infos = [] #DIC QUE ARMAZENARA INFORMAÇOES SOBRE OS TIPOS DE ESTABELECIMENTOS PROCURADOS

    #ACESSA WEBSITE USANDO A BASE URL E SEARCH QUE SERIA O ESTABELECIMENTO QUE DESEJA CONSULTAR
    def acess_website(self):
        try:
            log(f"ABRINDO NAVEGADOR")
            self.driver.get(self.base_url)
        except Exception as e:
            self.quit()
            log(f"ERRO AO TENTAR ABRIR NAVEGADOR","CRITICAL")
            log(traceback.format_exc())

    #APOS ACESSAR PAGINA ESPERA BASEADO NO SELETOR O CARREGAMENTO DA PAGINA SEER FEITO
    #E LISTA OS ESTABELECIMENTOS CITADOS
    def consult(self,search):
        log("AGUARDANDO PAGINA CARREGAR")
        
        input_search = self.__private_wait_selector(selector='[jsaction="submit:omnibox.searchboxFormSubmit"] input',time=30) #AGUARDA SELECTOR DO INPUT PARA PROCURAR ESTABELECIMENTO
        input_search.clear()
        input_search.send_keys(search)
        input_search.send_keys(Keys.ENTER)
        
        time.sleep(3)
        
        painel_el = self.__private_wait_selector(selector='div[role="feed"]') #AGUARDANDO O SELECTOR PAI DE LISTA DO ESTABEELECIMENTOS CARREGA
        
        self.__private_scroll_website(painel_el) #REALIZANDO SCROLL NO PAGINA PAGA TER MAIS RESULTADO
        
        cards = self.__private_wait_selectors(selector='div[role="article"]') #SELETOS QUE RETORNAR UM ARRAY DE LISTA EM HTML DO ESTABELECIMENTOS
        
        branchs_result = self.__private_get_infos_branchs(cards,search) #PEGANDO INFOS DOS ESTABELECIMENTOS
        
        self.branchs_infos.extend(branchs_result)
        log("CONSULTA FINALIZADA, INDO PRA PROXIMA SE HOUVER MAIS")
    
    
    #RETORNA UMA LISTA DE TODAS AS INFORMACOES CAPTURADAS DURANTE A CONSULTA
    def get_branchs(self):
        return self.branchs_infos
        
    def __private_get_infos_branchs(self,cards,search):

        results = []
        #PERCORRENDO POR CADA ESTABELECIMENTO
        for card in tqdm(cards, desc=f"Processando estabelecimentos do tipo: {search}"):
            try:
                
                #CAPTURANDO NOME DO ESTABELECIMENTOS
                name_branch = self.__private_get_name_branch(card)
                #CLICANDO NO ESTABELECIMENTO
                link = card.find_element(By.CSS_SELECTOR, "a")
                self.driver.execute_script("arguments[0].click();", link)
                
                #PEGANDO CONTEUDO DO ESTABELECIMENTO
                text_els = self.__private_wait_selector(f'[aria-label*="{name_branch}"]',15).get_attribute('innerText')
                type_branch = self.__private_get_place_type(text_els)
                star_evalaution = self.__private_get_stars_branch(text_els)
                total_evalaution = self.__private_get_evaluation_count()
                adress_branch = self.__private_get_address(name_branch)
                

                results.append({
                    "Nome do estabelecimento": name_branch,
                    "Tipo de Estabelecimento": type_branch,
                    "Tipo":search,
                    "Nota do estabelecimento": star_evalaution,
                    "Quantidade de avaliações": total_evalaution,
                    "Endereço completo": adress_branch
                })
                time.sleep(1)
            except Exception as e:
                print("Erro ao pegar dados: " + str(e))
        return results
    
    #RECEBE O O CARD E PEGAR O NAME DO ESTABELECIMENTO
    def __private_get_name_branch(self, card):
        try:
            name_branch = card.get_attribute("aria-label")
        except:
            name_branch = "Nome não encontrado"
            log("NOME DO ESTABELECIMENTO NAO ENCONTRADO", "WARNING")
            
        log(f"NOME DO ESTABELECIMENTO: {name_branch}")
        return name_branch
    
    
    #SERA RETORNANDO QUANTIDADE DE ESTRELAS
    def __private_get_stars_branch(self, text_els):
        try:
            regex = r'\d[.,]\d'
            return re.search(regex,text_els).group()
        except Exception:
            log("ESTRELAS NAO ENCONTRADO", "WARNING")
            return "Tipo não informado"
    
        
    #SERA RETORNANDO QUANTIDADE DE AVALIACOES
    def __private_get_evaluation_count(self):
        try:
            wait = WebDriverWait(self.driver, 5) #AGUARDA O CARREGAMENTO DO SITE FINALIZAR

            #ESPERA ELEMENTO QUE POSSIO O TOTAL DE AVALIACAO
            reviews_el = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//span[@role="img" and contains(@aria-label, "avalia")]')
            ))


            aria = reviews_el.get_attribute("aria-label")

            total_reviews = aria.split(" ")[0].replace(".", "").replace(",", "").strip()

            return int(total_reviews)

        except Exception as e:
            log(f"Total de avaliações não encontrado: {e}", "WARNING")
            return "Não encontrado"

    #PEGAR O TIPO DO ESTABELECIMENTO
    def __private_get_place_type(self, text_els):
        try:
            regex = r'(.*?)\s·'
            type_branch = re.search(regex,text_els).group()
            return type_branch.replace(" ·", "").strip()
        except Exception:
            log("TIPO DO ESTABELECIMENTO NAO ENCONTRADO", "WARNING")
            return "Tipo não informado"
        
    #PEGA O ENDERECO DO ESTABELECIMENTO
    def __private_get_address(self, name_branch):
        try:
            wait = WebDriverWait(self.driver, 15) #AGUARDA O CARREGAMENTO DO SITE FINALIZAR

            #ESPERAR MODAL DO ESTABELECIMENTO ANTERIOR SUMIR
            try:
                old_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-item-id="address"]')
                wait.until(EC.staleness_of(old_button))
            except:
                pass  # PRIMEIRA BUSCA NAO TEM

            #ESPERAR BOTAO COM ENDERECO APARECER COM ENDERECO DO ESTABELECIMENTO ATUAL
            address_el = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'button[data-item-id="address"]')
            ))

            # PEGANDO ENDERECO
            address_full = address_el.get_attribute("aria-label") \
                                    .replace("Endereço:", "") \
                                    .strip()

            return address_full

        except Exception as e:
            log(f"Endereço não encontrado: {e}", "WARNING")
            return "Endereço não localizado"


    #GOOGLE MAPS POSSUI UM SCROLL INFINITO,QUANTO MAIS SCROLL DEVER MAIS ESTABELECIMENTOS SERA LISTADOS
    #ESSA FUNDCAO RECEBE DIV_ELS, ONDE QUE EA AREA QUE E NECESSARIO REALIZAR O SCROLL, E PEGO A ALTURA ESSE SELETOR E BASEADO NISSO FORÇAMOS O SELENIUM DAR SCROLL NA PAGINA
    def __private_scroll_website(self,divs_els):
        try:
            log("DEVE SER FEITO O SCOLL NA PAGINA: " + str(self.scroll_page))
            if self.scroll_page:
                log("QUANTIDADE DE SCOLL: " + str(self.scroll_total))
                for _ in range(self.scroll_total):
                    self.driver.execute_script(
                        "arguments[0].scrollTop = arguments[0].scrollHeight", divs_els
                    )
                    time.sleep(2)
        except Exception as e:
            log("ERRO AO TENTAR DA SCOLL NA PAGINA", "WARNING")
            log(traceback.format_exc(), "DEBUG")
            


    #AGUARDA O SELETOR APARECER NA PAGINA POR UM TEMPO E RETORNAR UMA LISTA DE SELECTORES FILHOS PARA INTERACAO     
    #SELECTOR = SELECTOR QUE DESEJA ESPERAR CARREGAR NO SITE
    #TIME = TEMPO DEFINIDO QUE DEVE AGUARDAR O SELETOR APARECER NO SITE
    #TYPE_SELECTOR = TIPO DE SELECTOR QUE ESTA SENDO LIDADO CSS_SELECTOR ou X_PATH
    def __private_wait_selectors(self, selector, time=5, type_selector="CSS_SELECTOR"):
        try:
            log(f"AGUARDANDO SELETOR CARREGAR NO SITE ATE: {time}s")
            log(f"SE ENCONTRADO SERA RETORNADO UMA LISTA")
            by = getattr(By, type_selector)
            return WebDriverWait(self.driver, time).until(
                EC.presence_of_all_elements_located((by, selector))
            )
        except TimeoutException as e:
            self.quit()
            log("TEMPO DE ESPERA DO SELETOR EXCECIDO", "ERROR")
            log(traceback.format_exc(), "DEBUG")
    
    #AGUARDA O SELETOR APARECER NA PAGINA POR UM TEMPO E RETORNAR O SELETOR PARA REALIZAR INTERAÇÂO     
    #SELECTOR = SELECTOR QUE DESEJA ESPERAR CARREGAR NO SITE
    #TIME = TEMPO DEFINIDO QUE DEVE AGUARDAR O SELETOR APARECER NO SITE
    #TYPE_SELECTOR = TIPO DE SELECTOR QUE ESTA SENDO LIDADO CSS_SELECTOR ou X_PATH
    def __private_wait_selector(self, selector, time=5, type_selector="CSS_SELECTOR"):
        try:
            log(f"AGUARDANDO SELETOR CARREGAR NO SITE ATE: {time}s")
            by = getattr(By, type_selector)
            return WebDriverWait(self.driver, time).until(
                EC.presence_of_element_located((by, selector))
            )
        except TimeoutException as e:
            self.quit()
            log("TEMPO DE ESPERA DO SELETOR EXCECIDO", "ERROR")
            log(traceback.format_exc(), "DEBUG")
        
    #CONFIGURAÇÃO DO NAVEGADOR, DEFINI SE A CONSULTA SERA EM HEADLESS
    def __private_driver_options(self, headless):
        try:
            log(f"DEFININDO CONFIGURAÇÃO DO ROBO")
            log(f"MODO HEADLESS: {headless}")
            if headless:
                options = Options()
                options.add_argument("--headless=new")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--disable-gpu")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
                log("CONSULTA SEM AMOSTRA DA TELA")
            else:
                self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
                
                self.driver.maximize_window()
                log("CONSULTA COM AMOSTRA DA TELA")
        except Exception as e:
            self.quit()
            log("TEMPO DE ESPERA DO SELETOR EXCECIDO", "CRITICAL")
            log(traceback.format_exc(), "DEBUG")
    
    
    #FECHA O NAVEGADOR 
    def quit(self):
        try:
            self.driver.quit()
        except Exception as e:
            log("OCORREU UM ERRO INESPERADO AO FECHAR NAVEGADOR", "CRITICAL")
            log(traceback.format_exc(), "DEBUG")
            
#%%
try:
    print("INICIANDO CONSULTA")
    scrapper = Scrapper()
    scrapper.acess_website()
    for search in config.SEARCHS_DIC:
        scrapper.consult(search)
    branchs_dic = scrapper.get_branchs()
    utils.response_file_json(branchs_dic)
    utils.excel_file()
    scrapper.quit()
    print("CONSULTA FINALIZADA")
except Exception as e:
    scrapper.quit()
    log(f"Erro inesperado")
    log(traceback.format_exc(), "DEBUG")