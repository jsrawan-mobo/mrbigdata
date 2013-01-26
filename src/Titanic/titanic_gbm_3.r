
#
#
# Use gradient boosted tree's
#
# Rev1 - Try to use a small subset of data  (0.76)
# Rev2 - Try to correctly use quant and category (0.76)
# Rev3 - Use Cabin enoding, Married status  (0.74)
# Rev4 - Try to use last name as grouping #
#
require(gbm)
library(ggplot2)
library(calibrate)
library(grid)
library(stats)
rm(list=ls())


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

codeClass <- function(x) {  
    if (is.na(x) || nchar(x) < 1) {
        return ( c(as.character("X"),0) )
    }
    x = strsplit(x, "\\s", perl=TRUE)
    l = length(x[[1]])
    first = as.character(x[[1]][1])
    class = substr(first, start=1, stop=1)    
    return (c(class, l))
}
codeMarried <- function(x) {  
    
    last = strsplit(x, ",", perl=TRUE) 
    lastname = tolower(as.character(last[[1]][1]))
    lastname = sub(" ", "", lastname)
    
    if( length(i <- grep("miss",x, ignore.case=TRUE) ) )
        return ( c(as.character("single"),lastname) )
    else if ( length(i <- grep("mr.",x, ignore.case=TRUE) ) )
        return ( c(as.character("married"),lastname) )
    else if ( length(i <- grep("mrs.",x, ignore.case=TRUE) ) )
        return ( c(as.character("married"),lastname) )        
    else            
        return ( c(as.character("single"),lastname) )
}


idxCat <- c(2,11) 
col = c("Cat_survived","Cat_pclass","Cat_name","Cat_sex","Quant_age","Quant_sibsp","Quant_parch","Cat_ticket","Quant_fare","Cat_cabin","Cat_embarked")
training <- read.csv(file="train.csv",header=TRUE, sep=",", col.names=col)

# Now add additional columns for training 
class_count = sapply( as.character(training$Cat_cabin), codeClass)
class_married = sapply( as.character(training$Cat_name), codeMarried)

Xtrain <- training[, idxCat[1] : idxCat[2] ]
Xtrain <- cbind(Xtrain, 
                Cat_CabinClass=class_count[1,], 
                Quant_CabinCount=class_count[2,],
                Cat_Married = class_married[1,],
                Cat_LastName = class_married[2,])
 
row.names(Xtrain) <- NULL
XtrainClean = cleanInputDataForGBM(Xtrain)
 
## Now run Test Data set, clean and continue.
test <- read.csv(file="test.csv",header=TRUE, sep=",", col.names=col[idxCat[1] : idxCat[2]])
Xtest <- test
class_count = sapply( as.character(test$Cat_cabin), codeClass)
class_married = sapply( as.character(test$Cat_name), codeMarried)
Xtest <- cbind(Xtest, 
                Cat_CabinClass=class_count[1,], 
                Quant_CabinCount=class_count[2,],
                Cat_Married = class_married[1,])
row.names(Xtest) <- NULL
XtestClean = cleanInputDataForGBM(Xtest)


## GBM Parameters, choose optimal based on previous tree tests.
ntrees <- 10000
depth <- 5
minObs <- 10
shrink <- 0.001
folds <- 5
Ynames <- c(names(training)[1])
trainCols = c(1,3:6,8,10,11:13)
nCols = length(trainCols)

## Setup variables.
ntestrows = nrow(XtestClean)
ntrainrows = nrow(XtrainClean)
 

start=date()
start

X = cbind(XtrainClean[trainCols] )
names(X)
Y <- as.numeric(training[,1])
gdata <- cbind(Y,X)
mo1gbm <- gbm(Y~.,
			  data=gdata,
              distribution = "bernoulli",
              n.trees = ntrees,
              shrinkage = shrink,
              cv.folds = folds, 
			  verbose = TRUE)


#best.iter <- gbm.perf(mo1gbm,method="OOB")
#best.iter <- gbm.perf(mo1gbm,method="test")
best.iter <- gbm.perf(mo1gbm,method="cv")




sqrt(min(mo1gbm$cv.error))
which.min(mo1gbm$cv.error)

Yhattrain <- predict.gbm(mo1gbm, newdata=XtrainClean[trainCols], n.trees = ntrees, type="response") 
Yhattest <- predict.gbm(mo1gbm, newdata=XtestClean[trainCols], n.trees = ntrees, type="response")

gc()
end = date()
end

# plot the performance
# plot variable influence
summary(mo1gbm, n.trees=1)         # based on the first tree
summary(mo1gbm,n.trees=best.iter) # based on the estimated best number of trees

# compactly print the first and last trees for curiosity
print(pretty.gbm.tree(mo1gbm,1))
print(pretty.gbm.tree(mo1gbm,mo1gbm$n.trees))

#Plot the tree in countour
plot.gbm(mo1gbm,2,n.trees=1) #Sex
plot.gbm(mo1gbm,2:3,n.trees=1) # 
plot.gbm(mo1gbm,3:4,n.trees=1) # 

