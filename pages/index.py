# Imports from 3rd party libraries
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
# import plotly.express as px
# import plotly.graph_objects as go
import pandas as pd
import numpy as np
# import requests
# from datetime import datetime  
# from datetime import timedelta

# Imports from this application
from app import app
from functions import build_plotly_graph
from functions import build_prev_flow_dataframe
from functions import river_dict
from functions import get_weather_forecast

weather_forecast_df = get_weather_forecast()

prev_flow_df = build_prev_flow_dataframe(river_dict['South Fork Payette at Lowman'])

forecast_data = {
    'Forecast': [355, 350, 350, 350, 390, 350, 350, 350, 350,350],
    'date': ['2020-09-16','2020-09-17','2020-09-18','2020-09-19','2020-09-20','2020-09-21','2020-09-22','2020-09-23','2020-09-24','2020-09-25'],
     }
df = pd.DataFrame(data=forecast_data)

df['date'] = pd.to_datetime(df['date'])

prev_flow_df = prev_flow_df.append(df, ignore_index=True)

fig = build_plotly_graph(prev_flow_df, title='South Fork Payette at Lowman', x='date', y=['Observation','Forecast'])


# 2 column layout. 1st column width = 4/12
# https://dash-bootstrap-components.opensource.faculty.ai/l/components/layout
column1 = dbc.Col(
    [
        dcc.Markdown(
            """
        
            ## Will's model: live prediction
            """
        ),
        
        dcc.Graph(figure=fig, style={"border":"1px black solid", 'padding': 0}),

        dcc.Markdown(
            """
            ----
            """
        ),

        # html.Div(children=[dcc.Graph(figure=fig)], style={"border":"2px black solid"})
        dcc.Markdown(
            """
        
            ## The NWRFC model: live prediction
            """
        ),

        ## This is the live link
        html.Img(src='https://www.nwrfc.noaa.gov/station/flowplot/hydroPlot.php?id=PRLI1&pe=HG&v=1599087455/hydroPlot.png', className='img-fluid'),
    ]
)


column2 = dbc.Col(
    [



        dcc.Markdown(
            f"""
        
            ## Today's weather: {weather_forecast_df['shortForecast'][0]}

            High: {weather_forecast_df['max_temp'][0].round(0)}ºF

            """
        ),


        html.Img(src=weather_forecast_df['icon_url'][0], className='img-fluid'),
        
                dcc.Markdown(
            """
            ----
            """
        ),
        
        dcc.Markdown(
            """
        
            ## What's the future flow of the river?

            This website uses machine learning to predict a river's flow.

            Predictions are made up, for now.

            Read more about how the model was created here:

            https://towardsdatascience.com/predicting-the-flow-of-the-south-fork-payette-river-using-an-lstm-neural-network-65292eadf6a6


            """
        ),

        dcc.Markdown(
            """
            ----
            """
        ),


        html.Img(src='/assets/rockwater.jpg', className='img-fluid'),

        dcc.Markdown(
            """
            ----
            """
        ),

        dcc.Markdown(
            """
            ## Coming soon:

            - Live model

            - Integrations with weather forecasts

            - Incorporating Google Earth Engine data

            ## Coming later:

            - Owyhee River at Rome, OR forecast (not currently served by NWRFC)

            - South Fork Salmon at Krassel, ID (not currently served by NWRFC)

            - Wind River at Stabler, WA (not currently served by NWRFC)

            - Little White Salmon at Willard, WA (currently ungauged)


            """
        ),
        # dcc.Link(dbc.Button('Predict', color='primary'), href='/predictions')
    ],
    md=4,
)


layout = dbc.Row([column1, column2])