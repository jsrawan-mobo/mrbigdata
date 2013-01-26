
#
#
# Use gradient boosted tree's.  Report the %correct internaly (externally) -[cvBest, logistical error ]
#
# Rev1 - Try to use a small subset of data  (0.76)
# Rev2 - Try to correctly use quant and category (0.76)
# Rev3 - Use Cabin encoding and married (0.74)
# Rev4 - Improve Married Men data and code the tickets 0.83 (0.76) => [0.95,0.408]
# Use 3000 trees, 0.01 error, and depth = 3, 0.78 (0.76) => [0.977,0.46]
# Rev5 - Use prediction for age and random forest 0.86 (0.75) => [??], 0.374]
require(gbm)
library(ggplot2)
library(calibrate)
library(grid)
library(stats)
library(stringr)
library(glmnet)
library(randomForest)
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
			col <- as.numeric(as.character(col))
			column_mean = mean(col, na.rm = TRUE)
			col[index] = column_mean
			X[,i] <- col
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

 
    

cleanUnusedLevelsForPredict <- function(XtestClean, XtrainClean, matchLevels=FALSE) {
    
    # Cleans up the levels that do not exist, so we can do a prediction
    for(i in 1:length(XtestClean)) {
        
        name = names(XtestClean)[i]
        colTest = XtestClean[,i]  
        colTrain = XtrainClean[,i]    
        
        if ( is.factor(colTest) ) {
            print (name)            
            colTrain = as.factor(as.character(colTrain)) #recode the input, incase it was melted of original.
            id <- which(!(colTest %in% levels(colTrain)))                        
            colTestCleanFact <- colTest
            levels_to_delete = colTestCleanFact[id]
            if (length(levels_to_delete)>0) {
                print(id)    
                print(levels_to_delete)                
                colTestCleanFact[id] <- "X"
                colTestCleanFact<- factor(colTestCleanFact)               
                XtestClean[,i] = colTestCleanFact                                    
            }
            if (matchLevels) {
                levels(XtestClean[,i]) = levels(colTrain)
            }            
        }                        
    }
    return (XtestClean)    
}

# XTestAge = XtrainClean[inot,trainAgeCols]
# XtrainClean$Cat_TicketName = factor(XtrainClean$Cat_TicketName)
# 
# colTest = XTestAge[,7]  
# colTrain = X[,7]    
# id <- which(!(colTest %in% levels(colTrain)))
# 
# id <- which(!(XtrainClean$Cat_TicketName %in% levels(XtrainClean$Cat_TicketName)))
# id
#     
# XTestAgeFact = cleanUnusedLevelsForPredict(XTestAge,X)
# ages = predict(fitX, newdata=XTestAgeFact)


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
codeMarriedWomen <- function(x) {  

    #This is initial code married only based on 100% certain, miss and mr.
    last = strsplit(x, ",", perl=TRUE) 
    lastname = tolower(as.character(last[[1]][1]))
    lastname = sub(" ", "", lastname)
    
    if( length(i <- grep("miss",x, ignore.case=TRUE) ) )
        return ( c(as.character("single"),lastname) )
    else if ( length(i <- grep("mr\\.",x, ignore.case=TRUE) ) )
        return ( c(as.character("x"),lastname) )
    else if ( length(i <- grep("mrs\\.",x, ignore.case=TRUE) ) )
        return ( c(as.character("married"),lastname) )        
    else            
        return ( c(as.character("single"),lastname) )
}


codeMarriedMen <- function(x, class_married_info) { 
    
    # This is a way to code married men and who have partners on board.
    last = strsplit(x[1], ",", perl=TRUE) 
    lastname = tolower(as.character(last[[1]][1]))
    lastname = sub(" ", "", lastname)
     
    man_age = as.integer(x[2]) + 1 #rounding

    if ( length(i <- grep("mr\\.", x[1], ignore.case=TRUE) ) ) {
        
        i = which(  class_married_info[1,] == "married" &
                    class_married_info[2,] == lastname &
                    class_married_info[3,] == "female" &
                    class_married_info[4,] <=  man_age)
    
        if ( length(i) > 0  )
            return ( c(as.character("married"),lastname) )
        else
            return ( c(as.character("single"),lastname) )
    }
    else {
        return ( c(as.character("y"), lastname) )
    }
}

