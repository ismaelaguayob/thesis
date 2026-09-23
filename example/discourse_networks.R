## function to perform DNA with different specifications
#output: 
#  actor congruence (conflict) graph including community membership 
#  concept congruence (conflict) graph



discourse_networks <- function(dat, normalization=T, community_detection=T){

  #############################
  ##  create claims dataset  ##
  #############################
  
  claim_1 <- dat[which(!dat$Argument1 %in% ""),
                 c("id", "user", "Argument1", "Position.1")]
  claim_2 <- dat[which(!dat$Argument2 %in% ""),
                 c("id", "user", "Argument2", "Position.2")]
  claim_3 <- dat[which(!dat$Argument3 %in% ""),
                 c("id", "user", "Argument3", "Position.3")]
  names(claim_1) <- names(claim_2) <- names(claim_3) <- c("id", "user", "concept", "position")
  tweets <- as.data.frame(rbind(claim_1, claim_2, claim_3))
  tweets$position <- tolower(tweets$position)
  tweets$concept <- tolower(tweets$concept)
  
  remove_space <- function(x){
    spaced <- x[which(grepl(" ", x))]
    spaced[which(regexpr(' ', spaced)==nchar(spaced))] <- gsub(' ', '', spaced[which(regexpr(' ', spaced)==nchar(spaced))])
    x[which(grepl(" ", x))] <- spaced
    return(x)
  }
  tweets$concept <- remove_space(tweets$concept)
  tweets$position <- remove_space(tweets$position)
  
  n_actors <- length(unique(tweets$user))
  print(paste('number of actors:', n_actors))
  n_concepts <- length(unique(tweets$concept))
  print(paste('number of concepts:', n_concepts))
  
  print(paste("missing positions:" , length(which(tweets$position==""))))
  tweets <- tweets[which(tweets$position!=""),]
  print(paste("missing users:" , length(which(tweets$user==""))))
  tweets <- tweets[which(tweets$user!=""),]
  print(table(tweets$concept, tweets$position))
    
  #############################
  ##    adjacency matrix     ##
  #############################
  
  library(igraph)
  ag <- graph_from_data_frame(tweets[,2:4], directed=F)
  
  E(ag)$weight <- NA
  E(ag)$weight[which(E(ag)$position == 'neutral')] <- 0
  
  E(ag)$weight[which(E(ag)$position == 'pro')] <- 1
  E(ag)$weight[which(E(ag)$position == 'con')] <- -1
  

  am <- as.matrix(as_adjacency_matrix(ag, attr='weight'))
  
  #set two-mode ties to {-1,0,1} for easier interpretation and avoid inflating ties with "supervocal" participants
  #this sets a maximum user mention of each argument to 1: users either adopt it (either postively or negatively) or they dont. 
  am[which(am>0)] <- 1
  am[which(am<0)] <- -1
  
  ag <- graph_from_adjacency_matrix(am, weighted = T)
  print('total postive and negative mentions:')
  print(table(E(ag)$weight))
  
  print('missing tie weights (to be deleted):')
  print(E(ag)[which(is.na(E(ag)$weight))])
  ag <- delete_edges(ag, which(is.na(E(ag)$weight)))

  ###################################
  ##   concept and actor graphs    ##
  ###################################

  transpose <- am %*% t(am)
    
  #function to normalize graphs:
  #divide the transposed adjacency matrix by a weight matrix
  #weights equal the average number of different concepts the two actors use (either in a positive or negative way)
  if (normalization == T){
    print('weighting...')
    w <- do.call("cbind", lapply(1:ncol(am), function(i){rowSums(abs(am)) + colSums(abs(am))[i]}))/2
    transpose <- transpose / w
    transpose[is.nan(transpose)] <- 0
  }
  
  #matrix objects
  actor <- transpose[1:(n_actors-1), 1:(n_actors-1)]
  concept <- transpose[(nrow(transpose)-n_concepts+2):nrow(transpose), (ncol(transpose)-n_concepts+2):ncol(transpose)]

  #graph objects
  g_actor <- graph_from_adjacency_matrix(actor, weighted = T, mode='lower')
  g_actor <- simplify(g_actor)
  
  g_concept <- graph_from_adjacency_matrix(concept, weighted = T, mode='lower')
  g_concept <- simplify(g_concept)


  ########################
  ## detect communities ##
  ########################
  if (community_detection == T){
    #remove isolates
    print(paste(length(which(strength(g_actor)==0)), 'isolated (or ambivalent) actors deleted for community detection'))
    g_actor <- delete_vertices(g_actor, which(strength(g_actor)==0))
    
    c <- spinglass.community(g_actor, weights=E(g_actor)$normalized, implementation='neg', update.rule='simple', gamma = 1, gamma.minus = 1)
    V(g_actor)$community <- membership(c)
    print(paste('modularity:', round(c$modularity,3)))
  
  }

  out <- list(tweets, am, g_actor, round(c$modularity,3), g_concept)
  names(out) <- c('tweets', 'am', 'g_actor', 'modularity', 'g_concept')


  return(out)
}


