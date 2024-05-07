
import pandas as pd
import geopandas as gpd
import requests

def Data_retreiver(xmin=-77.32,ymin=38.83,xmax=-77.24,ymax=38.88,year=2020,dname='acs/acs5',var=['NAME'],key=''):
    
    payload2 = {'outFields':'STATE,COUNTY,TRACT,BLKGRP,GEOID',
           'geometryType': 'esriGeometryEnvelope',
           'geometry':str([xmin,ymin,xmax,ymax])[1:-1],
           'inSR':'4326',
           'f':'json'
          }

    r2=requests.post('https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Census2020/MapServer/8/query',data=payload2)
    
    features=gpd.read_file(r2.text)
    
    features['GEOID']='1500000US'+features['GEOID']

    sp=','
    cols=sp.join(var)
    cols += ',GEO_ID'
    
    states=features['STATE'].unique()
    counties=features['COUNTY'].unique()
    tracts=features['TRACT'].unique()
    
    if len(states)>1:
        states=sp.join(states)
        counties='*'
        tracts='*'
    elif len(counties)>1:
        states=sp.join(states)
        counties=sp.join(counties)
        tracts='*'
    else:
        states=sp.join(states)
        counties=sp.join(counties)
        tracts=sp.join(tracts)

    base_url=f'https://api.census.gov/data/{year}/{dname}'
    data_url=f'{base_url}?get={cols}&for=block group:*&in=state:{states} county:{counties} tract:{tracts}&key={key}'
    r21=requests.get(data_url)
    df = pd.read_json(r21.text)
    df.columns = df.iloc[0]
    df = df[1:]
    
    features=features.merge(df,how='left',left_on='GEOID',right_on='GEO_ID').iloc[:,:-5]
    
    
    return features
