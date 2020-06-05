import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
from datetime import datetime, timedelta

import plotly.graph_objs as go
import plotly.graph_objects as gogo
from plotly.subplots import make_subplots
import itertools

import numpy as np

import time
import base64

from flask import request

import requests
import math 
from scipy import optimize

import json
from collections import Counter

d = pd.read_csv('./all_cases.csv',engine='c')
proj = pd.read_csv('./all_cases_projections.csv',engine='c')

conf = d.loc[np.in1d(d['conf'],'Confirmed')]
recov = d.loc[np.in1d(d['conf'],'Recovered')]
death = d.loc[np.in1d(d['conf'],'Deaths')]

dates_proj = json.load(open('projections_dates.json'))

list_date = [x for x in d.iloc[:,5:].columns]

### colors ###
oray = (248, 148, 6, 0.2) #orange
redy = (242, 38, 19, 0.2) # red
grey = (30, 130, 76, 0.2) #green
    

dfy = pd.read_csv('./ISO.csv',index_col=0, engine='c')
world = pd.read_csv('./world_population.csv', engine='c')

diccy = {}
for i,j in zip(dfy['iso'],dfy['COUNTRY']):
    diccy[i] = j

app = dash.Dash(__name__)

app.index_string = """<!DOCTYPE html>
<html lang="en">
    <head>
        <link rel="preload" type="text/css" href="./assets/lou.css" as="style">
        <link rel="stylesheet" type="text/css" href="./assets/lou.css" async>
        
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta charset="UTF-8">
        <title>Coronavirus COVID-19</title>
        <meta name="description" content="Comprehensive overview of the progression of Coronavirus COVID-19 spread over time. Interactive Map of cases available for every country/state impacted, time series evolution, daily new cases by country with history, cumulative view of the coronavirus spread also with history. Modelling and forecasting of the spread. virus-corona heroku by: Louis du Plessis.">
        <link rel="icon" type="image/x-icon" href="/assets/favicon.ico">
        <!-- <link rel="preconnect" href="https://api.mapbox.com" crossorigin>
        <link rel="dns-prefetch" href="https://api.mapbox.com" async> -->
        <link rel="preconnect" href="https://www.google-analytics.com" crossorigin>
        <link rel="dns-prefetch" href="https://www.google-analytics.com" async>
        <!-- Global site tag (gtag.js) - Google Analytics -->
        
        <!-- PUT THE GOOGLE ANALYTICS TAG HERE -->

    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
            <link rel="apple-touch-icon" href="./assets/logoA.png" async>
            <meta http-equiv="Cache-control" content="public">
        </footer>
    </body>
</html>"""



server = app.server

app.config.suppress_callback_exceptions = True

tab_style = {'borderBottom': '1px solid #d6d6d6','padding': '6px','backgroundColor': '#FFFFFF'} #'fontWeight': 'bold',

tab_selected_style = {'borderTop': '1px solid #d6d6d6','borderBottom': '1px solid #d6d6d6','backgroundColor': '#119DFF','color': 'white','padding': '6px'}

