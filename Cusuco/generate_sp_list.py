#generate_sp_lists
import pandas as pd 
import numpy as np 

#load myrmecodex data
myrmecodex_ant =  pd.read_csv("myrmecodex_sp_list_1.csv")
#load llama data
llama = pd.read_csv("LLAMA_species_list.csv", encoding='windows-1252')

myrmecodex_ant['Genus_'] = myrmecodex_ant['Genus'].astype(str) + '_'
myrmecodex_ant=myrmecodex_ant[~myrmecodex_ant['gen_sp'].isin(myrmecodex_ant['Genus_'])] 
myrmecodex_ant=myrmecodex_ant.drop(['Genus_'], axis=1)

target_drop = ["Acromyrmex_cf_coronatus or subterraneus","Neoponera_villosa or bactronica or solisi","Cardiocondyla?_","_","Camponotus_senex?","?_" ,"ID Step 70 (stuck)_","Camponotus_albicoxis?", 
"????? old pachycondyla genus, revised genus not yet found_","Neoponera_villosa or bactronica or solisi","Key step 80: Pheidole of Nothridis_","Neoponera_villosa or bactronica or solisi","Neoponera_?",
"Procryptocerus_mayri or batsi","Leptogenys_JTL023??","Rasopone_mesoamericana/ferruginea","Pheidole_cf ursus","Acromyrmex_cf_coronatus"]

myrmecodex_ant=myrmecodex_ant[~myrmecodex_ant['gen_sp'].isin(target_drop)] 
myrmecodex_ant['gen_sp']=myrmecodex_ant['gen_sp'].str.replace("_cf_", "_")
myrmecodex_ant['Species']=myrmecodex_ant['Species'].str.replace("cf_", "")
myrmecodex_ant['gen_sp']=myrmecodex_ant['gen_sp'].str.replace("Gnamptogenys_interrupta?", "Gnamptogenys_interrupta")
myrmecodex_ant2 = myrmecodex_ant.drop_duplicates(subset=['gen_sp'], ignore_index=True)

myrmecodex_ant_list = pd.DataFrame(data=myrmecodex_ant2, columns=['gen_sp'])
llama_ants = pd.DataFrame(data=llama, columns=['Genus_species'])

species_lists = pd.concat([myrmecodex_ant_list,llama_ants], ignore_index=True, axis=1)
species_lists.columns = ["myrmecodex_ant_list","llama_ants"]

species_lists["Unique"] = species_lists["myrmecodex_ant_list"][~species_lists["myrmecodex_ant_list"].isin(species_lists["llama_ants"])].drop_duplicates()


column_names=["MyrmEcoDex_Ant_Species", "LLAMA_Ant_Species","Unique_MyrmEcoDex"]

species_lists.to_excel("species_lists.xlsx", index=False,header=column_names)

#load in gabi data
gabi=pd.read_csv("GABI_Data_Release1.0_18012020.csv")
honduras_cnp_gabi=gabi[['valid_species_name','locality','country','dubious','citation']]
honduras_cnp_gabi=honduras_cnp_gabi.loc[(honduras_cnp_gabi.country == "Honduras")] 

#locality_list = honduras_cnp['locality'].drop_duplicates() 
#locality_list.to_excel("locality_list.xlsx", index=False)

gabi_cnp_full = honduras_cnp_gabi[honduras_cnp_gabi.locality.str.contains('Cusuco', na=False)]
#gabi_cnp_full['valid_species_name']=gabi_cnp_full.loc['valid_species_name'].str.replace(".", "_")
gabi_cnp_full.to_excel("gabi_cnp_full.xlsx", index=False)

gabi_cnp_nodup = gabi_cnp_full.drop_duplicates()
gabi_cnp_nodup.to_excel("gabi_cnp_nodup.xlsx", index=False)

#load in antweb data
antweb_honduras =  pd.read_csv("antweb_honduras.csv", encoding='windows-1252')

#generate raw llama record data for the whole of honduras
llama_raw = antweb_honduras.loc[(antweb_honduras.CollectedBy == "LLAMA")]
llama_raw.to_excel("llama_raw.xlsx", index=False)

#generate llama data for cuscuo
llama_cusuco_raw = llama_raw[llama_raw.LocalityName.str.contains('Cusuco', na=False)]
llama_cusuco_raw.to_excel("llama_cusuco_raw.xlsx", index=False)

#generate cusuco data from whole of honduras antweb data
cusuco_antweb = antweb_honduras[antweb_honduras.LocalityName.str.contains('Cusuco', na=False)]
cusuco_antweb.to_excel("cusuco_antweb.xlsx", index=False)

#GENERATE MASTER LIST
#Bring together Cusuco_antweb, GABI Data, MyrmEcoDex

#add column indicating where the data came from
#myrmecodex
myrmecodex_ant['source']='myrmecodex'
myrmecodex_ant['citation']='myrmecodex_CNP_2018-2021'

#gabi
gabi_list_CNP=gabi_cnp_full[['valid_species_name','citation']]
gabi_list_CNP['source']='GABI'

gabi_list_CNP['valid_species_name']=gabi_list_CNP['valid_species_name'].str.replace(".", "_")

gabi_list_CNP[['Genus', 'Species']] = gabi_list_CNP['valid_species_name'].str.split('_', 1, expand=True)

gabi_list_CNP = gabi_list_CNP.rename({'valid_species_name': 'gen_sp'}, axis=1)

#antweb
#add antweb to begining of citaiton
cusuco_antweb_list=cusuco_antweb[['Subfamily', 'Genus','Species', 'CollectedBy']]
cusuco_antweb_list['source']='antweb'
cusuco_antweb_list['Genus']=cusuco_antweb_list['Genus'].str.capitalize()
cusuco_antweb_list['Subfamily']=cusuco_antweb_list['Subfamily'].str.capitalize()
cusuco_antweb_list = cusuco_antweb_list.rename({'CollectedBy': 'citation'}, axis=1)
#filter out unidentified stuff
cusuco_antweb_list=cusuco_antweb_list.loc[(cusuco_antweb_list.Species != '(indet)')]
cusuco_antweb_list=cusuco_antweb_list.loc[(cusuco_antweb_list.Species != 'indet')]

#merge gen and sp
cusuco_antweb_list['gen_sp'] = cusuco_antweb_list['Genus'].str.cat(cusuco_antweb_list['Species'],sep="_")

#add subfamilies to gabi
antweb_gen_subfam = cusuco_antweb_list[['Subfamily', 'Genus']]
gabi_list_CNP = pd.merge(gabi_list_CNP,  antweb_gen_subfam,  on ='Genus',  how ='left')


#Generate master list
sp_list_concat = pd.concat([myrmecodex_ant,cusuco_antweb_list,gabi_list_CNP])
print(sp_list_concat)
sp_list_concat.to_csv("sp_list_concat.csv", index=False)
#Master list without duplicates
sp_list_concat_nodup = sp_list_concat.drop_duplicates(subset=["gen_sp", "source"])
sp_list_concat_nodup.to_csv("sp_list_concat_nodup.csv", index=False)


#Generate cross table sheet comparing detection of species across sources
sp_list_concat_nodup['x']="x"
sp_list_concat_nodup=sp_list_concat_nodup[["gen_sp", "source", "x"]]
sp_list_cross=sp_list_concat_nodup.pivot_table(index=['gen_sp'], columns=['source'], values='x',aggfunc=len).fillna(0)
sp_list_cross.to_excel("sp_list_cross.xlsx")
print(sp_list_cross)
