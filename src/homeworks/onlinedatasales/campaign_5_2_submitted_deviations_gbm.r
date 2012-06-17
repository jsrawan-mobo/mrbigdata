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


#setup data
#setwd("/Users/Ivanko/Machine Learning/R/Kaggle/productsales")
data <- read.table(file="TrainingDataset.csv",header=TRUE, sep=",")
testData <- read.table(file="TestDataset.csv",header=TRUE, sep=",")

Xtrain <- data[,13:29]
Xtest <- testData[,2:18]
#add the difference between two dates as another variable
daysbetweencampaigns <- as.numeric(data[,14]-data[,19])
Xtrain <- cbind(Xtrain, daysbetweencampaigns)

daysbetweencampaigns <- as.numeric(testData[,3]-testData[,8])
Xtest <- cbind(Xtest, daysbetweencampaigns)

YMonthlySales <- as.matrix(data[,1:12])
YMonthlySales <- log(YMonthlySales)
YMonthlySales[is.na(YMonthlySales)] <- 0.0

YTotalSales <- as.numeric(data[,1])
#Y - labels as sum of all month sales
for(i in 1:nrow(data)){
  YTotalSales[i] <- log(sum(data[i,1:12],na.rm=TRUE))
}
YTotalSales[is.na(YTotalSales)] <- 0.0

#cleanup data - factor variables are still problematic on prediction
Xtrain <- cleanInputDataForGBM(Xtrain)
Xtest <- cleanInputDataForGBM(Xtest)
ntestRows <- nrow(Xtest)
Ytest <- matrix(nrow = ntestRows, ncol = 12)

numberOfRows <- nrow(Xtrain)
frac <- rep(0.0, 12)

#calculate sum of all sales for the current fold
sumAll <- sum(exp(YTotalSales))

#find "average" time series behavior
#1.  volume weighted  
#frac is total by month / grand total
for(i in 1:12){
  frac [i] <- sum(exp(YMonthlySales[,i]),na.rm=TRUE)/sumAll
}

#some checks
#see if frac sums to 1
sum(frac)
#plot to see if it's reasonable
plot(frac)

#estimate and predict total sales
gdata <- cbind(YTotalSales,Xtrain)
ntrees <- 4000
depth <- 5
minObs <- 10
shrink <- 0.001
folds <- 10

mo1gbm <- gbm(YTotalSales~. ,data=gdata,
              distribution = "gaussian",
              n.trees = ntrees,
              shrinkage = shrink,
              cv.folds = folds)

gbm.perf(mo1gbm,method="cv")

# Cross Validation error
mo1gbm$cv.error


YPredictedAnnualTest <- predict.gbm(mo1gbm, newdata=Xtest, n.trees = ntrees)
YPredictedAnnualTrain <- predict.gbm(mo1gbm, newdata=Xtrain, n.trees = ntrees)

# Currently we can predict the output to 0.54.  This is pretty weak (not using all inputs!)
computeRMSLE( exp(YPredictedAnnualTrain), exp(YTotalSales) )

#now estimate and predict deviations from the "average" monthly portions of the total
for( i in 1:12 ) {
  #get the deviation from the average for a given month's sales
  YDeviationThisMonth <- exp(YMonthlySales[,i])/exp(YTotalSales) - frac[i]
  YDeviationThisMonth[is.na(YDeviationThisMonth)] <- 0.0
  
  gdata <- cbind(YDeviationThisMonth, Xtrain)
  
  #fit the model
  mo2gbm <- gbm(YDeviationThisMonth~. ,
                data=gdata,
                distribution = "laplace",
                n.trees = ntrees,
                shrinkage = shrink,
                cv.folds = folds)
  
  #apply the model
  monthlySalesDeviationFromAverage <- predict.gbm(mo2gbm, newdata=Xtest, n.trees = ntrees)
   
  #save monthly sales prediction
  Ytest[,i] <- monthlySalesDeviationFromAverage * exp(YPredictedAnnualTest) + frac[i] * exp(YPredictedAnnualTest)
    gc()
}

#cvError <- sum(rmsles)/10
indices = seq(1,ntestRows,1)
Ytest <- cbind(indices,Ytest)
write.csv(Ytest, "campaign_5_deviations_gbm.csv", row.names=FALSE)



