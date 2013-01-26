""" Writing my first randomforest code.
Author : AstroDave
Date : 23rd September, 2012
please see packages.python.org/milk/randomforests.html for more

""" 

import numpy as np
import csv as csv
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import GradientBoostingRegressor

csv_file_object = csv.reader(open('train.csv', 'rb')) #Load in the training csv file
header = csv_file_object.next() #Skip the fist line as it is a header
train_data=[] #Creat a variable called 'train_data'
for row in csv_file_object: #Skip through each row in the csv file
    train_data.append(row) #adding each row to the data variable
train_data = np.array(train_data) #Then convert from a list to an array

#I need to convert all strings to integer classifiers:
#Male = 1, female = 0:
train_data[train_data[0::,3]=='male',3] = 1
train_data[train_data[0::,3]=='female',3] = 0
#embark c=0, s=1, q=2
train_data[train_data[0::,10] =='C',10] = 0
train_data[train_data[0::,10] =='S',10] = 1
train_data[train_data[0::,10] =='Q',10] = 2

train_data = np.delete(train_data,[2,7,9],1) #remove the name data, cabin and ticket
#I need to do the same with the test data now so that the columns are in the same
#as the training data

#I need to fill in the gaps of the data and make it complete.
#So where there is no price, I will assume price on median of that class
#Where there is no age I will give predicted value of age
age_predict = train_data[0::,3]
age_data = np.delete(train_data,[3],10)
age_predict_paired = age_predict
age_data_paired = age_data


raw_input(".")	
gb_age = GradientBoostingRegressor().fit(age_data_paired,age_predict_paired)
age_output = gb_age.predict(age_data)
j = 0
for rows in train_data:
	if(row[3]==''):
		row[3] = age_output[j]
	j += 1

#All missing embarks just predict where they're coming from:
em_predict = train_data[0::,7]
em_data = np.delete(train_data[0::,7],1)
em_predict_paired = em_predict
em_data_paired = em_data
i = 0
for row in em_predict_paired:
	if(em_predict_paired[7] == ''):
		np.delete(em_predict_paired[i,0::],1)
		np.delete(em_data_paired[i,0::],1)
	i += 1
gb_em = GradientBoostingRegressor().fit(em_data_paired,em_predict_paired)
em_output = gb_em.predict(em_data)
j = 0
for rows in train_data:
	if(row[7]==''):
		row[7] = em_output[j]
	j += 1


test_file_object = csv.reader(open('test.csv', 'rb')) #Load in the test csv file
header = test_file_object.next() #Skip the fist line as it is a header
test_data=[] #Creat a variable called 'test_data'
for row in test_file_object: #Skip through each row in the csv file
    test_data.append(row) #adding each row to the data variable
test_data = np.array(test_data) #Then convert from a list to an array

#I need to convert all strings to integer classifiers:
#Male = 1, female = 0:
test_data[test_data[0::,2]=='male',2] = 1
test_data[test_data[0::,2]=='female',2] = 0
#ebark c=0, s=1, q=2
test_data[test_data[0::,9] =='C',9] = 0 #Note this is not ideal, in more complex 3 is not 3 tmes better than 1 than 2 is 2 times better than 1
test_data[test_data[0::,9] =='S',9] = 1
test_data[test_data[0::,9] =='Q',9] = 2

test_data = np.delete(test_data,[1,6,8],1) #remove the name data, cabin and ticket

#All the ages with no data make the median of the data
age_predict = test_data[0::,2]
age_data = np.delete(test_data[0::,2],1)
age_predict_paired = age_predict
age_data_paired = age_data
i = 0
for row in age_predict_paired:
	if(age_predict_paired[2] == ''):
		np.delete(age_predict_paired[i,0::],1)
		np.delete(age_data_paired[i,0::],1)
	i += 1
gb_age = GradientBoostingRegressor().fit(age_data_paired,age_predict_paired)
age_output = gb_age.predict(age_data)
j = 0
for rows in test_data:
	if(row[2]==''):
		row[2] = age_output[j]
	j += 1

#All missing embarks just predict where they're coming from:
em_predict = test_data[0::,6]
em_data = np.delete(test_data[0::,6],1)
em_predict_paired = em_predict
em_data_paired = em_data
i = 0
for row in em_predict_paired:
	if(em_predict_paired[6] == ''):
		np.delete(em_predict_paired[i,0::],1)
		np.delete(em_data_paired[i,0::],1)
	i += 1
gb_em = GradientBoostingRegressor().fit(em_data_paired,em_predict_paired)
em_output = gb_em.predict(em_data)
j = 0
for rows in test_data:
	if(row[6]==''):
		row[6] = em_output[j]
	j += 1




#The data is now ready to go. So lets train then test!
# Random FOREST
# print 'Training '
# forest = RandomForestClassifier(n_estimators=100)

# forest = forest.fit(train_data[0::,1::],\
                    # train_data[0::,0])

# print 'Predicting'
# output = forest.predict(test_data)

gb = GradientBoostingClassifier().fit(train_data[0::,1::],\
                    train_data[0::,0])

output = gb.predict(test_data)
					
open_file_object = csv.writer(open("myfirstgb.csv", "wb"))
test_file_object = csv.reader(open('test.csv', 'rb')) #Load in the csv file


test_file_object.next()
i = 0
for row in test_file_object:
    row.insert(0,output[i].astype(np.uint8))
    open_file_object.writerow(row)
    i += 1
 
