
# coding: utf-8

# In[29]:

import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
get_ipython().magic(u'matplotlib inline')
import math
import geopandas as geopd
from shapely.geometry import Polygon, Point, LineString
import math


# In[207]:

def xiamenSept2Format(rawDF):
    output = rawDF
    output['SPEED/10'] = output["SPEED/10"] /3.6
    output['TRAJ_ID'] = -1
    output = output[['TRAJ_ID','VEHICLE_ID','GPS_TIME','LONGITUDE/1000000','LATITUDE/1000000','SPEED/10','DIRECTION','HEIGHT','VEHICLE_STATUS','ALARM_STATUS']]
    output.columns = ['TRAJ_ID','MOVER_ID','TIME','X','Y','SPEED','DIRECTION','HEIGHT','VEHICLE_STATUS','ALARM_STATUS']
    return output


# In[213]:

def removePointsByGeo(recordDF,seaGeoDF):
    pts = geopd.GeoSeries([Point(x,y) for x,y in zip(recordDF.X,recordDF.Y)])
    
    isInSea = [False] * len(recordDF)
    seaPoly = seaGeoDF.geometry
    for s in seaPoly:
        tmp = pts.within(s).values
        isInSea = np.logical_or(isInSea,tmp)

    isInSea = pd.Series(isInSea)

    gps = recordDF
    cleanIdx1 = np.logical_and(gps.X >  117.88333 ,gps.X < 118.433333)
    cleanIdx2 = np.logical_and(gps.Y > 24.383333,gps.Y <24.9)
    cIdx = np.logical_and(cleanIdx1,cleanIdx2)
    cleanIdx1 = np.logical_and(gps.X >  118.201627,gps.X < 118.804345)
    cleanIdx2 = np.logical_and(gps.Y > 24.449411,gps.Y <24.526584)
    cIdx2 = np.logical_and(cleanIdx1,cleanIdx2)
    cIdx = np.logical_and(cIdx,np.logical_not(cIdx2))
    cleanIdx1 = np.logical_and(gps.X >  118.072538,gps.X < 118.482465)
    cleanIdx2 = np.logical_and(gps.Y > 23.889365,gps.Y <24.420655)
    cIdx3 = np.logical_and(cleanIdx1,cleanIdx2)
    cIdx = np.logical_and(cIdx,np.logical_not(cIdx3))
    cleanIdx1 = np.logical_and(gps.X >  118.050956,gps.X < 118.545341)
    cleanIdx2 = np.logical_and(gps.Y > 23.971704,gps.Y <24.293167 )
    cIdx4 = np.logical_and(cleanIdx1,cleanIdx2)
    cIdx = np.logical_and(cIdx,np.logical_not(cIdx4))
    cleanIdx1 = np.logical_and(gps.X >  118.147258 ,gps.X < 118.187255)
    cleanIdx2 = np.logical_and(gps.Y > 24.551846 ,gps.Y <24.617017  )
    cIdx5 = np.logical_and(cleanIdx1,cleanIdx2)
    cIdx = np.logical_and(cIdx,np.logical_not(cIdx5))

    cIdx = np.logical_and(cIdx,np.logical_not(isInSea))
    
    output = recordDF[cIdx]
    return output


# In[212]:

def psgStateHelper(x):
    if(x == '0'):
        return 'Unloaded'
    if(x == '1'):
        return 'Loaded'

def decodeState(recordDF):
    output= recordDF
    output['VEHICLE_STATUS'] = output.VEHICLE_STATUS.apply(bin)
    output['VEHICLE_STATUS'] = output['VEHICLE_STATUS'].str[::-1] 
    output = output[output['VEHICLE_STATUS'].str[4] == '0']
    output['psgState'] = output.VEHICLE_STATUS.str[9]
    output['psgState'] = output.psgState.apply(psgStateHelper)
    output.drop(['HEIGHT','VEHICLE_STATUS','ALARM_STATUS'],inplace=True,axis=1)
    return output


# In[211]:

def splitByNmins(recordDF,mins):
    sort_records = recordDF.sort(['MOVER_ID','TIME'])
    isNotSameCar = sort_records[0:-1]['MOVER_ID'] != sort_records[1:]['MOVER_ID']
    sort_records['TIME'] = pd.to_datetime(sort_records['TIME'])
    timeDiffGreaterNmin = np.diff(sort_records['TIME'].astype(int))/math.pow(10,9) > mins*60
    ispsgStateChange = sort_records[:-1]['psgState'] != sort_records[1:]['psgState']
    isNewTraj = np.logical_or(isNotSameCar,timeDiffGreaterNmin)
    isNewTraj = np.logical_or(isNewTraj,ispsgStateChange)
    isNewTraj = np.insert(isNewTraj.values,0,True)

    tmp = sort_records[isNewTraj]['TIME']
    tmp2 = pd.DatetimeIndex(tmp).date.astype(str)
    pdtmp = pd.DataFrame(tmp2)
    pdtmp[0] = pdtmp[0] +':' +pdtmp.index.astype(str)
    pdtmp['a'] = sort_records[isNewTraj].index
    pdtmp = pdtmp.set_index('a')
    sort_records['TRAJ_ID'] = np.nan
    sort_records.ix[isNewTraj,'TRAJ_ID'] = pdtmp[0]
    sort_records['TRAJ_ID'].fillna(method='ffill',inplace=True)
    
    return sort_records


# In[ ]:



