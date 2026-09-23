
library(igraph)
library(ggraph)
library(graphlayouts)
library(ggplot2)
library(coin)



####################################
###         1. load data         ###
####################################

# content analysis data

setwd("//data package/data")
full <- read.csv("coding_full_anon.csv", stringsAsFactors=F, sep=",")
table(full$party)
table(full$day)
dim(full)

# discourse network analysis
#setwd("C:/Users/Erwin/Google Drive/PhD/Thesis/Data Package/Chapter 4/")
#source('discourse_networks.R')
#dna_full <- discourse_networks(full, 
#                               normalization=T, 
#                               community_detection = T)
#save(dna_full, file='dna_full.rdata')

# load dna objects
setwd("//data package/data")
load('dna_full.rdata')
tweets <- dna_full$tweets
g <- dna_full$g_actor
am <- dna_full$am
n_actors <- nrow(am)-length(unique(tweets$concept))
n_concepts <- length(unique(tweets$concept))
print(paste(n_actors, 'actors and ', n_concepts, 'concepts'))

###############################################
### 2. plot argument frequencies (figure 2) ###
###############################################

# plot parameters
min_proportion <- .01

df <- as.data.frame(table(tweets$concept, tweets$position), stringsAsFactors = F)
colnames(df) <- c('concepts', 'Position', 'freq')
#exclude neutral positions
df <- df[which(df$Position!='neutral'),]
#recode 'con' as negative
df[which(df$Position=='con'),3] <- df[which(df$Position=='con'),3]*-1

#argument frequency threshold for plot
freq <- abs(df[1:n_concepts,3])+df[(n_concepts+1):nrow(df),3]
min_arg_freq=sum(freq)*min_proportion
print(paste('absolute miminum argument frequency at', min_proportion, 'percent:', min_arg_freq))

#transform to long format
con <- df[1:n_concepts,][which(abs(df[1:n_concepts,3])+df[(n_concepts+1):nrow(df),3]>min_arg_freq),]
pro <- df[(n_concepts+1):nrow(df),][which(abs(df[1:n_concepts,3])+df[(n_concepts+1):nrow(df),3]>min_arg_freq),]
df <- rbind(con, pro)

filtered_concepts <- pro$concepts

#find ylim for plot
roundUp <- function(x,to=10){ to*(x%/%to + as.logical(x%%to)) }
ylim <- roundUp(max(df$freq), to=10)

#argument frequency plot (figure 2)
ggplot(df, aes(x=reorder(concepts, freq^2), y=freq, fill=Position))+geom_bar(stat="identity")+coord_flip()+
  xlab("") + ylab('Frequency') +
  scale_fill_manual(values=c("coral3", "aquamarine3")) +
  ylim(-ylim,ylim) +
  theme_minimal()


################################################
### 3. plot substantive positions (figure 5) ###
################################################
table(V(g)$community)
dna_full$modularity
clu_min_size <- 50
clu_no <- names(table(V(g)$community)[which(table(V(g)$community)>=clu_min_size)])

clu <- paste0('cluster_', names(table(V(g)$community)[which(table(V(g)$community)>=clu_min_size)]))
clu <- c('Proponents \n (N=551)', 
         'Opponents \n (N=418)', 
         'Experiment promotors \n (N=295)', 
         'Political promotors \n (N=53)')

#separate pro and con
profiles <- list()
for (k in 1:4){
  profile <- tweets[tweets$user %in% V(g)$name[V(g)$community==k], c('concept', 'position')]
  profile_pro <- profile[profile$position=='pro',]
  profile_con <- profile[profile$position=='con',]
  
  cnt_pro <- list()
  for (i in 1:length(unique(df$concept))){
    cnt_pro[[i]] <- sum(profile_pro$concept %in% unique(df$concept)[i])
  }
  cnt_con <- list()
  for (i in 1:length(unique(df$concept))){
    cnt_con[[i]] <- sum(profile_con$concept %in% unique(df$concept)[i])
  }
  profiles[[k]] <- cbind(clu[k], 
                         paste(rep(unique(df$concept),2),
                                c(rep('pro', length(unique(df$concept))), rep('con', length(unique(df$concept)))),
                                sep = '_'),
                         c(unlist(cnt_pro), unlist(cnt_con)))
}
profiles <- do.call('rbind', profiles)
colnames(profiles) <- c('cluster', 'position', 'Frequency')
profiles <- as.data.frame(profiles, stringsAsFactors=F)
profiles$Frequency <- as.numeric(profiles$Frequency)

