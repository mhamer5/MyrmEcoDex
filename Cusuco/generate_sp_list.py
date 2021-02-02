#generate_sp_lists
import pandas as pd 
import numpy as np 

#load myrmecodex data
myrmecodex_ant_1 =  pd.read_csv("CNP_ants_master_29012021.csv", encoding='windows-1252')
myrmecodex_ant=myrmecodex_ant_1[["Subfamily", "Genus", "Species", "gen_sp"]]

#load in ANTWEB data
antweb_honduras =  pd.read_csv("antweb_honduras.csv", encoding='windows-1252')

#generate raw llama record data for the whole of honduras
llama_raw = antweb_honduras.loc[(antweb_honduras.CollectedBy == "LLAMA")]
llama_raw.to_excel("llama_full_raw.xlsx", index=False)
#generate llama data for Cusuco (cnp)
llama_cusuco_raw = llama_raw[llama_raw.LocalityName.str.contains('Cusuco', na=False)]
llama_cusuco_raw.to_excel("cnp_full_llama.xlsx", index=False)
#generate cusuco data from whole of Honduras antweb data (antweb data is originally from Honduras but some records may not be from the LLAMA project)
cusuco_antweb = antweb_honduras[antweb_honduras.LocalityName.str.contains('Cusuco', na=False)]
cusuco_antweb.to_excel("cnp_full_antweb.xlsx", index=False)

#clean the myrmecodex data
myrmecodex_ant['Genus_'] = myrmecodex_ant['Genus'].astype(str) + '_'
#drop all genera only determinations in gen_sp 
myrmecodex_ant=myrmecodex_ant[~myrmecodex_ant['gen_sp'].isin(myrmecodex_ant['Genus_'])] 
#drop genus column
myrmecodex_ant=myrmecodex_ant.drop(['Genus_'], axis=1)

#big list of things that should be removed from myrmecodex data gen_sp column
target_drop = ["Acromyrmex_cf_coronatus or subterraneus","Neoponera_villosa or bactronica or solisi","Cardiocondyla?_","_","Camponotus_senex?","?_" ,"ID Step 70 (stuck)_","Camponotus_albicoxis?", 
"????? old pachycondyla genus, revised genus not yet found_","Neoponera_villosa or bactronica or solisi","Key step 80: Pheidole of Nothridis_","Neoponera_villosa or bactronica or solisi","Neoponera_?",
"Procryptocerus_mayri or batsi","Leptogenys_JTL023??","Rasopone_mesoamericana/ferruginea","Pheidole_cf ursus","Acromyrmex_cf_coronatus"]

#drop everything in target drop from gen_sp
myrmecodex_ant=myrmecodex_ant[~myrmecodex_ant['gen_sp'].isin(target_drop)] 
#remove all _cf_ from gen_sp (this should eventually not drop anything as we will be certain of our identifications eventually)
myrmecodex_ant['gen_sp']=myrmecodex_ant['gen_sp'].str.replace("_cf_", "_")
#do the same but with the species column
myrmecodex_ant['Species']=myrmecodex_ant['Species'].str.replace("cf_", "")


