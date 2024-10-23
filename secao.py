import pdfplumber
import re
import pandas as pd
from collections import defaultdict
import itertools

#This collect the PDF and create a dataframe
def createsectiondata(arquivo, codcidade):
    #Variables
    texto = ""
    i=1
    j=0
    secao_limpo = []
    zona = []
    secaoapto = []
    endereco = []
    local = []
    bairro = []
    secao = []
    filtro = []
    
    #Start the read of PDF
    with pdfplumber.open(arquivo + '.pdf') as pdf:
        total = len(pdf.pages)
        for pagina in pdf.pages:        
            if(i%100==0):
                print(str(i) + " de " + str(total))
            i += 1
            if codcidade in pagina.extract_text():
                texto = pagina.extract_text()
                #Clear the page formatting to make better the regex
                textolimpo = re.sub(r"\n", r" ", texto)
                #The zone is in start of page one time, so collect the zone and put to all register of the page
                zona += (re.findall(r"Zona: (.*?) Município",textolimpo))
                secaoapto += (re.findall(r"Aptos : (.*?) Local",textolimpo))
                local += (re.findall(r"Local : (.*?) Endereço", textolimpo))
                endereco += (re.findall(r"Endereço : (.*?) Bairro", textolimpo))
                bairro +=(re.findall(r"Bairro : (.*?) Seções:", textolimpo))
                #When have a new data inserted, zone is attribuited here.
                novosdados = re.findall(r"Endereço : (.*?) Bairro", textolimpo)
                for i in range(len(novosdados)-1):
                    zona.append(zona[-1])
        
        #Do a data cleaner in section
        for valor in secaoapto:
            removechar = "".join([letra for letra in valor if letra!="*"])
            secao_limpo.append(removechar)
        secaoapto = []
        for valor in secao_limpo:            
            subchar = re.sub(r"/", r" ", valor)
            subchar = subchar.split(" ")            
            secaoapto.append(subchar)
        
        #remove apto data
        for valor in secaoapto:
            for item in valor:
                if j%2==0:
                    filtro.append(item)
                j += 1
            filtro = set(filtro)
            filtro = list(filtro)
            filtro.sort() 
            secao.append(filtro)
            filtro = []
        
        #Create a DataFrame
        df = pd.DataFrame({
            'Zona': zona,
            'Seção': secao, #In the next time, do not save list in a dataframe, prefer string separated with space
            'Local': local,
            'Endereço': endereco,
            'Bairro': bairro        
        })
    return df

#Create a csv with pdf dataframe   
def createsectioncsv(df, codigo):
    df.to_csv(codigo + " - sections.csv")
    
#Read the csv file.    
def readsectioncsv(codigo):
    df = pd.read_csv(codigo + " - sections.csv")
    return df

#Group section per neighbor and return a df   
def bairrossection(df):
    dfbybairro = df.groupby('Bairro', as_index=False).agg({
        'Seção': lambda x: list(itertools.chain.from_iterable(x)),  # Concatenar listas de 'Seção'
        'Zona': lambda x: x.mode()[0]  # Moda para 'Zona'
    })
    return dfbybairro

#Create a dictionary with neighborhoods and votes.   
def votesperbairro(dfbybairro,dflist): 
    #Create the variables
    i = 0
    j = 0
    soma = 0
    votos = defaultdict(list) #Can to be create a list instead of dict 
    
    #Collect all sessions
    for sections in dfbybairro["Seção"]:
        #section is a list of chars, here convert to string
        sections = "".join([c for c in sections])
        #votos receive a attribute (neighbor name) that receive a dict with votes.
        votos[dfbybairro["Bairro"].iloc[i]] = defaultdict(dict)
        #Collect the neighbor zone 
        zona = str(dfbybairro["Zona"].iloc[i])
        #Standardize the variable zona with 0 in the end
        while len(zona)<4:
            zona = "0" + zona
        #Include the zone in dictionary
        votos[dfbybairro["Bairro"].iloc[i]]["zona"] = zona
        #Create a list with the string sections using regex and create a for
        sections = re.findall(r"'(\d{1,4})'", sections)
        for section in sections:
            #Standardize the variable section
            while len(section)<4:
                section = "0" + section
            #Iterate the dataframes list with section vote
            for votedf in dflist:
                #If the dataframe match, iterate candidates
                if re.search(r"Zona: " + zona + ", Seção: " + section,votedf.name) != None:
                    for candidato in votedf["Candidato"]:
                        #Insert new candidates or increment the votes
                        if candidato in votos[dfbybairro["Bairro"].iloc[i]]:
                            votos[dfbybairro["Bairro"].iloc[i]][candidato] += int(votedf['Votacao'].iloc[j])
                        else:
                            votos[dfbybairro["Bairro"].iloc[i]][candidato] = int(votedf['Votacao'].iloc[j])
                        j += 1
                    j = 0
                    break
        i += 1
    return(votos)
    
def createdfneighvote(dictvoto, csv):    
    neiglist = []
    candlist = []
    votelist = []
    for neigh, candidate_dict in dictvoto.items():
        del candidate_dict['zona']
        for candidate, vote in candidate_dict.items():            
            neiglist.append(neigh)
            candlist.append(candidate)
            votelist.append(vote)        
       
    df = pd.DataFrame({
        'Bairro': neiglist,
        'Candidato': candlist,
        'Votos': votelist
    })
    if csv==True:
        df.to_csv("teste.csv")
    return(df)