app.layout = html.Div([
                dcc.Store(id='dropdown-cache', data='initial value'),
                dcc.Store(id='dropdown1-cache', data='initial value'),
                dcc.Store(id='dropdown2-cache', data='initial value'),

                dcc.Tabs(id='tabs',value='tab-0', style={'top':'7px','height': '35px','position': 'fixed','width': '99%','z-index': '9999999'}, children=[
                               
            ############################################
            ############### first page #################
            ############################################
                dcc.Tab(label='Global summary', value='tab-0',style=tab_style, selected_style=tab_selected_style, children=[
                            
                html.Div([html.H5('')],style={'z-index': '9999998','top':'0px','filter': 'blur(5px)','position': 'fixed','height':'90px',
                                'width': '100%','backgroundColor': '#D8E0E5','margin-bottom': '7px'}),                                                          
                            
                html.Div([
                    html.Img(alt="logo", src='data:image/png;base64,{}'.format(base64.b64encode(open('logo.png', 'rb').read()).decode()),
                             style={'margin-left':'7px','width': '40px','height': '40px','vertical-align': 'middle','margin-top':'80px','display': 'inline-block'}),                                             
                    html.H1('Map of COVID-19 Cases',style={'vertical-align': 'middle','display': 'inline-block','margin-left':'7px', 'color':'black','margin-top':'95px'}),
                        ],style={'display': 'inline-block','vertical-align': 'middle','margin-bottom':'10px'}),
                                                             
                                                                     
                dcc.Markdown('''
                This dashboard contains a comprehensive overview of the progression of Coronavirus COVID-19 spread. 
                The COVID-19 data is updated once a day around 04:00 (UTC) - 1pm in Australia and 5am in France - thanks to John Hopkins University (JHU). 
                
                **1.** Click on any country or state on the map for the indicators, time series and graphs to update accordingly. (**click outside the country or in the ocean to reset**)   
                **2.** Use the dropdowns on the top panel to display selective data accross all 3 pages.
                
                **ATTENTION:**  
                JHU will not provide recovered cases at state level for the US as there is no reliable data source reporting recovered cases. (only recovered for the US overall will be displayed)    

                _*Use mouse (or finger on mobile) and highlight/select a region in the graphs to zoom into details. Double tap on graph to reset your action._  
                _*For best viewing experience, please use Chrome or Firefox._  
                ''',style={'margin-top': '0px','margin-bottom':'5px','margin-left': '7px','margin-right': '7px','vertical-align': 'top'}),                                                      
                
                ###############                                                     
                    html.A([html.Img(id='body-image1', alt="news covid19", src='data:image/png;base64,{}'.format(base64.b64encode(open('virus.png', 'rb').read()).decode()),
                                 style={'height':50,'position': 'fixed','left':'7px','bottom':'7px','z-index': '9999999'})],
                        id='url1', style={'margin-left': '7px','margin-right': '7px','width':'25%','height':50}), 
                #################
    
                            
                html.Div([html.H5('')],style={'margin-left': '7px','margin-right': '7px','width': '99%', 'display': 'inline-block', 'vertical-align': 'middle',
                                'backgroundColor': '#D8E0E5','margin-top': '10px','margin-bottom': '10px'}),                                                      
                                                                                   
                dcc.Dropdown(id='country',style={'width': '32.5%','margin-bottom': '4px','display': 'inline-block','position': 'fixed','left':'8px','top':'50px','background':'lightgrey',
                                                 'color':'black','z-index': '9999999'},multi=True,placeholder="Select a country..."),
                dcc.Dropdown(id='state',style={'width': '32.5%','margin-bottom': '4px','display': 'inline-block','position': 'fixed','left':'33.7%','top':'50px','background':'lightgrey',
                                               'color':'black','z-index': '9999999'},multi=True,placeholder="Select a province/state..."),
                dcc.Dropdown(id='conf',style={'width': '32.5%','margin-bottom': '4px','display': 'inline-block','position': 'fixed','right':'9px','top':'50px','background':'lightgrey',
                                              'color':'black','z-index': '9999999'}, multi=True,placeholder="Select a case..."),
                
                html.Div([
                    html.Div([dcc.Graph(id='kpi0', style={'height': 110,'margin-top': '0px'})]),
                    html.Div([dcc.Graph(id='kpi1', style={'height': 110,'margin-top': '10px'})]),
                    html.Div([dcc.Graph(id='kpi2', style={'height': 110,'margin-top': '10px'})]),
                    html.Div([dcc.Graph(id='kpi3', style={'height': 110,'margin-top': '10px'})]),   
                        ],id='test',style={'margin-top': '10px','margin-left': '7px','display': 'inline-block', 'vertical-align': 'top','width': '21%'}),
                                                                     
                                                                     
                html.Div([dcc.Graph(id='map1', style={'height': 240,'margin-top': '0px'}),
                          dcc.Graph(id='graph1', style={'height': 230,'margin-top': '10px'})],
                         id='test1',style={'margin-left': '7px','margin-right': '7px','width': '76%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                
                            
                html.Div([dcc.Graph(id='graph111', style={'height': 230,'margin-top': '10px'})],
                         id='test111',style={'margin-left': '7px','width': '48.4%', 'display': 'inline-block', 'vertical-align': 'middle'}),       
                html.Div([dcc.Graph(id='graph1111', style={'height': 230,'margin-top': '10px'})],
                         id='test1111',style={'margin-left': '7px','margin-right': '7px','width': '48.5%', 'display': 'inline-block', 'vertical-align': 'middle'}),       
                             
                
                dcc.Markdown('''
                _*The two graphs above forecast numbers for the next 45 days, it may detect multiple waves like Beijing and Heilongjiang in China or Victoria in Australia. If two waves are very close to one another, it will be counted as one like Saskatchewan in Canada._   
                ''',style={'margin-top': '0px','margin-bottom':'0px','margin-left': '7px','margin-right': '7px'}),         
                            
      
                html.Div([dcc.Graph(id='graph11', style={'height': 230,'margin-top': '0px'})],
                         id='test11',style={'margin-left': '7px','width': '48.4%', 'display': 'inline-block', 'vertical-align': 'middle'}),       
                            
                html.Div([dcc.Graph(id='graph41', style={'height': 230,'margin-top': '0px'})],
                         id='test41',style={'margin-left': '7px','margin-right': '7px','width': '48.5%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                            
                dcc.Markdown('''
                _* **Daily cases growth factor** measures how fast the number of new cases is going up or down. 
                If it goes above one, the number of new cases each day is going up and if it stays above one consistently, it is not a good sign. 
                If it stays below one, the outbreak is under control._   
                ''',style={'margin-top': '0px','margin-bottom':'0px','margin-left': '7px','margin-right': '7px'}),              
                                              
                            
                html.Div([html.H5('')],style={'margin-left': '7px','margin-right': '7px','width': '99%', 'display': 'inline-block', 'vertical-align': 'middle',
                                'backgroundColor': '#D8E0E5','margin-top': '30px','margin-bottom': '10px'}),                                                      
                                             
                dcc.Markdown('''
                ###### Tracking the evolution of countries once they hit 50 cases:
                
                If you want to understand what may happen in your country, take a look at what other countries are experiencing.
                The graph below may provide some insight by showing the evolution of the spread of the virus once a country hits around 50 cases. 
                (select another country(ies) and province/state within the country(ies) selected from the dropdowns to see comparison with the current epicenters)
                
                Of course, many factors affect how the spread is controlled and when government measures are put in place, e.g: travel ban, quarantines, shutdowns and social distancing.
                
                Some countries have reacted faster than others, like certain eastern countries that have learned from their experience with SARS in 2003, and the difference can now be seen through their numbers.
                
                ''',style={'margin-top': '30px','margin-left': '7px','margin-right': '7px','vertical-align': 'top'}),              
                                   
                html.Div([dcc.Graph(id='graph12', style={'height': 400,'margin-top': '10px'})],
                         style={'margin-left': '7px','margin-right': '7px','width': '97.5%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                    
                html.Div([html.H5('')],style={'margin-left': '7px','margin-right': '7px','width': '99%', 'display': 'inline-block', 'vertical-align': 'middle',
                                'backgroundColor': '#D8E0E5','margin-top': '30px','margin-bottom': '10px'}),                                                                      
                            
                dcc.Markdown('''
                ###### Modelling - importance of social distancing:
                
                The graph below displays the importance of social distancing with the early measures taken by governements 
                to slow the spread and therefore take pressure off the healthcare system.
                
                Mathematical models simulating viral spread within populations are typically based on SIR models which is a compartimental disease model.  
                Meaning that each individual in a population is assigned to one of the following compartments:  
                1. Susceptible: can become infected.  
                2. Infectious: are infected.  
                3. Recovered: are no longer infected and potential immune.
                
                The model below assumes:  
                1. the initial contact rate (transmission) is 0.5.  
                2. the average recovery rate is 15 days.  
                
                The slider below represents the date when a lockdown or social distancing measure is put in place. 
                it will therefore have a direct impact on the contact rate by decreasing (days 15 for example) or remain the same (days 60).
                
                Try different days to see the impact on a country, impressive right?
                
                ''',style={'margin-top': '30px','margin-left': '7px','margin-right': '7px','vertical-align': 'top'}),                          
                            
                html.Div([
                    dcc.Slider(id='slid1',min=0,max=60,step=1,updatemode='mouseup',marks={x: '{} days'.format(x) for x in range(0,61,10)},value=60,className='margin10'),              
                    dcc.Graph(id='graph14', style={'height': 400,'margin-top': '10px'})],
                         style={'margin-left': '7px','margin-right': '7px','width': '97.5%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                    
                                                    
                html.Div([html.H5('')],style={'margin-left': '7px','margin-right': '7px','width': '99%', 'display': 'inline-block', 'vertical-align': 'middle',
                                              'backgroundColor': '#D8E0E5','margin-top': '30px','margin-bottom': '10px'}),                                                      
                                      
                dcc.Markdown('''
                _DISCLAIMER: this dashboard, copyright 2020 Louis du Plessis, all rights reserved, is provided to the public strictly for information purposes. 
                The web-app relies upon publicly available data from multiple sources, that do not always agree. 
                I hereby disclaim any and all representations and warranties with respect to the web-app, including accuracy, fitness for use, and merchantability. 
                Reliance on the web-app for medical guidance or use of the web-app in commerce is strictly prohibited._
                 
                _*If you have any questions or comments, please contact Louis du Plessis @ <louis@du-plessis.fr> or connect with me on LinkedIn [here](https://www.linkedin.com/in/louis-du-plessis-de-gren%C3%A9dan-01a860196/)._
                ''',style={'margin-top': '30px','margin-left': '7px','margin-right': '7px','vertical-align': 'top'}),        
                 
                  ]),                                                     
                                                                     
                ##########################################
                ############# second page ################
                ##########################################
                dcc.Tab(label='Cases by country', value='tab-1',style=tab_style, 
                        selected_style=tab_selected_style, children=[
                    
                     html.Div([html.H5('')],style={'z-index': '9999998','top':'0px','filter': 'blur(5px)','position': 'fixed','height':'90px','margin-left': '0px',
                                'margin-right': '0px','width': '100%', 'vertical-align': 'middle','backgroundColor': '#D8E0E5','margin-top': '0px','margin-bottom': '7px'}),                                                      
                                          
                    html.Div([
                    html.Img(alt="logo", src='data:image/png;base64,{}'.format(base64.b64encode(open('logo.png', 'rb').read()).decode()),
                             style={'margin-left':'7px','width': '40px','height': '40px','vertical-align': 'middle','margin-top':'80px','display': 'inline-block'}),
                                                                     
                    html.H1('Map of COVID-19 Cases',style={'display': 'inline-block','margin-left':'7px','vertical-align': 'middle','color':'black','margin-top':'95px'}),
                        ],style={'display': 'inline-block','vertical-align': 'middle','margin-bottom':'10px'}),
                                                                     
                dcc.Markdown('''
                This page displays the cumulative cases by country with the number of cases per million people (first graph), as well as ratios for each country (second graph).
                Use the slider to display the data for a specific date and the dropdowns for a specific country(ies) and/or province(s). 
                
                _*Use mouse (or finger on mobile) and highlight/select a region in the graphs to zoom into details. Double tap on graph to reset your action._  
                _*For best viewing experience, please use Chrome or Firefox._   
                ''',style={'margin-top': '0px','margin-bottom':'5px','margin-left': '7px','margin-right': '7px','vertical-align': 'top'}),                                                      
                                                                     
                ###############                                                     
                html.A([html.Img(id='body-image2', alt="news covid19", src='data:image/png;base64,{}'.format(base64.b64encode(open('virus.png', 'rb').read()).decode()),
                                 style={'height':50,'position': 'fixed','left':'7px','bottom':'7px','z-index': '9999999'})],
                        id='url2',style={'margin-left': '7px','margin-right': '7px','width':'25%','height':50}), 
                #################                
                            
                            
                html.Div([html.H5('')],style={'margin-left': '7px','margin-right': '7px','width': '99%', 'display': 'inline-block', 'vertical-align': 'middle',
                                'backgroundColor': '#D8E0E5','margin-top': '10px','margin-bottom': '10px'}),                                                      
                              
                dcc.Dropdown(id='country1',style={'width': '32.5%','margin-bottom': '4px','display': 'inline-block','position': 'fixed','left':'8px','top':'50px',
                                                  'background':'lightgrey','color':'black','z-index': '9999999'},multi=True,placeholder="Select a country..."),
                dcc.Dropdown(id='state1',style={'width': '32.5%','margin-bottom': '4px','display': 'inline-block','position': 'fixed','left':'33.7%','top':'50px','background':'lightgrey',
                                                'color':'black','z-index': '9999999'},multi=True,placeholder="Select a province/state..."),
                dcc.Dropdown(id='conf1',style={'width': '32.5%','margin-bottom': '4px','display': 'inline-block','position': 'fixed','right':'9px','top':'50px',
                                               'background':'lightgrey','color':'black','z-index': '9999999'},multi=True,placeholder="Select a case..."),         
                            
                html.Div([ 
                    dcc.Slider(id='RangeSlider',min=0,max=len(list_date)-1,value=len(list_date)-1,updatemode='mouseup',
                               marks={int(x): list_date[x][:10] for x in np.sort(list(set([x for x in range(0,len(list_date)-1,21)])))},className='margin10')],
                            style={'margin-left': '7px','margin-right': '7px','margin-bottom': '15px','width': '97.5%', 'display': 'inline-block', 
                                   'vertical-align': 'middle'}),                                                   
                
                html.Div([            
                dcc.Markdown('''**Countries to display:** ''',style={'margin-left': '10px','display': 'inline-block'}),
                dcc.RadioItems(id="radioX",options=[{"label": "Top 5", "value": 5},{"label": "Top 15", "value": 15},
                                                    {"label": "Top 50", "value": 50},{"label": "All", "value": 55}],
                                         value=15,labelStyle={'display': 'inline-block', 'margin-left':'7px'},
                               style={"padding": "10px",'margin-left': '7px','display': 'inline-block'}),             
                                       
                dcc.Markdown('''**Sort graph:** ''',style={'margin-left': '10px','display': 'inline-block'}),
                dcc.RadioItems(id="radioX3",options=[{"label": "Cumulative cases", "value": 1},{"label": "Per million people", "value": 2}],
                               value=1,labelStyle={'display': 'inline-block', 'margin-left':'7px'},
                               style={"padding": "10px",'margin-left': '7px','display': 'inline-block'})
                ],style={'width': '99%'}),
                            
                html.Div([
                    html.Div([dcc.Graph(id='kpi00', style={'height': 110,'margin-top': '0px','font-size':'1.5rem'})]),
                    html.Div([dcc.Graph(id='kpi4', style={'height': 110,'margin-top': '10px','font-size':'1.5rem'})]),
                    html.Div([dcc.Graph(id='kpi5', style={'height': 110,'margin-top': '10px','font-size':'1.5rem'})]),
                    html.Div([dcc.Graph(id='kpi6', style={'height': 110,'margin-top': '10px','font-size':'1.5rem'})]),   
                    ],id='test2',style={'margin-top': '10px','margin-left': '7px','display': 'inline-block', 'vertical-align': 'top','width': '21%'}),
                               
                                         
                html.Div([
                    dcc.Graph(id='graph2', style={'height': 470,'margin-top': '10px'})],
                    id='test3',style={'margin-left': '7px','margin-right': '7px','width': '76%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                
                
                html.Div([html.H5('')],style={'margin-left': '7px','margin-right': '7px','width': '99%', 'display': 'inline-block', 'vertical-align': 'middle',
                                'backgroundColor': '#D8E0E5','margin-top': '30px','margin-bottom': '10px'}),                                                      
                                                 
                dcc.Markdown('''
                ###### Ratios by country:
                
                The first graph below shows the recovery rate as a percentage (Recovered cases / Confirmed cases), as well as the number of confirmed cases, which provides a comparative scale.
                For example, Nepal has 100% recovery rate for 1 confirmed case overall, while China has more than 77% recovery rate but for more than 80,000 confirmed cases, therefore it is more meaningful.
                
                The second graph below shows the mortality rate as a percentage (Death cases / Confirmed cases), as well as the number of confirmed cases, which provides a comparative scale.
                For example, Morocco has 33.3% mortality rate but for 3 confirmed cases overall.
                
                The third graph below shows the ratio of recovery to death as a format X:1 (X people recovered for 1 death: recovered cases / death cases), as well as the number of recovered cases, which provides a comparative scale.
                For example, China has more than 60,000 recovered cases for more than 3,000 deaths which gives a ratio of 20 recovered for 1 death, therefore 20:1.
                
                ''',style={'margin-top': '30px','margin-left': '7px','margin-right': '7px','vertical-align': 'top'}),              
                                  

                dcc.RadioItems(id="radio",options=[{"label": "Sort rates", "value": 1},{"label": "Sort cases", "value": 2}],
                                         value=2,labelStyle={'display': 'inline-block', 'margin-left':'20px'},
                               style={"padding": "10px", "max-width": "800px", 'margin-left': '7px','display': 'inline-block'}),            
                            
                html.Div([
                    dcc.Graph(id='graph21', style={'height': 510,'margin-top': '10px'})],
                         style={'margin-left': '7px','margin-right': '7px','width': '97.5%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                
                            
                html.Div([html.H5('')],style={'margin-left': '7px','margin-right': '7px','width': '99%', 'display': 'inline-block', 'vertical-align': 'middle',
                                'backgroundColor': '#D8E0E5','margin-top': '30px','margin-bottom': '10px'}),                                                      
                          
                            
                dcc.Markdown('''
                _DISCLAIMER: this dashboard, copyright 2020 Louis du Plessis, all rights reserved, is provided to the public strictly for information purposes. 
                The web-app relies upon publicly available data from multiple sources, that do not always agree. 
                I hereby disclaim any and all representations and warranties with respect to the web-app, including accuracy, fitness for use, and merchantability. 
                Reliance on the web-app for medical guidance or use of the web-app in commerce is strictly prohibited._
                 
                _*If you have any questions or comments, please contact Louis du Plessis @ <louis@du-plessis.fr> or connect with me on LinkedIn [here](https://www.linkedin.com/in/louis-du-plessis-de-gren%C3%A9dan-01a860196/)._
                ''',style={'margin-top': '30px','margin-left': '7px','margin-right': '7px','vertical-align': 'top'}),                                                     
                                                                     
                            
                ]),
                
                      
                #######################################
                ############### third page ############
                #######################################
                dcc.Tab(label='New cases by day', value='tab-2', style=tab_style, 
                        selected_style=tab_selected_style, children=[
                            
                    html.Div([html.H5('')],style={'z-index': '9999998','top':'0px','filter': 'blur(5px)','position': 'fixed','height':'90px','margin-left': '0px',
                                'margin-right': '0px','width': '100%', 'vertical-align': 'middle','backgroundColor': '#D8E0E5','margin-top': '0px','margin-bottom': '7px'}),                                                      
                                      
                    html.Div([
                    html.Img(alt="logo", src='data:image/png;base64,{}'.format(base64.b64encode(open('logo.png', 'rb').read()).decode()),
                             style={'margin-left':'7px','width': '40px','height': '40px','vertical-align': 'middle','margin-top':'80px','display': 'inline-block'}),
                                                                     
                    html.H1('Map of COVID-19 Cases',style={'display': 'inline-block','margin-left':'7px','vertical-align': 'middle','color':'black','margin-top':'95px'}),
                        ],style={'display': 'inline-block','vertical-align': 'middle','margin-bottom':'10px'}),
                                                                     
                                                                     
                dcc.Markdown('''
                This page displays new additional cases by day (first graph) and by country (second graph), use the slider to display data for a specific date and the dropdowns for a specific country(ies) and/or province(s).
                
                The **Growth Factor** in the first graph is the cumulative progression rate, meaning that if the virus is spreading faster, it goes up, if the virus is slowing down, it goes down.
                
                _*Use mouse (or finger on mobile) and highlight/select a region in the graphs to zoom into details. Double tap on graph to reset your action._  
                _*For best viewing experience, please use Chrome or Firefox._  
                ''',style={'margin-top': '0px','margin-bottom':'5px','margin-left': '7px','margin-right': '7px','vertical-align': 'top'}),                                                      
                                                                     
                
                ###############                                                     
                html.A([html.Img(id='body-image3', alt="news covid19", src='data:image/png;base64,{}'.format(base64.b64encode(open('virus.png', 'rb').read()).decode()),
                                 style={'height':50,'position': 'fixed','left':'7px','bottom':'7px','z-index': '9999999'})],
                        id='url3', style={'margin-left': '7px','margin-right': '7px','width':'25%','height':50}), 
                #################            
                            
                            
                html.Div([html.H5('')],style={'margin-left': '7px','margin-right': '7px','width': '99%', 'display': 'inline-block', 'vertical-align': 'middle',
                                'backgroundColor': '#D8E0E5','margin-top': '10px','margin-bottom': '10px'}),                                                      
                              
                dcc.Dropdown(id='country2',style={'width': '32.5%','margin-bottom': '4px','display': 'inline-block','position': 'fixed','left':'8px','top':'50px',
                                                  'background':'lightgrey','color':'black','z-index': '9999999'},multi=True,placeholder="Select a country..."),
                dcc.Dropdown(id='state2',style={'width': '32.5%','margin-bottom': '4px','display': 'inline-block','position': 'fixed','left':'33.7%','top':'50px',
                                                'background':'lightgrey','color':'black','z-index': '9999999'},multi=True,placeholder="Select a province/state..."),
                dcc.Dropdown(id='conf2',style={'width': '32.5%','margin-bottom': '4px','display': 'inline-block','position': 'fixed','right':'9px','top':'50px',
                                               'background':'lightgrey','color':'black','z-index': '9999999'},multi=True,placeholder="Select a case..."),             
                                   
                html.Div([
                    dcc.Slider(id='RangeSlider1',min=0,max=len(list_date)-1,value=len(list_date)-1,updatemode='mouseup',
                               marks={int(x): list_date[x][:10] for x in np.sort(list(set([x for x in range(0,len(list_date)-1,21)])))},className='margin10')], 
                    style={'margin-left': '7px','margin-right': '7px','margin-bottom': '15px','width': '97.5%', 'display': 'inline-block', 'vertical-align': 'middle'}),                                                   
                                                                                                                                                                                   
                html.Div([
                    html.Div([dcc.Graph(id='kpi000', style={'height': 110,'margin-top': '0px','font-size':'1.5rem'})]),
                    html.Div([dcc.Graph(id='kpi7', style={'height': 110,'margin-top': '10px','font-size':'1.5rem'})]),
                    html.Div([dcc.Graph(id='kpi8', style={'height': 110,'margin-top': '10px','font-size':'1.5rem'})]),
                    html.Div([dcc.Graph(id='kpi9', style={'height': 110,'margin-top': '10px','font-size':'1.5rem'})]),
                    ],id='test4',style={'margin-top': '10px','margin-left': '7px','display': 'inline-block', 'vertical-align': 'top','width': '21%'}),
                                                                                                                                 
                html.Div([
                    dcc.Graph(id='graph3', style={'height': 470,'margin-top': '10px'})],
                    id='test5',style={'margin-left': '7px','margin-right': '7px','width': '76%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                         
                html.Div([html.H5('')],style={'margin-left': '7px','margin-right': '7px','width': '99%', 'display': 'inline-block', 'vertical-align': 'middle',
                                'backgroundColor': '#D8E0E5','margin-top': '30px','margin-bottom': '10px'}),                                                      
                                    
                dcc.Markdown('''
                ###### New cases by country:
                
                Displays the new daily cases - Confirmed, Recovered, Deaths - for each country for the specific day you have selected above on the slider.
                ''',style={'margin-top': '30px','margin-left': '7px','margin-right': '7px','vertical-align': 'top'}),             
                
                dcc.Markdown('''Countries to display:  ''',style={'margin-left': '40px','display': 'inline-block'}),
                dcc.RadioItems(id="radioX2",options=[{"label": "Top 5", "value": 5},{"label": "Top 15", "value": 15},
                                                     {"label": "Top 50", "value": 50},{"label": "All", "value": 55}],
                                         value=15,labelStyle={'display': 'inline-block', 'margin-left':'7px'},
                               style={"padding": "10px",'margin-left': '7px','display': 'inline-block'}),             
                            
                html.Div([
                    dcc.Graph(id='graph4', style={'height': 510,'margin-top': '10px'})],
                         style={'margin-left': '7px','margin-right': '7px','width': '97.5%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                    
                            
                html.Div([html.H5('')],style={'margin-left': '7px','margin-right': '7px','width': '99%', 'display': 'inline-block', 'vertical-align': 'middle','backgroundColor': '#D8E0E5','margin-top': '30px','margin-bottom': '10px'}),                                                      
                                      
                            
                dcc.Markdown('''
                _DISCLAIMER: this dashboard, copyright 2020 Louis du Plessis, all rights reserved, is provided to the public strictly for information purposes. 
                The web-app relies upon publicly available data from multiple sources, that do not always agree. 
                I hereby disclaim any and all representations and warranties with respect to the web-app, including accuracy, fitness for use, and merchantability. 
                Reliance on the web-app for medical guidance or use of the web-app in commerce is strictly prohibited._
                 
                _*If you have any questions or comments, please contact Louis du Plessis @ <louis@du-plessis.fr> or connect with me on LinkedIn [here](https://www.linkedin.com/in/louis-du-plessis-de-gren%C3%A9dan-01a860196/)._
                ''',style={'margin-top': '30px','margin-left': '7px','margin-right': '7px','vertical-align': 'top'}),                        
                                                                                                                      

                 ]),
                    
                    
                ]),
        ])   


# pre-filled dropdowns COUNTRY
@app.callback([Output('country', 'options'),Output('country1', 'options'),Output('country2', 'options')],
              [Input('state', 'value'),Input('conf', 'value'),
               Input('state1', 'value'),Input('conf1', 'value'),
               Input('state2', 'value'),Input('conf2', 'value')])
def set_region(state,conf,state1,conf1,state2,conf2):
    fltr = d
    if state:
        fltr = fltr.loc[np.in1d(fltr['Province/State'],state)]
    if conf:
        fltr = fltr.loc[np.in1d(fltr['conf'],conf)]
    if state1:
        fltr = fltr.loc[np.in1d(fltr['Province/State'],state1)]
    if conf1:
        fltr = fltr.loc[np.in1d(fltr['conf'],conf1)]
    if state2:
        fltr = fltr.loc[np.in1d(fltr['Province/State'],state2)]
    if conf2:
        fltr = fltr.loc[np.in1d(fltr['conf'],conf2)]
    listo = [{'label': i, 'value': i} for i in list(fltr['Country/Region'].unique())]
    return listo,listo,listo


# pre-filled dropdowns STATE
@app.callback([Output('state', 'options'),Output('state1', 'options'),Output('state2', 'options')],
              [Input('country', 'value'),Input('conf', 'value'),
              Input('country1', 'value'),Input('conf1', 'value'),
              Input('country2', 'value'),Input('conf2', 'value')])
def set_state(country, conf,country1, conf1,country2, conf2):
    fltr = d
    if country:
        fltr = fltr.loc[np.in1d(fltr['Country/Region'],country)]
    if conf:
        fltr = fltr.loc[np.in1d(fltr['conf'],conf)]
    if country1:
        fltr = fltr.loc[np.in1d(fltr['Country/Region'],country1)]
    if conf1:
        fltr = fltr.loc[np.in1d(fltr['conf'],conf1)]
    if country2:
        fltr = fltr.loc[np.in1d(fltr['Country/Region'],country2)]
    if conf2:
        fltr = fltr.loc[np.in1d(fltr['conf'],conf2)]
    listo = [{'label': i, 'value': i} for i in list(fltr['Province/State'].unique())]
    return listo,listo,listo
  
    
# pre-filled dropdowns CONF/DEATH/RECOV
@app.callback([Output('conf', 'options'),Output('conf1', 'options'),Output('conf2', 'options')],
              [Input('state', 'value'),Input('country', 'value'),
              Input('state1', 'value'),Input('country1', 'value'),
              Input('state2', 'value'),Input('country2', 'value')])
def set_case(state,country,state1,country1,state2,country2):
    fltr = d
    if state:
        fltr = fltr.loc[np.in1d(fltr['Province/State'],state)]
    if country:
        fltr = fltr.loc[np.in1d(fltr['Country/Region'],country)]
    if state1:
        fltr = fltr.loc[np.in1d(fltr['Province/State'],state1)]
    if country1:
        fltr = fltr.loc[np.in1d(fltr['Country/Region'],country1)]
    if state2:
        fltr = fltr.loc[np.in1d(fltr['Province/State'],state2)]
    if country2:
        fltr = fltr.loc[np.in1d(fltr['Country/Region'],country2)]
    listo = [{'label': i, 'value': i} for i in list(fltr['conf'].unique())]
    return listo,listo,listo


###########################################################   
# callback portion for synchronizing dropdown across tabs #
###########################################################

######### dropdown 1 #########
@app.callback(Output('dropdown-cache', 'data'),[Input('country', 'value'),Input('country1', 'value'),Input('country2', 'value')],[State('tabs', 'value')])
def store_dropdown_cache(tab_0_drodown_sel,tab_1_drodown_sel, tab_2_drodown_sel, tab):
    if tab == 'tab-0':
        return tab_0_drodown_sel
    elif tab == 'tab-1':
        return tab_1_drodown_sel
    elif tab == 'tab-2':
        return tab_2_drodown_sel

@app.callback(Output('country', 'value'),[Input('tabs', 'value')],[State('dropdown-cache', 'data')])
def synchronize_dropdowns(_, cache):
    if type(cache) != type(list()):
        def get_country(ip_address):
            try:
                response = requests.get("http://ip-api.com/json/{}".format(ip_address))
                js = response.json()
                countr = js['countryCode']
                return countr
            except Exception:
                return 'nope'


        def home():
            if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
                ip_address = request.environ['REMOTE_ADDR']
            else:
                ip_address = request.environ['HTTP_X_FORWARDED_FOR'] 
            countr = get_country(ip_address)
            if countr == 'nope':
                return ''

            elif diccy[countr] in d['Country/Region'].unique():
                return [diccy[countr]]
            else:
                return ''
        return home()
        
    else:
        return cache
    
@app.callback(Output('country1', 'value'),[Input('tabs', 'value')],[State('dropdown-cache', 'data')])
def synchronize_dropdowns(_, cache):
    if type(cache) != type(list()):
        return ''
    else:
        return cache

@app.callback(Output('country2', 'value'),[Input('tabs', 'value')],[State('dropdown-cache', 'data')])
def synchronize_dropdowns(_, cache):
    if type(cache) != type(list()):
        return ''
    else:
        return cache

    
######### dropdown 2 #########
@app.callback(Output('dropdown1-cache', 'data'),[Input('state', 'value'),Input('state1', 'value'),Input('state2', 'value')],[State('tabs', 'value')])
def store_dropdown_cache(tab_0_drodown_sel, tab_1_drodown_sel, tab_2_drodown_sel, tab):
    if tab == 'tab-0':
        return tab_0_drodown_sel
    elif tab == 'tab-1':
        return tab_1_drodown_sel
    elif tab == 'tab-2':
        return tab_2_drodown_sel

@app.callback(Output('state', 'value'),[Input('tabs', 'value')],[State('dropdown1-cache', 'data')])
def synchronize_dropdowns(_, cache):
    if type(cache) != type(list()):
        return ''
    else:
        return cache
    
@app.callback(Output('state1', 'value'),[Input('tabs', 'value')],[State('dropdown1-cache', 'data')])
def synchronize_dropdowns(_, cache):
    if type(cache) != type(list()):
        return ''
    else:
        return cache

@app.callback(Output('state2', 'value'),[Input('tabs', 'value')],[State('dropdown1-cache', 'data')])
def synchronize_dropdowns(_, cache):
    if type(cache) != type(list()):
        return ''
    else:
        return cache
    
    
######### dropdown 3 #########
@app.callback(Output('dropdown2-cache', 'data'),[Input('conf', 'value'),Input('conf1', 'value'),Input('conf2', 'value')],[State('tabs', 'value')])
def store_dropdown_cache(tab_0_drodown_sel,tab_1_drodown_sel, tab_2_drodown_sel, tab):
    if tab == 'tab-0':
        return tab_0_drodown_sel
    elif tab == 'tab-1':
        return tab_1_drodown_sel
    elif tab == 'tab-2':
        return tab_2_drodown_sel

@app.callback(Output('conf', 'value'),[Input('tabs', 'value')],[State('dropdown2-cache', 'data')])
def synchronize_dropdowns(_, cache):
    if type(cache) != type(list()):
        return ''
    else:
        return cache 
    
@app.callback(Output('conf1', 'value'),[Input('tabs', 'value')],[State('dropdown2-cache', 'data')])
def synchronize_dropdowns(_, cache):
    if type(cache) != type(list()):
        return ''
    else:
        return cache

@app.callback(Output('conf2', 'value'),[Input('tabs', 'value')],[State('dropdown2-cache', 'data')])
def synchronize_dropdowns(_, cache):
    if type(cache) != type(list()):
        return ''
    else:
        return cache

    

@app.callback([Output("url1", "href"),Output("url2", "href"),Output("url3", "href")],
             [Input(component_id='country', component_property='value'),Input(component_id='state', component_property='value'),Input('map1', 'clickData'),
             Input(component_id='country1', component_property='value'),Input(component_id='state1', component_property='value'),
             Input(component_id='country2', component_property='value'),Input(component_id='state2', component_property='value')])
def update_url(select,select1,click,select2,select22,select3,select33):
    if click and click['points'][0]['marker.size'] != 1000000000000000:
        url = "https://news.google.com/news/search?q={}+when:3d".format('covid-19'+ ' ' +click['points'][0]['text'].split(':')[0])
    elif select1:
        url = "https://news.google.com/news/search?q={}+when:3d".format('covid-19'+ ' ' +select1[0])
    elif select:
        url = "https://news.google.com/news/search?q={}+when:3d".format('covid-19'+ ' ' +select[0])  
    elif select2:
        url = "https://news.google.com/news/search?q={}+when:3d".format('covid-19'+ ' ' +select2[0]) 
    elif select22:
        url = "https://news.google.com/news/search?q={}+when:3d".format('covid-19'+ ' ' +select22[0]) 
    elif select3:
        url = "https://news.google.com/news/search?q={}+when:3d".format('covid-19'+ ' ' +select3[0]) 
    elif select33:
        url = "https://news.google.com/news/search?q={}+when:3d".format('covid-19'+ ' ' +select33[0]) 
    else:
        url = "https://news.google.com/news/search?q={}+when:3d".format('covid-19')
          
    return url,url,url
    
    
######################################################
################### first page ###################### 
###################################################### 

########### KPI ###########
@app.callback(dash.dependencies.Output(component_id='kpi0',component_property='figure'),
    [dash.dependencies.Input(component_id='country', component_property='value'),
     dash.dependencies.Input(component_id='state', component_property='value'),
     dash.dependencies.Input(component_id='conf', component_property='value'),
     dash.dependencies.Input('map1', 'clickData')])

def update_kpi(select, select1, select2, click):
    df = d[['Country/Region','Province/State','conf',d.columns[-2],d.columns[-1]]]
    if select:
        df = df.loc[np.in1d(df['Country/Region'],select)]
    if select1:
        df = df.loc[np.in1d(df['Province/State'],select1)]
    if select2:
        df = df.loc[np.in1d(df['conf'],select2)]
    
    if click and click['points'][0]['marker.size'] != 1000000000000000:
        if ' - ' in click['points'][0]['text']:
            df = df.loc[df['Province/State'] == click['points'][0]['text'].split(' - ')[0]]
        else:
            df = df.loc[df['Province/State'] == '{} '.format(click['points'][0]['text'].split(':')[0])]
    

    if click and click['points'][0]['marker.size'] <  1000000000000000:
        return {'data': [go.Indicator(mode = "number",value=1,number = {'suffix':". {}".format(df['Province/State'].unique()[0])},title = {"text": '{}'.format(df.columns[-1][:10])})],
                'layout': go.Layout(margin={'l': 65, 'b': 0, 't': 30, 'r': 65},font=dict(color='black'),paper_bgcolor='#f2f5f7')}
    elif len(select) == 1:
        return {'data': [go.Indicator(mode = "number", value = df[(df[df.columns[-1]] > 0)]['Country/Region'].nunique(),title = {"text": '{}'.format(df.columns[-1][:10])}, number = {'suffix': " Country"},)],
                'layout': go.Layout(margin={'l': 65, 'b': 0, 't': 30, 'r': 65},font=dict(color='black'),paper_bgcolor='#f2f5f7')}
    else:
        return {'data': [go.Indicator(mode = "number", value = df[(df[df.columns[-1]] > 0)]['Country/Region'].nunique(),title = {"text": '{}'.format(df.columns[-1][:10])}, number = {'suffix': " Countries"},)],
                'layout': go.Layout(margin={'l': 40, 'b': 0, 't': 30, 'r': 40},font=dict(color='black'),paper_bgcolor='#f2f5f7')}


########### KPI ###########
@app.callback(dash.dependencies.Output(component_id='kpi1',component_property='figure'),
    [dash.dependencies.Input(component_id='country', component_property='value'),
     dash.dependencies.Input(component_id='state', component_property='value'),
     dash.dependencies.Input('map1', 'clickData')])

def update_kpi(select, select1, click):
    df = conf[['Country/Region','Province/State',conf.columns[-2],conf.columns[-1]]]
    if select:
        df = df.loc[np.in1d(df['Country/Region'],select)]
    if select1:
        df = df.loc[np.in1d(df['Province/State'],select1)]
    
    if click and click['points'][0]['marker.size'] != 1000000000000000:
        if ' - ' in click['points'][0]['text']:
            df = df.loc[df['Province/State'] == click['points'][0]['text'].split(' - ')[0]]
        else:
            df = df.loc[df['Province/State'] == '{} '.format(click['points'][0]['text'].split(':')[0])]
    
    
    return {'data': [go.Indicator(mode = "number+delta", number = {"valueformat": "09,"},value = df[df.columns[-1]].sum(),
                                  delta = {"reference": df[df.columns[-2]].sum(), "valueformat": ",:.0f",'increasing': {'color': "orange"}},title = {"text": 'Confirmed:'})],
             'layout': go.Layout(margin={'l': 50, 'b': 0, 't': 30, 'r': 50},font=dict(color='orange'),paper_bgcolor='#f2f5f7')}

########### KPI ###########
@app.callback(dash.dependencies.Output(component_id='kpi2',component_property='figure'),
    [dash.dependencies.Input(component_id='country', component_property='value'),
     dash.dependencies.Input(component_id='state', component_property='value'),
     dash.dependencies.Input('map1', 'clickData')])

def update_kpi(select, select1, click):
    df = recov[['Country/Region','Province/State',recov.columns[-2],recov.columns[-1]]]
    if select:
        df = df.loc[np.in1d(df['Country/Region'],select)]
    if select1:
        df = df.loc[np.in1d(df['Province/State'],select1)]
    
    if click and click['points'][0]['marker.size'] != 1000000000000000:
        if ' - ' in click['points'][0]['text']:
            df = df.loc[df['Province/State'] == click['points'][0]['text'].split(' - ')[0]]
        else:
            df = df.loc[df['Province/State'] == '{} '.format(click['points'][0]['text'].split(':')[0])]
    
    
    return {'data': [go.Indicator(mode = "number+delta", number = {"valueformat": "09,"},value = df[df.columns[-1]].sum(),
                                  delta = {"reference": df[df.columns[-2]].sum(), "valueformat": ",:.0f",'increasing': {'color': "green"}},title = {"text": 'Recovered:'})],
             'layout': go.Layout(margin={'l': 50, 'b': 0, 't': 30, 'r': 50}, font=dict(color='green'),paper_bgcolor='#f2f5f7')}

########### KPI ###########
@app.callback(dash.dependencies.Output(component_id='kpi3',component_property='figure'),
    [dash.dependencies.Input(component_id='country', component_property='value'),
     dash.dependencies.Input(component_id='state', component_property='value'),
     dash.dependencies.Input('map1', 'clickData')])

def update_kpi(select, select1, click):
    df = death[['Country/Region','Province/State',death.columns[-2],death.columns[-1]]]
    if select:
        df = df.loc[np.in1d(df['Country/Region'],select)]
    if select1:
        df = df.loc[np.in1d(df['Province/State'],select1)]
    
    ##### from mapbox hover #####        
    if click and click['points'][0]['marker.size'] != 1000000000000000:
        if ' - ' in click['points'][0]['text']:
            df = df.loc[df['Province/State'] == click['points'][0]['text'].split(' - ')[0]]
        else:
            df = df.loc[df['Province/State'] == '{} '.format(click['points'][0]['text'].split(':')[0])]
    #############################
    
    return {'data': [go.Indicator(mode = "number+delta", number = {"valueformat": "09,"},value = df[df.columns[-1]].sum(),
                                  delta = {"reference": df[df.columns[-2]].sum(), "valueformat": ",:.0f",'increasing': {'color': "red"}},title = {"text": 'Deaths:'})],
             'layout': go.Layout(margin={'l': 50, 'b': 0, 't': 30, 'r': 50},font=dict(color='red'),paper_bgcolor='#f2f5f7')}

    
########### map ###########
@app.callback(
    dash.dependencies.Output(component_id='map1',component_property='figure'),
    [dash.dependencies.Input(component_id='country', component_property='value'),
     dash.dependencies.Input(component_id='state', component_property='value'),
     dash.dependencies.Input(component_id='conf', component_property='value')])

def update_graph0(select, select1, select2):
    df = d[['Country/Region','Province/State','conf','Long','Lat',d.columns[-1]]]
    if select:
        df = df.loc[np.in1d(df['Country/Region'],select)]
    if select1:
        df = df.loc[np.in1d(df['Province/State'],select1)]
    if select2 and len(select2) == 1:
        df = df.loc[np.in1d(df['conf'],select2)]
    

    if len(select2) >= 2 or not select2:
        df = df.loc[np.in1d(df['conf'],'Confirmed')]
        namy = 'Confirmed'
    
    if select2:
        if select2 == ['Deaths']:
            colory = 'red'
            namy = 'Deaths'
        elif select2 == ['Confirmed']:
            colory = 'orange'
            namy = 'Confirmed'
        elif select2 == ['Recovered']:
            colory = 'green'
            namy = 'Recovered'
        else:
            colory = 'orange'
            namy = 'Confirmed'
    else:
        colory = 'orange'
        namy = 'Confirmed'

    if (not select and not select1):
        lon_range = df.loc[df['Country/Region'] == 'Algeria']['Long'].mean()
        lat_range = df.loc[df['Country/Region'] == 'Algeria']['Lat'].mean()
        zoom=1
    elif select == ['France'] and not select1:
        lon_range = df.loc[(df['Country/Region'] == 'France') & (df['Province/State'] == 'France ')]['Long'].mean()
        lat_range = df.loc[(df['Country/Region'] == 'France') & (df['Province/State'] == 'France ')]['Lat'].mean()
        zoom=1.8
    elif select == ['United Kingdom'] and not select1:
        lon_range = df.loc[(df['Country/Region'] == 'United Kingdom') & (df['Province/State'] == 'United Kingdom ')]['Long'].mean()
        lat_range = df.loc[(df['Country/Region'] == 'United Kingdom') & (df['Province/State'] == 'United Kingdom ')]['Lat'].mean()
        zoom=1.8
    else:
        lon_range = df['Long'].mean()
        lat_range = df['Lat'].mean()
        zoom=1.8
    
    df = df[df[df.columns[-1]] > 0]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scattermapbox(lat=df['Lat'],lon=df['Long'],mode='markers',text = ['{} - {}: {:,.0f}'.format(x,y,z) if x != '{} '.format(y) else '{}: {:,.0f}'.format(y,z) for x,y,z in zip(df['Province/State'],df['Country/Region'],df[df.columns[-1]])],
                                   hovertemplate ='%{text}',name=namy,marker=go.scattermapbox.Marker(size = [x for x in np.log(df[df.columns[-1]])**2/2],color=colory,opacity=0.4)))
    
    fig.add_trace(go.Scattermapbox(lon = [lon_range],lat = [lat_range],hoverinfo='none',marker=go.scattermapbox.Marker(size = [1000000000000000],opacity=0.0)))

    
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor='rgba(0,0,0,0)',
                      hoverlabel= {'bgcolor': 'rgba(255,255,255,0.2)','bordercolor': 'rgba(0,0,0,0)','font': {'color': 'black'}},
                      margin={'l': 0, 'b': 0, 't': 10, 'r': 0},autosize=True,showlegend = False,hovermode='closest',
                      mapbox=go.layout.Mapbox(style="carto-positron",center=go.layout.mapbox.Center(lat=lat_range,lon=lon_range),zoom=zoom))
    
    return fig    
    


@app.callback(Output(component_id='graph1',component_property='figure'),
              [dash.dependencies.Input(component_id='country', component_property='value'),
               dash.dependencies.Input(component_id='state', component_property='value'),
               dash.dependencies.Input(component_id='conf', component_property='value'),
               dash.dependencies.Input('map1', 'clickData')])

def clean_data(select, select1, select2, click):
    df = d
    if select:
        df = df.loc[np.in1d(df['Country/Region'],select)]
    if select1:
        df = df.loc[np.in1d(df['Province/State'],select1)]
    
    ##### from mapbox hover #####
    if click and click['points'][0]['marker.size'] != 1000000000000000:
        if ' - ' in click['points'][0]['text']:
            df = df[df['Province/State'] == click['points'][0]['text'].split(' - ')[0]]
        else:
            df = df[df['Province/State'] == '{} '.format(click['points'][0]['text'].split(':')[0])]
    #############################
    
    
    df1x = df.loc[np.in1d(df['conf'],'Confirmed')].iloc[:,5:].sum().T
    df1x = pd.DataFrame(index=df1x.index, data=df1x.values, columns=["data"])
    df1x["delta_data"] = df1x["data"] - df1x["data"].shift(1)
    df1x['incr'] = np.round((df1x["data"]/ df1x["data"].shift(1)-1)*100,1)
    
    df2x = df.loc[np.in1d(df['conf'],'Recovered')].iloc[:,5:].sum().T
    df2x = pd.DataFrame(index=df2x.index, data=df2x.values, columns=["data"])
    df2x["delta_data"] = df2x["data"] - df2x["data"].shift(1)
    df2x['incr'] = np.round((df2x["data"]/ df2x["data"].shift(1)-1)*100,1)
    
    df3x = df.loc[np.in1d(df['conf'],'Deaths')].iloc[:,5:].sum().T
    df3x = pd.DataFrame(index=df3x.index, data=df3x.values, columns=["data"])
    df3x["delta_data"] = df3x["data"] - df3x["data"].shift(1)
    df3x['incr'] = np.round((df3x["data"]/ df3x["data"].shift(1)-1)*100,1)
    
    fig = go.Figure()
    
    if 'Confirmed' in select2 or not select2:
        fig.add_trace(go.Scatter(x=df1x.index, y=df1x['data'],text=['new cases: {:,}, incr: {}%'.format(y,z) for y,z in zip(df1x["delta_data"],df1x['incr'])],
                                 mode='lines+markers', marker=dict(size=5),line=dict(color='orange',shape='spline', smoothing=1.3),name='Confirmed',fill='tozeroy',opacity=0.3))
        fig.update_layout(annotations=[dict(showarrow=False,x=df1x.index[7],y=max(df1x['data'])*0.60,
                                           text="Avg <b>{:,}</b> confirmed cases per day<br>for the <b>past 7 days</b>".format(np.round(np.mean(df1x["delta_data"][-7:]),1)),xanchor="left",xshift=10,opacity=0.9),
                                      dict(showarrow=False,x=df1x.index[7],y=max(df1x['data'])*0.30,
                                           text="Avg <b>{:,}</b> confirmed cases per day<br>for the <b>past 14 days</b>".format(np.round(np.mean(df1x["delta_data"][-14:]),1)),xanchor="left",xshift=10,opacity=0.9)])

    if 'Recovered' in select2 or not select2:
        fig.add_trace(go.Scatter(x=df2x.index, y=df2x['data'],text=['new cases: {:,}, incr: {}%'.format(y,z) for y,z in zip(df2x["delta_data"],df2x['incr'])],
                                 mode='lines+markers', marker=dict(size=5),line=dict(color='green',shape='spline', smoothing=1.3),name='Recovered',fill='tozeroy',opacity=0.3))
 
    if 'Deaths' in select2 or not select2:
        fig.add_trace(go.Scatter(x=df3x.index, y=df3x['data'],text=['new cases: {:,}, incr: {}%'.format(y,z) for y,z in zip(df3x["delta_data"],df3x['incr'])],
                                 mode='lines+markers', marker=dict(size=5),line=dict(color='red',shape='spline', smoothing=1.3),name='Deaths',fill='tozeroy',opacity=0.3))
    
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor='#f2f5f7',margin={'l': 7, 'b': 15, 't': 40, 'r': 7},title='Cumulative cases over time:',
                      autosize=True,showlegend = True,hovermode='x',legend_orientation="h",legend=dict(x=0, y=1.08),#y=1.1
                      xaxis=dict(showspikes=True,showgrid=False),yaxis=dict(title='Nbr of cumulative cases',showspikes=True,showgrid=False))
    
    return fig


@app.callback(Output(component_id='graph11',component_property='figure'),
              [dash.dependencies.Input(component_id='country', component_property='value'),
               dash.dependencies.Input(component_id='state', component_property='value'),
               dash.dependencies.Input(component_id='conf', component_property='value'),
               dash.dependencies.Input('map1', 'clickData')])

def clean_data(select, select1, select2, click):
    df = d[['Country/Region','Province/State','conf',d.columns[-1]]]
    if select:
        df = df.loc[np.in1d(df['Country/Region'],select)]
    if select1:
        df = df.loc[np.in1d(df['Province/State'],select1)]
    if select2:
        df = df.loc[np.in1d(df['conf'],select2)]
    
    if not select2:
        df = df.loc[np.in1d(df['conf'],'Confirmed')]
    
    orang = [[0, 'rgb(254,230,206)'],[0.05, 'rgb(253,208,162)'],[0.15, 'rgb(253,174,107)'],[0.5,'rgb(253,141,60)'],[1, 'orange']] #1, 'rgb(255,245,235)'
    
    if select2:
        if select2 == ['Deaths']:
            colory = 'Reds'
            namy = 'deaths'
            nam = 'Deaths'
        elif select2 == ['Confirmed']:
            colory = orang #'YlOrRd'
            namy = 'confirmed'
            nam = 'Confirmed'
        elif select2 == ['Recovered']:
            colory = 'Greens'
            namy = 'recovered'
            nam = 'Recovered'
        else:
            colory = orang
            namy = 'confirmed'
            nam = 'Confirmed'
    else:
        colory = orang
        namy = 'confirmed'
        nam = 'Confirmed'
    
    ##### from mapbox hover #####
    if click and click['points'][0]['marker.size'] != 1000000000000000:
        if ' - ' in click['points'][0]['text']:
            df = df.loc[df['Province/State'] == click['points'][0]['text'].split(' - ')[0]]
        else:
            df = df.loc[df['Province/State'] == '{} '.format(click['points'][0]['text'].split(':')[0])]
    #############################
    
    if not select and not select1 and (not click or click['points'][0]['marker.size'] == 1000000000000000):
        df2 = df.groupby(['Country/Region']).agg({df.columns[-1]:np.sum}).reset_index().rename(columns={'Country/Region':'id',df.columns[-1]:'value'})
        df2['parent'] = ['total' for x in df2['id']]
        df3 = df2 #pd.concat((df1,df2), ignore_index = True)
        total = pd.Series(dict(id='total', parent='',value=d[d['conf'] == nam][d.columns[-1]].sum()))
        df3 = df3.append(total, ignore_index=True,sort=False)
        df3['value'] = df3['value'].astype(int)
        
    elif click and click['points'][0]['marker.size'] != 1000000000000000:
        df1 = df.groupby(['Province/State','Country/Region']).agg({df.columns[-1]:np.sum}).reset_index().rename(columns={'Province/State':'id','Country/Region':'parent',df.columns[-1]:'value'})
        df2 = df.groupby(['Country/Region']).agg({df.columns[-1]:np.sum}).reset_index().rename(columns={'Country/Region':'id',df.columns[-1]:'value'})
        df2['parent'] = ['total' for x in df2['id']]
        df3 = pd.concat((df1,df2), ignore_index = True, sort=False)
        total = pd.Series(dict(id='total', parent='',value=d[d['conf'] == nam][d.columns[-1]].sum()))
        df3 = df3.append(total, ignore_index=True,sort=False)
        df3['value'] = df3['value'].astype(int)
       
    else:   
        df1 = df.groupby(['Province/State','Country/Region']).agg({df.columns[-1]:np.sum}).reset_index().rename(columns={'Province/State':'id','Country/Region':'parent',df.columns[-1]:'value'})
        df2 = df.groupby(['Country/Region']).agg({df.columns[-1]:np.sum}).reset_index().rename(columns={'Country/Region':'id',df.columns[-1]:'value'})
        df2['parent'] = ['total' for x in df2['id']]
        df3 = pd.concat((df1,df2), ignore_index = True, sort=False)
        total = pd.Series(dict(id='total', parent='',value=d[d['conf'] == nam][d.columns[-1]].sum()))
        df3 = df3.append(total, ignore_index=True,sort=False)
        df3['value'] = df3['value'].astype(int)
    
    tot = df3.loc[np.in1d(df3['id'],'total')]['value'].sum()
    
    if len(select) == 1:
        starting = select[0]     
    else:
        starting = select
    
    return {'data': [gogo.Treemap(labels = df3['id'],parents = df3['parent'],values = df3['value'],branchvalues='total',level=starting,marker_colorscale = colory,
                                  opacity=0.5,textinfo = "label+value+percent parent",hovertemplate=['{}: {:,}, {:.1%} of total'.format(y, x,x/z) for x,y,z in zip(df3['value'],df3['id'],[tot for t in df3['value']])],name='')],
                    'layout': gogo.Layout(plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor='#f2f5f7',
                            margin={'l': 1, 'b': 1, 't': 1, 'r': 1},autosize=True,showlegend = False,yaxis=dict(type='log'),hovermode='x')}

@app.callback(Output(component_id='graph41',component_property='figure'),
              [dash.dependencies.Input(component_id='country', component_property='value'),
               dash.dependencies.Input(component_id='state', component_property='value'),
               dash.dependencies.Input(component_id='conf', component_property='value'),
               dash.dependencies.Input('map1', 'clickData')])

def clean_data(select, select1, select2, click):
    df = d
    if select:
        df = df.loc[np.in1d(df['Country/Region'],select)]
    if select1:
        df = df.loc[np.in1d(df['Province/State'],select1)]
    if select2:
        df = df.loc[np.in1d(df['conf'],select2)]

    if not select2:
        df = df.loc[np.in1d(df['conf'],'Confirmed')]
        cas = 'con'
    
    ##### from mapbox hover #####
    if click and click['points'][0]['marker.size'] != 1000000000000000:
        if ' - ' in click['points'][0]['text']:
            df = df.loc[df['Province/State'] == click['points'][0]['text'].split(' - ')[0]]
        else:
            df = df.loc[df['Province/State'] == '{} '.format(click['points'][0]['text'].split(':')[0])]
    #############################
    
    all_dates_proj = df['Province/State'].unique()
    
    if select2:
        if select2 == ['Deaths']:
            colory = 'red'
            namy = 'Deaths'
            cas = 'dea'
        elif select2 == ['Confirmed']:
            colory = 'darkorange'
            namy = 'Confirmed'
            cas = 'con'
        elif select2 == ['Recovered']:
            colory = 'green'
            namy = 'Recovered'
            cas = 'reco'
        else:
            colory = 'darkorange'
            namy = 'Confirmed'
    else:
        colory = 'darkorange'
        namy = 'Confirmed'
        
    df = df.iloc[:,5:].sum().T
    df = pd.DataFrame(index=df.index, data=df.values, columns=["data"])
    df["delta_data"] = df["data"] - df["data"].shift(1)

    ### rolling average ###
    df["delta_data_roll"] = np.round(df["delta_data"].rolling(window=3, center=False).mean(), 2)  #window=7

    df['diff'] = df["delta_data_roll"] / df["delta_data_roll"].shift(1)
    df['new'] = df.index
    df['new'] = pd.to_datetime(df['new'], infer_datetime_format=True)
    
    #### add mid date:
    for i,j in zip(range(0,len(df['new'])),range(0,len(df['diff']))):
        if (df['diff'][j] > 1 and df['diff'][j-1] < 1) or (df['diff'][j] < 1 and df['diff'][j-1] > 1):
            data = pd.DataFrame({'new':df['new'][i-1] + (df['new'][i]-df['new'][i-1])/2,'diff':1},index=[0.5])
            df = df.append(data, ignore_index=True,sort=False)
               
    df = df.sort_values('new').reset_index(drop=True)
    df['diff'] = df['diff'].round(2)
    
    df['abo'] = [x if x >= 1  else None for x in df['diff']]
    df['low'] = [x if x <= 1 else None for x in df['diff']]
    ##################

    fig = go.Figure()
    
    if select or select1 or click:
        dictoo = {}
        for i in all_dates_proj:
            for key, value in dates_proj[cas][i].items():
                dictoo[key] = value
    
        k = Counter(dictoo) 
        high = k.most_common(1)
    
        shapes=[]
        for i in high:
            x = pd.to_datetime(i[0])
            idxs = pd.date_range(start=x+ pd.DateOffset(-5), end=x+timedelta(days=5), freq='D')

            shape = dict(type="circle",xref="x",yref="y",fillcolor="PaleTurquoise",opacity=0.2,x0=idxs[0],y0=1-0.25,x1=idxs[-1],y1=1+0.25,line_color="LightSeaGreen")
            shapes.append(shape)
        
            fig.add_trace(go.Scatter(x=[x+timedelta(days=5)],y=[1+0.55],text=["Peak of<br>the curve:<br>{}".format(i[0])],mode="text",name='',showlegend=False))

        fig.update_layout(shapes=shapes)
        
    idx = pd.date_range(start=df['new'].to_list()[-1], end=df['new'].to_list()[-1]+timedelta(days=42), freq='D')

    fig.add_trace(go.Scatter(x=df['new'], y=df['abo'],  name='above 1', mode='lines',line=dict(width=1.5, color='red',shape='spline', smoothing=1.3)))
        
    fig.add_trace(go.Scatter(x=df['new'], y=df['low'],  name='below 1', mode='lines',line=dict(width=1.5, color='green',shape='spline', smoothing=1.3)))

    fig.add_trace(go.Scatter(x=df['new'].to_list()+idx.to_list(), y=[1 for x in df['new'].to_list()+idx.to_list()],mode='lines',line = dict(width=1,color='black', dash='dash'),opacity=0.4,name='',hoverinfo='none'))
        
    fig.update_layout(title='Daily cases growth factor: (better if < 1 )',legend_orientation="h",legend=dict(x=0, y=1.08),
                  plot_bgcolor='rgba(0,0,0,0)',margin={'l': 7, 'b': 15, 't': 40, 'r': 7},
                  paper_bgcolor='#f2f5f7',xaxis=dict(showspikes=True,showgrid=False),yaxis=dict(showspikes=True,showgrid=False,range=[0,2]),)
        
    return fig


@app.callback(Output(component_id='graph111',component_property='figure'),
              [dash.dependencies.Input(component_id='country', component_property='value'),
               dash.dependencies.Input(component_id='state', component_property='value'),
               dash.dependencies.Input(component_id='conf', component_property='value'),
               dash.dependencies.Input('map1', 'clickData')])

def clean_data(select, select1, select2, click):
    df = d
    df_proj = proj
    if select:
        df = df.loc[np.in1d(df['Country/Region'],select)]
        df_proj = df_proj.loc[np.in1d(df_proj['Country/Region'],select)]
    if select1:
        df = df.loc[np.in1d(df['Province/State'],select1)]
        df_proj = df_proj.loc[np.in1d(df_proj['Province/State'],select1)]
    if select2:
        df = df.loc[np.in1d(df['conf'],select2)]
        df_proj = df_proj.loc[np.in1d(df_proj['conf'],select2)]
    
    if not select2:
        df = df.loc[np.in1d(df['conf'],'Confirmed')]
        df_proj = df_proj.loc[np.in1d(df_proj['conf'],'Confirmed')]
    
    ##### from mapbox hover #####
    if click and click['points'][0]['marker.size'] != 1000000000000000:
        if ' - ' in click['points'][0]['text']:
            df = df.loc[df['Province/State'] == click['points'][0]['text'].split(' - ')[0]]
            df_proj = df_proj.loc[df_proj['Province/State'] == click['points'][0]['text'].split(' - ')[0]]
        else:
            df = df.loc[df['Province/State'] == '{} '.format(click['points'][0]['text'].split(':')[0])]
            df_proj = df_proj.loc[df_proj['Province/State'] == '{} '.format(click['points'][0]['text'].split(':')[0])]
    #############################
    
    if select2:
        if select2 == ['Deaths']:
            colory = 'red'
            coloryy = redy
            namy = 'deaths'
        elif select2 == ['Confirmed']:
            colory = 'orange'
            coloryy = oray
            namy = 'confirmed'
        elif select2 == ['Recovered']:
            colory = 'green'
            coloryy = grey
            namy = 'recovered'
        else:
            colory = 'orange'
            coloryy = oray
            namy = 'confirmed'
    else:
        colory = 'orange'
        coloryy = oray
        namy = 'confirmed'
    
    df = df.iloc[:,5:].sum().T
    df = pd.DataFrame(index=df.index, data=df.values, columns=["data"])
    
    df_proj = df_proj.iloc[:,5:].sum().T
    df_proj = pd.DataFrame(index=df_proj.index, data=df_proj.values, columns=["forecast"])
    
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=df_proj.index, y=df_proj["forecast"],  name='projections',line=dict(width=0.1, color='rgba{}'.format(coloryy),shape='spline', smoothing=1.3),opacity=0.3, fill='tozeroy'))
        
    fig.add_trace(go.Scatter(x=df.index, y=df["data"], mode='lines+markers',marker=dict(size=5),name='actuals', line={"color":colory,'shape':'spline', 'smoothing':1.3}))
    
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)',title='Projections of {} cumulative cases:'.format(namy),
                      paper_bgcolor='#f2f5f7',margin={'l': 7, 'b': 15, 't': 40, 'r': 7},showlegend = True,hovermode='x',
                      legend_orientation="h",legend=dict(x=0, y=1.08),xaxis=dict(showspikes=True,showgrid=False),
                      yaxis=dict(showspikes=True,showgrid=False))
    
    return fig


@app.callback(Output(component_id='graph1111',component_property='figure'),
              [dash.dependencies.Input(component_id='country', component_property='value'),
               dash.dependencies.Input(component_id='state', component_property='value'),
               dash.dependencies.Input(component_id='conf', component_property='value'),
               dash.dependencies.Input('map1', 'clickData')])

def clean_data(select, select1, select2, click):
    df = d 
    df_proj = proj
    if select:
        df = df.loc[np.in1d(df['Country/Region'],select)]
        df_proj = df_proj.loc[np.in1d(df_proj['Country/Region'],select)]
    if select1:
        df = df.loc[np.in1d(df['Province/State'],select1)]
        df_proj = df_proj.loc[np.in1d(df_proj['Province/State'],select1)]
    if select2:
        df = df.loc[np.in1d(df['conf'],select2)]
        df_proj = df_proj.loc[np.in1d(df_proj['conf'],select2)]

    if not select2:
        df = df.loc[np.in1d(df['conf'],'Confirmed')]
        df_proj = df_proj.loc[np.in1d(df_proj['conf'],'Confirmed')]
    
    ##### from mapbox hover #####
    if click and click['points'][0]['marker.size'] != 1000000000000000:
        if ' - ' in click['points'][0]['text']:
            df = df.loc[df['Province/State'] == click['points'][0]['text'].split(' - ')[0]]
            df_proj = df_proj.loc[df_proj['Province/State'] == click['points'][0]['text'].split(' - ')[0]]
        else:
            df = df.loc[df['Province/State'] == '{} '.format(click['points'][0]['text'].split(':')[0])]
            df_proj = df_proj.loc[df_proj['Province/State'] == '{} '.format(click['points'][0]['text'].split(':')[0])]
    #############################
    
    
    if select2:
        if select2 == ['Deaths']:
            colory = 'red'
            coloryy = redy
            namy = 'deaths'
        elif select2 == ['Confirmed']:
            colory = 'orange'
            coloryy = oray
            namy = 'confirmed'
        elif select2 == ['Recovered']:
            colory = 'green'
            coloryy = grey
            namy = 'recovered'
        else:
            colory = 'orange'
            coloryy = oray
            namy = 'confirmed'
    else:
        colory = 'orange'
        coloryy = oray
        namy = 'confirmed'
        
    
    df = df.iloc[:,5:].sum().T
    df = pd.DataFrame(index=df.index, data=df.values, columns=["data"])
    df["delta_data"] = df["data"] - df["data"].shift(1)
    
    df_proj = df_proj.iloc[:,5:].sum().T
    df_proj = pd.DataFrame(index=df_proj.index, data=df_proj.values, columns=["forecast"])
    df_proj["delta_forecast"] = df_proj["forecast"] - df_proj["forecast"].shift(1)
#     df_proj["delta_forecast"] = df_proj["delta_forecast"].round(2)
    
    ### outliers
    df_proj.loc[df_proj.index == str(pd.to_datetime(df.index[-1])+timedelta(days=1)),"delta_forecast"] = (df_proj[df_proj.index == str(df.index[-1])]["delta_forecast"][0]+df_proj[df_proj.index == str(pd.to_datetime(df.index[-1])+timedelta(days=2))]["delta_forecast"][0])/2 
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=df_proj.index, y=df_proj["delta_forecast"], name='projections', line=dict(width=0.1, color='rgba{}'.format(coloryy),shape='spline', smoothing=1.3),opacity=0.3, fill='tozeroy'))

    fig.add_trace(go.Bar(x=df.index, y=df["delta_data"], name='actuals', marker_color=colory))
        
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)',title='Projections of {} daily cases:'.format(namy),
                      paper_bgcolor='#f2f5f7',margin={'l': 7, 'b': 15, 't': 40, 'r': 7},
                      showlegend = True,hovermode='x',legend_orientation="h",legend=dict(x=0, y=1.08),
                      xaxis=dict(showspikes=True,showgrid=False),yaxis=dict(showspikes=True,showgrid=False))
    return fig


@app.callback(Output(component_id='graph12',component_property='figure'),
              [dash.dependencies.Input(component_id='country', component_property='value'),
               dash.dependencies.Input(component_id='state', component_property='value'),
               dash.dependencies.Input(component_id='conf', component_property='value'),
               dash.dependencies.Input('map1', 'clickData')])

def clean_data(select, select1, select2, click):
    df = d  
    if not select and not select1 and select2:
        df = df.loc[np.in1d(df['conf'],select2)]
    
    if not select2:
        df = df.loc[np.in1d(df['conf'],'Confirmed')]
    
    if select2:
        if select2 == ['Deaths']:
            namy = 'deaths'
        elif select2 == ['Confirmed']:
            namy = 'confirmed'
        elif select2 == ['Recovered']:
            namy = 'recovered'
        else:
            namy = 'confirmed'
    else:
        namy = 'confirmed'
    
    list_countries = list(set(['China','Italy'] + list(select)))    
    
    dt = df.loc[np.in1d(df['Country/Region'],list_countries)]

    dicto = {}
    for i in dt['Country/Region'].unique():
        if i == 'China' and dt['conf'].unique() == ['Confirmed']:
            g = dt.loc[dt['Country/Region'] == i]
            dicto[i] = [45,62,121,198,291,440] + [g[x].sum() for x in g.iloc[:,5:].columns if g[x].sum() > 50]
        else:
            g = dt.loc[dt['Country/Region'] == i]
            dicto[i] = [g[x].sum() for x in g.iloc[:,5:].columns if g[x].sum() > 50]

    if select1:
        for i in list(select1):
            g = dt.loc[dt['Province/State'] == i]
            dicto[i] = [g[x].sum() for x in g.iloc[:,5:].columns if g[x].sum() > 50]
            
    
    ##### from mapbox hover #####
    if click and click['points'][0]['marker.size'] != 1000000000000000:
        if ' - ' in click['points'][0]['text']:
            g = df.loc[df['Province/State'] == click['points'][0]['text'].split(' - ')[0]]
            dicto[click['points'][0]['text'].split(' - ')[0]] = [g[x].sum() for x in g.iloc[:,5:].columns if g[x].sum() > 50]
        else:
            g = df.loc[df['Province/State'] == '{} '.format(click['points'][0]['text'].split(':')[0])]
            dicto['{} '.format(click['points'][0]['text'].split(':')[0])] = [g[x].sum() for x in g.iloc[:,5:].columns if g[x].sum() > 50]
    #############################
            
 
    dictos = {}
    for i in dicto.keys():
        if len(dicto[i]) >= 1:
            dictos[i] = [(dicto[i][x]/dicto[i][x-1])*100-100 for x in range(0,len(dicto[i][1:])+1)]
    
    fig = go.Figure()
    
    for i in dicto.keys():
        if len(dicto[i]) >= 1:
            fig.add_trace(go.Scatter(x=list(range(1,len(dicto['China'])+1)), y=dicto[i],mode='lines+markers',name=i, marker=dict(size=5),
                                     text=['{:,} cases, {:.02f}% increase'.format(x,dictos[i][y]) if y > 0 else '{:,} cases'.format(x)  for x,y in zip(dicto[i],range(0,len(dictos[i])))],
                                     line=dict(shape='spline', smoothing=1.3),hovertemplate ='%{text}',))

    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor='#f2f5f7',
                      margin={'l': 7, 'b': 20, 't': 80, 'r': 7},title='{} cases - Tracking the evolution of countries once they hit 50 {} cases:'.format(dt['conf'].unique()[0],namy),
                      showlegend = True,hovermode='x',legend_orientation="h",legend=dict(x=0, y=1.08),
                      xaxis1=dict(showticklabels=True,showgrid=False,title='days'),yaxis1=dict(type='log',showgrid=False,title='log'))

    listu = [50,287678]
    fig.add_trace(go.Scatter(x=[1,34], y=listu,text="30% daily increase",hovertemplate="30% daily increase",mode='lines',line = dict(color='black', width=2, dash='dash'),opacity=0.4,name=''))

    listuu = [50,1873]
    fig.add_trace(go.Scatter(x=[1,39], y=listuu,text="10% daily increase",hovertemplate="10% daily increase",mode='lines',line = dict(color='black', width=2, dash='dash'),opacity=0.4,name=''))
        
    return fig


@app.callback(Output(component_id='graph14',component_property='figure'),
              [Input(component_id='country', component_property='value'),Input('slid1', 'value')])

def clean_data(select, val1):
    if not select:
        df = world
    elif select:
        df = world.loc[np.in1d(world['Country/Region'],select)]
    
    # Total population, N.
    N = df['population'].sum()
    # Initial number of infected, recovered individuals and dead, I0 and R0.
    I0, R0, D0 = 1, 0, 0
    # S0: susceptible to infection initially.
    S0 = N - I0 - R0 - D0
    # Contact rate; beta, and mean recovery rate; gamma, (in 1/days).
    beta, gamma = 0.5, 1./15 
    # number of days
    t = list(range(1,300))
    
    val2 = 150
    
    listy = [[S0,I0,R0]]
    for ts in t:
        S, I, R = listy[-1][0],listy[-1][1],listy[-1][2]
        if len(listy) > val1 and len(listy) <= val1+15:  #val1
            beta=(val1/val2+0.5)/2.5 #val1 instead of 20
            dSdt = listy[-1][0] + -beta * S * I / N
            dIdt = listy[-1][1] + beta * S * I / N - gamma * I
            dRdt = listy[-1][2] + gamma * dIdt#I
            listy.append([dSdt,dIdt,dRdt])
        elif len(listy) > val1+15: #val1
            beta=val1/val2  #val1
            dSdt = listy[-1][0] + -beta * S * I / N
            dIdt = listy[-1][1] + beta * S * I / N - gamma * I
            dRdt = listy[-1][2] + gamma * dIdt#I
            listy.append([dSdt,dIdt,dRdt])
        else:
            beta=0.5
            dSdt = listy[-1][0] + -beta * S * I / N
            dIdt = listy[-1][1] + beta * S * I / N - gamma * I
            dRdt = listy[-1][2] + gamma * dIdt#I
            listy.append([dSdt,dIdt,dRdt])

    S, I, R = np.array(listy).T
    R = R*0.93
    D = R*0.07
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=S,mode='lines',name='Susceptible',line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=t, y=I,mode='lines',name='Infected',line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=t, y=R,mode='lines',name='Recovered with potential immunity',line=dict(color='green')))
    fig.add_trace(go.Scatter(x=t, y=D,mode='lines',name='Dead',line=dict(color='red')))

    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor='#f2f5f7',
                      margin={'l': 7, 'b': 20, 't': 80, 'r': 7},title='Modelling',showlegend = True,hovermode='x',
                      legend_orientation="h",legend=dict(x=0, y=1.08),
                      xaxis=dict(title='Days',showgrid=False),
                      yaxis=dict(title='Number cases',showgrid=False))
    return fig

################################################
############### second page ####################
################################################

########### KPI ###########
@app.callback(dash.dependencies.Output(component_id='kpi00',component_property='figure'),
    [dash.dependencies.Input(component_id='country1', component_property='value'),
     dash.dependencies.Input(component_id='state1', component_property='value'),
     dash.dependencies.Input('RangeSlider', 'value')])

def update_kpi(select, select1, value):
    da = list_date[value]
    df1 = conf[['Country/Region','Province/State',da]]
    if select:
        df1 = df1.loc[np.in1d(df1['Country/Region'],select)]
    if select1:
        df1 = df1.loc[np.in1d(df1['Province/State'],select1)]
    
    if df1[df1[da] > 0]['Country/Region'].nunique() == 1:
        return {'data': [go.Indicator(mode = "number", value = df1[df1[da] > 0]['Country/Region'].nunique(),
                                  title = {"text": '{}'.format(da[:10])},number = {'suffix': " Country"},)],
             'layout': go.Layout(margin={'l': 60, 'b': 0, 't': 30, 'r': 60},font=dict(color='black'),paper_bgcolor='#f2f5f7',hovermode='x')}
    else:
        return {'data': [go.Indicator(mode = "number", value = df1[df1[da] > 0]['Country/Region'].nunique(),
                                  title = {"text": '{}'.format(da[:10])},number = {'suffix': " Countries"},)],
             'layout': go.Layout(margin={'l': 40, 'b': 0, 't': 30, 'r': 40},font=dict(color='black'),paper_bgcolor='#f2f5f7',hovermode='x')}


########### KPI ###########
@app.callback(dash.dependencies.Output(component_id='kpi4',component_property='figure'),
    [dash.dependencies.Input(component_id='country1', component_property='value'),
     dash.dependencies.Input(component_id='state1', component_property='value'),
     dash.dependencies.Input('RangeSlider', 'value')])

def update_kpi(select, select1, value):
    da = list_date[value]
    df1 = conf[['Country/Region','Province/State',da]]
    df2 = recov[['Country/Region','Province/State',da]]
    if select:
        df1 = df1.loc[np.in1d(df1['Country/Region'],select)]
        df2 = df2.loc[np.in1d(df2['Country/Region'],select)]
    if select1:
        df1 = df1.loc[np.in1d(df1['Province/State'],select1)]
        df2 = df2.loc[np.in1d(df2['Province/State'],select1)]
    
    return {'data': [go.Indicator(mode = "number",value = np.round((df2[da].sum()/df1[da].sum())*100,2),
                                  title = {"text": 'Recovery:'},number = {'suffix': "%","valueformat": "05,.02f"})],
             'layout': go.Layout(margin={'l': 60, 'b': 0, 't': 30, 'r': 60},font=dict(color='green'),paper_bgcolor='#f2f5f7',hovermode='x')}


########### KPI ###########
@app.callback(dash.dependencies.Output(component_id='kpi5',component_property='figure'),
    [dash.dependencies.Input(component_id='country1', component_property='value'),
     dash.dependencies.Input(component_id='state1', component_property='value'),
     dash.dependencies.Input('RangeSlider', 'value')])

def update_kpi(select, select1, value):
    da = list_date[value]
    df1 = conf[['Country/Region','Province/State',da]]
    df3 = death[['Country/Region','Province/State',da]]
     
    if select:
        df1 = df1.loc[np.in1d(df1['Country/Region'],select)]
        df3 = df3.loc[np.in1d(df3['Country/Region'],select)]
    if select1:
        df1 = df1.loc[np.in1d(df1['Province/State'],select1)]
        df3 = df3.loc[np.in1d(df3['Province/State'],select1)]
    
    return {'data': [go.Indicator(mode = "number", value = np.round((df3[da].sum()/df1[da].sum())*100,2),
                                  title = {"text": 'Mortality:'},number = {'suffix': "%","valueformat": "05,.02f"})],
             'layout': go.Layout(margin={'l': 60, 'b': 0, 't': 30, 'r': 60},font=dict(color='red'),paper_bgcolor='#f2f5f7',hovermode='x')}


########### KPI ###########
@app.callback(dash.dependencies.Output(component_id='kpi6',component_property='figure'),
    [dash.dependencies.Input(component_id='country1', component_property='value'),
     dash.dependencies.Input(component_id='state1', component_property='value'),
     dash.dependencies.Input('RangeSlider', 'value')])

def update_kpi(select, select1, value):
    da = list_date[value]
    df2 = recov[['Country/Region','Province/State',da]]
    df3 = death[['Country/Region','Province/State',da]]
    
    if select:
        df2 = df2.loc[np.in1d(df2['Country/Region'],select)]
        df3 = df3.loc[np.in1d(df3['Country/Region'],select)]
    if select1:
        df2 = df2.loc[np.in1d(df2['Province/State'],select1)]
        df3 = df3.loc[np.in1d(df3['Province/State'],select1)]
    
    return {'data': [go.Indicator(mode = "number", value = np.round(df2[da].sum()/df3[da].sum(),1),
                                  title = {"text": 'Recov to Deaths:'},number = {'suffix': ":1"})],
             'layout': go.Layout(margin={'l': 65, 'b': 0, 't': 30, 'r': 65},font=dict(color='orange'),paper_bgcolor='#f2f5f7',hovermode='x')}



@app.callback(Output(component_id='graph2',component_property='figure'),
              [dash.dependencies.Input(component_id='country1', component_property='value'),
               dash.dependencies.Input(component_id='state1', component_property='value'),
               dash.dependencies.Input('RangeSlider', 'value'),Input('radioX', 'value'),Input('radioX3', 'value')])

def clean_data(select, select1, value,radio,radioX3):
    da = list_date[value]
    
    df1 = d.groupby(['Country/Region','conf']).agg({da:np.sum}).reset_index()
    df1 = df1.merge(world, how='left',left_on='Country/Region',right_on='Country/Region')
    df1['per_mil'] = df1[da] / df1['population'] * 1000000
    df1['per_mil'] = df1['per_mil'].fillna(0).astype(int)
    
    if radioX3 == 1:
        sorting = da
    else:
        sorting = 'per_mil'
    
    if radio <= 50:
        df11 = df1.loc[np.in1d(df1['conf'],'Confirmed')].sort_values(sorting,ascending=False).head(radio)
        df22 = df1.loc[np.in1d(df1['conf'],'Recovered')].sort_values(sorting,ascending=False).head(radio)
        df33 = df1.loc[np.in1d(df1['conf'],'Deaths')].sort_values(sorting,ascending=False).head(radio)
    else:
        df11 = df1.loc[np.in1d(df1['conf'],'Confirmed')].sort_values(sorting,ascending=False)
        df22 = df1.loc[np.in1d(df1['conf'],'Recovered')].sort_values(sorting,ascending=False)
        df33 = df1.loc[np.in1d(df1['conf'],'Deaths')].sort_values(sorting,ascending=False)
        
    
    if not select:
        opa1 = 0.4
        opa2 = 0.4
        opa3 = 0.4
    elif select:
        opa1 = [0.4 if x not in select else 1 for x in df11['Country/Region']]
        opa2 = [0.4 if x not in select else 1 for x in df22['Country/Region']]
        opa3 = [0.4 if x not in select else 1 for x in df33['Country/Region']]
    
    fig = make_subplots(rows=3, cols=1)

    fig.add_trace(go.Bar(x=df11['Country/Region'], y=df11[da],name='Confirmed',texttemplate=df11['Country/Region'], textposition='auto',marker=dict(color='orange',opacity=opa1),yaxis='y1'),1, 1)
    
    fig.add_trace(go.Scatter(x=df11['Country/Region'],y=df11['per_mil'],opacity=0.8,mode='lines+markers',marker=dict(size=5),
                    line=dict(color='darkorange',width=1.5,shape='spline', smoothing=1.3),name='per million',yaxis='y4'),1, 1)

    fig.add_trace(go.Bar(x=df22['Country/Region'], y=df22[da],name='Recovered',texttemplate=df22['Country/Region'], textposition='auto',marker=dict(color='green',opacity=opa2),yaxis='y2'),2, 1)
    
    fig.add_trace(go.Scatter(x=df22['Country/Region'],y=df22['per_mil'],opacity=0.8,mode='lines+markers',marker=dict(size=5),
                    line=dict(color='green',width=1.5,shape='spline', smoothing=1.3),name='per million',yaxis='y5'),2, 1)
    
    fig.add_trace(go.Bar(x=df33['Country/Region'], y=df33[da],name='Deaths',texttemplate=df33['Country/Region'], textposition='auto',marker=dict(color='red',opacity=opa3),yaxis='y3'),3, 1)
    
    fig.add_trace(go.Scatter(x=df33['Country/Region'],y=df33['per_mil'],opacity=0.8,mode='lines+markers',marker=dict(size=5),
                    line=dict(color='red',width=1.5,shape='spline', smoothing=1.3),name='per million',yaxis='y6'),3, 1)

    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor='#f2f5f7',uniformtext_mode='show',
                      margin={'l': 7, 'b': 20, 't': 80, 'r': 7},title='Cumulative cases by country:',
                      showlegend = True,hovermode='x',legend_orientation="h",legend=dict(x=0, y=1.08),
                      xaxis1=dict(showticklabels=False,showgrid=False,),yaxis1=dict(type='log',showgrid=False,),
                      xaxis2=dict(showticklabels=False,showgrid=False,),yaxis2=dict(type='log',showgrid=False,title='Nbr of cumulative cases, Log'),
                      xaxis3=dict(showticklabels=False,showgrid=False,title='Countries'),yaxis3=dict(showgrid=False,type='log'))
    
    fig['data'][1].update(yaxis='y4')
    fig['data'][3].update(yaxis='y5')
    fig['data'][5].update(yaxis='y6')
    
    fig['layout']['yaxis4'] = dict(anchor='x1',type='log',autorange= True, rangemode='tozero',side='right',overlaying='y1',showgrid=False,zeroline=False)
    fig['layout']['yaxis5'] = dict(anchor='x2',type='log',title='Cases per million people',autorange= True, rangemode='tozero',side='right',overlaying='y2',showgrid=False,zeroline=False)
    fig['layout']['yaxis6'] = dict(anchor='x3',type='log',autorange= True, rangemode='tozero',side='right',overlaying='y3',showgrid=False,zeroline=False)        
    
    return fig


