rm(list=ls())
require(gbm)

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


#1. setup data
#setwd("/Users/Ivanko/Machine Learning/R/Kaggle/productsales")
traindata <- read.table(file="TrainingDataset.csv",header=TRUE, sep=",")
testData <- read.table(file="TestDataset.csv",header=TRUE, sep=",")

Xtrain <- traindata[,13:29]
Xtest <- testData[,2:18]

#cleanup data - factor variables are still problematic on prediction
XtrainClean <- cleanInputDataForGBM(Xtrain)
XtestClean <- cleanInputDataForGBM(Xtest)
ntestRows <- nrow(Xtest)
ntrainRows <- nrow(Xtrain)

#2. add the difference between two dates as another variable.  
# Date
# 
#
daysbetweencampaignsTrain <- as.numeric(Xtrain[,2]-Xtrain[,7])
daysbetweencampaignsTrain[is.na(daysbetweencampaignsTrain)] <- 0.0
Xtrain <- cbind(Xtrain, daysbetweencampaignsTrain)

#
#
daysbetweencampaignsTest <- as.numeric(Xtest[,2]-Xtest[,7])
daysbetweencampaignsTest[is.na(daysbetweencampaignsTest)] <- 0.0
Xtest <- cbind(Xtest, daysbetweencampaignsTest)


YMonthlySalesTrain <- log(as.matrix(traindata[,1:12]))
YMonthlySalesTrain[is.na(YMonthlySalesTrain)] <- 0.0


# Note I made a fundamental switch here
# Any data that was N/A was being cleaned in the total
# I do it ahead of time so we always get a sum
YTotalSalesTrain <- matrix(nrow = ntrainRows, ncol = 1)
#Y - labels as sum of all month sales
for(i in 1:nrow(traindata)){
	YTotalSalesTrain[i] <- log(sum(traindata[i,1:12],na.rm=TRUE))
}



frac <- rep(0.0, 12)
sumAll <- sum(exp(YTotalSalesTrain))

# find "average" time series behavior.  This is modelling the average time series
# 
#1.  volume weighted  
#frac is total by month / grand total
for(i in 1:12){
  frac [i] <- sum(exp(YMonthlySalesTrain[,i]),na.rm=TRUE)/sumAll
}

#some checks
#see if frac sums to 1
#plot to see if it's reasonable
sum(frac)
plot(frac)

# Model to predice total sales
# estimate and predict total sales as function of x
gdata <- cbind(YTotalSalesTrain), XtrainClean)
ntrees <- 4000
depth <- 5
minObs <- 10
shrink <- 0.001
folds <- 10

mo1gbm <- gbm(exp(YTotalSalesTrain)~. ,data=gdata,
              distribution = "gaussian",
              n.trees = ntrees,
              shrinkage = shrink,
              cv.folds = folds)

gbm.perf(mo1gbm,method="cv")

# Cross Validation error is is using the log.  
mo1gbm$cv.error


YPredictedAnnualTest <- predict.gbm(mo1gbm, newdata=XtestClean, n.trees = ntrees)
YPredictedAnnualTrain <- predict.gbm(mo1gbm, newdata=XtrainClean, n.trees = ntrees)

# Currently we can predict the output to 0.54.  This is pretty weak (not using all inputs!)
rmlseOfTotalSales = computeRMSLE( exp(YPredictedAnnualTrain), exp(YTotalSalesTrain) )
rmlseOfTotalSales

exp(YPredictedAnnualTrain)

Yhattest <- matrix(nrow = ntestRows, ncol = 12)
Yhattrain <- matrix(nrow = ntrainRows, ncol = 12)

YDeviationThisMonth <- exp(YMonthlySalesTrain[,1])/exp(YTotalSalesTrain) - frac[1]



#now estimate and predict deviations from the "average" monthly portions of the total
for( i in 1:12 ) {
  #get the deviation from the average for a given month's sales
  YDeviationThisMonth <- exp(YMonthlySalesTrain[,i])/exp(YTotalSalesTrain) - frac[i]
  YDeviationThisMonth[is.na(YDeviationThisMonth)] <- 0.0
  
  gdata <- cbind(YDeviationThisMonth, XtrainClean)
  
  cat ("*****************************************************************", '\n' )
  cat ("********************Column", i,"*************************",'\n' )
  cat ("*****************************************************************",'\n' )
  
  #fit the model
  mo2gbm <- gbm.fit(x=Xtrain, y=YDeviationThisMonth,
                #data=gdata,
                distribution = "laplace",
                n.trees = ntrees,
                shrinkage = shrink,
                #cv.folds = folds
  			  )
  
  #apply the model
  monthlySalesDeviationFromAverage <- predict.gbm(mo2gbm, newdata=XtestClean, n.trees = ntrees)
  monthlySalesDeviationFromAverageTrain <- predict.gbm(mo2gbm, newdata=XtrainClean, n.trees = ntrees)
  
   
  #save monthly sales prediction
  Yhattest[,i] <- monthlySalesDeviationFromAverage * exp(YPredictedAnnualTest) + frac[i] * exp(YPredictedAnnualTest)
  Yhattrain[,i] <- monthlySalesDeviationFromAverageTrain * exp(YPredictedAnnualTrain) + frac[i] * exp(YPredictedAnnualTrain)
  gc()
  
}

#cvError <- sum(rmsles)/10


YhattrainRMLSE <- Yhattrain
YtrainRMLSE <- as.matrix(traindata[,1:12])
YtrainRMLSE[is.na(YtrainRMLSE)] <- 0.0
rmsle <- computeRMSLE(YhattrainRMLSE, YtrainRMLSE)
rmsle

indices = seq(1,ntestRows,1)
Ytest <- cbind(indices,Yhattest)
write.csv(Yhattest, "campaign_5_deviations_gbm.csv", row.names=FALSE)



