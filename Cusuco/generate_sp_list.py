#generate_sp_lists
import pandas as pd 
import numpy as np 
myrmecodex_ant =  pd.read_csv("myrmecodex_sp_list_1.csv")
llama = pd.read_csv("LLAMA_species_list.csv", encoding='windows-1252')

myrmecodex_ant['Genus_'] = myrmecodex_ant['Genus'].astype(str) + '_'
myrmecodex_ant=myrmecodex_ant[~myrmecodex_ant['gen_sp'].isin(myrmecodex_ant['Genus_'])] 
myrmecodex_ant=myrmecodex_ant.drop(['Genus_'], axis=1)

target_drop = ["Acromyrmex_cf_coronatus or subterraneus","Neoponera_villosa or bactronica or solisi","Cardiocondyla?_","_","Camponotus_senex?","?_" ,"ID Step 70 (stuck)_","Camponotus_albicoxis?", 
"????? old pachycondyla genus, revised genus not yet found_","Neoponera_villosa or bactronica or solisi","Key step 80: Pheidole of Nothridis_","Neoponera_villosa or bactronica or solisi","Neoponera_?",
"Procryptocerus_mayri or batsi","Leptogenys_JTL023??","Rasopone_mesoamericana/ferruginea","Pheidole_cf ursus","Acromyrmex_cf_coronatus"]

myrmecodex_ant=myrmecodex_ant[~myrmecodex_ant['gen_sp'].isin(target_drop)] 
myrmecodex_ant['gen_sp']=myrmecodex_ant['gen_sp'].str.replace("_cf_", "_")
myrmecodex_ant['gen_sp']=myrmecodex_ant['gen_sp'].str.replace("Gnamptogenys_interrupta?", "Gnamptogenys_interrupta")
myrmecodex_ant = myrmecodex_ant.drop_duplicates(subset=['gen_sp'], ignore_index=True)

myrmecodex_ant_list = pd.DataFrame(data=myrmecodex_ant, columns=['gen_sp'])
llama_ants = pd.DataFrame(data=llama, columns=['Genus_species'])

species_lists = pd.concat([myrmecodex_ant_list,llama_ants], ignore_index=True, axis=1)
species_lists.columns = ["myrmecodex_ant_list","llama_ants"]

species_lists["Unique"] = species_lists["myrmecodex_ant_list"][~species_lists["myrmecodex_ant_list"].isin(species_lists["llama_ants"])].drop_duplicates()


column_names=["MyrmEcoDex_Ant_Species", "LLAMA_Ant_Species","Unique_MyrmEcoDex"]

species_lists.to_excel("species_lists.xlsx", index=False,header=column_names)

gabi=pd.read_csv("GABI_Data_Release1.0_18012020.csv")
honduras_cnp=gabi[['valid_species_name','locality','country','dubious','citation']]
honduras_cnp=honduras_cnp.loc[(honduras_cnp.country == "Honduras")] 

#locality_list = honduras_cnp['locality'].drop_duplicates() 
#locality_list.to_excel("locality_list.xlsx", index=False)

gabi_cnp_full = honduras_cnp[honduras_cnp.locality.str.contains('Cusuco', na=False)]
#gabi_cnp_full['valid_species_name']=gabi_cnp_full.loc['valid_species_name'].str.replace(".", "_")
gabi_cnp_full.to_excel("gabi_cnp_full.xlsx", index=False)

gabi_cnp_nodup = gabi_cnp_full.drop_duplicates()
gabi_cnp_nodup.to_excel("gabi_cnp_nodup.xlsx", index=False)
