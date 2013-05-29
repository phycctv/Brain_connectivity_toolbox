################################################################
# Compute the networks parameters for a given range of
# threshold.
# indegree, Lp, Cp, Q, gamma, lambda, sigma, Eglob, Eloc, Cost
# and the regional efficiency, regional local efficiency
################################################################

# first version : 30/08/2012
# last update 	: 12/10/2012
# from computeThresholdPenalizedEffControls_MST_Vaude.R
# from read_results_patients_Vaude.R
# from plot_mvt.R
# note: this version works with package igraph, version before 0.6
# if your version is older than 0.6, use package igraph0


#compute_Graph("/home/cindy/Bureau/","/home/cindy/Bureau/celiaOFF/celia090212withCSF/",78,"celia.090212.r01.withCSF_AllROIs","file_coord.txt")

compute_Graph <- function(Rpath,path,templBaseName,file_coord,compute.cor,graphs)# path endroit ou il ya les fichiers, Rpath endroit ou il y a les fichiers fonction de R
{
    serie_temp<-paste('func_ROI_',templBaseName,'_ts.txt',sep='')
	data.roi<-read.table(paste(path,'Functional/corrected_data',templBaseName,serie_temp,sep='/'))
	proc.length<-dim(data.roi)[1]
	n.regions<-dim(data.roi)[2]-1 # /!\ a changer selon le nb de regions souhaitees
	cat("nb_pt_tps ", proc.length, " nb_regions ", n.regions,"\n")

	source(paste(Rpath,'parameters.R',sep='/')) # utilise les param du fichiers param
	source(paste(Rpath,'evaluate_knn.R',sep='/')) # appel de la fonction
	
	#compute.cor<-0 # calcul des mat de correlation mettre a 0 pour ne pas calculer
	
	#graphs<-TRUE # calcul des graphs, FALSE pr ne pas faire tourner
	
	library('brainwaver')
	
######### modif: igraph or igrahp0
	library('igraph0') # commence a 1

######### DOSSIER DE SORTIE
	name.dir<-paste(path,'Graph_Measures',templBaseName,'',sep='/') # faire une boucle sur le path pr avoir un dossier par run
	
	system(paste('mkdir ',name.dir,sep='')) # Juste pour Unix (pour Windows dans le code Python)
	
	cat('serie_temp ',serie_temp,'n regions ',n.regions,' proc length ',proc.length,'\n')
	

	if(compute.cor){# si compute.cor vaut 1 on rentre dans le if
	    data.roi<-read.table(paste(path,'Functional/corrected_data',templBaseName,serie_temp,sep='/'))
	    data.roi<-as.matrix(data.roi)
##### modifications - 10/10/12
	# n.regions is given in function arguments
		data.roi<-data.roi[,1:n.regions] # prend le nb de region qu'on veut donc 78/79
	    
##### end of modifications
	    
	    cor.list<-const.cor.list(data.roi, method = method, wf = wf,
	                     n.levels = n.levels, boundary = boundary,
	                     save.wave = FALSE, export.data = FALSE) # calcul des mat

##### modifications - 09/10/12	
	### Test for zero on all the region ###
	# coef 0 for empty regions
	# special treatment for first and last region

		for(j in 1:n.regions){
	        if(sum(data.roi[,j])==0){
	            warning(paste('problem region',j,'equal to 0'))
				if(j ==1){
					for(k in 1:n.levels){
						cor.list[[k]][,j]<-c(1,rep(0,length((j+1):n.regions)))
			            cor.list[[k]][j,]<-c(1,rep(0,length((j+1):n.regions)))
					}
				}
				if(j==n.regions){
					for(k in 1:n.levels){
			            cor.list[[k]][,j]<-c(rep(0,length(1:(j-1))),1)
			            cor.list[[k]][j,]<-c(rep(0,length(1:(j-1))),1)
					}
				}
				else{
					for(k in 1:n.levels){
			           	cor.list[[k]][,j]<-c(rep(0,length(1:(j-1))),1,rep(0,length((j+1):n.regions)))
			            cor.list[[k]][j,]<-c(rep(0,length(1:(j-1))),1,rep(0,length((j+1):n.regions)))
			        }
				}
				
	        }
	    }

	# previous code
#	    for(j in 1:n.regions){
#	        if(sum(data.roi[,j])==0){
#	            warning(paste('problem region',j,'equal to 0'))
#	            for(k in 1:n.levels){
#	                cor.list[[k]][,j]<-c(rep(0,length(1:(j-1))),1,rep(0,length((j+1):n.regions)))
#	                cor.list[[k]][j,]<-c(rep(0,length(1:(j-1))),1,rep(0,length((j+1):n.regions)))
#	            }
#	
#	        }
#	    }

##### end of modifications

	### save the correlation matrices ###
	    for(i in 1:n.levels){

		    write.table(cor.list[[i]],paste(name.dir,'wave.cor.mat_n.levels_',i,'_n.regions_',n.regions,'.grey.matter.txt',sep=''),col.names=F,row.names=F,quote=F)
		    write.table(cor.list[[i+n.levels]],paste(name.dir,'wave.cor.mat.lower_n.levels_',i,'_n.regions_',n.regions,'.grey.matter.txt',sep=''),col.names=F,row.names=F,quote=F)
		    write.table(cor.list[[i+2*n.levels]],paste(name.dir,'wave.cor.mat.upper_n.levels_',i,'_n.regions_',n.regions,'.grey.matter.txt',sep=''),col.names=F,row.names=F,quote=F)
	    }
	}
	
#########################################################################################
### GRAPHS
	
	if(graphs){
	    coord<-paste(Rpath,file_coord,sep='/')
	    set1 <- read.table(coord, header=TRUE)
	    set3 <- array(0,c(3,90))
	    for(i in 1:3)
        set3[i,] <- set1[,i+1]
        
	    euclid <- 2 * dist(t(set3), method = "euclidean")
	    x.euclid <- as.matrix(euclid)
	    #### only for scale num.levels
        

	    cor.mat<-read.table(paste(name.dir,'wave.cor.mat_n.levels_',num.levels,'_n.regions_',n.regions,'.grey.matter.txt',sep=''))
	
	    cat(paste(name.dir,'wave.cor.mat_n.levels_',num.levels,'_n.regions_',n.regions,'.grey.matter.txt',sep=''),'\n') # affich la mat de correlation qu'on etudie
	
	    cor.mat<-as.matrix(cor.mat)
        
# parametres de base	
	    Eglob<-array(0,dim=c(length.nb.edges)) # efficacite global= plus court chemin 1 valeur par nb aretes
	    # moyenne sur le graphe de l'efficacite globale
	    Eloc<-array(0,dim=c(length.nb.edges))# moyenne sur le graphe de l'efficacite locale = clustering
	    tot.Eglob<-array(0,dim=c(n.regions,length.nb.edges)) # sur le total des regions 78X40
	    tot.Eloc<-array(0,dim=c(n.regions,length.nb.edges))
	    in.degree<-array(0,dim=c(n.regions,length.nb.edges))# degres

	    tot.nbedges<-array(0,dim=c(length.nb.edges))# nb d'aretes selectionnes en tout car pas exactement le nb demandé au seuil (si 400 peut etre 395, 402 etc)
	    tot.sup<-array(0,dim=c(length.nb.edges)) # valeur de correlation utilisee pr mettre le seuil (voir si pas tp faible ou pas tp fort)

## parametres de graph	    
	    Percolation<-array(0,dim=c(length.nb.edges))
	    total_distance_connections<-array(0,dim=c(length.nb.edges))
	    ratio_long_dist_connections<-array(0,dim=c(length.nb.edges))
	    max.nodes.removal<-n.regions
	    attack_robustness<-array(0,dim=c(max.nodes.removal,length.nb.edges))
	    attack_robustness_nodes<-array(0,dim=c(max.nodes.removal,length.nb.edges))

	    total_distance_connections<-array(0,dim=c(length.nb.edges))
	    ratio_long_dist_connections<-array(0,dim=c(length.nb.edges))
	    max.nodes.removal<-n.regions
	    attack_robustness<-array(0,dim=c(max.nodes.removal,length.nb.edges))
	    attack_robustness_nodes<-array(0,dim=c(max.nodes.removal,length.nb.edges))
	    total_distance_connections_nodes<-array(0,dim=c(n.regions,length.nb.edges))
	    
	    fastgreedy.merges<-vector('list',length.nb.edges) # modularite
	    fastgreedy.modularity<-vector('list',length.nb.edges)
# matrice d'adjacence (meme taille mat corr) => meme VARIANCE pr ttes les paires, calculee a partir du nb de pts ds la serie temporelle
	    adj.mat<-const.adj.mat(cor.mat, thresh = p, sup = 0.000000001, proc.length = proc.length,num.levels=num.levels) #on teste si c sup a zero
	    
################### /!\ /!\ /!\ A mettre en relation avec le nb d'aretes qu'on a choisi d'extraire au debut		
	corr_zero<-sum(adj.mat)/2 # nb de correlation signif != 0 ( ne depend plus du seuil, nb de correlation qu'on a le dt d'extraire pr une mat donnee)
	    cat('nb correlation signif diff zero ', c(sum(adj.mat)/2),'\n') # affiche le nb de correlation signif
	
	abs.cor.mat<-abs(cor.mat)
	abs.cor.mat[adj.mat==1]->min_signif
	min(min_signif)
######################## boucle sur le nb d'aretes
	    count<-1
	    
	    cost<-round(num.nb.edges/4005*100*(n.regions*(n.regions-1))/2/100) # nb d'aretes en % par rapport au nb total possible tous les 2.5% on commence a 5% car sinon 75 aretes pas suffisant pr minimum spaning tree

# on ne garde pas les regions deconnectees donc on cree le minimum spanning tree    
	    for(i in cost){
		if (i<=corr_zero){
	        # OK
	        #### MST
	        diag(abs.cor.mat)<-rep(0,n.regions)
	        MST<-mst(abs.cor.mat)>0 ### ajacency matrix with MST connextions
	        MST_adj_mat<-MST
	        MST_adj_mat[lower.tri(MST_adj_mat)]<-0
	        adj.mat<-matrix(0,n.regions,n.regions)
	        pvalue.cor <- abs(cor.mat[upper.tri(cor.mat)])
	        MST_no_edges<-(MST_adj_mat[upper.tri(MST_adj_mat)]==0)
	        cor_wo_MST<-pvalue.cor[MST_no_edges]
	        
	        pvalue.thresh <- sort(cor_wo_MST,decreasing=T)[i-(n.regions-1)] ### only valid for number of edges greater than n.regions
	        n.sup<-pvalue.thresh # plus petite valeur de corr pr obtenir i aretes
	        test.sign <- (pvalue.cor >= pvalue.thresh)
	        l <- 1
	        for (k in 2:(n.regions)) {
	            for (q in 1:(k - 1)) {
	                if ((test.sign[l]) == TRUE) {
	                    adj.mat[k, q] <- 1
	                }
	                else{
	                    if(MST[k,q]==1){ 
	                        adj.mat[k, q] <- 1
	                        cat('MST edges',k,' ',q,' ',abs.cor.mat[k,q],'\n')
	                    }
	                }
	                l <- l + 1
	            }
	        }

	        adj.mat<-adj.mat+t(adj.mat) # matrice d'adjacence avec i aretes premier a 5%=150 aretes
	
	        print(c(i,"*****",n.sup))
	        
	        tot.sup[count]<-n.sup
	        
	        tot.nbedges[count]<-sum(adj.mat)/2
	        in.degree[,count]<-rowSums(adj.mat)
	        
	        tmp<-global.efficiency(adj.mat,weight.mat=matrix(1,n.regions,n.regions))
	        Eglob[count]<-tmp$eff
	        tot.Eglob[,count]<-tmp$nodal.eff
	        
	        tmp1<-local.efficiency(adj.mat,weight.mat=matrix(1,n.regions,n.regions))

	        Eloc[count]<-tmp1$eff
	        
	        tot.Eloc[,count]<-tmp1$loc.eff
	        
	        tmp2<-small.world(adj.mat, dat = "reduced", distance = "norm", coord = 0, export.data = FALSE)
	        
	        Percolation[count]<-tmp2$size.large.connex
	        
	        total_distance_connections[count]<-sum(adj.mat*x.euclid)

	        tmp3<-sum(adj.mat*(x.euclid>85))
	        
	        ratio_long_dist_connections[count]<-100*tmp3/sum(adj.mat)/2
	        
	        tmp4<-targeted.attack(adj.mat,max.nodes.removal)
	        
	        attack_robustness[,count]<-tmp4$size.large.connex
	        attack_robustness_nodes[,count]<-tmp4$rem.nodes
	        
	        total_distance_connections_nodes[,count]<-rowSums(adj.mat*x.euclid)

	        tmp.graph<-graph.adjacency(adjmatrix=adj.mat,mode='undirected',weighted=NULL,diag=F)
	        
	        res1<-fastgreedy.community(tmp.graph)
	        fastgreedy.merges[[count]]<-res1$merges
	        fastgreedy.modularity[[count]]<-res1$modularity
	        
	        count<-count+1
	
	    }
	}
	    write.table(Eglob,paste(name.dir,'Eglob_mean_n.levels_',num.levels,'_n.regions_',n.regions, '.mst.grey.matter.txt',sep=''),col.names=F,row.names=F,quote=F)
	    
	    write.table(Eloc,paste(name.dir,'Eloc_mean_n.levels_',num.levels,'_n.regions_',n.regions, '.mst.grey.matter.txt',sep=''),col.names=F,row.names=F,quote=F)
	    
	    write.table(tot.sup,paste(name.dir,'Thresh_mean_n.levels_',num.levels,'_n.regions_',n.regions, '.mst.grey.matter.txt',sep=''),col.names=F,row.names=F,quote=F)
	    
	    write.table(tot.nbedges,paste(name.dir,'Nb.edges_mean_n.levels_',num.levels,'_n.regions_',n.regions,'.mst.grey.matter.txt',sep=''),col.names=F,row.names=F,quote=F)
	    
	    write.table(in.degree,paste(name.dir,'In.degree_n.levels_',num.levels,'_n.regions_',n.regions, '.mst.grey.matter.txt',sep=''),col.names=F,row.names=F,quote=F)
	    
	    
	    write.table(tot.Eglob,paste(name.dir,'Eglob_n.levels_',num.levels,'_n.regions_',n.regions, '.mst.grey.matter.txt',sep=''),col.names=F,row.names=F,quote=F)
	    
	    write.table(tot.Eloc,paste(name.dir,'Eloc_n.levels_',num.levels,'_n.regions_',n.regions, '.mst.grey.matter.txt',sep=''),col.names=F,row.names=F,quote=F)
	    
	    
	    write.table(c(corr_zero,min_signif),paste(name.dir,'corr_zero_n.levels_',num.levels,'_n.regions_',n.regions, '.mst.grey.matter.txt',sep=''),col.names=F,row.names=F,quote=F)
	    
	    write.table(Percolation,paste(name.dir,'Percolation_n.levels_',num.levels,'_n.regions_', n.regions,'.mst.grey.matter.txt',sep=''),col.names=F,row.names=F,quote=F)
	    
	    write.table(total_distance_connections,paste(name.dir,'total_distance_connections_n.levels_', num.levels,'_n.regions_',n.regions,'.mst.grey.matter.txt',sep=''),col.names=F,row.names=F,quote=F)
	    
	    write.table(ratio_long_dist_connections,paste(name.dir,'ratio_long_dist_connections_n.levels_' ,num.levels,'_n.regions_',n.regions,'.mst.grey.matter.txt',sep=''),col.names=F,row.names=F,quote=F)
	    
	    write.table(attack_robustness,paste(name.dir,'attack_robustness_n.levels_',num.levels, '_n.regions_',n.regions,'.mst.grey.matter.txt',sep=''),col.names=F,row.names=F,quote=F)
	    
	    write.table(attack_robustness_nodes,paste(name.dir,'attack_robustness_nodes_n.levels_', num.levels,'_n.regions_',n.regions,'.mst.grey.matter.txt',sep=''),col.names=F,row.names=F,quote=F)
	  
	    write.table(total_distance_connections_nodes,paste(name.dir, 'total_distance_connections_nodes_n.levels_',num.levels,'_n.regions_',n.regions,'.mst.grey.matter.txt',sep=''),col.names=F,row.names=F,quote=F)
	
	    save(fastgreedy.merges,file=paste(name.dir,'fastgreedy.merges_n.levels_',num.levels, '_n.regions_',n.regions,'.mst.grey.matter.txt',sep=''))
	    save(fastgreedy.modularity,file=paste(name.dir,'fastgreedy.modularity_n.levels_',num.levels, '_n.regions_',n.regions,'.mst.grey.matter.txt',sep=''))
	    
	}
}