@app.callback(Output(component_id='graph21',component_property='figure'),
              [dash.dependencies.Input(component_id='country1', component_property='value'),
               dash.dependencies.Input(component_id='state1', component_property='value'),
               dash.dependencies.Input('RangeSlider', 'value'),Input('radio', 'value'),Input('radioX', 'value')])

def clean_data(select, select1, value,radio,radioX):
    da = list_date[value]
    
    df1 = pd.DataFrame(d.pivot_table(index='Country/Region',columns='conf',values=da,aggfunc=np.sum).to_records())
    
    df1['Recovery Rate'] = df1['Recovered'] / df1['Confirmed'] *100
    df1['Mortality Rate'] = df1['Deaths'] / df1['Confirmed'] *100
    df1['Ratio Recovery to death'] = [x/y if y > 0 else 0 for x,y in zip(df1['Recovered'],df1['Deaths'])]
    
    if radio == 1:
        df222 = df1.sort_values('Recovery Rate',ascending=False)
        df333 = df1.sort_values('Mortality Rate',ascending=False)
        df444 = df1.sort_values('Ratio Recovery to death',ascending=False)
    elif radio == 2:
        df222 = df1.sort_values('Confirmed',ascending=False)
        df333 = df1.sort_values('Confirmed',ascending=False)
        df444 = df1.sort_values('Recovered',ascending=False)   
        
        
    if radioX <= 50:
        df222 = df222.head(radioX)
        df333 = df333.head(radioX)
        df444 = df444.head(radioX)
    else:
        df222 = df222
        df333 = df333
        df444 = df444 
         
        
    if not select:
        opa1 = 0.4
        opa2 = 0.4
        opa3 = 0.4
    elif select:
        opa1 = [0.4 if x not in select else 1 for x in df222['Country/Region']]
        opa2 = [0.4 if x not in select else 1 for x in df333['Country/Region']]
        opa3 = [0.4 if x not in select else 1 for x in df444['Country/Region']]
    
    fig = make_subplots(rows=3, cols=1) #, shared_yaxes=True)

    fig.add_trace(go.Bar(x=df222['Country/Region'], y=df222['Recovery Rate'],name='Recovery Rate',
                         text=['{0:.1f}%'.format(x) for x in df222['Recovery Rate']],hovertemplate='%{text}',
                         texttemplate=df222['Country/Region'], textposition='auto',marker=dict(color='green',opacity=opa1),yaxis='y1'),1, 1)
    
    fig.add_trace(go.Scatter(x=df222['Country/Region'],y=df222['Confirmed'],opacity=0.8,mode='lines+markers',marker=dict(size=5),
                             line=dict(color='darkorange',width=1.5,shape='spline', smoothing=1.3),name='Confirmed',yaxis='y4'),1, 1)
    
    fig.add_trace(go.Bar(x=df333['Country/Region'], y=df333['Mortality Rate'],name='Mortality Rate',
                         text=['{0:.1f}%'.format(x) for x in df333['Mortality Rate']],hovertemplate='%{text}',
                         texttemplate=df333['Country/Region'], textposition='auto',marker=dict(color='red',opacity=opa2),yaxis='y2'),2, 1)
    
    fig.add_trace(go.Scatter(x=df333['Country/Region'],y=df333['Confirmed'],opacity=0.8,mode='lines+markers',marker=dict(size=5),
                             line=dict(color='darkorange',width=1.5,shape='spline', smoothing=1.3),name='Confirmed',yaxis='y5'),2, 1)
    
    fig.add_trace(go.Bar(x=df444['Country/Region'], y=df444['Ratio Recovery to death'],name='Ratio Recovery to death',
                         text=['{0:.1f}:{1}'.format(x,1) if x > 0 else '{0:.1f}:{1}'.format(y,0) for x,y in zip(df444['Ratio Recovery to death'],df444['Recovered'])],hovertemplate='%{text}',
                         texttemplate=df444['Country/Region'], textposition='auto',marker=dict(color='orange',opacity=opa3),yaxis='y3'),3, 1)
    
    fig.add_trace(go.Scatter(x=df444['Country/Region'],y=df444['Recovered'],opacity=0.8,mode='lines+markers',marker=dict(size=5),
                             line=dict(color='green',width=1.5,shape='spline', smoothing=1.3),name='Recovered',yaxis='y6'),3, 1)

    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor='#f2f5f7',uniformtext_mode='show',
                      margin={'l': 7, 'b': 20, 't': 80, 'r': 7},title='Ratios by country:',showlegend = True,hovermode='x',legend_orientation="h",legend=dict(x=0, y=1.08),
                      xaxis1=dict(showticklabels=False,showgrid=False,),yaxis1=dict(anchor='x1',type='log',showgrid=False),
                      xaxis2=dict(showticklabels=False,showgrid=False,),yaxis2=dict(anchor='x2',type='log',showgrid=False,title='Ratios, Log'),
                      xaxis3=dict(showticklabels=False,showgrid=False,title='Countries'),yaxis3=dict(showgrid=False,type='log'))
    
    fig['data'][1].update(yaxis='y4')
    fig['data'][3].update(yaxis='y5')
    fig['data'][5].update(yaxis='y6')
    
    fig['layout']['yaxis4'] = dict(anchor='x1',type='log',title='Confirmed cases',autorange= True, rangemode='tozero',side='right',overlaying='y1',showgrid=False,zeroline=False)
    fig['layout']['yaxis5'] = dict(anchor='x2',type='log',title='Confirmed cases',autorange= True, rangemode='tozero',side='right',overlaying='y2',showgrid=False,zeroline=False)
    fig['layout']['yaxis6'] = dict(anchor='x3',type='log',title='Recovered cases',autorange= True, rangemode='tozero',side='right',overlaying='y3',showgrid=False,zeroline=False)        
    
    return fig


