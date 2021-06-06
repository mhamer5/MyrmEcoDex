rm(list=ls())
dev.off()

#load libraries
library(tidyverse)
library(iNEXT)
library(vegan)
library(reshape2)
library(openxlsx)

####Read in data and clean ####
#Read in antweb data
antweb_cnp_full<-read_csv("cnp_full_antweb.csv")

###generate clean antweb ant species list

antweb_cnp_full$Genus<-str_to_title(antweb_cnp_full$Genus)
antweb_cnp_full$Subfamily<-str_to_title(antweb_cnp_full$Subfamily)
antweb_cnp_full$gen_sp<-paste(antweb_cnp_full$Genus, antweb_cnp_full$Species, sep="_")

myrmecodex_cnp_full<-read_csv("CNP_ants_master_05042021.csv")[,1:30]

###generate clean myrmecodex ant species list
myrmecodex_cnp_full$`Count per morphospecies`<-gsub("+", "", myrmecodex_cnp_full$`Count per morphospecies`)
myrmecodex_cnp_full$gen_sp_nocf<-gsub("_cf_", "_", myrmecodex_cnp_full$gen_sp)
print(unique(myrmecodex_cnp_full$gen_sp_nocf))
#remove genus only identifications
med_genus<-data.frame(unique(myrmecodex_cnp_full$Genus))
med_genus$dash<-rep("_")
med_genus$unique.myrmecodex_cnp_full.Genus.<-paste(med_genus$unique.myrmecodex_cnp_full.Genus., med_genus$dash, sep="")
genus_<-med_genus$unique.myrmecodex_cnp_full.Genus.

for (i in 1:length(genus_)){
  myrmecodex_cnp_full <- myrmecodex_cnp_full[myrmecodex_cnp_full$gen_sp_nocf!=genus_[i], ] 
}


myrmecodex_cnp_full<-myrmecodex_cnp_full%>%
  drop_na(gen_sp_nocf)

rm(list=ls()[! ls() %in% c("antweb_cnp_full","myrmecodex_cnp_full")])
#write.csv(antweb_cnp_full, "clean_antweb_cnp_full.csv")
#write.csv(myrmecodex_cnp_full, "clean_myrmecodex_cnp_full.csv")

####Produce master specie list antweb and myrmecodex####
myrmecodex_ants<-myrmecodex_cnp_full%>%select(
  Subfamily, Genus, Species, gen_sp_nocf, `Sampling method`, Altitude
)%>%
  rename(Elevation = Altitude,
         gen_sp = gen_sp_nocf,
         Method = `Sampling method`
  )%>%
  drop_na()

myrmecodex_ants$Elevation<-gsub("m","", myrmecodex_ants$Elevation)
myrmecodex_ants$Elevation<-as.numeric(myrmecodex_ants$Elevation)
myrmecodex_ants<-na.omit(myrmecodex_ants)
myrmecodex_ants$Source<-"MyrmEcoDex"

antweb<-antweb_cnp_full%>%select(
  Subfamily, Genus, Species, gen_sp, Method, Elevation
)%>%filter(!grepl("indet",Species))%>%
  filter(!grepl("(indet)",Species))
antweb$Source<-"AntWeb"

combined<-bind_rows(antweb, myrmecodex_ants)

combined_unique<-unique(combined)
#generate summary table from data made in the python script (it might be possible to make this table in python instead?)
#needs author names 
#master<-read_csv("master_antweb_myrmecodex.csv")
#master$Altitude<-as.numeric(master$Altitude)

table.1 <- combined_unique %>%
  select(Subfamily, Genus, gen_sp, Elevation, Method, Source)%>%
  group_by(gen_sp)%>%
  summarise(
    MinAltitude = min(Elevation),
    MaxAltitude = max(Elevation),
    method = paste(unique(Method), collapse = ', '),
    source = paste(unique(Source), collapse = ', ')
  ) 

table.1$altitude=paste(table.1$MinAltitude, "-",table.1$MaxAltitude)

table.1<-select(table.1, -c(MinAltitude,MaxAltitude))

table.1$Subfamily <- with(combined_unique,
                          Subfamily[match(table.1$gen_sp,
                                          gen_sp)])