#plot each variable split
plot.gbm(mo1gbm,1,best.iter)
plot.gbm(mo1gbm,2,best.iter)
plot.gbm(mo1gbm,3,best.iter)
plot.gbm(mo1gbm,4,best.iter)
plot.gbm(mo1gbm,5,best.iter)
plot.gbm(mo1gbm,6,best.iter)
plot.gbm(mo1gbm,7,best.iter)
plot.gbm(mo1gbm,8,best.iter)
plot.gbm(mo1gbm,9,best.iter)
plot.gbm(mo1gbm,10,best.iter)
plot.gbm(mo1gbm,11,best.iter)
plot.gbm(mo1gbm,12,best.iter)



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

write.csv(YhattrainBool, "titanic_3_gbm_train.csv", row.names=FALSE)


YhattestBool = as.numeric(Yhattest)
YhattestBool[ which(YhattestBool <= levelT) ] <- 0
YhattestBool[ which(YhattestBool >= levelT) ] <- 1

write.csv(as.matrix(YhattestBool), "titanic_3_gbm_test.csv", row.names=FALSE, col.names=FALSE)


#########################################################
# Extra's
########################################################
# 1. Which columns look like other columns
# Take the correlation, and find where its greater that 0.9999
# Of course remove the 1 correlaion
# You must set EACH column to a numeric one
# Finally the 'diff' returns where its not a diagonol
# TODO return the exact columnnames


# training correlations

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

###Input data correlations

trainingMatrix = as.matrix( training )
trainingMatrix = cleanInputAsNumeric( training)
trainingMatrix[is.na(trainingMatrix)] <- 0.0

corr <- cor(trainingMatrix)
idx <- which(corr > 0.9999, arr.ind = TRUE)
idxCopy <- idx[ apply(idx, 1, diff) > 0, ]
corr


# 2.  Wikiepedia : 705 out of 2224 survived ( 31% )

length(which(training$Cat_survived == 1))/length(training$Cat_survived)

# 3.  Wikipedia : 90% of men died in 2nd class, correlate fair by surivial
men <- training[which(training$Cat_sex == "male"),]
row.names(men) <- NULL 
length(which(men$Cat_survived == 0))/length(men$Cat_survived)
#pairs(men)
plot(men[,9], men[,1] )

# Plot the % surivial by age bucket.
surv_men <- men[which(men$Cat_survived == 1),]
row.names(surv_men) <- NULL 
nsuv_men <- men[which(men$Cat_survived == 0),]
row.names(nsuv_men) <- NULL 

hist(surv_men$Quant_fare,  breaks=12, col="red", xlab="Fare") 
hist(nsuv_men$Quant_fare,  breaks=12, col="red", xlab="Fare")  

men.histogram <- transform(men, Cat_survived = ifelse(Cat_survived == 1, "Yes", "No"))
fig = ggplot(data=men.histogram) 
fig + geom_histogram(binwidth = 20
                     , aes(    x = Quant_fare
                              ,alpha = Cat_survived
                              ,linetype = Cat_survived)
                     , colour="black"
                     , fill="white"
                     , position="stack") 


# Lets do a manual boxplot that shows us the % survived by fare, which is highely correlated.
bin <- cut(men.histogram$Quant_fare, breaks=c(seq(0,100,10),1000), labels=c(seq(0,100,10)), right=FALSE, , include.lowest=TRUE)
table(bin)
men.histogram_2 <- cbind(Cat_survived=men.histogram$Cat_survived, Quant_fare_bin=bin)
men.histogram_2 <- transform(men.histogram_2, Cat_survived = ifelse(Cat_survived == "Yes", 1, 0))

men.agg = aggregate(men.histogram_2, by=list(Quant_fare_bin), FUN=mean, na.rm=FALSE)
 
plot(as.numeric(men.agg$Group.1), men.agg$Cat_survived, type="p" )

fit <- lm(Cat_survived ~ as.numeric(Group.1), data=men.agg)
summary(fit)
fitted(fit)
residuals(fit)
abline(fit, lty=2, lwd=2, col="red")


#4.  Women and children first, followed by officers

#5.  Other visulation

art <- xtabs(~ fare + survival, data = training, subset = sex == "male")
art
mosaic(art, gp = shading_Friendly)
mosaic(art, gp = shading_max)


summary(training)


#6.  Summary stats


stats <- function(x) {
    ans <- boxplot.stats(x)
    data.frame(ymin = ans$conf[1], ymax = ans$conf[2])
}

vgrid <- function(x,y) {
    viewport(layout.pos.row = x, layout.pos.col = y)
}

idxPlot <- c(1:2,4:7,9,11) 
nCol = length(idxPlot)
pushViewport(viewport(layout=grid.layout(1,nCol)))
count = 0
for(iCol in idxPlot ){
    
    count = count + 1
    name = names(training)[iCol]
    print(name)
    data_col = training[,iCol]
    p <- ggplot(data=training, aes(name, data_col )) + 
        geom_boxplot(notch = TRUE, notchwidth = 0.5) +
        stat_summary(fun.data = stats, geom = "linerange", colour = "skyblue", size = 5)
    q = list(p)
    print(q[[1]], vp=vgrid(1, count))
}

summary(XtrainClean)
