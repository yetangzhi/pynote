
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
get_ipython().magic('matplotlib inline')
import math
import datetime
import lda


# In[2]:

def splitByNmins(date,mins):
    records = pd.read_csv("../../data/rfidnj/storage/normalCarRecords/cars_{:%Y-%m-%d}.csv".format(date),parse_dates=['TIME'])
    sort_records = records.sort(['MOVER_ID','TIME'])

    isNotSameCar = sort_records[0:-1]['MOVER_ID'] != sort_records[1:]['MOVER_ID']
    timeDiffGreater30min = np.diff(sort_records['TIME'].astype(int))/math.pow(10,9) > mins*60
    isNewTraj = np.logical_or(isNotSameCar,timeDiffGreater30min)
    isNewTraj = np.insert(isNewTraj.values,0,True)

    tmp = sort_records[isNewTraj]['TIME']
    tmp2 = pd.DatetimeIndex(tmp).date.astype(str)
    pdtmp = pd.DataFrame(tmp2)
    pdtmp[0] = pdtmp[0] +':' +pdtmp.index.astype(str)
    pdtmp['a'] = sort_records[isNewTraj].index
    pdtmp = pdtmp.set_index('a')
    sort_records['s_id'] = np.nan
    sort_records.ix[isNewTraj,'s_id'] = pdtmp[0]
    sort_records['s_id'].fillna(method='ffill',inplace=True)

    return sort_records


# In[3]:

def getSegmentDF(splitedRecords):
    segmentG = splitedRecords.groupby('s_id')
    segmentDF = pd.DataFrame()
    segmentDF[['s_time','s_cell_id']] = segmentG.first()[['TIME','CELL_ID']]
    segmentDF[['e_time','e_cell_id']] = segmentG.last()[['TIME','CELL_ID']]
    segmentDF['word'] = segmentDF['s_cell_id'] * 10 **4 + segmentDF['e_cell_id']
    segmentDF['MOVER_ID'] = segmentG.first()['MOVER_ID']
    segmentDF = segmentDF[segmentDF['s_time'] != segmentDF['e_time']]
    return segmentDF




