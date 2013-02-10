**************The Yelp data set *********************


Has 474,434 json records, one per line


1) Split into different files depending on the type
 cat yelp_academic_dataset.json | grep -ie '"type": "business"' > yelp_business_all.json
 cat yelp_academic_dataset.json | grep -ie '"type": "user"' > yelp_user_all.json
 cat yelp_academic_dataset.json | grep -ie '"type": "review"' > yelp_review_all.json
wc -l to get lines.

Business - 13490
Users - 130873
Review - 330071

There are two 3 types of record

(Business) ----has--n-->(Review)<---has-n---(User)

Each User has done on average 3 reviews.  
Each Business has about 30 reviews
The average number of shared business review by a given pair of users is
= 330071/13490 = 30


************* Synopsis ******************

Therefore, we want to recommend users to business via similar reviews.  
Following Canopy-kmeans.ppt we want to find which users have reviewed similar business.

This will heavily bias towards grouping by lat-long, we can check this in the result, since
shared reviews are likely to be in a similar geolocation

If we want to remove gelocation bias, the we need to compare though some other means, 
Category similarity is probably best if we want to do this.



Similarities -

Cosine - This will potentially be bad if there is a not a lot of reviews in common between users.
Given we only have 30 reviews per business, and over 130K users this probably won't work to well

Jaccard - This will essentially remove the zeros in the denominator, and give a higher number if there is some match

Regularized -

Pearson  - 


Goodness of fit :

AIC -
BIC -

Also look at obvious avg, std, max, min for parameters like lat,long and other obvious things, that show its working.



***********************Design*******************************

1) Generate a set of Business, list(user_id, rating))
Input : Reviews
Output: Business_id, list(user_id, rating)
Output: User_id, list(business_id, rating)

Note: we can do these at same time with smart selection of keys "business_id:13123" vs "user_id:asdfu123"
Each Reducer can work on the appropriate output
the final output can have both of these lines, and the next mapper, will filter out whatever it wants.

2) Come up with a set of Canopy Clusters, where each point in the space is a Business
and the distance is set to the similarity betwen ratings. 
For each new business, if its within T1 of a given cluster center, then we pass through, otherwise we ignore
The Reducer is responsible for merging Canopy Clusters, that have center within a tolerance (and building a circle that encompases both)
Inputs: Business_id, list(user_id, rating)
Output: Cx,Cy => list(user,ratings)


3) Next come up with kmeans clusters that are 1:1 with Canopy with Radius T2.
Iterate through and make small clusters.

Inputs: Cx,Cy
Inputs: user_id => list (business_id, rating)
Outputs: Kx,Ky 

4) Now split into various.



***********************Running*******************************

python yelp_generatedata.py < yelp_academic_dataset.json > data/rating_vectors.txt
python yelp_initializecanopy.py < data/rating_vectors.txt > data/canopy.txt





******* Apppendix, data formats ******************

1) Business Record

{ "business_id" : "8HqUl6witSBb156Kohx74A",
  "categories" : [ "Japanese",
      "Restaurants"
    ],
  "city" : "Austin",
  "full_address" : "1712 Lavaca St\nDowntown\nAustin, TX 78701",
  "latitude" : 30.279938000000001,
  "longitude" : -97.741150000000005,
  "name" : "Lavaca Teppan",
  "neighborhoods" : [ "Downtown" ],
  "open" : true,
  "photo_url" : "http://s3-media2.ak.yelpcdn.com/bphoto/OeqbEE-POg5Rwrw2iLiWlg/ms.jpg",
  "review_count" : 35,
  "schools" : [ "University of Texas - Austin" ],                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
  "stars" : 3.5,
  "state" : "TX",
  "type" : "business",
  "url" : "http://www.yelp.com/biz/lavaca-teppan-austin"
}


2) Review record



{ "business_id" : "AU5C7IX0mogLK32u2EEOBQ",
  "date" : "2012-07-16",
  "review_id" : "h6SHjzwNB8YjrEfZ3sSD3Q",
  "stars" : 2,
  "text" : "Oh Gia. I lived very close to here for over two years, and gave it many more chances than it deserved.\n\nI've tried the salads, the breakfast sandwiches, the coffee. It's all fine, but it's all about 30% more expensive than it's worth. The wait time for Gia is really long, however, and I've spent (not even kidding) upwards of 15 minutes to get a non-toasted bagel. Process that for a second. A *non* toasted bagel. They used to have a delicious cinnamon sugar bagel that when toasted, was pure heaven I admit. Before they got rid of it, they burned it the last two times I got it, making me almost cry when I opened up my takeout bag. \n\nThey've also tried to rip me off a couple of times-make sure to count your change as it's often been $1-2 full dollars short. When called out on it, I'm immediately given back the money, making me believe it was less than accidental. Also, watch out for any popular meal times, as Gia will be CROWDED.",
  "type" : "review",
  "user_id" : "cR5bvpc0xeQpm-Bsx67A8w",
  "votes" : { "cool" : 0,
      "funny" : 2,
      "useful" : 1
    }
}

3) User Record

{ "average_stars" : 4.0,
  "name" : "Bridget S.",
  "review_count" : 17,
  "type" : "user",
  "url" : "http://www.yelp.com/user_details?userid=B9XWs8RxF9FCMBcGA5dwuA",
  "user_id" : "B9XWs8RxF9FCMBcGA5dwuA",
  "votes" : { "cool" : 15,
      "funny" : 15,
      "useful" : 77
    }
}

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      




