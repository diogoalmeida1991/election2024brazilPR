''' This code uses the databases hosted in site:
https://resultados.tse.jus.br/oficial/app/index.html#/eleicao/dados-de-urna;e=e619;uf=pr;mu=78859;ufbu=pr;mubu=78859;tipo=3;zn=0008;se=0020/boletim-de-urna
The objective is automate data analisys about São José dos Pinhais city election
and observe the regions with more votes to Nina Singer Mayor or the "man of the hat" 
Geraldo Mendes

The first problem is the date is separated with a lot of separated archive. The 
city has to zones(area) to voting, first was 0008 and the second was 0199, and
various sections (in the zone 0008 has the sections: 0020 - 0024, 0028 - 0031, 
0038 - 0040, 0045 - 0055, 0077 - 0088, 0104 - 0117, 0119 - 0141, 0145 - 0149, 
0178, 0184, 0185, 0195, 0196, 0199, 0200, 0202, 0211, 0214, 0222, 0227, 
0231 - 0233, 0236 - 0295, 0300 - 0305, 0311 - 0350, 0352, 0354 - 0379, 
0381 - 0439, 0441 - 0457, 0461 - 0500, and in the zone 0199: 0001 - 0031, 
0036 - 0038, 0042 - 0070, 0072 - 0089, 0120 - 0124, 0126 - 0146,  0148 - 0152,
0155 - 0159, 0162 - 0180, 0182 - 0207, 0209, 0211, 0214 - 0227, 0229 - 0249,
0251 - 0320, 0322 - 0324, 0326 - 0338, 0340 - 0345), with this may to happen 
typping mistakes or another human problems in captation of this datas. We can 
to use the Selenium library in the first step, to automate this proccess.

***The page with datas has javascript code, this do BeautifulSoup useless.'''

#Here is library import
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
import re

#To active chrome to run in a headless mode (without open the browser in screen)
chrome_options = Options() #Create configuration to chrome
chrome_options.add_argument("--headless=new")  # Activate headless mode
chrome_options.add_argument("--disable-gpu")  # Necessary in some systems
chrome_options.add_argument("--no-sandbox")  # Necessary in some Chrome versions
chrome_options.add_argument("--disable-dev-shm-usage") #Remove dev advice
chrome_options.add_argument("--window-position=-2400,-2400") 

def collectzone(codcidade):
    codcidade = str(codcidade)
    #The page use 0000 to zone(area) and 0000 to section that send us to a default html that has the zones.
    url = 'https://resultados.tse.jus.br/oficial/app/index.html#/eleicao;e=e619;uf=pr;mu=' + codcidade + ';ufbu=pr;mubu=' + codcidade + ';zn=0000;se=0000;tipo=3/dados-de-urna/boletim-de-urna'
    
    #The variable service install a chrome independent browser.
    service = Service(executable_path=ChromeDriverManager().install(), log_path='NUL')
    #The variable driver is a browser instance 
    driver = webdriver.Chrome(service=service, options=chrome_options)
    #open the page    
    driver.get(url)
    
    #Refresh the page, the first page is a page with a advice about elections
    driver.refresh()
    
    #print(driver.page_source)#Debug mode
    
    #To avoid the time library insertion, we use this code to "sleep" for ten seconds. 
    wait = WebDriverWait(driver, 10)
    
    #Wait to be clickable and click at mat-select-0 combo box
    combo_box = wait.until(EC.element_to_be_clickable((By.ID, "mat-select-0")))
    combo_box.click()
    
    #After click the javascript code open the menu
    wait.until(EC.visibility_of_element_located((By.ID, "mat-select-0-panel")))    
    
    #This open the text with zone(area) named as "Zona " + number 
    options = driver.find_elements(By.XPATH, "//mat-option/span[@class='mdc-list-item__primary-text']")
    options = [option.text for option in options] #transform a selenium element to list
    options = [''.join(filter(str.isdigit, option)) for option in options] #to avoid regex library
    options.pop(0) #Remove the first result "Zona" without number.
    
    driver.quit()
    return options    
    