################################################
############### third page ####################
################################################

########### KPI ###########
@app.callback(dash.dependencies.Output(component_id='kpi000',component_property='figure'),
    [dash.dependencies.Input(component_id='country2', component_property='value'),
     dash.dependencies.Input(component_id='state2', component_property='value'),
     dash.dependencies.Input('RangeSlider1', 'value')])

def update_kpi(select, select1, value):
    da = list_date[value]
    df1 = conf[['Country/Region','Province/State',da]]
    
    if select:
        df1 = df1.loc[np.in1d(df1['Country/Region'],select)]
    if select1:
        df1 = df1.loc[np.in1d(df1['Province/State'],select1)]
    
    if df1[df1[da] > 0]['Country/Region'].nunique() == 1:
        return {'data': [go.Indicator(mode = "number", value = df1[df1[da] > 0]['Country/Region'].nunique(),title = {"text": '{}'.format(da[:10])},number = {'suffix': " Country"},)],
             'layout': go.Layout(margin={'l': 60, 'b': 0, 't': 30, 'r': 60},font=dict(color='black'),paper_bgcolor='#f2f5f7',hovermode='x')}
    else:
        return {'data': [go.Indicator(mode = "number", value = df1[df1[da] > 0]['Country/Region'].nunique(),title = {"text": '{}'.format(da[:10])},number = {'suffix': " Countries"},)],
             'layout': go.Layout(margin={'l': 40, 'b': 0, 't': 30, 'r': 40},font=dict(color='black'),paper_bgcolor='#f2f5f7',hovermode='x')}