#############################################################################################################################################

read_results <- function(Rpath,path,n.regions,file_coord,proc.length){
# from read_results_patients_Vaude.R
	
	library(Cairo)
######### modif: igraph or igrahp0

	library('igraph0')
#########
	
	source(paste(Rpath,'parameters.R',sep='/'))
	source(paste(Rpath,'evaluate_knn.R',sep='/'))
	#n.regions<-90	#### modif 10/10/12
	
	a<-unlist(strsplit(path, "/"))# recupere le nom du fichier pr en faire un titre
	print(tail(a,1))
	ref<-tail(a,1)
	b<-unlist(strsplit(ref, ""))
	
	Sujet <- ""
	
	coord<-paste(Rpath,file_coord,sep='/')
	
	set2 <- read.table(coord)
	
	euclid <- 2 * dist(set2, method = "euclidean")
	
	x.euclid <- as.matrix(euclid)
	
	index <- c(1:(n.regions/2))*2 # regions gauches et droites
	set2 <- as.matrix(set2)
	set2[index,c(2,3)] <- set2[index,c(2,3)] + 10 #	decale les pts superposes sur le graphe
	
	n.levels<-num.levels
	
	name.dir<-paste(path,"Graph_Measures/",sep="/") # sortie

#lecture mat corr
	cor.mat<-read.table(paste(name.dir,'wave.cor.mat_n.levels_',num.levels,'_n.regions_',n.regions,'.grey.matter.txt',sep=''))
	cor.mat<-as.matrix(cor.mat)
	abs.cor.mat<-abs(cor.mat) # val abs

	adj.mat<-const.adj.mat(cor.mat, thresh = p, sup = 0.000000001, proc.length = proc.length,num.levels=num.levels) #on teste si c sup a zero    	
	corr_zero<-sum(adj.mat)/2 # nb

	cost<-round(num.nb.edges/4005*100*(n.regions*(n.regions-1))/2/100)# vect %

	for(dim.edges in cost){
		if (dim.edges < corr_zero){
	    CairoPDF(file=paste(name.dir,'graph_',Sujet,ref,'_dim',dim.edges,'.pdf',sep=''),width = 14, height = 8,family='times')
	    par(mar=c(4.5, 0.1, 5, 0.3),mfrow=c(1,2))
	    
	    # RECALCULE Matrice d'adjacence
	    diag(abs.cor.mat)<-rep(0,n.regions)
	    MST<-mst(abs.cor.mat)>0 ### ajacency matrix with MST connextions
	    MST_adj_mat<-MST
	    MST_adj_mat[lower.tri(MST_adj_mat)]<-0
	    
	    adj.mat<-matrix(0,n.regions,n.regions)
	    pvalue.cor <- abs(cor.mat[upper.tri(cor.mat)])
	    MST_no_edges<-(MST_adj_mat[upper.tri(MST_adj_mat)]==0)
	    
	    cor_wo_MST<-pvalue.cor[MST_no_edges]
	    
	    pvalue.thresh <- sort(cor_wo_MST,decreasing=T)[dim.edges-(n.regions-1)] ### only valid for number of edges greater than n.regions
	    
	    n.sup<-pvalue.thresh
	    
	    test.sign <- (pvalue.cor >= pvalue.thresh)
	    l <- 1
	    for (k in 2:(n.regions)) {
	        for (q in 1:(k - 1)) {
	            if ((test.sign[l]) == TRUE) {
	                adj.mat[k, q] <- 1
	            }else{
	                if(MST[k,q]==1){ adj.mat[k, q] <- 1
	                    #cat('MST edges',k,' ',q,'\n')
	                }
	            }
	            l <- l + 1
	        }
	    }
	    adj.mat<-adj.mat+t(adj.mat)
	    
	    
	    x.coord<-1 #i
	    y.coord<-2 # j
	    
	    plot(set2[,x.coord], set2[,y.coord], type = "p",xlab= "", ylab="",cex.lab=2,asp=1,ylim=c(min(set2[,y.coord]),max(set2[,y.coord])),xlim=c(min(set2[,x.coord]),max(set2[,x.coord])),xaxt='n',yaxt='n',bty='n',main=paste(Sujet,ref,dim.edges),cex=0.5,pch=16,cex.main=2) #points noirs
	    
	   ### text(labels.coord[1,],labels.coord[2,],labels.names,cex = 1)
	    
	    for(kk in 2:(n.regions)){
	        for(q in 1:(kk-1)){
	                
	            if(adj.mat[kk,q]==1)
	            {
	                        
	                if(x.euclid[kk,q]>85) visu <- "blue" #longues/courtes arretes, A CHANGER
	                    else visu <- "red"
	                lines(c(set2[kk,x.coord], set2[q,x.coord]), c(set2[kk,y.coord], set2[q,y.coord]), col = visu,lw=2)
	            }
	    
	        }
	    }
	    
	    x.coord<-2 #j
	    y.coord<-3 #k

	    plot(set2[,x.coord], set2[,y.coord], type = "p",xlab= "", ylab="",cex.lab=2,asp=1,ylim=c(min(set2[,y.coord]),max(set2[,y.coord])),xlim=c(min(set2[,x.coord]),max(set2[,x.coord])),xaxt='n',yaxt='n',bty='n',main=paste(Sujet,ref,dim.edges),cex=0.5,pch=16,cex.main=2) #points noirs
	    
	    
	    #text(labels.coord[1,],labels.coord[2,],labels.names,cex = 2)
	    
	    for(kk in 2:(n.regions)){
	        for(q in 1:(kk-1)){
	                
	            if(adj.mat[kk,q]==1)
	            {
	                        
	                if(x.euclid[kk,q]>85) visu <- "blue" 
	                    else visu <- "red"
	                lines(c(set2[kk,x.coord], set2[q,x.coord]), c(set2[kk,y.coord], set2[q,y.coord]), col = visu,lw=2)
	            }
	    
	        }
	    }
	    dev.off()
	}
	
}
}
#############################################################################################################################################