codeMarried <- function(training) { 
    
    # This codes all relationships married and non married on board
    class_married_women = sapply( as.character(training$Cat_name), codeMarriedWomen)
    class_married_info = rbind(class_married_women, t(cbind(training["Cat_sex"], training['Quant_age'] ) ) )
    row.names(class_married_info) <- NULL
    class_married_men = apply(cbind(as.character(training$Cat_name), training$Quant_age), MARGIN=1,  codeMarriedMen, class_married_info)
    row.names(class_married_men) <- NULL
    
    i = class_married_info[1,]=="x"
    class_married = class_married_women
    class_married[1,i] = class_married_men[1,i]
    return (class_married)
    
}

codeTicket <- function(x) {  
    
    #This returns the string part of the ticket followed by the number part
    tk_num <- str_extract(x, "(\\d{2}\\d+)$")    
    ticket <- gsub("(\\d)", "", x, perl=TRUE)
    ticket <- tolower(gsub("(\\.)", "", ticket, perl=TRUE))
    ticket <- sub("\\s+", "", ticket, perl = TRUE)
    ticket_array <- strsplit(ticket, "/", perl=TRUE)    
    t = ticket_array[[1]]    
    if (length(t) > 1) {
        tk_cat <- paste(t[1],t[2], sep="")        
    }
    else if ( length(t) == 0 ) {
        tk_cat <- as.character("X")
    }
    else {
        tk_cat <- t[1]        
    }            
    return ( c(tk_cat, tk_num ) )
}

codeData <- function(testData, idxCat) {  

    # Code Cabin Class (cabin and number of cabins)
    class_cabin = sapply( as.character(testData$Cat_cabin), codeClass)
    # Code Married (title, lastname)
    class_married = codeMarried(testData)
    #Code ticketname
    class_ticketname = sapply( as.character(testData$Cat_ticket), codeTicket)
    
    
    XtestData <- testData[, idxCat[1] : idxCat[2] ]
    XtestData <- cbind(XtestData, 
                    Cat_CabinClass = class_cabin[1,], 
                    Quant_CabinCount = class_cabin[2,],
                    Cat_Married = class_married[1,],
                    Cat_LastName = class_married[2,],
                    Cat_TicketName = class_ticketname[1,],
                    Quant_TicketNo = class_ticketname[2,])
    
    row.names(XtestData) <- NULL
    XtestDataClean = cleanInputDataForGBM(XtestData)
    return (XtestDataClean) 
}

predictAge <- function(training, XtrainClean) {      
    i <- which(is.na(training[,5])==FALSE)
    inot <- which(is.na(training[,5])== TRUE)    
    
    #trainAgeCols <- c(1,3,5:6,8,10) 
    #trainAgeCols <- c(1,3,5:6,8,10) 
    trainAgeCols <- c(1,3,5:6,8,10,11:13,15,16) # full
    
    Y <- XtrainClean[i,4]
    X <- cbind(XtrainClean[i,trainAgeCols])
    
    gdata <- cbind(Y,X)
    fitX<-lm(Y~., data=gdata)
    summary(fitX)
    plot(1:length(fitX$fitted),fitX$fitted)
    #names(fitX$fitted)
    #text(1:length(fitX$fitted),fitX$fitted, names(fitX$fitted), cex=0.6, pos=4, col="red") 
    mse <- sum( residuals(fitX)^2)/length(fitX$fitted) 
    mse
    plot(Y,fitX$fitted)
    
    XTestAge = XtrainClean[inot,trainAgeCols]
    XTestAgeFact = cleanUnusedLevelsForPredict(XTestAge,X, TRUE)
    ages = predict(fitX, newdata=XTestAgeFact)
    print(ages)
    
    XtrainClean[inot,4] <- ages   
    return (XtrainClean)
}


predictGBM <- function(Y, XtrainClean, trainCols) {
    
    ## GBM Parameters, choose optimal based on previous tree tests.
    #note optimal seems to be 300,3,10,0.001,10
    ntrees <- 3000
    depth <- 3
    minObs <- 10
    shrink <- 0.001
    folds <- 10
    
    start=date()
    start
    X = cbind(XtrainClean[trainCols] )
    gdata <- cbind(Y,X)
    
    
    mo1gbm <- gbm(Y~.,
                  data=gdata,
                  distribution = "bernoulli",
                  n.trees = ntrees,
                  shrinkage = shrink,
                  cv.folds = folds, 
                  verbose = TRUE,
                  keep.data = TRUE)
    
    #best.iter <- gbm.perf(mo1gbm,method="OOB")
    #best.iter <- gbm.perf(mo1gbm,method="test")
    best.iter <- gbm.perf(mo1gbm,method="cv")
    
    
    print ( sqrt(min(mo1gbm$cv.error)) )
    print ( which.min(mo1gbm$cv.error) )
    
    Yhattrain <- predict.gbm(mo1gbm, newdata=XtrainClean[trainCols], n.trees = ntrees, type="response") 
    
    XtestCleanFact = cleanUnusedLevelsForPredict(XtestClean[trainCols],  XtrainClean[trainCols])
    Yhattest <- predict.gbm(mo1gbm, newdata=XtestCleanFact, n.trees = ntrees, type="response")
    
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
#     plot.gbm(mo1gbm,2,n.trees=1) #Sex
#     plot.gbm(mo1gbm,2:3,n.trees=1) # 
#     plot.gbm(mo1gbm,3:4,n.trees=1) # 
    
     
    for (i in 1:length(trainCols) ) {
        plot.gbm(mo1gbm, i, best.iter)
    }
    
    ret <- list(Yhattrain, Yhattest)
    return (ret)
}