########### KPI ###########
@app.callback(dash.dependencies.Output(component_id='kpi7',component_property='figure'),
    [dash.dependencies.Input(component_id='country2', component_property='value'),
     dash.dependencies.Input(component_id='state2', component_property='value'),
     dash.dependencies.Input('RangeSlider1', 'value')])

def update_kpi(select, select1, value):
    da = list_date[value]
    da2 = list_date[value-1]
    df1 = conf[['Country/Region','Province/State',da2,da]]
    if select:
        df1 = df1.loc[np.in1d(df1['Country/Region'],select)]
    if select1:
        df1 = df1.loc[np.in1d(df1['Province/State'],select1)]
    
    return {'data': [go.Indicator(mode = "number+delta", number = {"valueformat": "09,"},value = df1[da].sum(),
                                  delta = {"reference": df1[da2].sum(),"valueformat": ",:.0f",'increasing': {'color': "orange"}},
                                  title = {"text": 'Confirmed:'})],
             'layout': go.Layout(margin={'l': 50, 'b': 0, 't': 30, 'r': 50},font=dict(color='orange'),paper_bgcolor='#f2f5f7',hovermode='x')}

########### KPI ###########
@app.callback(dash.dependencies.Output(component_id='kpi8',component_property='figure'),
    [dash.dependencies.Input(component_id='country2', component_property='value'),
     dash.dependencies.Input(component_id='state2', component_property='value'),
     dash.dependencies.Input('RangeSlider1', 'value')])