#separate concept_agreement tuples (appendix c)
ggplot(profiles, aes(x=factor(cluster, levels = c('Proponents \n (N=551)', 
                                                  'Opponents \n (N=418)', 
                                                  'Experiment promotors \n (N=295)', 
                                                  'Political promotors \n (N=53)')), 
                     y=position, fill= Frequency)) + geom_tile() + xlab("") + ylab("") +
  scale_fill_gradient2(low="white", high="black") +
  theme_minimal()+
  theme(axis.text.x = element_text(angle = 90))+
  scale_x_discrete(position = "top")

#combined into one heatmap (figure 5)
df <- list()
for (i in 1:length(clu)){
  users <- V(g)$name[which(V(g)$community==clu_no[i])]
  x <- data.frame(colnames(am[which(rownames(am) %in% users),(n_actors+1):ncol(am)]),
                  clu[i],
                  colSums(am[which(rownames(am) %in% users),(n_actors+1):ncol(am)]) 
  )
  colnames(x) <- c('y', 'x', 'Frequency') 
  x <- x[which(x$y %in% filtered_concepts),]
  df[[i]] <- x
}
df <- do.call('rbind', df)
rownames(df) <- NULL


ggplot(df, aes(x=factor(x, levels = c('Proponents \n (N=551)', 
                                            'Opponents \n (N=418)', 
                                            'Experiment promotors \n (N=295)', 
                                            'Political promotors \n (N=53)')), y, fill= Frequency)) + geom_tile() + xlab("") + ylab("") +
  scale_fill_gradient2(low="coral3", mid="white", high="aquamarine3") +
  theme_minimal()+
  theme(axis.text.x = element_text(angle = 90))+
  scale_x_discrete(position = "top")

##############################################
###   4. elite-cluster crosstab (table 2)  ###
##############################################
politici <- read.csv('politwoops.csv', sep=';', stringsAsFactors = F)
politici <- politici[which(politici$username %in% V(g)$name),]
politici <- politici[which(politici$party %in% c('vvd', 'cda', 'd66', '50plus', 'gl', 'pvda', 'sp')),]
nrow(politici)


V(g)$party <- NA
for (i in 1:nrow(politici)){
  V(g)$party[which(V(g)$name %in% politici$username[i])] <- politici$party[i] 
}
#exclude 50plus
V(g)$party[V(g)$party=='50plus'] <- NA

elites <- as.matrix(table(V(g)$party, V(g)$community))
elites <- elites[,1:length(clu)]
colnames(elites) <- c('Liberal-egalitarian', 
                      'Opponents', 
                      'Experiment promotors', 
                      'Political promotors')
elites <- elites[c('gl', 'sp', 'cda', 'd66', 'pvda','vvd'),]
party_labels <- rownames(elites)

elites <- as.data.frame(elites)
names(elites) <- c("party", "position", "freq")

proponents <- cbind(c('gl', 'sp', 'cda', 'd66', 'pvda','vvd'), "Proponents", tapply(elites$freq[elites$position %in% c('Liberal-egalitarian', 
                                                        'Experiment promotors', 
                                                        'Political promotors')], elites$party[elites$position %in% c('Liberal-egalitarian', 
                                                                                                                     'Experiment promotors', 
                                                                                                                     'Political promotors')], sum))
colnames(proponents) <- c("party", "position", "freq")
elites=rbind(elites, proponents )

elites_2= elites[elites$position %in% c("Proponents", "Opponents"),]
elites_2$freq <- as.numeric(elites_2$freq)
elites_2 <- elites_2[order(elites_2$party),]
elites_2$p=unlist(tapply(elites_2$freq, elites_2$party, function(x){x/sum(x)}))

elites_2$party <- factor(elites_2$party, levels=c("pvda", "gl", "d66", "sp", "cda", "vvd"))

ggplot(elites_2, aes(fill=position, y=p, x=party)) + 
  geom_bar(position="stack", stat="identity") +
  xlab("") +ylab("% Politicians \nin favour or against UBI \nper party") +
  theme_minimal()

#significance tests
?fisher.test
?independence_test
fisher.test(elites)
df_elites <- data.frame(party=as.factor(V(g)$party), community=as.factor(V(g)$community))
df_elites <- df_elites[!is.na(df_elites$party),]
independence_test(party ~ community, data = df_elites)


chisq <- chisq.test(elites)
z <- (chisq$observed-chisq$expected)/sqrt(chisq$expected)
sqrt(chisq$expected*(1-rowSums(elites)/sum(elites))*(1-colSums(elites)/sum(elites)))

