# first version : 	30/08/2012
# last update : 	10/10/2012
# from const_time_serie_template_patients_oro_nifti_functional_Vaude.R

extractTS <- function(Rpath,path0,path1,templBaseName){

	library('oro.nifti')
	
	# only template templBaseName
	
	# Original AAL
	#location<-read.table(paste(Rpath,paste(c(templBaseName),'txt',sep='.'),sep='/'),header=FALSE)
	#n.regions<-dim(location)[1]
	#noms <- location[,2]
	#location<-location[,3]
	name.long.temp<-paste('natw',templBaseName,sep="")
	name.ts<-paste('func_ROI_',templBaseName,sep="")
	

	# only one patient

	name.temp<-list.files(path=paste(path1,'Anat/Atlased/',sep='/'),pattern=glob2rx(paste(name.long.temp,"*.nii",sep='')))
	vol.template<-readNIfTI(paste(path1,'Anat/Atlased/',name.temp,sep='/'),reorient=F)
    location<-unique(as.vector(vol.template))
    location<-location[location!=0]
    n.regions<-length(location)			
    
	name.grey.matter<-list.files(path=paste(path1,'Anat/Segmented/',sep='/'),pattern=glob2rx("rc1*.nii"))
	vol.grey.matter<-readNIfTI(paste(path1,'Anat/Segmented/',name.grey.matter,sep='/'),reorient=F)

	list.of.in.files<-list.files(path=paste(path1,'Functional/Realigned/',sep='/'),pattern=glob2rx("r*.nii"))
	cat(list.of.in.files[1],'\n')
	length.proc<-length(list.of.in.files)

	# initialization
    print('Initialisation folders')
    

	for(i in 1:n.regions){

		name.txt<-paste(paste(path1,'Functional/data',templBaseName,'',sep='/'),name.ts,'_voxels_time_series_region_',i,'.txt',sep='')

		write.table(paste("Time series of each voxel for region",i,' ',sep=''),name.txt,quote=FALSE,col.names=FALSE,row.names=FALSE,eol=" ")
		write.table(" ",name.txt,quote=FALSE,col.names=FALSE,row.names=FALSE,eol="\n",append=TRUE)
		name.matter.txt<-paste(paste(path1,'Functional/grey_matter_data',templBaseName,'',sep='/'),'grey_matter_',name.ts,'_voxels_time_series_region_',i,'.txt',sep='')

		write.table(paste("Grey matter coefficients for region",i,' ',sep=''),name.matter.txt,quote=FALSE,col.names=FALSE,row.names=FALSE,eol=" ")
		write.table(" ",name.matter.txt,quote=FALSE,col.names=FALSE,row.names=FALSE,eol="\n",append=TRUE)

		index<-which(vol.template==location[i],arr.ind=TRUE)
		size.r<-dim(index)[1]
		tmp<-vol.grey.matter[index]
		tmp[is.na(tmp)]<-0
		write.table(c(tmp),name.matter.txt,quote=FALSE,col.names=FALSE,row.names=FALSE,append=TRUE,eol=" ")
		write.table(" ",name.matter.txt,quote=FALSE,col.names=FALSE,row.names=FALSE,eol="\n",append=TRUE)
		
		name.index.txt<-paste(paste(path1,'Functional/index',templBaseName,'',sep='/'),'index_',name.ts,'_voxels_time_series_region_',i,'.txt',sep='')
		
		write.table(paste("Voxels coordinates for region",i,sep=''),name.index.txt,quote=FALSE,col.names=FALSE,row.names=FALSE,eol=" ")
		write.table(" ",name.index.txt,quote=FALSE,col.names=FALSE,row.names=FALSE,eol="\n",append=TRUE)
		
		for(j in 1:3){
               write.table(c(index[,j]),name.index.txt,quote=FALSE,col.names=FALSE,row.names=FALSE,eol=" ",append=TRUE)
               write.table(" ",name.index.txt,quote=FALSE,col.names=FALSE,row.names=FALSE,eol="\n",append=TRUE)
           }    
	}

	# time series
    print('ts writting')
       
	for(i in 1:length.proc){	# loop on time

		# functional/Realigned/r*.nii files
		vol<-readNIfTI(paste(path1,'Functional/Realigned/',list.of.in.files[i],sep='/'),reorient=F)

		for(j in 1:n.regions){	# loop on region
			
			index<-which(vol.template==location[j],arr.ind=TRUE)
			size.r<-dim(index)[1]

			name.txt<-paste(paste(path1,'Functional/data',templBaseName,'',sep='/'),name.ts,'_voxels_time_series_region_',j,'.txt',sep='')

			# TS for each voxel of each region
 				write.table(c(i,vol[index]),name.txt,quote=FALSE,col.names=FALSE,row.names=FALSE,append=TRUE,eol=" ")
			write.table(" ",name.txt,quote=FALSE,col.names=FALSE,row.names=FALSE,eol="\n",append=TRUE)
		}
	}
	
	data.ts<-matrix(0,length.proc,n.regions)
	data.ts.gm<-matrix(0,length.proc,n.regions)

	for(i in 1:n.regions){	# loop on regions

		name.txt<-paste(paste(path1,'Functional/data',templBaseName,'',sep='/'),name.ts,'_voxels_time_series_region_',i,'.txt',sep='')
		tmp<-read.table(name.txt,header=FALSE,skip=1)
		data<-as.matrix(tmp)[,-1]
		nb.voxels<-dim(data)[2]

		name.grey.matter<-paste(paste(path1,'Functional/grey_matter_data',templBaseName,'',sep='/'),'grey_matter_',name.ts,'_voxels_time_series_region_',i,'.txt',sep='')

		coef.grey.matter<-read.table(name.grey.matter,header=FALSE,skip=1)
		
		data.ts.gm[,i]<-(data%*%t(coef.grey.matter))/nb.voxels
		if(is.vector(data))	data.ts[,i]<-sum(data)/nb.voxels
		if(is.matrix(data))	data.ts[,i]<-rowSums(data)/nb.voxels

	}
	

	# Movement correction
	print('Movement correction')
	
	set1<-data.ts	# time series
	N <- length(set1[,1]) # length of the time series
	print(c("ts length :",N))

       ###list.of.in.files<-list.files(path=paste(path,'/Functional/realigned/',sep=''),pattern=glob2rx("rf*.nii"))

	path1.mov<-list.files(path=paste(path1,'Functional/Realigned/',sep='/'),pattern=glob2rx("rp*.txt"))
	cat(c(path1),'\n')
	cat(c(path1.mov),'\n')
	cat(paste(path1,'Functional/Realigned',path1.mov,sep='/'),'\n')
	set2 <- read.table(paste(path1,'Functional/Realigned',path1.mov,sep='/'), header=FALSE)
	set2 <- as.data.frame(set2)

	set3 <- rbind(0, set2[-N,])
	set3 <- cbind(set2, set2 - set3) #set3 is a reorgnisation of data in set2
	names(set3) <- c("p1","p2","p3","p4","p5","p6","p1d","p2d","p3d","p4d","p5d","p6d")	

	set4 <- resid(lm(as.matrix(set1) ~ as.matrix(set3))) #set4 gets the residuals of the linear regression between the ts and the movement data

	set4 <- as.data.frame(set4)	

	data.correct<-set4

	write.table(data.correct,paste(path1,'/Functional/corrected_data/',templBaseName,'/'	,name.ts,'_ts.txt',sep=''),col.names=FALSE,row.names=FALSE,quote=FALSE)
	
	
}