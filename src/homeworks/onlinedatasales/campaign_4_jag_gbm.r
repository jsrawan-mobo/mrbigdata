#
#
# Use gradient boosted tree's
#
# Rev1 - Try to use a small subset of data 
#
#
#
# Rev2 - Try to use all data and train over the set
#
#
# Rev3 - predict the sum
#
# Rev4 - Use the time series to predict the output and % change.
# 
# Submission Info:
# Fri, 01 Jun 2012 05:13:23
# GBM + no negatives
# RMLSE = 0.76373
#
# Note, we need 6000 tree's to drive down, but can use far less to get a first hand estimate
# The predicted RMLSE from "computeRMSLE" is [1] 0.7337036
# So that is pretty accurate.
#
# When using 1000 tree (earliest convergence) the computedRMLSE is 
# 1.112594
#
# When using more inputs,
#
rm(list=ls())
require(gbm)
 


# Give it a the estimator and real value.  Will return the RMLSE calculation. This is on training set 
# Obviously. 
# e
computeRMSLE <- function(Ysimulated, Yreal) {
	
	#zero out negative elements  
	Ysimulated <- ifelse(Ysimulated<0,0,Ysimulated)
	Yreal <- ifelse(Yreal<0,0,Yreal)
	
	#initialize values
	rmsle <- 0.0
	n <- 0
	
	#perform calculations
	Ysimulated <- log(Ysimulated + 1)
	Yreal <- log(Yreal + 1)
		
	#for vectors, n is the length of the vector
	n <- length(Yreal)
	rmsle <- sqrt(sum((Ysimulated - Yreal)^2)/n)
	
	return (rmsle)
}


### Clean and make right category
#
# If sparse, don't use the mean.   Set it to the majority sparcicity value.
cleanInputDataForGBM <- function(X) {
	names(X);
	for(i in 1:length(X)) {
		
		name = names(X)[i]
		print (name)
		col = X[,i]  
		
		index = which(is.na(col))
		
		if ( substr(name,1,3) == 'Cat'  ) {
			col[index] = "Unknown"
			X[,i] <- as.factor(col)
		}
		
		if ( substr(name,1,4) == 'Quan' ) {
			column_mean = mean(col, na.rm = TRUE)
			col[index] = column_mean
			X[,i] <- as.numeric(col)
		}
		
		if ( substr(name,1,4) == 'Date' ) {  	
			column_mean = mean(col, na.rm = TRUE)
			col[index] = column_mean
			X[,i] <- as.numeric(col)
		}
		
		result = is.factor(X[,i])
		print(result);
	}
	return (X)
}

cleanInputAsNumeric <- function(X) {
	names(X);
	for(i in 1:length(X)) {
		
		name = names(X)[i]
		print (name)
		col = X[,i]  
    	X[,i] <- as.numeric(col)	 
		result = is.factor(X[,i])
		print(result);
	}
	return (X)
}

#idxCat <- c(13,558)
idxCat <- c(13,29)  #31st column is messed, 

training <- read.table(file="TrainingDataset.csv",header=TRUE, sep=",")
Xtrain <- training[, idxCat[1] : idxCat[2] ]
XtrainClean = cleanInputDataForGBM(Xtrain)


## Create levelsets for the NA's that are factors.   If numeric then abort if there is an NA

## Now run Test Data set, clean and continue.
test <- read.table(file="TestDataset.csv",header=TRUE, sep=",")
Xtest <- test[,  2:(idxCat[2] - idxCat[1] + 2)  ]
XtestClean = cleanInputDataForGBM(Xtest)


## GBM Parameters
ntrees <- 6000
depth <- 5
minObs <- 10
shrink <- 0.001
folds <- 10
Ynames <-   c('id', names(training[,1:12]))

## Setup variables.
ntestrows = nrow(XtestClean)
ntrainrows = nrow(XtrainClean)
Yhattest =  matrix(nrow = ntestrows , ncol = 13, dimnames = list (1:ntestrows,Ynames ) )
Yhattrain =  matrix(nrow = ntrainrows , ncol = 13, dimnames = list (1:ntrainrows,Ynames ) )

X = XtrainClean
nColsOutput = 12

## Density
#Y <-  training[,1:12] 
#Ysum <- rowSums ( Y, na.rm=TRUE)
#plot(1:12, Y[2,] )
  

start=date()
start
for( i in 1:nColsOutput ) {
	
 	Y <- as.numeric(training[,i])
	Y <- log(Y)  ## TBD how does this get reconciled?
	Y[is.na(Y)] <- 0.0	
	gdata <- cbind(Y,X)
	

	
	
	mo1gbm <- gbm(Y~. ,
				  data=gdata,
	              distribution = "gaussian",
	              n.trees = ntrees,
	              shrinkage = shrink,
	              cv.folds = folds, 
				  verbose = FALSE)
	
	
	gbm.perf(mo1gbm,method="cv")
	
	
	sqrt(min(mo1gbm$cv.error))
	which.min(mo1gbm$cv.error)
 	
 	Yhattest[,i+1] <- exp(predict.gbm(mo1gbm, newdata=XtestClean, n.trees = ntrees)) 
 	Yhattrain[,i+1] <- exp(predict.gbm(mo1gbm, newdata=XtrainClean, n.trees = ntrees)) 
 	gc()
 	
}

end = date()
end
Yhattest[,1] <- seq(1,ntestrows,1)

## Calculate total training error
YhattrainRMLSE <- Yhattrain[,2:13]
YtrainRMLSE <- as.matrix(training[,1:12])
YtrainRMLSE[is.na(YtrainRMLSE)] <- 0.0
rmsle <- computeRMSLE(YhattrainRMLSE, YtrainRMLSE)
rmsle

## Is there some set of data, where the RMSLE is different

#1. For campaigns from various overallsales (historgram)


#2. 


write.csv(Yhattest, "campaign_4_jag_gbm.csv", row.names=FALSE)


#########################################################
# Extra's
########################################################
# 1. Which columns look like other columns
# Take the correlatoin, and find where its greater that 0.9999
# Of course remove the 1 correlaion
# You must set EACH column to a numeric one
# Finally the 'diff' returns where its not a diagonol
# TODO return the exact columnnames

trainingMatrix = as.matrix( training )
trainingMatrix = cleanInputAsNumeric( training)
trainingMatrix[is.na(trainingMatrix)] <- 0.0

corr <- cor(trainingMatrix)
idx <- which(corr > 0.9999, arr.ind = TRUE)
idxCopy <- idx[ apply(idx, 1, diff) > 0, ]


# 2.
#
#
#