def update_kpi(select, select1, value): 
    da = list_date[value]
    da2 = list_date[value-1]
    df2 = recov[['Country/Region','Province/State',da2,da]]

    if select:
        df2 = df2.loc[np.in1d(df2['Country/Region'],select)]
    if select1:
        df2 = df2.loc[np.in1d(df2['Province/State'],select1)]
    
    return {'data': [go.Indicator(mode = "number+delta", number = {"valueformat": "09,"},value = df2[da].sum(),
                                  delta = {"reference": df2[da2].sum(),"valueformat": ",:.0f",'increasing': {'color': "green"}},
                                  title = {"text": 'Recovered:'})],
             'layout': go.Layout(margin={'l': 50, 'b': 0, 't': 30, 'r': 50},font=dict(color='green'),paper_bgcolor='#f2f5f7',hovermode='x')}


########### KPI ###########
@app.callback(dash.dependencies.Output(component_id='kpi9',component_property='figure'),
    [dash.dependencies.Input(component_id='country2', component_property='value'),
     dash.dependencies.Input(component_id='state2', component_property='value'),
     dash.dependencies.Input('RangeSlider1', 'value')])

def update_kpi(select, select1, value):
    da = list_date[value]
    da2 = list_date[value-1]
    df3 = death[['Country/Region','Province/State',da2,da]]
     
    if select:
        df3 = df3.loc[np.in1d(df3['Country/Region'],select)]
    if select1:
        df3 = df3.loc[np.in1d(df3['Province/State'],select1)]
    
    return {'data': [go.Indicator(mode = "number+delta", number = {"valueformat": "09,"},value = df3[da].sum(),
                                  delta = {"reference": df3[da2].sum(),"valueformat": ",:.0f",'increasing': {'color': "red"}},
                                  title = {"text": 'Deaths:'})],
             'layout': go.Layout(margin={'l': 50, 'b': 0, 't': 30, 'r': 50},font=dict(color='red'),paper_bgcolor='#f2f5f7',hovermode='x')}


