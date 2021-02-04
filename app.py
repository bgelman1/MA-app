# -*- coding: utf-8 -*-
"""
Created on Sat Jan 23 18:15:47 2021

@author: zevge
"""


import pandas as pd
import matplotlib.pyplot as plt
import geopandas
import plotly.graph_objects as go
import plotly.io as pio
import json
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
import json
#read in and merge voting data
hist = pd.DataFrame()
dist = pd.read_csv('district.csv')
sorr = pd.read_csv('sorround.csv')



dist.columns = ['Town']
sorr.columns = ['Town']
dist['MA3'] = 1
sorr['MA3'] = 0

hist = pd.concat([dist, sorr])

sen = pd.read_csv('sen.csv')
pres = pd.read_csv('pres.csv')
gov = pd.read_csv('gov.csv')
df2 = pd.read_csv('df2.csv')



sen['Town'] = sen['Town'].str.upper()
gov['Town'] = gov['Town'].str.upper()
pres['Town'] = pres['Town'].str.upper()
df2['Town'] = df2['Town'].str.upper()
hist['Town'] = hist['Town'].str.upper()

xyz = pres.merge(sen, on = "Town")
xyz = xyz.merge(gov, on = 'Town', how = 'left')
hist = xyz.merge(hist, on = 'Town')
hist = hist.merge(df2, on='Town', how='left')

hist = hist[["Town", "Sen_diff_Dem", "pres_diff_Dem", 'Gov_diff_Dem', 'MA3', 'Cong_diff_Dem']]

hist['Cong_diff_Dem'] = hist['Cong_diff_Dem'] * 100

hist['Cong_diff_Dem'] = pd.to_numeric(hist['Cong_diff_Dem'])


names = hist['Town']


with open("gj.geojson") as geofile:
    j_file = json.load(geofile)


towns_geo = []

found = []
#fix format of town names
hist['Town'] = hist['Town'].str.upper()
tmp = pres.set_index('Town')
# Looping over the custom GeoJSON file

for town in j_file['features']:
    # town name detection
    town_name = town['properties']['TOWN']
    
  # Checking if that town is in the dataset
    if town_name in tmp.index:
        
      # Getting information from both GeoJSON file and dataFrame
      geometry = town['geometry']
      properties = town['properties']
      
    
  
        # Adding 'id' information for further match between map and data 
      towns_geo.append({
            'type': 'Feature',
            'geometry': geometry,
            'id':town_name,
            'properties': properties
         })
     
        
geo_world_ok = {'type': 'FeatureCollection', 'features': towns_geo}




#make map

app = dash.Dash()
app.layout = html.Div([
    dcc.Dropdown(
        id='demo-dropdown',
       options=[ 
           {"label": "Senate", "value": 'Sen_diff_Dem'},
           {"label": "President", "value": 'pres_diff_Dem'},
           {"label": "Governor", "value": 'Gov_diff_Dem'},
           {"label": "Congress", "value": 'Cong_diff_Dem'} ],
                    
        value = 'Sen_diff_Dem'
    ),
    dcc.Dropdown(
        id='district',
       options=[ 
           {"label": "MA3", "value": 1},
           {"label": "Sorrounding", "value": 0},
            {"label": "Both", "value": 'both'}],
                    
        value = 1
    ),
    

    html.Hr(),
    dcc.Graph(id='display-selected-values'),

])

@app.callback(
    dash.dependencies.Output('display-selected-values', 'figure'),
    [dash.dependencies.Input('demo-dropdown', 'value'),
     dash.dependencies.Input('district', 'value')])
def update_output(race_slctd, in_out):
   
    
    if race_slctd == 'Sen_diff_Dem':
        race = 'Senate'
        hist['Senate'] = hist[race_slctd]
    elif race_slctd == 'pres_diff_Dem':
        race = 'President'
        hist['President'] = hist[race_slctd]
    elif race_slctd == 'Gov_diff_Dem':
        race = 'Governor'
        hist['Governor'] = hist[race_slctd]
    elif race_slctd == 'Cong_diff_Dem':
        race = 'Congress'
        hist['Congress'] = hist[race_slctd]
    
    hist['show'] = 0
    if in_out == 'both':
       hist['show'] = 1
    elif in_out == 1:
         hist['show'][hist['MA3'] == 1] = 1
    elif in_out == 0:
         hist['show'][hist['MA3'] == 0] = 1
    
    
    fig = px.choropleth_mapbox(hist.loc[hist['show'] == 1], geojson=geo_world_ok, locations='Town', color= race,
                           color_continuous_scale="ice",
                           range_color=(hist[race].min(), hist[race].max()),
                           hover_name = 'Town',
                           hover_data = {'Town': False},
                           mapbox_style="carto-positron",
                           zoom=7.5, center = {"lat": 42.5607, "lon": -71.6199},
                           title = 'Difference in Past Two Elections by Town: ' + race,
                           opacity=0.5)
    fig.update_layout(coloraxis_colorbar=dict(
        title= "Dem Change in Past Two Races: "+race,
        thicknessmode="pixels", thickness=50
        
))
       
    return fig
                           



    
   
     
        
    
  
    

       
  

if __name__ == '__main__':
    app.run_server()
server = app.server()
