import plotly.express as px
from datetime import datetime  
from datetime import timedelta
import requests
import pandas as pd
import joblib
from joblib import load
from sklearn.ensemble import RandomForestRegressor
from numpy import concatenate
import numpy as np
from tensorflow import keras


## Eventually, in order to make more graphs, I'll build out this structure


# Weather.gov API documentation
# https://www.weather.gov/documentation/services-web-api
river_dict = {

    'South Fork Payette at Lowman': ('https://waterservices.usgs.gov/nwis/iv/?format=json&sites=13235000&period=P10D&parameterCd=00060&siteStatus=all',
                                    "https://api.weather.gov/gridpoints/BOI/169,112/forecast"),
    'Owyhee at Rome':('https://waterservices.usgs.gov/nwis/iv/?format=json&sites=13181000&period=P10D&parameterCd=00060&siteStatus=all',
                    'https://api.weather.gov/gridpoints/LKN/117,175/forecast')  #Fawn Creek Snotel
}


def build_LSTM_1_day_model_inputs(future_weather_df, current_flow, days_ahead):

    '''
    These are the inputs needed to calculate the next days' flow forecast

    Returns array [['TMAX','TMIN','DAY_OF_YEAR','STREAMFLOW']]
    '''

    # random forest model inputs
    #['TMAX','TMIN','DAY_OF_YEAR','STREAMFLOW']


    tomorrows_forecast = future_weather_df[future_weather_df['date']==pd.to_datetime(str(datetime.now()+ timedelta(days=days_ahead))[:10])]

    day_of_year = datetime.now().timetuple().tm_yday

    # print(previous_flow_dataframe['cfs'][:-1])

    input_array = [
                    current_flow,
                    tomorrows_forecast['max_temp'],
                    tomorrows_forecast['min_temp'],
                    day_of_year+days_ahead,
                    ]
    
    return input_array



def LSTM_prediction(array_of_inputs):

    ## Import the saved model
    model = keras.models.load_model("data/LSTM_model.h5")
  
    ## notice the extra brackets as I make it an array
    array_of_inputs = np.array([array_of_inputs])
    # ensure all data is float
    array_of_inputs = array_of_inputs.astype('float32')

    scaler=load('data/std_scaler.bin')
    # normalize features
    # scaler = MinMaxScaler(feature_range=(0, 1))
    scaled = scaler.transform(array_of_inputs)

    test_X = scaled.reshape((scaled.shape[0], 1, scaled.shape[1]))

    # print(test_X)

    yhat = model.predict(test_X)

    test_X = test_X.reshape((test_X.shape[0], test_X.shape[2]))
    # invert scaling for forecast
    inv_yhat = concatenate((yhat, test_X[:, 1:]), axis=1)
    inv_yhat = scaler.inverse_transform(inv_yhat)
    # print(inv_yhat)
    inv_yhat = inv_yhat[:,0]

    #### MY FINAL PREDICTION!!!!!!
    return inv_yhat[0]




def generate_2_7_day_prediction(prediction_df, weather_forecast_df):

    for i in range(2,7):
        current_flow = prediction_df['Forecast'].iloc[-1]
        model_inputs = build_1_day_model_inputs(weather_forecast_df, current_flow, days_ahead=i)
        forecast = generate_1_day_prediction(model_inputs)
        new_row = {'Forecast':forecast, 'date':datetime.now() + timedelta(days=i)}
        prediction_df = prediction_df.append(new_row, ignore_index=True)
    prediction_df['date'] = pd.to_datetime(prediction_df['date'])

    return prediction_df



def generate_1_day_prediction(input_array):

    model = joblib.load("data/random_forest_model.joblib")

    flow_prediction = model.predict(input_array)

    return flow_prediction[0]


def build_1_day_model_inputs(future_weather_df, current_flow, days_ahead):

    '''
    These are the inputs needed to calculate the next days' flow forecast

    Returns array [['TMAX','TMIN','DAY_OF_YEAR','STREAMFLOW']]
    '''

    # random forest model inputs
    #['TMAX','TMIN','DAY_OF_YEAR','STREAMFLOW']


    tomorrows_forecast = future_weather_df[future_weather_df['date']==pd.to_datetime(str(datetime.now()+ timedelta(days=days_ahead))[:10])]

    day_of_year = datetime.now().timetuple().tm_yday

    # print(previous_flow_dataframe['cfs'][:-1])

    input_array = [
                    tomorrows_forecast['max_temp'],
                    tomorrows_forecast['min_temp'],
                    day_of_year+days_ahead,
                    current_flow
                    ]
    
    return [input_array]