@app.callback(Output(component_id='graph3',component_property='figure'),
              [dash.dependencies.Input(component_id='country2', component_property='value'),
               dash.dependencies.Input(component_id='state2', component_property='value'),
               dash.dependencies.Input('RangeSlider1', 'value')])

def clean_data(select, select1, value): 
    df = d
    if select:
        df = df.loc[np.in1d(df['Country/Region'],select)]
    if select1:
        df = df.loc[np.in1d(df['Province/State'],select1)]
            
    da = list_date[value]
    
    df1x = df.loc[np.in1d(df['conf'],'Confirmed')].iloc[:,5:].sum().T
    df1x = pd.DataFrame(index=df1x.index, data=df1x.values, columns=["data"])
    df1x["delta_data"] = df1x["data"] - df1x["data"].shift(1)
    df1x['incr'] = (df1x["data"]/ df1x["data"].shift(1)-1)
    
    opa1 = [0.4 if x != da else 1 for x in df1x.index]
    
    df2x = df.loc[np.in1d(df['conf'],'Recovered')].iloc[:,5:].sum().T
    df2x = pd.DataFrame(index=df2x.index, data=df2x.values, columns=["data"])
    df2x["delta_data"] = df2x["data"] - df2x["data"].shift(1)
    df2x['incr'] = (df2x["data"]/ df2x["data"].shift(1)-1)
    
    opa2 = [0.4 if x != da else 1 for x in df2x.index]
    
    df3x = df.loc[np.in1d(df['conf'],'Deaths')].iloc[:,5:].sum().T
    df3x = pd.DataFrame(index=df3x.index, data=df3x.values, columns=["data"])
    df3x["delta_data"] = df3x["data"] - df3x["data"].shift(1)
    df3x['incr'] = (df3x["data"]/ df3x["data"].shift(1)-1)
    
    opa3 = [0.4 if x != da else 1 for x in df3x.index]
    
    fig = make_subplots(rows=3, cols=1)

    fig.add_trace(go.Bar(x=df1x.index, y=df1x["delta_data"],name='Confirmed',marker=dict(color='orange',opacity=opa1),yaxis='y1'),1, 1)
    fig.add_trace(go.Scatter(x=df1x.index, y=df1x['incr'],line=dict(color='orange',width=1,shape='spline', smoothing=1.3),name='Conf. Growth Factor',yaxis='y4'),1, 1)
    
    fig.add_trace(go.Bar(x=df2x.index, y=df2x["delta_data"],name='Recovered',marker=dict(color='green',opacity=opa2),yaxis='y2'),2, 1)
    fig.add_trace(go.Scatter(x=df2x.index, y=df2x['incr'],line=dict(color='green',width=1,shape='spline', smoothing=1.3),name='Recov. Growth Factor',yaxis='y5'),2, 1)
    
    fig.add_trace(go.Bar(x=df3x.index, y=df3x["delta_data"],name='Deaths',marker=dict(color='red',opacity=opa3),yaxis='y3'),3, 1)
    fig.add_trace(go.Scatter(x=df3x.index, y=df3x['incr'],line=dict(color='red',width=1,shape='spline', smoothing=1.3),name='Deaths Growth Factor',yaxis='y6'),3, 1)

    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)',title='New cases by day:',paper_bgcolor='#f2f5f7',
                      margin={'l': 7, 'b': 15, 't': 80, 'r': 7},showlegend = True,hovermode='x',
                      legend_orientation="h",legend=dict(x=0, y=1.08),
                      xaxis1=dict(showspikes=True,showgrid=False,showticklabels=False),yaxis1=dict(showgrid=False,type='log',),
                      xaxis2=dict(showspikes=True,showgrid=False,showticklabels=False),yaxis2=dict(showgrid=False,type='log',title='Nbr of new cases, log'),
                      yaxis3=dict(showgrid=False,type='log'),xaxis3=dict(showspikes=True,showgrid=False))
    
    fig['data'][1].update(yaxis='y4')
    fig['data'][3].update(yaxis='y5')
    fig['data'][5].update(yaxis='y6')
    
    fig['layout']['yaxis4'] = dict(anchor='x1',type='log',tickformat=',.0%',autorange= True, rangemode='tozero',side='right',overlaying='y1',showgrid=False,zeroline=False)
    fig['layout']['yaxis5'] = dict(anchor='x2',type='log',tickformat=',.0%',title='Growth Factor, log',autorange= True, rangemode='tozero',side='right',overlaying='y2',showgrid=False,zeroline=False)
    fig['layout']['yaxis6'] = dict(anchor='x3',type='log',tickformat=',.0%',autorange= True, rangemode='tozero',side='right',overlaying='y3',showgrid=False,zeroline=False)        
    
    return fig