def collectsection(codcidade, zona):
    codcidade = str(codcidade)
    zona = str(zona)
    #The page use 0000 to section that send us to a default html that has the zones.
    url = 'https://resultados.tse.jus.br/oficial/app/index.html#/eleicao;e=e619;uf=pr;mu=' + codcidade + ';ufbu=pr;mubu=' + codcidade + ';zn=' + zona + ';se=0000;tipo=3/dados-de-urna/boletim-de-urna'
    
    #The variable service install a chrome independent browser.
    service = Service(executable_path=ChromeDriverManager().install(), log_path='NUL')
    #The variable driver is a browser instance 
    driver = webdriver.Chrome(service=service, options=chrome_options)
    #open the page    
    driver.get(url)
    
    #Refresh the page, the first page is a page with a advice about elections
    driver.refresh()
    
    #print(driver.page_source)#Debug mode
    
    #To avoid the time library insertion, we use this code to "sleep" for ten seconds. 
    wait = WebDriverWait(driver, 10)
    
    #Wait to be clickable and click at mat-select-0 combo box
    combo_box = wait.until(EC.element_to_be_clickable((By.ID, "mat-select-2")))
    combo_box.click()
    
    #After click the javascript code open the menu
    wait.until(EC.visibility_of_element_located((By.ID, "mat-select-2-panel")))    
    
    #This open the text with zone(area) named as "Zona " + number 
    options = driver.find_elements(By.XPATH, "//mat-option/span[@class='mdc-list-item__primary-text']")
    options = [option.text for option in options] #transform a selenium element to list
    options = [''.join(filter(str.isdigit, option)) for option in options] #to avoid regex library
    
    
    #In the section exists aggregation section, for we is important the 4 digits only
    options = [option for option in options if len(option)==4] #Reduce to 4 digits each string
    
    driver.quit()
    return options 
    
def createmayordf(codcidade, zona, section):
    try:
        url = 'https://resultados.tse.jus.br/oficial/app/index.html#/eleicao;e=e619;uf=pr;mu=' + codcidade + ';ufbu=pr;mubu=' + codcidade + ';zn=' + zona + ';se=' + section + ';tipo=3/dados-de-urna/boletim-de-urna'
        #The variable service install a chrome independent browser.
        service = Service(executable_path=ChromeDriverManager().install(), log_path='NUL')
        #The variable driver is a browser instance 
        driver = webdriver.Chrome(service=service, options=chrome_options)
        #open the page    
        driver.get(url)
        
        #Refresh the page, the first page is a page with a advice about elections
        driver.refresh()
        
        #To avoid the time library insertion, we use this code to "sleep" for ten seconds. 
        wait = WebDriverWait(driver, 40)
        
        #Wait the page is loaded
        element = wait.until(EC.text_to_be_present_in_element((By.XPATH, "//h1[contains(text(), 'Prefeito.')]"), "Prefeito."))
        
        #Now we collect the candidate and votes.
        candidatos = driver.find_elements(By.XPATH, "//p[@class='mx-4+safe font-bold flex-1']")
        votos = driver.find_elements(By.XPATH, "//div[@class='font-bold flex justify-end text-roxo']")
        #We collect another informations (Blanks and Nulls votes)
        outros = driver.find_elements(By.XPATH, "//p[@class='mx-4+safe flex-1 titulo-sm']")
        outros_votos = driver.find_elements(By.XPATH, "//p[@class='mx-4+safe flex-1 font-bold']")
        
        #Transform object in string
        candidatos = [candidato.text for candidato in candidatos]
        votos = [int(voto.text) for voto in votos]
        outros = [outro.text for outro in outros]
        outros_votos = [int(outro_voto.text) for outro_voto in outros_votos]
        
        #Clear data and councillor data.
        if "Não há votos nominais" in candidatos:
            indice = candidatos.index("Não há votos nominais")
            del candidatos[indice]
            del votos[indice]
        indice = outros.index("Eleitores Aptos")
        i=0
        for i in range(6):
            del outros[indice]
            del outros_votos[indice]
        
        #Remove wrong results
        candidatos = [candidato for candidato in candidatos if not candidato.isdigit()]
        
        #The pattern is two number + space + candidate name for mayor, so, compare the space
        candidatos = [candidato for candidato in candidatos if not candidato[2].isdigit()]
        
        #This collect the last votes based in variable candidatos
        votos = votos[-len(candidatos):]
        
        #This group all results.
        candidatos = candidatos + outros
        votos = votos + outros_votos
        
        #Never forget to send a quit in driver, the connection is openned and a DDOS attack can to be detected
        driver.quit()
        
        #Create dataframe and give a name.
        df = pd.DataFrame({
            'Candidato': candidatos,
            'Votacao': votos
        })
        df.name = "Cidade: " + codcidade + ", Zona: " + zona + ", Seção: " + section
        return df
    except:
        return 0
    
def createarchive(codcidade):
    #Remove the file, if exists
    if os.path.exists(codcidade + '.csv'):
        os.remove(codcidade + '.csv')
    #Start the creation of file
    with open(codcidade + '.csv', 'a') as arquivo:
        secao = []
        zonas = collectzone(codcidade)
        for zona in zonas:
            secao.append(collectsection(codcidade, zona)) 
        i=0
        for zona in zonas:
            for item in secao[i]:
                df = createmayordf(codcidade, zona, item)
                if isinstance(df, pd.DataFrame): #If return a Dataframe:
                    #Write the title
                    arquivo.write("\n" + df.name + "\n")
                    #Write the datas
                    df.to_csv(arquivo)
                else: #Case return 0
                    return False
            i += 1
            #The resulting archive is a array of dataframes
    return True
    
            

#The same thing than createarchive, but continue where stop in createarchive            
def startagain(codcidade):
    if not os.path.exists(codcidade + '.csv'):
        print("Arquivo não encontrado")
        return
    else:
        dfs = readmayorcsv(codcidade)
        codzona = re.findall(r"Zona: (\d{4})", dfs[-1].name)[0]
        codsecao = re.findall(r"Seção: (\d{4})", dfs[-1].name)[0]
        with open(codcidade + '.csv', 'a') as arquivo:
            secao = []
            zonas = collectzone(codcidade)            
            zonas = zonas[zonas.index(codzona):]
            for zona in zonas:
                secao.append(collectsection(codcidade, zona)) 
            if len(secao[0]) != 1:#If stop in a last zone section go to another zone
                secao[0] = secao[0][secao[0].index(codsecao)+1:]
                i = 0
            else:
                i = 1
            print(secao[i])
            for zona in zonas:                
                for item in secao[i]:
                    df = createmayordf(codcidade, zona, item)
                    if isinstance(df, pd.DataFrame):
                        arquivo.write("\n" + df.name + "\n")
                        df.to_csv(arquivo)
                    else:
                        return False
                i += 1
    return True

#This function read the csv and return a list of dataframes                
def readmayorcsv(codcidade):
    dfs = []
    with open(codcidade + '.csv', 'r') as file:
        #Read lines of the csv
        lines = file.readlines()
        #Section do the control if line find a dataframe title
        secao = None
        for i, line in enumerate(lines):
            #Remove the spaces in start and end of string
            line = line.strip()
            if line.startswith("Cidade:"):
                #The section was encountered!
                secao=line
            elif secao and line:
                data = []
                #If not EOF and not is a Section Line, do:
                while i < len(lines) and not lines[i].startswith("Cidade:"):
                    line = lines[i].strip()
                    #If line not is a void string save the info
                    if line:
                        data.append(line.split(','))
                    i += 1
                #Create the dataframe
                df = pd.DataFrame(data[1:], columns=data[0])
                df.name = secao
                dfs.append(df)
                secao = None
    return dfs
                
                