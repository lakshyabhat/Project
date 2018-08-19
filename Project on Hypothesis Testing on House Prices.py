
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[ ]:

import pandas as pd
import numpy as np
import string as s
import re
from scipy import stats
from scipy.stats import ttest_ind


# # Project - Hypothesis Testing

# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this project:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this project, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this project below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[ ]:

# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[ ]:

def get_list_of_university_towns():
    data = pd.read_csv('university_towns.txt', delimiter="\t", header = None)
    with open('university_towns.txt') as f:
        content = f.read().splitlines()
    lst = []
    state_region_lst = []
    df = pd.DataFrame()
    state = ''
    region = ''
    for i in content:
        i = str(i)
        if i.find("[e")!=-1:
            state = i.replace('[edit]', '')
        elif i.find(" \("):
            region = re.sub(' \(.*', '', i)
            lst = [state,region]
            df2 = pd.DataFrame([lst], columns=['State','RegionName'])
            df = df.append(df2)
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    
    return df


# In[ ]:

data = pd.read_excel('gdplev.xls', delimiter="\t", header = None)
data = data[8:]
data = data.drop(data.columns[[3,7]],axis=1)
data.columns = ['Year','GDP in billions of current dollars_year','GDP in billions of chained 2012 dollars','Year_Quarter','GDP in billions of current dollars_quarter','GDP in billions of chained 2012 dollars_q']
data = data.drop(data.columns[[0,1,2]],axis=1)
data = data[212:]
data = data.reset_index()


# In[ ]:

def get_recession_start():
    c = ''
    for i in range(2,len(data['GDP in billions of current dollars_quarter'])-2):
        if ((data['GDP in billions of chained 2012 dollars_q'][i] < data['GDP in billions of chained 2012 dollars_q'][i-1]) & 
            (data['GDP in billions of chained 2012 dollars_q'][i-2] > data['GDP in billions of chained 2012 dollars_q'][i-1]) &
            (data['GDP in billions of chained 2012 dollars_q'][i] < data['GDP in billions of chained 2012 dollars_q'][i+1]) & 
            (data['GDP in billions of chained 2012 dollars_q'][i+1] < data['GDP in billions of chained 2012 dollars_q'][i+2])): 
            c = data['Year_Quarter'][i-3]
            
    
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    
    return c


# In[ ]:

def get_recession_end():
    c = ''
    for i in range(0,len(data['GDP in billions of current dollars_quarter'])-4):
        if ((data['GDP in billions of chained 2012 dollars_q'][i] > data['GDP in billions of chained 2012 dollars_q'][i+1]) & 
            (data['GDP in billions of chained 2012 dollars_q'][i+1] > data['GDP in billions of chained 2012 dollars_q'][i+2]) &
            (data['GDP in billions of chained 2012 dollars_q'][i+2] < data['GDP in billions of chained 2012 dollars_q'][i+3]) & 
            (data['GDP in billions of chained 2012 dollars_q'][i+3] < data['GDP in billions of chained 2012 dollars_q'][i+4])): 
            c = data['Year_Quarter'][i+4]
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
       
    return c


# In[ ]:

def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    c = ''
    for i in range(0,len(data['GDP in billions of current dollars_quarter'])-4):
        if ((data['GDP in billions of chained 2012 dollars_q'][i] > data['GDP in billions of chained 2012 dollars_q'][i+1]) & 
            (data['GDP in billions of chained 2012 dollars_q'][i+1] > data['GDP in billions of chained 2012 dollars_q'][i+2]) &
            (data['GDP in billions of chained 2012 dollars_q'][i+2] < data['GDP in billions of chained 2012 dollars_q'][i+3]) & 
            (data['GDP in billions of chained 2012 dollars_q'][i+3] < data['GDP in billions of chained 2012 dollars_q'][i+4])): 
            c = data['Year_Quarter'][i+2]
    
    return c


# In[ ]:

def convert_housing_data_to_quarters():
    house = pd.read_csv('City_Zhvi_AllHomes.csv')
    house_1 = house
    #house_1 = house_1[['RegionID','RegionName','State','Metro','CountyName','SizeRank']]
    house_1 = house_1[['RegionName','State']]
    house_2 = house.loc[:,'2000-01':]
    house = pd.concat([house_1,house_2],axis=1)
    house['State'] = house['State'].map(states)
    house = house.sort_values(['State','RegionName']).set_index(['State','RegionName'])
    house.columns = pd.to_datetime(house.columns)
    house = house.resample('Q',axis=1).mean()
    house = house.rename(columns=lambda x: str(x.to_period('Q')).lower())
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    
    Note: Quarters are defined in the project description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    
    return house


# In[ ]:

def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    better =''
    different = bool
    university = get_list_of_university_towns()
    superset = convert_housing_data_to_quarters()
    rec_start=get_recession_start()
    rec_bottom = get_recession_bottom()
    qrt_bfr_rec_start_id = superset.columns.get_loc(rec_start) - 1
    qrt_bfr_rec_start = superset.columns[qrt_bfr_rec_start_id]
    

    superset['PriceRatio'] = superset[qrt_bfr_rec_start].div(superset[rec_bottom])

    university_merged = university.merge(superset,left_on = ['State','RegionName'],right_index=True,how = 'left')
    university_merged = university_merged.sort_values(['State','RegionName']).set_index(['State','RegionName']).dropna()

    non_university_merged = university.merge(superset,left_on = ['State','RegionName'],right_index=True,how = 'right',indicator=True)
    non_university_merged = non_university_merged[non_university_merged['_merge'] == 'right_only']
    non_university_merged = non_university_merged.drop(['_merge'],axis=1).dropna()
    
    a,p = stats.ttest_ind(university_merged['PriceRatio'],non_university_merged['PriceRatio'])
    if p<0.01:
        different = True
    else:
        different = False
    if university_merged['PriceRatio'].mean()>non_university_merged['PriceRatio'].mean():
        better = 'non-university town'
    else:
        better = 'university town'
        
    
    return (different,p,better)


# In[ ]:



