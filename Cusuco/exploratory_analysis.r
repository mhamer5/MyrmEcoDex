rm(list=ls())
dev.off()

#load libraries
library(tidyverse)
library(iNEXT)
library(vegan)
library(reshape2)
library(pixiedust)
library(openxlsx)


cnp_ants_raw<-read_csv("CNP_ants_master_29012021.csv")[,1:30]
cnp_ants_raw$`Count per morphospecies`<-gsub("+", "", cnp_ants_raw$`Count per morphospecies`)
###generate clean myrmecodex ant species list
target_drop<-c("Acromyrmex_cf_coronatus or subterraneus",
"Neoponera_villosa or bactronica or solisi",
"Cardiocondyla?_"   ,
"_" ,
"Atta_" ,
"Camponotus_",
"_",
"Camponotus_senex?",
"Labidus_",
"?_" ,
"ID Step 70 (stuck)_",
"Camponotus_albicoxis?", 
"Tetramorium_" ,
"Rasopone_" ,
"Gnamptogenys_cf_strigata",
"Procryptocerus_",
"Pheidole_",
"Acromyrmex_cf_nobilis",
"????? old pachycondyla genus, revised genus not yet found_",
"Pachycondyla_",
"Neoponera_villosa or bactronica or solisi",
"Key step 80: Pheidole of Nothridis_",
"Atta_cf_cephalotes",
"Neoponera_villosa or bactronica or solisi",
"Neoponera_?",
"Procryptocerus_mayri or batsi",
"Stenamma_",
"Nylanderia_",
"Temnothorax_",
"Leptogenys_cf_imperatrix",
"Hypoponera_",
"Strumigenys_cf_myllorhapha",
"Adelomyrmex_cf_microps",
"Leptogenys_JTL023??",
"Eciton_",
"Apterostigma_",
"Pseudoponera_",
"Gnamptogenys_cf_mordax",
"Leptogenys_cf_foveonates",
"Rasopone_mesoamericana/ferruginea",
"Pheidole_cf ursus",
"Cardiocondyla_",
"Strumigenys_cf_calamita",
"Cephalotes_cf_multispinosus",
"Acromyrmex_",
"Leptogenys_",
"Gnamptogenys_",
"Solenopsis_",
"Odontomachus_",
"Pseudomyrmex_",
"Acromyrmex_cf_coronatus",
"Myrmelachista_",
"Azteca_",
"Neoponera_cf_bugabensis",
"Gnamptogenys_interrupta?")
data_clean<-filter(cnp_ants_raw, !(gen_sp %in% target_drop))
#print(unique(splist_clean$gen_sp))

#generate subsite by species matrix (this needs cleaning and annotation)
matrix<-data_clean%>%filter( `Sampling method` == "PF")%>%
  select("Count per morphospecies", "Field-note-neat", "gen_sp")
colnames(matrix)<-c("count","subsite","species")
matrix$count<-as.numeric(matrix$count)
matrix<-melt(matrix)
matrix<-dcast(matrix, subsite ~ species, value.var = "value", fill=0)

matrix<-matrix %>% 
  remove_rownames %>% 
  column_to_rownames(var="subsite")

#####
#rank abundance plot for whole park and each camp
species<-data_clean%>%
  select("Count per morphospecies", "gen_sp")
colnames(species)<-c("count","species")
drop_na(species)


species$count<-as.numeric(species$count, na.rm=T)
species<-na.omit(species)
species<-aggregate(species$count, by=list(Category=species$species), FUN=sum)

species_abundance<-ggplot(species, aes(x=reorder(Category, -x), y=x,)) +
  geom_bar(stat="identity")+theme_minimal()+
  theme(axis.text.x = element_text(angle = 90, hjust = 1))+
  labs(title="Species Abundance in CNP", 
       x="Species", y = "Abundance")
species_abundance

genus<-cnp_ants_raw%>%
  select("Count per morphospecies", "Genus")%>%
  drop_na(Genus)
colnames(genus)<-c("count","genus")
genus$count<-as.numeric(genus$count, na.rm=T)
genus<-na.omit(genus)
genus<-aggregate(genus$count, by=list(Category=genus$genus), FUN=sum)

genus_abundance<-ggplot(genus, aes(x=reorder(Category, -x), y=x,)) +
  geom_bar(stat="identity")+theme_minimal()+
  theme(axis.text.x = element_text(angle = 90, hjust = 1))+
  labs(title="Genus Abundance in CNP", 
       x="Genus", y = "Abundance")
genus_abundance

subfamily<-cnp_ants_raw%>%
  select("Count per morphospecies", "Subfamily")%>%
  drop_na(Subfamily)
colnames(subfamily)<-c("count","subfamily")
subfamily$count<-as.numeric(subfamily$count, na.rm=T)
subfamily<-na.omit(subfamily)
subfamily<-aggregate(subfamily$count, by=list(Category=subfamily$subfamily), FUN=sum)

subfamily_abundance<-ggplot(subfamily, aes(x=reorder(Category, -x), y=x,)) +
  geom_bar(stat="identity")+theme_minimal()+
  labs(title="Subfamily Abundance in CNP", 
       x="Subfamily", y = "Abundance")
subfamily_abundance
rm(subfamily_abundance,subfamily,genus_abundance,genus,species_abundance,species)
dev.off()

#sp accum curves for each camps pitfall data summed into respective camps
splist_clean<-data_clean%>%filter( `Sampling method` == "PF")

ants_camps<-splist_clean%>%
  select("Count per morphospecies", "gen_sp", "associated_camp")%>%
  drop_na("Count per morphospecies","associated_camp")
colnames(ants_camps)<-c("count","species","camp")

ants_camps$count<-as.numeric(ants_camps$count)
ants_camps<-melt(ants_camps)
ants_camps<-dcast(ants_camps, camp ~ species, value.var = "value", fill=0)

ants_camps<-ants_camps %>% 
  remove_rownames %>% 
  column_to_rownames(var="camp")
ants_camps<-as.data.frame(t(ants_camps))

ants_camps<- list(guanales = ants_camps$guanales,
                basecamp = ants_camps$basecamp,
                cantilles=ants_camps$cantilles,
                cortecito=ants_camps$cortecito,
                danto   =ants_camps$danto)
ants_accum<-iNEXT(ants_camps, q=0, datatype="abundance", size=NULL, endpoint=NULL, knots=40, se=TRUE, conf=0.95, nboot=50)
ggiNEXT(ants_accum, type=1, facet.var="none")

#generate summary table from data made in the python script (it might be possible to make this table in python instead?)
#needs author names 
master<-read_csv("master_antweb_myrmecodex.csv")
master$Altitude<-as.numeric(master$Altitude)

table.1 <- master %>%
  select(gen_sp, Altitude, Method, source)%>%
  group_by(gen_sp)%>%
  summarise(
    MinAltitude = min(Altitude),
    MaxAltitude = max(Altitude),
    method = paste(unique(Method), collapse = ', '),
    source = paste(unique(source), collapse = ', ')
    ) 

table.1$altitude=paste(table.1$MinAltitude, "-",table.1$MaxAltitude)

table.1<-select(table.1, -c(MinAltitude,MaxAltitude))
table.1$Subfamily <- with(master,
                          Subfamily[match(table.1$gen_sp,
                                       gen_sp)])

write.xlsx(table.1, 'summary_table.xlsx')
#after exporting, the table is sorted in excel and pasted into a landscape orientated word file
#there must be a better more automated way of doing this?
