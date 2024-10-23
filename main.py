from prefeito import *
from secao import *
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


#SJP "78859" 
#Porto Amazonas "77810"
codcidade = "78859"
arquivo = "enderecoPR"


#df = createsectiondata(arquivo)
#createsectioncsv(df, codcidade)

#Create csv with a dataframe list about votes using selenium in TSE site
def createvotedfs(codcidade):
    ok = createarchive(codcidade)
    while(not ok):
        ok = startagain(codcidade)

#Create csv with a dataframe about section using pdfpumbler     
def createneighsection(arquivo, codcidade):    
    df = createsectiondata(arquivo, codcidade)
    createsectioncsv(df, codcidade)

#Create a dict with votes for neighborhood, the keys is the neigh name with dict inside with votes
def createdictneighvotes(codcidade):   
    df = readsectioncsv(codcidade)
    dfbairro = bairrossection(df)
    dfs = readmayorcsv(codcidade)
    dictvotes = votesperbairro(dfbairro,dfs)
    return dictvotes

#Show the dict votes
def showneighborvote(dictvote):
    votes = createdictneighvotes(codcidade)
    for neigh in votes.keys():
        print(neigh)
        for candidate in votes[neigh].keys():
            print(candidate + " = " + str(votes[neigh][candidate]))
        print("\n")

#Create a df with neighbor and votes
def createdfvote(dictvoto, csv):
    df = createdfneighvote(dictvoto, csv)
    return df

def percentvote(df):
    dfcandidatos = df[df['Candidato'].str.contains(r'^\d')]
    df = dfcandidatos.groupby(['Bairro', 'Candidato'], as_index=False)['Votos'].sum()
    df_totais = df.groupby('Bairro')['Votos'].sum().reset_index()
    df_totais.columns = ['Bairro', 'Validos']
    df_final = pd.merge(df, df_totais, on='Bairro')
    df_final['Percentual(%)'] = (df_final['Votos'] / df_final['Validos']) * 100
    df_final['Percentual(%)'] = df_final['Percentual(%)'].round(2)
    df_final.drop("Votos", axis=1, inplace=True)
    df_final.drop("Validos", axis=1, inplace=True)
    return df_final
    
def percentvotenull(df):
    # Filtrando os dados para obter 'Eleitores Aptos' e 'Votos nominais'
    eleitores = df[df['Candidato'] == 'Eleitores Aptos']
    votos_nominiais = df[df['Candidato'] == 'Votos nominais']

    # Mesclando os DataFrames filtrados 
    merged_df = pd.merge(eleitores, votos_nominiais, on='Bairro', suffixes=('_Aptos', '_Nominais'))

    # Calculando a diferença
    merged_df['Votos'] = merged_df['Votos_Aptos'] - merged_df['Votos_Nominais']
    merged_df['Candidato'] = "00 Votos invalidos"    

    # Selecionando apenas o Bairro e a diferença
    resultado = merged_df[['Bairro', 'Candidato','Votos']]
    dfcandidatos = df[df['Candidato'].str.contains(r'^\d')]
    df_concatenado = pd.concat([dfcandidatos, resultado], ignore_index=True)
    df = percentvote(df_concatenado)
    return df
    
   
dictio = createdictneighvotes(codcidade)
df = createdfvote(dictio, True)

dfper =  percentvotenull(df)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
print(dfper)

dfper.sort_values(by=['Bairro', 'Percentual(%)'], ascending=[True, True],inplace=True)

# Listas únicas de bairros e candidatos
bairros = dfper['Bairro'].unique()
candidatos = dfper['Candidato'].unique()

# Configurações de posições para as barras
bar_width = 0.2  # Largura das barras
index = np.arange(len(bairros))  # Índices para as barras

# Configurando o gráfico
fig, ax = plt.subplots(figsize=(20, 12))

# Desenhar as barras lado a lado para cada candidato
for i, candidato in enumerate(candidatos):
    df_candidato = dfper[dfper['Candidato'] == candidato]
    
    if 'WILSON CABELO' in candidato:
        cor = 'red'
    elif 'NINA SINGER' in candidato:
        cor = 'blue'
    elif 'GERALDO MENDES' in candidato:
        cor = 'green'
    else:
        cor = 'black'
    
    ax.barh(index + i * bar_width, df_candidato['Percentual(%)'], bar_width, color=cor, label=candidato)

# Configurações adicionais
ax.set_xlabel('Percentual (%)')
ax.set_title('Percentual de Votos por Bairro e Candidato')
ax.set_yticks(index + bar_width * (len(candidatos) - 1) / 2)
ax.set_yticklabels(bairros)
ax.legend(title="Candidato")

# Exibindo o gráfico
plt.tight_layout()
plt.show()


