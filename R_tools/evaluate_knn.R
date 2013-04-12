###########COPY BELOW INTO R#############

knn  <- function(graph){
##
## k-nearest neighbours with the weights as correlations
##
## graph = absolute value of correlation matrices 
##         with 0 on the diagonal to avoid the loops

## f<-as.matrix(read.table('Control_0/wave.cor.mat_n.levels_2_n.regions_90.white.matter.txt'))
## diag(f)<-0; f<-abs(f)
## graph<-f

graphi <- graph
thcg <- graph[,]
thcg[,] <- 0
diag(graphi) <- 0
diag(graph) <- 0
thcgi <- 1
k <- 0
as <- vector()

while(sum(graph) > 0){

k <- k + 1

a <- cbind(sort(apply(graphi, 1, function(x) sort(x, decreasing = T))[k,], index.return = T, decreasing = T)$ix, (apply(graphi, 1, function(x) (sort(x, decreasing = T, index.return = T)$ix))[k,])[sort(apply(graphi, 1, function(x) sort(x, decreasing = T))[k,], index.return = T, decreasing = T)$ix])[ sort(apply(graphi, 1, function(x) sort(x, decreasing = T))[k,], index.return = T, decreasing = T)$x  > 0 ,]

###  apply(graphi, 1, function(x) sort(x, decreasing = T))$x[k,] the highest correlations for each region
###  apply(graphi, 1, function(x) sort(x, decreasing = T))$ix[k,] the corresponding region with the highest correlations 
### sort(apply(graphi, 1, function(x) sort(x, decreasing = T))[k,], index.return = T, decreasing = T)$ix the regions with the highest coirrelations
## (apply(graphi, 1, function(x) (sort(x, decreasing = T, index.return = T)$ix))[k,])[sort(apply(graphi, 1, function(x) sort(x, decreasing = T))[k,], index.return = T, decreasing = T)$ix] the correponding regions of the highest correlations
## Question : what's the role of >0 ? : to remove the 0 correlations where no link can be defined


if(is.matrix(a)){
aa <- rbind(a, cbind(a[,2], a[,1]))
} else{
aa <- rbind(aa, aa[c(2,1)]) ## does aa always exist ?
}


if(length(as) > 1){
ad <- rbind(aa, as, cbind(as[,2], as[,1]))
} else{
ad <- aa
}


if(is.matrix(aa)){

iii <- c(1:(length(aa[,1])/2), (1:(length(aa[,1])/2) + .5))[(!duplicated(ad, fromLast = T))[1:length(aa[,1])]]

aa <- ad[(!duplicated(ad, fromLast = T))[1:length(aa[,1])],]
## remove all the pairs related twice 

iii <- sort(iii, index.return = T)$ix

aa <- aa[iii,] ## to get all the pairs


} else{
aa <- ad[(!duplicated(ad, fromLast = T))[1,],]
}




if(length(aa) > 2){
aa <- aa[aa[,1] > aa[,2],] ## to get only one set of pair 
}
as <- rbind(as, aa)


if(length(aa) == 2){
thcg[aa[1], aa[2]] <- thcgi
thcg[aa[2], aa[1]] <- thcgi
thcgi <- thcgi + 1
} 

if(length(aa) > 2){


for(i in 1:nrow(aa)){
thcg[aa[i,1], aa[i,2]] <- thcgi
thcg[aa[i,2], aa[i,1]] <- thcgi
thcgi <- thcgi + 1
}  } #if, else
 
graph[thcg > 0] <- 0
}
return(thcg)
}



####mst

mst <- function(graph){

## graph is the correlation matrix 


corTs2 <- abs(graph)
#corTs2 <- abs(cor(t(wavTs2)))[-badindex,-badindex]

diag(corTs2) <- 0 # 0 on the diagonal to avoid the loops

thc <- corTs2
thc[,] <- 0


g3 <- graph.adjacency(1-corTs2, weighted = T, mode = 'lower', diag = F)

G4 <- minimum.spanning.tree(g3)

for(i in 1:(dim(graph)[1])){
thc[i, neighbors(G4, i -1) + 1] <- 1 ### to construct the correspondin adjacency matrix
}

#insert stuff from GT
corTs2 <- corTs2*thc
diag(corTs2) <- 0
corTs2[upper.tri(corTs2)] <- 0
index <- sort(corTs2, index.return = T, decreasing = T)
ttt <- corTs2
ttt[,] <- 0
ttt[index[[2]][1:sum(corTs2 > 0)]] <- 1:sum(corTs2 > 0) ## 90x90 matrix
ttt[upper.tri(ttt)] <- t(ttt)[upper.tri(ttt)] ## so as ttt is symmetric
return(ttt)

### the matrix with the MST connections with a given order related to the levels of correlations 

}



combine.mst <- function(g.mst = tm, g.o = ata){

### To combine two graphs 

g.r <- g.mst
i.mst <- g.mst > 0 ## adjacency matrix of g.mst

g.o[i.mst] <- Inf  ### wehted matrix without the MST connexions

g.o[g.o==0]<-Inf ### to get rid of the edges where the correlation is exactly equal to 0

diag(g.o) <- Inf

g.o[upper.tri(g.o)] <- Inf ## to get rid of the upper triangle

index <- sort(g.o, index.return = T)

g.ra <- g.r
g.ra[,] <- 0
g.ra[index$ix[1:sum(!is.infinite(g.o))]] <- (((sum(g.mst > 0))/2) + 1):(((sum(g.mst > 0))/2) + length(index$ix[1:sum(!is.infinite(g.o))])) ## 90:4005
g.ra[upper.tri(g.ra)] <- t(g.ra)[upper.tri(g.ra)] ### so as the matrix is symmetric
g.r <- g.r + g.ra  ## the ordered edges + MST
return(g.r)

## The 1:89 are the edges from the MST and after just adding the edges in the order of the correlations

}

extract <- function(graph, index = index, edge = 1){
diag(graph) <- 0
newindex <- index < (edge + 1)
thc <- graph
thc[,] <- 0
thc[newindex] <- 1
graphnew <- graph*thc  ## only edge as number of edges
return(graphnew)
}