def build_prev_flow_dataframe(river):
    response = requests.get(river)
    payload = response.json()

    #building an empty dataframe
    prev_flow_df = pd.DataFrame({
                    'cfs': [],
                    'date': []
                    })
    
    # this parses the USGS JSON response
    for i in range(len(payload['value']['timeSeries'][0]['values'][0]['value'])):
        cfs = float(payload['value']['timeSeries'][0]['values'][0]['value'][i]['value'])
        date = payload['value']['timeSeries'][0]['values'][0]['value'][i]['dateTime']
        date = pd.to_datetime(date)
        new_row = {'Observation':cfs, 'date':date}
        prev_flow_df = prev_flow_df.append(new_row, ignore_index=True)
    
    return prev_flow_df


# https://api.weather.gov/gridpoints/BOI/169,112/forecast

def get_weather_forecast(weather_gov_api_url):

    response = requests.get(weather_gov_api_url)
    payload = response.json()
    
    # building two empty dataframes
    future_max_temp_df = pd.DataFrame({
                    'max_temp':[],
                    'icon_url':[],
                    'shortForecast':[],
                   'date': []})

    future_min_temp_df = pd.DataFrame({
                    'min_temp':[],
                   'date': []})

    for i in range(len(payload['properties']['periods'])):
        date = pd.to_datetime(payload['properties']['periods'][i]['endTime'][:10])
        icon_url = payload['properties']['periods'][i]['icon']
        shortForecast = payload['properties']['periods'][i]['shortForecast']
        # print(payload['properties']['periods'][i])
        if payload['properties']['periods'][i]['isDaytime'] == True:
            max_temp = payload['properties']['periods'][i]['temperature']
            new_row = {'max_temp': max_temp, 'icon_url':icon_url,'shortForecast':shortForecast,'date':date}
            future_max_temp_df = future_max_temp_df.append(new_row, ignore_index=True)
        else:
            min_temp = payload['properties']['periods'][i]['temperature']
            new_row = {'min_temp': min_temp, 'date':date}
            future_min_temp_df = future_min_temp_df.append(new_row, ignore_index=True)
    future_temp_df = future_max_temp_df.merge(future_min_temp_df, on='date', how='outer')
    
    
    return future_temp_df




def build_plotly_graph(dataframe, title, x, y):




    

    ## Building the Plotly figure
    fig = px.line(
                    dataframe,
                    x=x,
                    y=y,
                    # line_shape='hvh',
                    # line_shape='linear'
                    # width=700
                )

    # Add image
    fig.add_layout_image(
        dict(
            source="/assets/circle-cropped.png",
            xref="paper", yref="paper",
            x=0.04, y=0.92,
            sizex=0.25, sizey=0.25,
            xanchor="left",
            yanchor="top",
            opacity=0.5,
            layer="below"
        ))

    fig.update_layout({
                        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                    })

    fig.update_layout(
        title={
            'text': f"<b>{title}</b>",
            'y':.99,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        xaxis_title="<b>Day of Month </b>",
        yaxis_title="<b>Discharge, cfs </b>",
        legend_title="",
        # showlegend=False,
        # title = 'Time Series with Custom Date-Time Format',
        xaxis_tickformat = '%d',
        font=dict(
            # family="Courier New, monospace",
            size=12,
            color="BLACK", 
        ),
        legend=dict(
        orientation="h",
        yanchor="top",
        y=.96,
        xanchor="right",
        x=0.98,
        bgcolor="White",
        bordercolor="Black",
        borderwidth=1
        ),
        margin=dict(l=25, r=25, t=30, b=30),
    )
    
    fig.update_yaxes(range=[min(min(dataframe[y[0]]),min(dataframe[y[1]]))*.5, max(max(dataframe[y[0]]),max(dataframe[y[1]]))*2])
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
    fig.update_yaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
    fig.update_xaxes(nticks=21)

    fig.add_annotation(
                x=datetime.now() + timedelta(days=1.5),
                y=200,
                text="1-3 Day <br> Forecast")
    fig.add_annotation(
                x='2020-09-22',
                y=200,
                text="4-7 Day <br> Forecast")
    fig.update_annotations(dict(
                xref="x",
                yref="y",
                # showarrow=True,
                # arrowhead=7,
                ax=0,
                # ay=-40
    ))


    # Add shape regions
    fig.update_layout(
        shapes=[
            dict(
                type="rect",
                # x-reference is assigned to the x-values
                xref="x",
                # y-reference is assigned to the plot paper [0,1]
                yref="paper",
                x0=datetime.now(),
                y0=0,
                x1=datetime.now() + timedelta(days=3),
                y1=1,
                fillcolor="LightGreen",
                opacity=0.2,
                layer="below",
                line_width=0,
            ),

            dict(
                type="rect",
                # x-reference is assigned to the x-values
                xref="x",
                # y-reference is assigned to the plot paper [0,1]
                yref="paper",
                x0=datetime.now() + timedelta(days=3),
                y0=0,
                x1=datetime.now() + timedelta(days=10),
                y1=1,
                fillcolor="LightPink",
                opacity=0.2,
                layer="below",
                line_width=0,
            ),
        ]
    )
    ## end of figure generation
    return fig
