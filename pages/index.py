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
from datetime import datetime  
from datetime import timedelta

# Imports from this application
from app import app
from functions import *




weather_forecast_df = get_weather_forecast(river_dict['South Fork Payette at Lowman'][1])
prev_flow_df = build_prev_flow_dataframe(river_dict['South Fork Payette at Lowman'][0])

current_flow = prev_flow_df['Observation'].iloc[-1]

model_inputs = build_1_day_model_inputs(weather_forecast_df, current_flow, days_ahead=1)

one_day_forecast = generate_1_day_prediction(model_inputs)

## Create forecast dataframe
forecast_data = {
    'Forecast': [current_flow, one_day_forecast],
    'date': [datetime.now(), datetime.now() + timedelta(days=1)]
     }
df = pd.DataFrame(data=forecast_data)

two_seven_day_forecast = generate_2_7_day_prediction(df, weather_forecast_df)


prev_flow_df = prev_flow_df.append(two_seven_day_forecast, ignore_index=True)

fig = build_plotly_graph(
                        prev_flow_df,
                        title='South Fork Payette at Lowman',
                        x='date',
                        y=['Observation','Forecast']
                        )


# 2 column layout. 1st column width = 4/12
# https://dash-bootstrap-components.opensource.faculty.ai/l/components/layout
column1 = dbc.Col(
    [

        
        dcc.Graph(figure=fig, style={"border":"1px black solid", 'padding': 0}),

        dcc.Markdown(
            f"""
            Forecast created {str(datetime.now())[:16]} MST
            ### Will's model ☝️
            
            """
        ),

        dcc.Markdown(
            """
            ----
            """
        ),

        # html.Div(children=[dcc.Graph(figure=fig)], style={"border":"2px black solid"})


        ## This is the live link
        html.Img(src='https://www.nwrfc.noaa.gov/station/flowplot/hydroPlot.php?id=PRLI1&pe=HG&v=1599087455/hydroPlot.png', className='img-fluid'),
    
        dcc.Markdown(
            """
        
            ### Northwest River Forecast Center model ☝️
            """
        ),   
    
    ]
)


column2 = dbc.Col(
    [



        dcc.Markdown(
            f"""
            Banner Summit, ID
            ### Today's weather: {weather_forecast_df['shortForecast'][0]}

            High: {weather_forecast_df['max_temp'][0].round(0)}ºF

            """
        ),


        html.Img(src=weather_forecast_df['icon_url'][0], className='img-fluid'),
        
                dcc.Markdown(
            """
            ----
            """
        ),

        

        # dcc.Markdown(
        #     """
        #     ----
        #     """
        # ),


        


        dcc.Markdown(
            """
        
            ## **River Prediction**

            This website uses machine learning to predict a river's flow. 
            Read more about how the model was created [here.](https://towardsdatascience.com/predicting-the-flow-of-the-south-fork-payette-river-using-an-lstm-neural-network-65292eadf6a6)


            """
        ),

        # dcc.Markdown(
        #     """
        #     ----
        #     """
        # ),

        dcc.Markdown(
            """
            ### Coming soon:

            - Owyhee River at Rome, OR forecast (not currently served by NWRFC)

            - Integrations with precipitation data

            - Neural network model
            

            ### Coming later:

            - Incorporating Google Earth Engine data into model

            - South Fork Salmon at Krassel, ID (not currently served by NWRFC)

            - Wind River at Stabler, WA (not currently served by NWRFC)

            - Little White Salmon at Willard, WA (currently ungauged)


            """
        ),

        # html.Img(src='/assets/rockwater.jpg', className='img-fluid'),
        # dcc.Link(dbc.Button('Predict', color='primary'), href='/predictions')
    ],
    md=4,
)


layout = dbc.Row([column1, column2])