z_adj <- (chisq$observed-chisq$expected)/sqrt(chisq$expected*(1-rowSums(elites)/sum(elites))*(1-colSums(elites)/sum(elites)))
p <- round(2*pnorm(-abs(z_adj)),3)
p

install.packages("GmAMisc")
library(GmAMisc)
chiperm(elites)
#column percentages
elites <- do.call("rbind", lapply(1:nrow(elites), function(i){round(elites[i,]/colSums(elites),3)}))
rownames(elites) <- party_labels
elites

write.csv(elites, file='elites_table.csv')

##############################################
###   5. plot concept network (figure 6)   ###
##############################################
g_concept <- dna_full$g_concept
hist(E(g_concept)$weight)

#argument ownership
#which community predominantly connects arguments?
#construct concept adjacency matrix per cluster
concept_am <- function(am_sub, clu){
  ## concept network
  transpose <- am_sub %*% t(am_sub)
  
  n_actors <- sum(V(g)$community==clu)
  n_concepts <- length(unique(tweets$concept))
  
  concept <- transpose[(nrow(transpose)-n_concepts+1):nrow(transpose), (ncol(transpose)-n_concepts+1):ncol(transpose)]
  
  return(concept)
}

#liberal-egalitarian matrix
clu=1
keep = c(V(g)$name[which(V(g)$community==clu)], unique(tweets$concept))
am_sub <- am[which(rownames(am) %in% keep), which(colnames(am) %in% keep)]
c1 <- concept_am(am_sub, clu=clu)
#opposition matrix
clu=2
keep = c(V(g)$name[which(V(g)$community==clu)], unique(tweets$concept))
am_sub <- am[which(rownames(am) %in% keep), which(colnames(am) %in% keep)]
c2 <- concept_am(am_sub, clu=clu)

#ownership is defined as the degree to which one community engages with arguments more often than another
arg_ownership <- abs(c1)-abs(c2)
g_own <- graph_from_adjacency_matrix(concept, weighted = T, mode='lower')
g_own <- simplify(g_own)

#append ownership edge value to g_concept
concept_edges <- paste(ends(g_concept, 1:1021)[,1], ends(g_concept, 1:1021)[,2], sep='_')
own_edges <- paste(ends(g_own, 1:939)[,1], ends(g_own, 1:939)[,2], sep='_')

E(g_concept)$own <- 0
for (i in 1:length(own_edges)){
  E(g_concept)$own[concept_edges %in% own_edges[i]] <- E(g_own)$weight[i]
}
E(g_concept)$own <- (E(g_concept)$own-mean(E(g_concept)$own))/sd(E(g_concept)$own)
hist(E(g_concept)$own)


#layout based on absolute mentions
E(g_concept)$weight <- abs(E(g_concept)$weight)
#keep concepts with min_arg_freq
cnt <- rowSums(abs(am[which(rownames(am) %in% unique(tweets$concept)),]))
g_concept <- delete.vertices(g_concept, cnt<min_arg_freq)
#keep edges with edge_threshold
edge_threshold <-  .08
g_concept <- delete.edges(g_concept, which(E(g_concept)$weight<edge_threshold))
#remove isolates
g_concept <- delete.vertices(g_concept, which(strength(g_concept)==0))


ggraph(g_concept,layout="centrality",centrality = strength(g_concept))+
  draw_circle(use = "cent")+
  geom_edge_link(aes(width = weight, color = own), show.legend=F)+
  scale_edge_colour_gradient2(
    low = "coral4",
    mid = "aliceblue",
    high = "aquamarine4",
    midpoint = 0,
    space = "Lab",
    na.value = "grey50",
    guide = "edge_colourbar"
  ) +
  geom_node_point(fill = "azure", color = 'grey', size = sqrt(abs(strength(g_concept)*100)), shape = 22)+
  geom_node_text(aes(label = name)) +
  theme_graph()+
  coord_fixed()



##########################################
###   actor network plot (figure 4)    ###
##########################################
g <- dna_full$g_actor

#agreement only (for plotting)
g <- delete.edges(g, which(E(g)$weight<0))
g <- delete.vertices(g, which(strength(g)==0))
#tie strength threshold
layout <- layout_with_fr(g)
tie_threshold=.60
g <- delete.edges(g, which(E(g)$weight<tie_threshold))
hist(E(g)$weight)
#set edge color gradient
percentile=seq(from=.01, to=1.01, by=.01)
E(g)$color <- NA
for (i in 1:length(percentile)){
  E(g)$color[which(E(g)$weight >= percentile[i] & E(g)$weight < percentile[i+1])] <- paste0('grey',i)  
}