### GENERATE A LIST OF SPECIES UNIQUE TO MYRMECODEX
#this script below will find the ant species unique to myrmecodex by comparing species collected in by the LLAMA project (llama data from sp list on their website, this data could be improved with data from antweb?)
#drop duplicates in myrmecodex species (llama data is already unique)
myrmecodex_ant2 = myrmecodex_ant.drop_duplicates(subset=['gen_sp'], ignore_index=True)
#turn it into a dataframe with the column gen_sp
myrmecodex_ant_list = pd.DataFrame(data=myrmecodex_ant2, columns=['gen_sp'])
#turn llama data into dataframe with genus species column
llama_cusuco_raw_2=llama_cusuco_raw[["Genus","Species"]]
llama_cusuco_raw_2['gen_sp'] = llama_cusuco_raw_2['Genus'].str.cat(llama_cusuco_raw_2['Species'],sep="_")
llama_cusuco_raw_2['gen_sp']=llama_cusuco_raw_2['gen_sp'].str.capitalize()
llama_cusuco_raw_2['gen_sp']=llama_cusuco_raw_2['gen_sp'].drop_duplicates()
llama_ants = pd.DataFrame(data=llama_cusuco_raw_2, columns=['gen_sp'])
#concatinate myrmecodex ant species and llama together and rename columns
species_lists = pd.concat([myrmecodex_ant_list,llama_ants], ignore_index=True, axis=1)
species_lists.columns = ["myrmecodex_ant_list","llama_ants"]
#find the unique species between myrmecodex and llama species list and drop any duplicates. Rename the columns as appropriate and save to excel
species_lists["Unique"] = species_lists["myrmecodex_ant_list"][~species_lists["myrmecodex_ant_list"].isin(species_lists["llama_ants"])].drop_duplicates()
column_names=["MyrmEcoDex_Ant_Species", "LLAMA_Ant_Species","Unique_MyrmEcoDex"]
#save to excel
species_lists.to_excel("myrmecodex_unique_species_lists.xlsx", index=False,header=column_names)


#GENERATE SHEETS UNIQUE TO DIFFERENT SOURCES

#load in GABI data
gabi=pd.read_csv("GABI_Data_Release1.0_18012020.csv")
#select necessary columns in gabi
honduras_cnp_gabi=gabi[['valid_species_name','locality','country','dubious','citation']]
honduras_cnp_gabi=honduras_cnp_gabi.loc[(honduras_cnp_gabi.country == "Honduras")] 

#locality_list = honduras_cnp['locality'].drop_duplicates() 
#locality_list.to_excel("locality_list.xlsx", index=False)

#generate full list of records from cuscuo from GABI data
gabi_cnp_full = honduras_cnp_gabi[honduras_cnp_gabi.locality.str.contains('Cusuco', na=False)]
#gabi_cnp_full['valid_species_name']=gabi_cnp_full.loc['valid_species_name'].str.replace(".", "_")
gabi_cnp_full.to_excel("cnp_full_GABI.xlsx", index=False)

#generate similar sheet without duplicates
gabi_cnp_nodup = gabi_cnp_full.drop_duplicates()
gabi_cnp_nodup.to_excel("cnp_nodup_GABI.xlsx", index=False)


#### GENERATE MASTER LIST 
#Bring together Cusuco_antweb, GABI Data, MyrmEcoDex

#add column indicating where the data came from
#myrmecodex
myrmecodex_ant['source']='myrmecodex'
myrmecodex_ant['citation']='myrmecodex_CNP_2018-2021'

#sort gabi
gabi_list_CNP=gabi_cnp_full[['valid_species_name','citation']]
gabi_list_CNP['source']='GABI'
#change . to _ in valid species name
gabi_list_CNP['valid_species_name']=gabi_list_CNP['valid_species_name'].str.replace(".", "_")
#split valid sp name by _
gabi_list_CNP[['Genus', 'Species']] = gabi_list_CNP['valid_species_name'].str.split('_', 1, expand=True)
#rename valid sp list to gen_sp like other data
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
sp_list_concat.to_csv("cnp_master_splist_full.csv", index=False)
#Master list without duplicates
sp_list_concat_nodup = sp_list_concat.drop_duplicates(subset=["gen_sp", "source"])
sp_list_concat_nodup.to_csv("cnp_master_splist_nodup.csv", index=False)

#Generate cross table sheet comparing detection of species across sources
sp_list_concat_nodup['x']="x"
sp_list_concat_nodup=sp_list_concat_nodup[["gen_sp", "source", "x"]]
sp_list_cross=sp_list_concat_nodup.pivot_table(index=['gen_sp'], columns=['source'], values='x',aggfunc=len).fillna(0)
sp_list_cross.to_excel("cnp_splist_cross.xlsx")


### Generate Full data sheet for Cusuco
#subfam, gen, sp, source, citation, altitude, collection type, site name, date


myrmecodex_2=pd.read_csv("CNP_ants_master_29012021.csv", encoding='windows-1252')
myrmecodex_2=myrmecodex_2[["Subfamily", "Genus", "Species", "gen_sp", "Sampling method","Altitude"]]
#clean the myrmecodex data
#add a new column of Genus_ to use later to remove only Genus_ in gen_sp column
myrmecodex_2['Genus_'] = myrmecodex_2['Genus'].astype(str) + '_'
#drop all genera only determinations in gen_sp 
myrmecodex_2=myrmecodex_2[~myrmecodex_2['gen_sp'].isin(myrmecodex_2['Genus_'])] 
#drop genus column
myrmecodex_2=myrmecodex_2.drop(['Genus_'], axis=1)
#big list of things that should be removed from myrmecodex data gen_sp column
target_drop = ["Acromyrmex_cf_coronatus or subterraneus","Neoponera_villosa or bactronica or solisi","Cardiocondyla?_","_","Camponotus_senex?","?_" ,"ID Step 70 (stuck)_","Camponotus_albicoxis?", 
"????? old pachycondyla genus, revised genus not yet found_","Neoponera_villosa or bactronica or solisi","Key step 80: Pheidole of Nothridis_","Neoponera_villosa or bactronica or solisi","Neoponera_?",
"Procryptocerus_mayri or batsi","Leptogenys_JTL023??","Rasopone_mesoamericana/ferruginea","Pheidole_cf ursus","Acromyrmex_cf_coronatus"]
#drop everything in target drop from gen_sp
myrmecodex_2=myrmecodex_2[~myrmecodex_2['gen_sp'].isin(target_drop)] 
#remove all _cf_ from gen_sp (this should eventually not drop anything as we will be certain of our identifications eventually)
myrmecodex_2['gen_sp']=myrmecodex_2['gen_sp'].str.replace("_cf_", "_")
#do the same but with the species column
myrmecodex_2['Species']=myrmecodex_2['Species'].str.replace("cf_", "")
myrmecodex_2['source']='myrmecodex'
myrmecodex_2 = myrmecodex_2.rename({'Sampling method': 'Method'}, axis=1)

#antweb
antweb_honduras2 =  pd.read_csv("antweb_honduras.csv", encoding='windows-1252')
cusuco_antweb2 = antweb_honduras2[antweb_honduras2.LocalityName.str.contains('Cusuco', na=False)]
cusuco_antweb2=cusuco_antweb2[['Subfamily', 'Genus','Species', "Method", "Elevation"]]
cusuco_antweb2['source']='antweb'
cusuco_antweb2=cusuco_antweb2.loc[(cusuco_antweb2.Species != '(indet)')]
cusuco_antweb2=cusuco_antweb2.loc[(cusuco_antweb2.Species != 'indet')]
#merge gen and sp
cusuco_antweb2['Genus']=cusuco_antweb2['Genus'].str.capitalize()
cusuco_antweb2['Method']=cusuco_antweb2['Method'].str.capitalize()
cusuco_antweb2['gen_sp'] = cusuco_antweb2['Genus'].str.cat(cusuco_antweb2['Species'],sep="_")
cusuco_antweb2['Subfamily']=cusuco_antweb2['Subfamily'].str.capitalize()
cusuco_antweb2 = cusuco_antweb2.rename({'Elevation': 'Altitude'}, axis=1)
master_antweb_myrmecodex = pd.concat([cusuco_antweb2,myrmecodex_2])
master_antweb_myrmecodex=master_antweb_myrmecodex.dropna(subset=['Altitude'])
master_antweb_myrmecodex['Altitude'] = master_antweb_myrmecodex['Altitude'].astype(int)
master_antweb_myrmecodex.to_csv("master_antweb_myrmecodex.csv", index=False)
