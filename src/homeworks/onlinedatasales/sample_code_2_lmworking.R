#
# The objective of the competition is to help us build as good a model as possible to predict monthly online sales of a product. Imagine the products are online  self-help programs following an initial advertising campaign.
#
# We have shared the data in the comma separated values (CSV) format.  Each row in this data set represents a different consumer product.
#
# The first 12 columns (Outcome_M1 through Outcome_M12) contains the monthly online sales for the first 12 months after the product launches.  
#
# Date_2 is the day number the product was announced and a pre-release advertising campaign began.
# Date_1 is the day number the major advertising campaign began and the product launched.  
#
#
# Other columns in the data set are features of the product and the advertising campaign.  Quan_x are quantitative variables and Cat_x are categorical variables. Binary categorical variables are measured as (1) if the product had the feature and (0) if it did not.


#
# Score parts 
#
# Date it advertising the 
#
# Decay function from month to month.
# % of the total at of the end of the month
#
#  Factor  - NA with "a" leave alone
#  Numeric - replace with -1 for numeric, add the column
#
#
#

library(ggplot2)
library(calibrate)
library(grid)
library(stats)
rm(list=ls())

stats <- function(x) {
	ans <- boxplot.stats(x)
	data.frame(ymin = ans$conf[1], ymax = ans$conf[2])
}

vgrid <- function(x,y) {
	viewport(layout.pos.row = x, layout.pos.col = y)
}



training = read.csv("TrainingDataset.csv", na.strings="NaN")
test = read.csv("TestDataset.csv", na.strings="NaN")


# The box plot gives us the distribution
# the box lower, middle, upper gives the 25%, mean, 75%
# the black line gives you the 10%, 90%.  The dots are out of range.
# Doesn't handle floating point values
# Output data

nCol = 12
start = 2
pushViewport(viewport(layout=grid.layout(1,nCol)))
for(iCol in start:(nCol+start-1) ){
	
	name = names(training)[iCol]
	print(name)
	data_col = training[,iCol]
	p <- ggplot(data=training, aes(name, data_col )) + 
		geom_boxplot(notch = TRUE, notchwidth = 0.5) +
		stat_summary(fun.data = stats, geom = "linerange", colour = "skyblue", size = 5)
	q = list(p)
	print(q[[1]], vp=vgrid(1, iCol-start+1))
}


# Output data
nCol = 12
start = 2
pushViewport(viewport(layout=grid.layout(1,nCol)))
for(iCol in start:(nCol+start-1) ){
	
	name = names(training)[iCol]
	print(name)
	data_col = training[,iCol]
	p <- ggplot(data=training, aes(name, data_col )) + 
		geom_boxplot(notch = TRUE, notchwidth = 0.5) +
		stat_summary(fun.data = stats, geom = "linerange", colour = "skyblue", size = 5)
	q = list(p)
	print(q[[1]], vp=vgrid(1, iCol-start+1))
}


#function for adding NAs indicators to dataframe and replacing NA's with a value---"cols" is vector of columns to operate on
#   (necessary for randomForest package)
cleanNAs <- function(dataset, cols) {
	dataset[is.na(dataset)] = -1
	return(dataset)
}

#replacements:
trainingCleaned <- appendNAs(training,13:ncol(training))
testCleaned <- appendNAs(test,2:ncol(test))

#begin building submission data frame:
submission_rf = data.frame(id = test$id)

library(ggplot2)
library(calibrate)
library(glmnet)
library(splines)



data_set <- training
tCol = ncol(data_set)
diff = ( data_set[,14] - data_set[,19] ) /24
X = cleanNAs ( data_set[,18:18] )
Y = cleanNAs ( rowSums ( data_set[,1:12] ) )
nCol = ncol(X)
Index <- 1:nrow(X)

x = as.matrix(X)
y = as.matrix(Y)


C2 = cor(x, y)
sort(C2)
print(C2)
which.max(C2)
plot(x, y, main="Sum of Sales vs days between advertising")
fitX <- lm(y ~ x)
abline(fitX, lty=2, lwd=2, col="red")
summary(fitX)
plot(1:nrow(fitX$fitted),fitX$fitted)
names(fitX$fitted)
text(1:nrow(fitX$fitted),fitX$fitted, names(fitX$fitted), cex=0.6, pos=4, col="red") 
residuals(fitX)

cleanedTest =  cleanNAs(test)


fitX$coefficients
yHat <- rep (0.0, nrow(cleanedTest) )
for(i in 1:nrow(cleanedTest)) {
	yHat[i]  <- fitX$coefficients[1] + fitX$coefficients[2] * cleanedTest[i,7]
}
yHat
plot(yHat)


### Now check do a error per column and look for outlier
bloodsweatandtear = read.csv("bloodsweatandtears.csv")

errorMatrix = ( bloodsweatandtear - yHat)
print (errorMatrix)

linearCVObject = cv.glmnet (x, y, alpha=1)
#linearCVObject$cvm = glmnet.cv(x,y. )
str(linearCVObject)
plot(linearCVObject)
plot (linearCVObject$cvm)
min(linearCVObject$cvm)
which.min(linearCVObject$cvm)
plot(x[,3], y, main="Sum of Sales vs days between advertising")


