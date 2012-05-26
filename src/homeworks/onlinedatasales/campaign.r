setwd("/home/mike-bowles/Downloads/campaignData/")
data <- read.table(file="TrainingDataset.csv",header=TRUE, sep=",")
str(data)
require(gbm)


X <- data[,13:30]
Y <- as.numeric(data[,2])
Y <- log(Y)
Y[is.na(Y)] <- 0.0

idxCat <- c(1,18)
for(i in 1:length(idxCat)) {
  v <- as.factor(X[,idxCat[i]])
  X[,idxCat[i]] <- v
}





gdata <- cbind(Y,X)
ntrees <- 6000
depth <- 5
minObs <- 10
shrink <- 0.001

folds <- 10
mo1gbm <- gbm(Y~. ,data=gdata,
              distribution = "gaussian",
              n.trees = ntrees,
              shrinkage = shrink,
              cv.folds = folds)


gbm.perf(mo1gbm,method="cv")


sqrt(min(mo1gbm$cv.error))
which.min(mo1gbm$cv.error)


