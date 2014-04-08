#
#
# Use gradient boosted tree's
#
# Rev1 - Join Data and use GBM
# RMLSE = 2, Using gbm.fit, 20 trees
# WMAE = 18413.44987
#
#
# When using more inputs,
#
rm(list=ls())
require(gbm)
require(dplyr)



# Mean Average Error, Weighted
# https://www.kaggle.com/c/walmart-recruiting-store-sales-forecasting/details/evaluation
computeWMAE <- function(Ysimulated, Yreal, XHoliday) {
	
	XWeight <- ifelse(XHoliday==TRUE,5,1)
	XWeight <- XWeight/sum(XWeight)
		 
	n <- length(Yreal)
	wmae <- sum(XWeight %*% abs(Ysimulated - Yreal))
	
	return (wmae)
}



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
cleanInputDataForGBM <- function(X, transform_date=TRUE) {
	names(X);
	i_pos = length(X)
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
		
        #Date is 2014-01-01. Split into 3 columns
		if (transform_date == TRUE) {
    		if ( substr(name,1,4) == 'Date' ) {  	
    			#column_mean = mean(col, na.rm = TRUE)
    			#col[index] = column_mean
    			splitvec <- strsplit(as.character(col),'-',TRUE)
    			X[,i_pos+1] <- as.numeric(unlist(lapply(splitvec,"[[",1)))
    			colnames(X)[i_pos+1] = "Quant_Year"
    			X[,i_pos+2] <- as.numeric(unlist(lapply(splitvec,"[[",2)))
    			colnames(X)[i_pos+2] = "Quant_Month"
    			X[,i_pos+3] <- as.numeric(unlist(lapply(splitvec,"[[",3)))
    			colnames(X)[i_pos+3] = "Quant_Day"
    		}
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

predictGBM <- function(Y, XtrainClean, XtestClean, trainCols) {
    ## GBM Parameters
    ntrees <-  3000
    depth <- 20
    minObs <- 5
    shrink <- 0.002
    folds <- 5
    
    start=date()
    start
    
    X = cbind(XtrainClean[trainCols] )
    gdata <- cbind(Y,X)
    
    if(LOAD_DATA) {
        load(file=paste(RELOAD_PATH,"mogbm.gbm",sep="/"))
    } else {
        mo1gbm <- gbm(Y~. ,
                      data=gdata,
                      distribution = "gaussian",
                      n.trees = ntrees,
                      shrinkage = shrink,
                      cv.folds = folds, 
                      verbose = TRUE)
                      #keep.data = TRUE)
        mogbm = mo1gbm
        save(mogbm, file="mogbm.gbm")
        
        
        
        #fit the model
        # mo2gbm <- gbm.fit(y=Y, x=X,
        #                   verbose = TRUE,
        #                   #data=gdata,
        #                   distribution = "laplace",
        #                   n.trees = ntrees,
        #                   shrinkage = shrink,
        #                   #cv.folds = folds
        # )
        # mogbm = mo2gbm
    }
    
    best.iter <- gbm.perf(mogbm,method="cv")
    print ( sqrt(min(mogbm$cv.error)) )
    print ( which.min(mogbm$cv.error) )
    summary(mogbm, n.trees=1)         # based on the first tree
    summary(mogbm,n.trees=best.iter) # based on the estimated best number of trees
    # compactly print the first and last trees for curiosity
    print(pretty.gbm.tree(mogbm,1))
    print(pretty.gbm.tree(mogbm,mo1gbm$n.trees))
    #Plot the tree in countour
    #plot.gbm(mogbm,2,n.trees=1) #Sex
    #plot.gbm(mogbm,2:3,n.trees=1) # 
    #plot.gbm(mogbm,3:4,n.trees=1) # 
    
    for (i in 1:length(trainCols) ) {
        plot.gbm(mogbm, i, best.iter)
    }
    
    if (LOAD_DATA) {
        load(file=paste(RELOAD_PATH,"Yhattest.pred",sep="/"))
        load(file=paste(RELOAD_PATH,"Yhattrain.pred",sep="/"))
    } else { 
        Yhattrain <- predict.gbm(mogbm, newdata=XtrainClean[trainCols], n.trees = ntrees) 
        Yhattest <- predict.gbm(mogbm, newdata=XtestClean[trainCols], n.trees = ntrees)
        save(Yhattest, file="Yhattest.pred")
        save(Yhattrain, file="Yhattrain.pred")    
    }
    end = date()
    
    Yhattrain <- predict.gbm(mo1gbm, newdata=XtrainClean[trainCols], n.trees = ntrees, type="response") 
    end = date()
    end
     
    ret <- list(Yhattrain, Yhattest,mogbm)
    return (ret)
}

predictRF <- function(Y, XtrainClean, XtestClean, trainCols) {
    
    ## RF Parameters, choose optimal based on previous tree tests.
    #note optimal seems to be  
    ntrees <- 300
    maxNodes <- 3
    sampSize <- 100
    shrink <- 0.001
    folds <- 10
    
    start=date()
    Y <- as.factor(Y)
    X = cbind( XtrainClean[trainCols] )
    gdata <- cbind(Y,X)
    
    mo1rf <- randomForest(Y~.,
                          data=gdata, 
                          do.trace=TRUE,
                          importance=TRUE, 
                          proximity=TRUE,
                          sampsize = sampSize, 
                          ntree = ntrees)
    
    print( round(importance(mo1rf), 2) )
    
    YhattrainBool <- predict(mo1rf, newdata=XtrainClean[trainCols])     
    XtestCleanFact = cleanUnusedLevelsForPredict(XtestClean[trainCols],  XtrainClean[trainCols], TRUE)
    YhattestBool <- predict(mo1rf,  newdata=XtestCleanFact)   
    
    Yhattrain <- predict(mo1rf,  newdata=XtrainClean[trainCols], type="prob", norm.votes=FALSE)
    Yhattest <- predict(mo1rf,  newdata=XtestCleanFact, type="prob", norm.votes=FALSE)   
    
    gc()
    end = date()
    end        
    
    ret <- list(Yhattrain, Yhattest, YhattrainBool, YhattestBool,mo1rf )
    return (ret)    
    
}




# http://www.kaggle.com/c/walmart-recruiting-store-sales-forecasting
# train.csv - Store,Dept,Date,Weekly_Sales,IsHoliday
# - 45 stores * 143 days * 62 depts/per store (max 81 dept types) = 421570
# features.csv - Store,Date,Temperature,Fuel_Price,MarkDown1,MarkDown2,MarkDown3,MarkDown4,MarkDown5,CPI,Unemployment,IsHoliday
# - 45 stores * 182 days (3 years) = 8190
# stores.csv - Store,Type,Size
# - The type of store and its square footage.  
#   Good chance the footage is related to the sales anyways..
# 
# Predict for sales by dept.  Inner join store/days.  Use left join once more sophiticated
#

###############################################
##  Configuration variable
###############################################
LOAD_DATA <-FALSE
RELOAD_PATH <- "submissions/submit4"


###############################################
## Load training data and join with feature
###############################################
train <- read.table(file="input/train.csv",header=TRUE, sep=",", na.strings=c("NA","NaN", " "))
feature <- read.table(file="input/features.csv",header=TRUE, sep=",", na.strings=c("NA","NaN", " "))

ind <- sample(length(train[,1]),25000,FALSE)
train_df <- tbl_df(train[ind,1:4])
#train_df <- tbl_df(train[,1:4])
feature_df <- tbl_df(feature)
training <- inner_join(train_df, feature_df, by=c('Cat_Store','Date'))
training <- training[, c(4,3,2,5:14)] 
XtrainClean = cleanInputDataForGBM(training)
XtrainClean = XtrainClean[, c(3:16)]  

train$Qaunt_Weekly_Sales
min(train$Qaunt_Weekly_Sales)
histogram(train$Qaunt_Weekly_Sales, breaks = 1000, xlim=c(0,10000))
min(training[,1])
max(training[,1])
mean(training[,1])


#####################
## Test Data load and clean
#####################
test <- read.table(file="input/test.csv",header=TRUE, sep=",", na.strings=c("NA","NaN", " "))
#indt <- sample(length(test[,1]),25000,FALSE)
test_df <- tbl_df(test[,1:3])
test_df <- inner_join(test_df, feature_df, by=c('Cat_Store','Date'))
test_df <- test_df[, c(3,2,4:13)] 
XtestClean = cleanInputDataForGBM(test_df)
XtestClean = XtestClean[, c(2:15)]   


#####################
## GBM
#####################
trainCols = c(1:14) # full
Y <- log(as.numeric(training[,1]))
rindex = !is.na(Y) & !is.infinite(Y)
Y = Y[rindex]
X = XtrainClean[rindex,]
ret = predictGBM(Y, X, XtestClean, trainCols)
Yhattrain = exp(ret[[1]])
Yhattest = exp(ret[[2]])
mogbm = ret[[3]]
histogram(Yhattrain)
histogram(exp(Y))
YhattrainRMLSE <- Yhattrain
YhattestRMLSE <- Yhattest


#####################
## RF
#####################
require(randomForest)
trainCols = c(1:14) # full
Y <- as.numeric(training[,1])
ret = predictRF(Y, XtrainClean, XtestClean, trainCols)
Yhattrain = ret[[1]]
Yhattest = ret[[2]]
mogbm = ret[[5]]
YhattrainRMLSE <- Yhattrain
YhattestRMLSE <- Yhattest

######################
## Linear Model
######################
trainCols = c(1:14) # full
Y <- as.numeric(training[,1])
X <- XtrainClean[2:14]
Xtest <- XtestClean[2:14]
C2 = cor(cleanInputAsNumeric(X), Y)
sort(C2)
print(C2)
which.max(C2)

plot(X$Cat_Dept, Y, main="Sale vs Input")
col = colnames(trainCols)
X$Qaunt_MarkDown1[is.na(X$Qaunt_MarkDown1)] = 0
X$Quant_MarkDown2[is.na(X$Quant_MarkDown2)] = 0
X$Qaunt_MarkDown3[is.na(X$Qaunt_MarkDown3)] = 0
X$Qaunt_MarkDown4[is.na(X$Qaunt_MarkDown4)] = 0
X$Qaunt_MarkDown5[is.na(X$Qaunt_MarkDown5)] = 0



YY = cbind( Y,X )
fitX <- lm(Y ~ X)
fitX <- lm(Y ~. , data = X)
abline(fitX, lty=2, lwd=2, col="red")
summary(fitX)
plot(1:nrow(fitX$fitted),fitX$fitted)
names(fitX$fitted)
text(1:nrow(fitX$fitted),fitX$fitted, names(fitX$fitted), cex=0.6, pos=4, col="red") 
residuals(fitX)

Yhattrain = predict(fitX,X)
Yhattest = predict(fitX,Xtest)
Yhattrain[is.na(Yhattrain)] <- 0
Yhattest[is.na(Yhattest)] <- 0

plot(Yhattest)


############################
# GLMnet
############################
require(glmnet)
linearCVObject = cv.glmnet(X, Y, alpha=1)
str(linearCVObject)
plot(linearCVObject)
plot (linearCVObject$cvm)
min(linearCVObject$cvm)
which.min(linearCVObject$cvm)
plot(x[,3], y, main="Sum of Sales vs days between advertising")



#####################
## Analyze training error vectors and plot error variables
#####################
YhattrainRMLSE <- Yhattrain
YtrainRMLSE <- Y
YtrainRMLSE[is.na(YtrainRMLSE)] <- 0.0
rmsle <- computeRMSLE(YhattrainRMLSE, YtrainRMLSE)
rmsle
wmae <-  computeWMAE(YhattrainRMLSE, YtrainRMLSE, XtrainClean[,3])
wmae

##Absolute error sorted, for graphing as required
Yerror = abs(YhattrainRMLSE -  YtrainRMLSE)
Yerror_all = cbind(Yerror, training)
sorted_error = Yerror_all[ order(-Yerror_all$Yerror), ]

ggplot(sorted_error, aes(x=sorted_error$Date, y=max(Yerror), colour=supp)) + 
  geom_errorbar(aes(ymin=max(Yerror)-se, ymax=max(Yerror)+se), width=.1) +
  geom_line() +
  geom_point()


#########################################################
# Submissions
#########################################################
write.csv(Yhattrain, "walmart_1_jag_gbm_train.csv", row.names=FALSE)
submit_key = do.call(paste,c(test[,1:3], sep="_"))
Yhattest_final = cbind(submit_key, Yhattest)

colnames(Yhattest_final)[1] = "Id"
colnames(Yhattest_final)[2] = "Weekly_Sales"
write.csv(Yhattest_final, "walmart_1_jag_gbm.csv", row.names=FALSE,quote = FALSE)


#########################################################
# Extra's
########################################################
# 1. Which columns look like other columns
# Take the correlatoin, and find where its greater that 0.9999
# Of course remove the 1 correlaion
# You must set EACH column to a numeric one
# Finally the 'diff' returns where its not a diagonol
# TODO return the exact columnnames

train_mat <- cbind(Y,XtrainClean)
trainingMatrix = as.matrix( train_mat )
trainingMatrix = cleanInputAsNumeric( train_mat)
trainingMatrix[is.na(trainingMatrix)] <- 0.0

corr <- cor(trainingMatrix)
idx <- which(corr > 0.9999, arr.ind = TRUE)
idxCopy <- idx[ apply(idx, 1, diff) > 0, ]


# 2. Plot error
# Output data
library(ggplot2)
library(calibrate)
library(grid)
library(stats)

stats <- function(x) {
  ans <- boxplot.stats(x)
  data.frame(ymin = ans$conf[1], ymax = ans$conf[2])
}

vgrid <- function(x,y) {
  viewport(layout.pos.row = x, layout.pos.col = y)
}



nCol = 15
start = 2
pushViewport(viewport(layout=grid.layout(1,nCol)))
for(iCol in start:(nCol+start-1) ){
  
  name = names(train_mat)[iCol]
  print(name)
  data_col = train_mat[,iCol]
  p <- ggplot(data=train_mat, aes(name, data_col )) + 
    geom_boxplot(notch = TRUE, notchwidth = 0.5) +
    stat_summary(fun.data = stats, geom = "linerange", colour = "skyblue", size = 5)
  q = list(p)
  print(q[[1]], vp=vgrid(1, iCol-start+1))
}

