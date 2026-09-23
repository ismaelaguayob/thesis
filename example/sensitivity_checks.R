#this scrips performs a sensitivity check to see the difference in edge weights between two normalizing procedures
#the first one procedure, here named the "posterior" approach, first constructs a weighted adjacency matrix and then normalizes the edges
#the second procedure (commonly used in the software discourse network analyzer), here named the "prior" approach,
#separately constructs and normalizes the conflict and congruence networks, and subtracts the difference in edge weights. 

get_matrices <- function(am, n_actors, n_concepts, type='both'){
  
  #function to transpose multidimensional arrays
  tarray <- function(x) aperm(x, rev(seq_along(dim(x))))
        
  #three-dimensional matrix multiplication
  #multiplies adjacency matrix with its transpose (like %*%) without summing multiplicatives
  #instead, each multiplication is saved in the third dimension
  transpose3 <- tarray(array(unlist(lapply(1:nrow(am), function(j){
                              lapply(1:nrow(am), function(i){
                                am[i,] * am[,j]
                              })
                            })), 
                            dim=c(nrow(am), nrow(am), nrow(am) ), 
                            dimnames = list(rownames(am),
                                            rownames(am), 
                                            rownames(am) 
                            )))
  
  #actor slice:
  #am3[1:n_actors,1:n_actors,]
  #concept slice:
  #am3[(n_actors+1):nrow(am3),(n_actors+1):nrow(am3),]
  
  #sum multiplicatives in third dimension
  #after execution the result is again equivalent to a simple matrix multiplication
  flatten_matrix <- function(m){do.call("rbind", lapply(1:ncol(m), function(j){rowSums(m[,j,])}))}
  
  #normalizing function (jaccard):
  #divide the transposed adjacency matrix by a weight matrix
  #weights equal the average number of concepts used by the two actors (either positive or negative)
  normalize <- function(transpose, am){
    print('weighting...')
    #computing weight matrix w
    w <- do.call("cbind", lapply(1:ncol(transpose), function(i){rowSums(abs(am)) + colSums(abs(am))[i]}))/2
    transpose <- transpose / w
    #correct division by zero
    transpose[is.nan(transpose)] <- 0
    return(round(transpose,3))
    
  }

  if (type == 'congruence'){
    transpose3[transpose3<0] <- 0
  }
  if (type == 'conflict'){
    am
    transpose3[transpose3>0] <- 0
  
  }
  
  transpose <- flatten_matrix(transpose3)
  transpose <- normalize(transpose, am)
  actor <- transpose[1:n_actors, 1:n_actors]
  concept <- transpose[(n_actors+1):nrow(transpose), (n_actors+1):nrow(transpose)]
  
  rtrn <- list(actor, concept)
  names(rtrn) <- c('actor', 'concept')
  return(rtrn)
  

}
##########################################
##########################################
####           TOY EXAMPLE            ####
##########################################
##########################################
am <- matrix(c( 0, 0, 0,-1, 0, 1,
                0, 0, 0, 1, 1, 0,
                0, 0, 0, 1, 1, 1,
                -1, 1, 1, 0, 0, 0,
                0, 1, 1, 0, 0, 0,
                1, 0, 1, 0, 0, 0), 
             ncol=6, nrow=6, byrow = T)
rownames(am) <- colnames(am) <- c('a', 'b', 'c', 'A', 'B', 'C')
n_actors=3
n_concepts=3
##########################################
##  METHOD 1: posterior normalization   ##
##########################################

total_adoption <- get_matrices(am, n_actors=3, n_concepts=3)
total_adoption$actor

##########################################
##  METHOD 2: prior normalization       ##
##########################################


congruence <- get_matrices(am, n_actors=3, n_concepts=3, type = 'congruence')
conflict <- get_matrices(am, n_actors=3, n_concepts=3, type = 'conflict') 

co_adoption <- list()
co_adoption$actor <- congruence$actor + conflict$actor
co_adoption$actor

table(total_adoption$actor == co_adoption$actor)
#results are exactly the same

##########################################
##########################################
####   REPLICATION WITH REAL DATA     ####
##########################################
##########################################
setwd(paste0("//data package/data"))
load('dna_1.rdata')
am <- dna_1$am
n_actors = 494
n_concepts = 42

##########################################
##  METHOD 1: posterior normalization   ##
##########################################

total_adoption_day1 <- get_matrices(am, n_actors, n_concepts)
total_adoption_day1$actor[1:10,1:10]

##########################################
##  METHOD 2: prior normalization       ##
##########################################

congruence <- get_matrices(am, n_actors, n_concepts, type = 'congruence')
conflict <- get_matrices(am, n_actors, n_concepts, type = 'conflict') 

co_adoption_day1 <- list()
co_adoption_day1$actor <- congruence$actor + conflict$actor
co_adoption_day1$actor[1:10,1:10]


#results are the same, except for a few minor rounding errors (in the 100ths)
table(total_adoption_day1$actor == co_adoption_day1$actor)
total_adoption_day1$actor[total_adoption_day1$actor != co_adoption_day1$actor]
co_adoption_day1$actor[co_adoption_day1$actor != total_adoption_day1$actor]