table.1$Genus <- with(combined_unique,
                          Genus[match(table.1$gen_sp,
                                          gen_sp)])

table.1 <- table.1[, c(5, 6, 1, 2, 4, 3)]

table.1<-table.1[
  with(table.1, order(Subfamily, Genus, source)),
]

table.1<-table.1%>%select(-Genus)
#export data frame with todays date
filename<-paste0(format(Sys.time(), "%m%d%Y"),'_combine_cnp_sp_list.xlsx')
write.xlsx(table.1, filename)

#after exporting, the table is sorted in excel and pasted into a landscape orientated word file
#there must be a better more automated way of doing this? you can export to a comma delimated txt file instead

####Create number summary tables for whole sp list, myrmecodex, antweb#####
rm(list=ls()[! ls() %in% c("antweb_cnp_full","myrmecodex_cnp_full", "myrmecodex_ants", "antweb", "combined_unique")])

#ANTWEB
antweb<-antweb%>%
  select(Subfamily, Genus, Species, gen_sp)
antweb<-unique(antweb)

no.sp<-length(unique(antweb$gen_sp))
no.gen<-length(unique(antweb$Genus))
no.subfam<-length(unique(antweb$Subfamily))

summary_antweb<-data.frame(no.sp,no.gen,no.subfam)
colnames(summary_antweb)<-c("#No.Species", "#No.Genera", "#No.Subfamilies")
summary_antweb<-data.frame(t(summary_antweb))
summary_antweb<-rownames_to_column(summary_antweb)
colnames(summary_antweb)<-c("Total #No. of", "Count")
#add in a function to save into 'summary_tables' directory
filename<-paste0(format(Sys.time(), "%m%d%Y"),'summary_antweb.xlsx')
write.xlsx(summary_antweb, filename)

#Myrmecodex
myrmecodex_ants<-myrmecodex_ants%>%
  select(Subfamily, Genus, Species, gen_sp)
myrmecodex_ants<-unique(myrmecodex_ants)

no.sp<-length(unique(myrmecodex_ants$gen_sp))
no.gen<-length(unique(myrmecodex_ants$Genus))
no.subfam<-length(unique(myrmecodex_ants$Subfamily))

summary_myrmecodex<-data.frame(no.sp,no.gen,no.subfam)
colnames(summary_myrmecodex)<-c("#No.Species", "#No.Genera", "#No.Subfamilies")
summary_myrmecodex<-data.frame(t(summary_myrmecodex))
summary_myrmecodex<-rownames_to_column(summary_myrmecodex)
colnames(summary_myrmecodex)<-c("Total #No. of", "Count")

filename<-paste0(format(Sys.time(), "%m%d%Y"),'summary_myrmecodex.xlsx')
write.xlsx(summary_myrmecodex, filename)

#antweb, myrmecodex combined
combined_unique<-combined_unique%>%
  select(Subfamily, Genus, Species, gen_sp)
combined_unique<-unique(combined_unique)

no.sp<-length(unique(combined_unique$gen_sp))
no.gen<-length(unique(combined_unique$Genus))
no.subfam<-length(unique(combined_unique$Subfamily))

summary_combined<-data.frame(no.sp,no.gen,no.subfam)
colnames(summary_combined)<-c("#No.Species", "#No.Genera", "#No.Subfamilies")
summary_combined<-data.frame(t(summary_combined))
summary_combined<-rownames_to_column(summary_combined)
colnames(summary_combined)<-c("Total #No. of", "Count")

filename<-paste0(format(Sys.time(), "%m%d%Y"),'summary_combined.xlsx')
write.xlsx(summary_combined, filename)

rm(list=ls()[! ls() %in% c("antweb_cnp_full","myrmecodex_cnp_full")])

####Generate subsite by species matrix (this needs cleaning and annotation)#####

MED_matrix<-myrmecodex_cnp_full%>%filter( `Sampling method` == "PF")%>%
 select("Count per morphospecies", "Field-note-neat", "gen_sp_nocf")
colnames(MED_matrix)<-c("count","subsite","species")
matrix$count<-as.numeric(MED_matrix$count)
MED_matrix<-melt(MED_matrix)
MED_matrix<-dcast(MED_matrix, subsite ~ species, value.var = "value", fill=0)
MED_matrix<-MED_matrix %>% 
 remove_rownames %>% 
 column_to_rownames(var="subsite")

