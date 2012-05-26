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
#
#

library(ggplot2)
library(calibrate)
library(grid)
rm(list=ls())

training = read.csv("TrainingDataset.csv", na.strings="NaN")
test = read.csv("TestDataset.csv", na.strings="NaN")

wine_raw = training

#wine_raw <- read.table(file="winequality-red.txt",  sep=';', header=T)
#data_set_frame <- data.frame(
#	data_set = wine_raw,
#	xValue = 1:1599
	)

 
#
# The box plot gives us the distribution
# the box lower, middle, upper gives the 25%, mean, 75%
# the black line gives you the 10%, 90%.  The dots are out of range.
# Doesn't handle floating point values

nCol = 1
pushViewport( viewport(layout=grid.layout(1,nCol)) )

for(iCol in 1:nCol){
	
	name = names(wine_raw)[iCol]
	print(name)
	data_col = wine_raw[,iCol]
	p <- ggplot(data=wine_raw, aes(name, data_col )) + 
		geom_boxplot(notch = TRUE, notchwidth = 0.5) +
		stat_summary(fun.data = stats, geom = "linerange", colour = "skyblue", size = 5)
	q = list(p)
	print(q[[1]], vp=vgrid(1,iCol))
}




#Sample submission-- column means
submission_colMeans = data.frame(id = test[,1])
for (var in names(training)[1:12]) {
  submission_colMeans[,var] = mean(training[,var], na.rm=TRUE)
}
write.csv(submission_colMeans, "sample_submission_using_training_column_means.csv", row.names=FALSE)


#randomForest benchmark submission:
library(randomForest)

#function for adding NAs indicators to dataframe and replacing NA's with a value---"cols" is vector of columns to operate on
#   (necessary for randomForest package)
appendNAs <- function(dataset, cols) {
  append_these = data.frame( is.na(dataset[, cols] ))
  names(append_these) = paste(names(append_these), "NA", sep = "_")
  dataset = cbind(dataset, append_these)
  dataset[is.na(dataset)] = -1
  return(dataset)
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

#train a random forest (and make predictions with it) for each prediction column
for (var in names(training)[1:12]) {
  print(var)
  rf = randomForest(training[,13:ncol(training)],training[,var], do.trace=TRUE,importance=TRUE, sampsize = 100, ntree = 500)
  submission_rf[,var] = predict(rf, test[,2:ncol(test)])
}

write.csv(submission_rf, "RandomForestBenchmark.csv", row.names=FALSE)


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


linearCVObject = cv.glmnet (x, y, alpha=1)
#linearCVObject$cvm = glmnet.cv(x,y. )
str(linearCVObject)
plot(linearCVObject)
plot (linearCVObject$cvm)
min(linearCVObject$cvm)
which.min(linearCVObject$cvm)
plot(x[,3], y, main="Sum of Sales vs days between advertising")