plot_mvt <- function(Rpath,path){
# from plot_mvt.R
	
	library(Cairo)
	
	a<-unlist(strsplit(path, "/"))
	print(tail(a,1))
	ref<-tail(a,1)
	b<-unlist(strsplit(ref, ""))

	Sujet <- ""
	print(paste(path,'/Graph_Measures/mvt_zoom_',Sujet,ref,'.pdf',sep=''))
	pdf(paste(path,'/Graph_Measures/mvt_zoom_',Sujet,ref,'.pdf',sep=''))
	par(mfrow=c(2,1))	
	
	path.mov<-list.files(path=paste(path,'Functional/Realigned/',sep='/'),pattern=glob2rx("rp*.txt"))
	mvt <- read.table(paste(path,'Functional/Realigned/',path.mov,sep='/'), header=FALSE)# fichiers des param de mvts
	
	ymin<-min(mvt[,1:3])-0.05
	ymax<-max(mvt[,1:3])+0.05
	
	plot(mvt[,1],type='l',col='blue',ylim=c(ymin,ymax),ylab='mm',xlab='image',main=paste(ref,'\nTranslation',sep=''))
	lines(mvt[,2],type='l',col='green')
	lines(mvt[,3],type='l',col='red')
	legend(x='topleft',legend=c('x','y','z'),col=c('blue','green','red'),lty=1)
	
	ymin<-min(mvt[,4:6]*180/pi)-0.05
	ymax<-max(mvt[,4:6]*180/pi)+0.05
	plot(mvt[,4]*180/pi,type='l',col='blue',ylim=c(ymin,ymax),ylab='degrees',xlab='image',main=paste('Rotation'))
	lines(mvt[,5]*180/pi,type='l',col='green')
	lines(mvt[,6]*180/pi,type='l',col='red')
	legend(x='topleft',legend=c('pitch','roll','yaw'),col=c('blue','green','red'),lty=1)
	dev.off()
	
	CairoPDF(file=paste(path,'/Graph_Measures/mvt_',ref,'.pdf',sep=''),width = 15, height = 11)
	par(mfrow=c(1,2))
	print(paste(path,'/Graph_Measures/mvt_',Sujet,ref,'.pdf',sep=''))
	
	ymin<- -20
	ymax<-20
	
	plot(mvt[,1],type='l',col='blue',ylim=c(ymin,ymax),ylab='mm',xlab='image',main=paste(ref,'\nTranslation',sep=''))
	lines(mvt[,2],type='l',col='green')
	lines(mvt[,3],type='l',col='red')
	vec<-rep(1,400)
	lines(2*vec,type='l',col='cyan')
	lines(-2*vec,type='l',col='cyan')
	legend(x='topleft',legend=c('x','y','z'),col=c('blue','green','red'),lty=1)
	
	ymin<- -20
	ymax<- 20
	
	plot(mvt[,4]*180/pi,type='l',col='blue',ylim=c(ymin,ymax),ylab='degrees',xlab='image',main=paste('Rotation'))
	lines(mvt[,5]*180/pi,type='l',col='green')
	lines(mvt[,6]*180/pi,type='l',col='red')
	lines(2*vec,type='l',col='cyan')
	lines(-2*vec,type='l',col='cyan')
	legend(x='topleft',legend=c('pitch','roll','yaw'),col=c('blue','green','red'),lty=1)
	dev.off()

}