rm(list=ls()[! ls() %in% c("antweb_cnp_full","myrmecodex_cnp_full")])
####Rank abundance plot for whole park and each camp####

species<-myrmecodex_cnp_full%>%
  select("Count per morphospecies", "gen_sp")
colnames(species)<-c("count","species")
drop_na(species)

#species
species$count<-as.numeric(species$count, na.rm=T)
species<-na.omit(species)
species<-aggregate(species$count, by=list(Category=species$species), FUN=sum)

species_abundance<-ggplot(species, aes(x=reorder(Category, -x), y=x,)) +
  geom_bar(stat="identity")+theme_minimal()+
  theme(axis.text.x = element_text(angle = 90, hjust = 1))+
  labs(title="Species Abundance in CNP", 
       x="Species", y = "Abundance")
species_abundance

#genera
genus<-myrmecodex_cnp_full%>%
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

#subfamily
subfamily<-myrmecodex_cnp_full%>%
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
dev.off()

rm(list=ls()[! ls() %in% c("antweb_cnp_full","myrmecodex_cnp_full")])

#######Species accum curves for each camps pitfall data summed into respective camps####
splist_clean<-myrmecodex_cnp_full%>%filter( `Sampling method` == "PF")

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

rm(list=ls()[! ls() %in% c("antweb_cnp_full","myrmecodex_cnp_full")])

####Percentage breakdown per subfamily ####


#####Number of species per genera####

#####Number of species per genera compared to Honduras as a whole####
#download gabi, download antweb, merge. compare to cnp data

gabi<-read_csv("GABI_Data_Release1.0_18012020.csv")
gabi_honduras<-gabi%>%filter(country == "Honduras")%>%
  select(genus_name_pub,species_name_pub)
gabi_honduras$genus_name_pub<-str_trim(gabi_honduras$genus_name_pub)
gabi_honduras$species_name_pub<-str_trim(gabi_honduras$species_name_pub)
gabi_honduras$Genus_species<-paste(gabi_honduras$genus_name_pub,"_",gabi_honduras$species_name_pub)
colnames(gabi_honduras)<-c("Genus", "Species", "Genus_species")
rm(gabi)

antweb_honduras<-read_csv("antweb_honduras.csv")
antweb_honduras<-antweb_honduras%>%select(Genus, Species)
antweb_honduras$Genus<-str_to_title(antweb_honduras$Genus)
antweb_honduras$Genus_species<-paste(antweb_honduras$Genus,"_",antweb_honduras$Species)

antweb_gabi_honduras<-bind_rows(gabi_honduras, antweb_honduras)
antweb_gabi_honduras$Genus_species<-str_replace_all(antweb_gabi_honduras$Genus_species, " ", "")
antweb_gabi_honduras<-unique(antweb_gabi_honduras)
antweb_gabi_honduras<-arrange(antweb_gabi_honduras, Genus)
#file<-"antweb_gabi_honduras.xlsx"
#write.xlsx(antweb_gabi_honduras,file)

antweb_gabi_honduras_edited<-read_csv("antweb_gabi_honduras_edited.csv")
species_counts_aw_gabi<-antweb_gabi_honduras_edited%>%
  count(Genus)
colnames(species_counts_aw_gabi)<-c("Genus", "aw_gabi")


myrmecodex_lama_cnp<-read_csv("06062021_combine_cnp_sp_list.csv")[,2]
myrmecodex_lama_cnp<-myrmecodex_lama_cnp%>%separate(gen_sp, c("Genus", "Species"), sep = "([_])")

species_counts_myrmecodex<-myrmecodex_lama_cnp%>%
  count(Genus)
colnames(species_counts_myrmecodex)<-c("Genus", "myrmecodex")

cnp_compared_honduras<-full_join(species_counts_myrmecodex,species_counts_aw_gabi)
cnp_compared_honduras<-drop_na(cnp_compared_honduras)
cnp_compared_honduras$percentage<-(cnp_compared_honduras$myrmecodex/cnp_compared_honduras$aw_gabi)*100
filename<-"cnp_compareto_honduras.xlsx"
write.xlsx(cnp_compared_honduras, filename)

