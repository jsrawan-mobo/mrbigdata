rm(list=ls())
require(gbm)

setwd("/Users/Ivanko/Machine Learning/R/Kaggle/productsales")
data <- read.table(file="TrainingDataset.csv",header=TRUE, sep=",")
testData <- read.table(file="TestDataset.csv",header=TRUE, sep=",")

X <- data[,14:29]
Xtest <- testData[,3:18]
Ytestrows <- nrows(Xtest)
Ytest <- matrix(nrow = Ytestrows , ncol = 13)

gdata <- cbind(Y,X)
ntrees <- 6000
depth <- 5
minObs <- 10
shrink <- 0.001

#for each month, make a prediction on all variables
for(i in 1:12) {

  Y <- as.numeric(data[,i])
  Y <- log(Y)
  Y[is.na(Y)] <- 0.0


  #idxCat <- c(1,18)
  #for(i in 1:length(idxCat)) {
  #  v <- as.factor(X[,idxCat[i]])
  #  X[,idxCat[i]] <- v
  #}

  folds <- 10
  mo1gbm <- gbm(Y~. ,data=gdata,
                distribution = "gaussian",
                n.trees = ntrees,
                shrinkage = shrink,
                cv.folds = folds)
  
  #gbm.perf(mo1gbm,method="cv")
  #sqrt(min(mo1gbm$cv.error))
  #which.min(mo1gbm$cv.error)
    
  #idxCat <- c(1,18)
  #for(i in 1:length(idxCat)) {
  #  v <- as.factor(Xtest[,idxCat[i]])
  #  Xtest[,idxCat[i]] <- v
  #}
  
  Ytest[,i] <- exp(predict.gbm(mo1gbm, newdata=Xtest, n.trees = ntrees))
  
}