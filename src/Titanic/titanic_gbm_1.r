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

computeLogisticalError <- function(Ysimulated,Yreal) {
	
	loge = sum(Yreal * log(Ysimulated) + (1-Yreal) * log (1-Ysimulated))
	n = length(Yreal)
	loge = loge /-n
	return (loge)	
}


### Clean and make right category
#
# If sparse, don't use the mean.   Set it to the majority sparcicity value.
cleanInputDataForGBM <- function(X, forceQuan = FALSE) {
	names(X);
	for(i in 1:length(X)) {
		
		name = names(X)[i]
		print (name)
		col = X[,i]  
		
		index = which(is.na(col))
		
		if ( substr(name,1,3) == 'Cat' && forceQuan != TRUE ) {
			col[index] = "Unknown"
			X[,i] <- as.factor(col)
		}
		
		if ( substr(name,1,4) == 'Quan' || forceQuan == TRUE) {
			column_mean = mean(col, na.rm = TRUE)
			col[index] = column_mean
			X[,i] <- as.numeric(col)
		}
		
		if ( substr(name,1,4) == 'Date'&& forceQuan != TRUE ) {  	
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
idxCat <- c(2,11)  #31st column is messed, 

#col = c("Cat_survived","Cat_pclass","Cat_name","Cat_sex","Quant_age","Cat_sibsp","Cat_parch","CAT_ticket","Quant_fare","Cat_cabin","Cat_embarked")
col = c("Cat_survived","Cat_pclass","Cat_name","Cat_sex","Quant_age","Cat_sibsp","Quant_parch","CAT_ticket","Quant_fare","Cat_cabin","Cat_embarked")


training <- read.csv(file="train.csv",header=TRUE, sep=",", col.names=col)
Xtrain <- training[, idxCat[1] : idxCat[2] ]
XtrainClean = cleanInputDataForGBM(Xtrain)


## Create levelsets for the NA's that are factors.   If numeric then abort if there is an NA

## Now run Test Data set, clean and continue.
test <- read.csv(file="test.csv",header=TRUE, sep=",", col.names=col[idxCat[1] : idxCat[2]])
Xtest <- test
XtestClean = cleanInputDataForGBM(Xtest)


## GBM Parameters
ntrees <- 6000
depth <- 5
minObs <- 10
shrink <- 0.0005
folds <- 5
Ynames <- c(names(training)[1])

## Setup variables.
ntestrows = nrow(XtestClean)
ntrainrows = nrow(XtrainClean)
Yhattest =  matrix(nrow = ntestrows , ncol = 13, dimnames = list (1:ntestrows,Ynames ) )
Yhattrain =  matrix(nrow = ntrainrows , ncol = 13, dimnames = list (1:ntrainrows,Ynames ) )



## Density
#Y <-  training[,1:12] 
#Ysum <- rowSums ( Y, na.rm=TRUE)
#plot(1:12, Y[2,] )


#
# Correlations
# This is as we expected, the top category is male/female
# followed by cabin class.  The least correlated is name parch?
ytraincorr <- training[,1]
ytraincorr[is.na(ytraincorr)] <- 0.0

xtraincorrIn <- training[,  idxCat[1] : idxCat[2]  ]
xtraincorr = cleanInputDataForGBM(xtraincorrIn, TRUE)

C2 = cor(xtraincorr, ytraincorr)
C2 [ is.na(C2)] <- 0.0
sort(C2)
print(C2)
maxV = max(abs(C2))
which( C2 == maxV, arr.ind = TRUE )
which( C2 == -1*maxV, arr.ind = TRUE )

  

start=date()
start

trainCols = c(1,3:6,8,10)
X = cbind(XtrainClean[trainCols] )
nColsOutput = 12
Y <- as.numeric(training[,1])

gdata <- cbind(Y,X)



mo1gbm <- gbm(Y~.,
			  data=gdata,
              distribution = "bernoulli",
              n.trees = ntrees,
              shrinkage = shrink,
              cv.folds = folds, 
			  verbose = TRUE)


gbm.perf(mo1gbm,method="cv")


sqrt(min(mo1gbm$cv.error))
which.min(mo1gbm$cv.error)

Yhattrain <- predict.gbm(mo1gbm, newdata=XtrainClean[trainCols], n.trees = ntrees, type="response") 
Yhattest <- predict.gbm(mo1gbm, newdata=XtestClean[trainCols], n.trees = ntrees, type="response")
gc()
 	
end = date()
end



## Calculate total training error
YhattrainRMLSE <- Yhattrain
YtrainRMLSE <- as.matrix(training[,1])
loge <- computeLogisticalError(YhattrainRMLSE, YtrainRMLSE)
loge

# Calculate how many correct % (leaders are 98%)
YhattrainBool <- as.numeric(YhattrainRMLSE)
levelT <- 0.50
YhattrainBool[ which(YhattrainBool <= levelT) ] <- 0
YhattrainBool[ which(YhattrainBool >= levelT) ] <- 1

total <- length (YhattrainBool)

length ( which(YhattrainBool == 1) )
length ( which(YhattrainBool == 0) )
correct <- length ( which(YhattrainBool == Y) )

#.787 correlations
precentCorr <-correct/total
precentCorr

write.csv(YhattrainBool, "titanic_1_gbm_train.csv", row.names=FALSE)


Yhattest
YhattestBool = as.numeric(Yhattest)
YhattestBool[ which(YhattestBool <= levelT) ] <- 0
YhattestBool[ which(YhattestBool >= levelT) ] <- 1

write.csv(YhattestBool, "titanic_1_gbm_test.csv", row.names=FALSE)


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