@app.callback(Output(component_id='graph4',component_property='figure'),
              [dash.dependencies.Input(component_id='country2', component_property='value'),
               dash.dependencies.Input(component_id='state2', component_property='value'),
               dash.dependencies.Input('RangeSlider1', 'value'),Input('radioX2', 'value')])

def clean_data(select, select1, value,radioX2):    
    das = list_date[value]
    das1 = list_date[value-1]
    
    df1 = d.groupby(['Country/Region','conf']).agg({das1:np.sum,das:np.sum}).reset_index()
    df1['new'] = df1[das] - df1[das1]
    df1 = df1.sort_values('new',ascending=False)
    
    if radioX2 <= 50:
        df11 = df1.loc[np.in1d(df1['conf'],'Confirmed')].head(radioX2)
        df22 = df1.loc[np.in1d(df1['conf'],'Recovered')].head(radioX2)
        df33 = df1.loc[np.in1d(df1['conf'],'Deaths')].head(radioX2)
    else:
        df11 = df1.loc[np.in1d(df1['conf'],'Confirmed')]
        df22 = df1.loc[np.in1d(df1['conf'],'Recovered')]
        df33 = df1.loc[np.in1d(df1['conf'],'Deaths')]
    
    if select:
        opa1 = [0.4 if x not in select else 1 for x in df11['Country/Region']]
        opa2 = [0.4 if x not in select else 1 for x in df22['Country/Region']]
        opa3 = [0.4 if x not in select else 1 for x in df33['Country/Region']]
    else:
        opa1 = 0.4
        opa2 = 0.4
        opa3 = 0.4
    
    fig = make_subplots(rows=3, cols=1)
    
    fig.add_trace(go.Bar(x=df11['Country/Region'], y=df11['new'],name='Confirmed',texttemplate=df11['Country/Region'], textposition='auto',marker=dict(color='orange',opacity=opa1)), 1, 1)
    fig.add_trace(go.Bar(x=df22['Country/Region'], y=df22['new'],name='Recovered',texttemplate=df22['Country/Region'], textposition='auto',marker=dict(color='green',opacity=opa2)),2, 1)
    fig.add_trace(go.Bar(x=df33['Country/Region'], y=df33['new'],name='Deaths',texttemplate=df33['Country/Region'], textposition='auto',marker=dict(color='red',opacity=opa3)),3, 1)

    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)',title='New cases by country on the {}:'.format(das[:10]),
                      paper_bgcolor='#f2f5f7',uniformtext_mode='show',margin={'l': 7, 'b': 20, 't': 80, 'r': 7},
                      showlegend = True,hovermode='x',legend_orientation="h",legend=dict(x=0, y=1.08),
                      xaxis1=dict(showspikes=True,showgrid=False,showticklabels=False),yaxis1=dict(type='log',showgrid=False,),
                      xaxis2=dict(showspikes=True,showgrid=False,showticklabels=False),yaxis2=dict(showgrid=False,title='New cases on the {}, log'.format(das[:10]),type='log'),
                      xaxis3=dict(showspikes=True,showgrid=False,showticklabels=False,title='Countries'),yaxis3=dict(showgrid=False,type='log'))
    return fig
    

if __name__ == '__main__':
    app.run_server()