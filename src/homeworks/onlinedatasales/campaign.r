#
#
# Use gradient boosted tree's
#
# Rev1 - Try to use a small subset of data 
#
#
#
# Rev2- Try to use all data then.
#
#
#
#
require(gbm)


data <- read.table(file="TrainingDataset.csv",header=TRUE, sep=",")



#
# Pull out X for whatever columsn
#
idxCat <- c(13,29)


X <- data[, idxCat[1] : idxCat[2] ]
Y <- as.numeric(data[,2])
Y <- log(Y)
Y[is.na(Y)] <- 0.0


### Clean and make right category
#
# If sparse, don't use the mean.   Set it to the majority sparcicity value.
names(X);
for(i in 1:length(X)) {
	
  name = names(X)[i]
  print (name)
  col = X[,i]  
  
  index = which(is.na(col))
  
  if ( substr(name,1,3) == 'Cat'  ) {
    #col[index] = "Unknown"
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


## Create levelsets for the NA's that are factors.   If numeric then abort if there is an NA




## learn 

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



## Now run Test Data set, clean and continue.
data <- read.table(file="TestDataset.csv",header=TRUE, sep=",")

 




