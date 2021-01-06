#generate_sp_lists
import pandas as pd 
import numpy as np 
myrmecodex_ant =  pd.read_csv("myrmecodex_sp_list_1.csv")
llama = pd.read_csv("LLAMA_species_list.csv")

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