plot(g, 
     vertex.size=(strength(g, weights=E(g)$weight))^(1/3),
     vertex.label=NA,
     vertex.label.color='black',
     vertex.label.family = 'Calibri',
     vertex.label.font = 2,
     vertex.color=colors()[V(g)$community*3],
     edge.color=E(g)$color,
     layout=layout)

#plot legend
lgnd <- cbind(1:length(unique(V(g)$community)), 
              colors()[unique(V(g)$community)*3])
#substantial names
clu <- c('Proponents \n (N=511)', 
         'Opponents \n (N=418)', 
         'Experiment promotors \n (N=295)', 
         'Political promotors \n (N=53)')
lgnd <- cbind(clu, lgnd[as.numeric(clu_no), 2])
legend(x='left', 
       legend= lgnd[,1], 
       fill=lgnd[,2])
dev.off()
 
#########################################
####  day-by-day plots (appendix x)  ####
#########################################
setwd("//data package/data")
full <- read.csv("coding_full.csv", stringsAsFactors=F, sep=",")
table(full$day)
day_1 <- full[full$day=='21/09/2014',]
day_2 <- full[full$day=='12/04/2015',]
day_3 <- full[full$day=='05/08/2015',]

# discourse network analysis
setwd(".../data package")
source('discourse_networks.R')
dna_1 <- discourse_networks(day_1, 
                            normalization=T, 
                            community_detection = T)
save('dna_1.rdata')
dna_2 <- discourse_networks(day_2, 
                            normalization=T, 
                            community_detection = T)
save('dna_2.rdata')
dna_3 <- discourse_networks(day_3, 
                            normalization=T, 
                            community_detection = T)
save('dna_3.rdata')

# load day data
setwd("//data package/data")
load('dna_3.rdata')
tweets <- dna_3$tweets
g <- dna_3$g_actor
am <- dna_3$am
n_actors <- nrow(am)-length(unique(tweets$concept))
n_concepts <- length(unique(tweets$concept))
print(paste(n_actors, 'actors and ', n_concepts, 'concepts'))
table(V(g)$community)
dna_3$modularity

#plot parameters
clu_min_size <- 30
clu_no <- names(table(V(g)$community)[which(table(V(g)$community)>=clu_min_size)])
clu <- paste0('cluster_', clu_no)
filtered_concepts

#substantive position heatmap
df <- list()
for (i in 1:length(clu)){
  users <- V(g)$name[which(V(g)$community==clu_no[i])]
  x <- data.frame(colnames(am[which(rownames(am) %in% users),(n_actors+1):ncol(am)]),
                  clu[i],
                  colSums(am[which(rownames(am) %in% users),(n_actors+1):ncol(am)]) 
  )
  colnames(x) <- c('y', 'x', 'Frequency') 
  x <- x[which(x$y %in% filtered_concepts),]
  df[[i]] <- x
}
df <- do.call('rbind', df)
rownames(df) <- NULL

ggplot(df, aes(x, y, fill= Frequency)) + geom_tile() + xlab("") + ylab("") +
  scale_fill_gradient2(low="coral3", mid="white", high="aquamarine3") +
  theme_minimal()+
  theme(axis.text.x = element_text(angle = 90))+
  scale_x_discrete(position = "top")

#actor graph 
#agreement only (for plotting)
g <- delete.edges(g, which(E(g)$weight<0))
g <- delete.vertices(g, which(strength(g)==0))
#tie strength threshold
layout <- layout_with_fr(g)
tie_threshold=.60
g <- delete.edges(g, which(E(g)$weight<tie_threshold))
hist(E(g)$weight)
#set edge color gradient
percentile=seq(from=.01, to=1.01, by=.01)
E(g)$color <- NA
for (i in 1:length(percentile)){
  E(g)$color[which(E(g)$weight >= percentile[i] & E(g)$weight < percentile[i+1])] <- paste0('grey',i)  
}

plot(g, 
     vertex.size=(strength(g, weights=E(g)$weight))^(1/3),
     vertex.label=NA,
     vertex.label.color='black',
     vertex.label.family = 'Calibri',
     vertex.label.font = 2,
     vertex.color=colors()[V(g)$community*3],
     edge.color=E(g)$color,
     layout=layout)



#plot legend
lgnd <- cbind(1:length(unique(V(g)$community)), 
              colors()[unique(V(g)$community)*3])
lgnd <- cbind(clu, lgnd[as.numeric(clu_no), 2])
legend(x='left', 
       legend= lgnd[,1], 
       fill=lgnd[,2])
dev.off()