predictRF <- function(Y, XtrainClean, trainCols) {
    
    ## RF Parameters, choose optimal based on previous tree tests.
    #note optimal seems to be  
    ntrees <- 3000
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
    
    YhattrainBool <- predict(mo1rf, newdata=XtrainClean[trainCols], type="response")     
    XtestCleanFact = cleanUnusedLevelsForPredict(XtestClean[trainCols],  XtrainClean[trainCols], TRUE)
    YhattestBool <- predict(mo1rf,  newdata=XtestCleanFact, type="response")   
    
    Yhattrain <- predict(mo1rf,  newdata=XtrainClean[trainCols], type="prob", norm.votes=FALSE)
    Yhattest <- predict(mo1rf,  newdata=XtestCleanFact, type="prob", norm.votes=FALSE)   
     
    gc()
    end = date()
    end        
    
    ret <- list(Yhattrain, Yhattest, YhattrainBool, YhattestBool )
    return (ret)    
 
}



######################################################
# Start here
######################################################
# Define X input columns and their cleaning type
idxCat <- c(2,11) 
col = c("Cat_survived","Cat_pclass","Cat_name","Cat_sex","Quant_age","Quant_sibsp","Quant_parch","Cat_ticket","Quant_fare","Cat_cabin","Cat_embarked")
training <- read.csv(file="train.csv",header=TRUE, sep=",", col.names=col)
XtrainClean <- codeData(training, idxCat)
#train_ordered_by_family= XtrainClean[ order(XtrainClean[,2]), ]
#XtrainClean <- predictAge(training, XtrainClean)

## Test data load and clean
test <- read.csv(file="test.csv", header=TRUE, sep=",", col.names=col[idxCat[1] : idxCat[2]])
XtestClean <- codeData(test, c(1,10))
XtestClean <- predictAge(test, XtestClean)
 

# Now pick columns to train over, for Y and X
Ynames <- c(names(training)[1])
#trainCols = c(1,3:6,8,10,11:13,15,16) # full
trainCols = c(1,3:6,8,10,11:13,15,16) # full
#trainCols = c(3) # gender and age
#trainCols = c(1,3,4) # class, gender and age
names(XtrainClean)


#####################
## GBM
#####################
# Y <- as.numeric(training[,1])
# ret = predictGBM(Y, XtrainClean, trainCols)
# Yhattrain = ret[[1]]
# Yhattest = ret[[2]]
# YhattrainRMLSE <- Yhattrain
# YhattestRMLSE <- Yhattest
# YtrainRMLSE <- as.matrix(training[,1])

#####################
## RF
#####################
Y <- as.numeric(training[,1])
ret = predictRF(Y, XtrainClean, trainCols)
Yhattrain = ret[[3]] 
Yhattest = ret[[4]] 
YhattrainRMLSE <- ret[[1]]
YhattrainRMLSE <- YhattrainRMLSE[,2]
YhattestRMLSE <- ret[[2]]
YhattestRMLSE <- YhattestRMLSE[,2]
YtrainRMLSE <- as.matrix(training[,1])


## Calculate total training error

loge <- computeLogisticalError(YhattrainRMLSE, YtrainRMLSE)
loge

# Calculate how many correct % (leaders are 98%).  Note 0.5 may not be optimal bias
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
write.csv(YhattrainBool, "titanic_5_rf_train.csv", row.names=FALSE)

#encode the output
YhattestBool = as.numeric(YhattestRMLSE)
YhattestBool[ which(YhattestBool <= levelT) ] <- 0
YhattestBool[ which(YhattestBool >= levelT) ] <- 1


write.table(as.matrix(YhattestBool)[,1], "titanic_5_rf_test.csv", row.names=FALSE, col.names=FALSE)


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
