# Imports from 3rd party libraries
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd

# Imports from this application
from app import app
# from functions import build_plotly_graph
# from functions import build_prev_flow_dataframe
# from functions import river_dict
from functions import *

weather_forecast_df = get_weather_forecast(river_dict['Owyhee at Rome'][1])
prev_flow_df = build_prev_flow_dataframe(river_dict['Owyhee at Rome'][0])

forecast_data = {
    'Forecast': [100, 110, 120, 110, 110, 120, 130, 90, 95,100],
    'date': ['2020-09-16','2020-09-17','2020-09-18','2020-09-19','2020-09-20','2020-09-21','2020-09-22','2020-09-23','2020-09-24','2020-09-25'],
     }
df = pd.DataFrame(data=forecast_data)

df['date'] = pd.to_datetime(df['date'])

prev_flow_df = prev_flow_df.append(df, ignore_index=True)

fig = build_plotly_graph(prev_flow_df, title='Owyhee at Rome', x='date', y=['Observation','Forecast'])

# 2 column layout. 1st column width = 4/12
# https://dash-bootstrap-components.opensource.faculty.ai/l/components/layout
column1 = dbc.Col(
    [   
        dcc.Graph(figure=fig, style={"border":"1px black solid", 'padding': 0}),

        
    ],
    md=8,
)

column2 = dbc.Col(
    [



        dcc.Markdown(
            f"""
            Near Owyhee, NV
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
    
            The Owyhee has a USGS gauge, but no prediction from the Northwest River Forecast Center.

            Predictions are made up, for now.

            """
        ),
    ]
)

layout = dbc.Row([column1, column2])