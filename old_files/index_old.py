# Imports from 3rd party libraries
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
# import plotly.graph_objects as go
import pandas as pd
import numpy as np
import resource
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

LSTM_model_inputs = build_LSTM_1_day_model_inputs(weather_forecast_df, current_flow, days_ahead=1)

# example_values = [2900,90,60,153]

one_day_forecast = current_flow
# one_day_forecast = LSTM_prediction(LSTM_model_inputs)
print(f'NEURAL NETWORK PREDICTION: {one_day_forecast}')

## Random forest forecast
# one_day_forecast = generate_1_day_prediction(model_inputs)


## Create forecast dataframe
forecast_data = {
    'Forecast': [current_flow, one_day_forecast],
    'date': [datetime.now(), datetime.now() + timedelta(days=1)]
     }
forecast_df = pd.DataFrame(data=forecast_data)

# print(forecast_df)



## add another day of forecast on there
# forecast_df = generate_2_3_day_LSTM_prediction(forecast_df, weather_forecast_df)


# two_seven_day_forecast = generate_2_7_day_prediction(df, weather_forecast_df)

# two_seven_day_forecast = {
#     'Forecast': [345.95, 375.85, 368.8, 364.2],
#     'date': ['2020-09-19','2020-09-20','2020-09-21','2020-09-22'],
#      }
# two_seven_day_forecast = pd.DataFrame(data=two_seven_day_forecast)
# two_seven_day_forecast = two_seven_day_forecast.append(forecast_df, ignore_index=True)
# prev_flow_df = prev_flow_df.append(two_seven_day_forecast, ignore_index=True)

prev_flow_df = prev_flow_df.append(forecast_df, ignore_index=True)
# print(prev_flow_df)
# exit()

# forecast_list = prev_flow_df['date'].tail(7).tolist()
# print(forecast_list)




fig = build_plotly_graph(
                        prev_flow_df,
                        title='South Fork Payette at Lowman',
                        x='date',
                        y=['Observation','Forecast']
                        )






# import pandas as pd
# us_cities = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv")



## This should get wrapped in a function

### And I guess I need a global database to store all the current values of each river
## This map generation should reference that database
mapping_data = {
    'lat': [42.838680, 44.082420],
    'lon': [-117.629028,-115.613130],
    'station':['Owyhee at Rome','SF Payette at Lowman'],
    "today's flow":[-999,str(current_flow) + " CFS"],
    "tomorrow's flow":[-999,str(one_day_forecast)+"CFS"]
     }


mapping_df = pd.DataFrame(data=mapping_data)

# print(mapping_df)

# exit()

# import plotly.express as px

map_fig = px.scatter_mapbox(mapping_df, lat="lat", lon="lon", hover_name="station", 
                            hover_data={"lat":False, "lon":False,"today's flow":True,"tomorrow's flow":True},
                        color_continuous_scale=px.colors.sequential.Blues, zoom=5, height=400)
map_fig.update_layout(
    mapbox_style="white-bg",
    mapbox_layers=[
        {
            "below": 'traces',
            "sourcetype": "raster",
            "sourceattribution": "United States Geological Survey",
            "source": [
                "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
            ]
        }
      ])
map_fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
# map_fig.update_traces(hovertemplate=None)
# map_fig.update_layout(hovermode="y")
# fig.show()


# 2 column layout. 1st column width = 4/12
# https://dash-bootstrap-components.opensource.faculty.ai/l/components/layout
column1 = dbc.Col(
    [

        dcc.Graph(figure=map_fig, style={"border":"1px black solid", 'padding': 0}),
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

                    
 ### The Random Forest predicts that tomorrow's flow will be **{one_day_forecast}**.

        dcc.Markdown(
            f"""
           
            # The Neural Network predicts that tomorrow's flow will be **{one_day_forecast}**.
            ----
            """
        ),


        


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




## Resource usage
peak_memory_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
print(f'This app is using {(peak_memory_usage/1000000):.2f}MB max')

time_in_user_mode = resource.getrusage(resource.RUSAGE_SELF).ru_utime
print(f'This app takes {(time_in_user_mode):.2f} seconds to run')

shared_memory_size = resource.getrusage(resource.RUSAGE_SELF).ru_ixrss
print(f'This app is using {(peak_memory_usage/1000000):.2f}MB shared memory')

# #!/usr/bin/env python
# import psutil
# # gives a single float value
# print(f'single float value {psutil.cpu_percent()}')
# # gives an object with many fields
# print(f'object with many fields{psutil.virtual_memory()}')
# # you can convert that object to a dictionary 
# print(dict(psutil.virtual_memory()._asdict()))
# # you can have the percentage of used RAM
# print(psutil.virtual_memory().percent)

# # you can calculate percentage of available memory
# print(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total)
