
### This file doesn't connect with the rest of the app. 

### It will run periodically, gathering flow and weather data, then export a csv that's used in the rest of the app

## We'll see if it deploys or not!


import pandas as pd
import requests
from datetime import datetime  
from datetime import timedelta
import numpy as np
from numpy import concatenate
import random
from tensorflow import keras
import joblib
from joblib import load

## database
import os
import psycopg2
import psycopg2.extras as extras


current_MDT = datetime.utcnow() - timedelta(hours=6)
current_MDT

print("THIS IS MY ONE OFF TASK")

river_dict = {

    'South Fork Payette at Lowman': ('https://waterservices.usgs.gov/nwis/iv/?format=json&sites=13235000&period=P10D&parameterCd=00060&siteStatus=all',
                                    "https://api.weather.gov/gridpoints/BOI/169,112/forecast", ##Banner Summit SNOTEL
                                    44.082420,
                                   -115.613130,
                                   'South Fork Payette at Lowman',
                                #    '/content/SouthForkPayetteatKrassel_LSTM.h5',
                                   'models/SouthForkPayetteatKrassel_LSTM.h5',
                                #    '/content/SouthForkPayetteatKrassel_std_scaler.bin'
                                    'models/SouthForkPayetteatKrassel_std_scaler.bin'
                                   ),
    'Owyhee at Rome' : ("https://waterservices.usgs.gov/nwis/iv/?format=json&sites=13181000&period=P10D&parameterCd=00060&siteStatus=all",
                    'https://api.weather.gov/gridpoints/LKN/117,175/forecast',  #Fawn Creek Snotel
                    42.838680,
                   -117.629028,
                    'Owyhee at Rome',
                    'models/OwyheeatRome_LSTM_model.h5',
                    'models/OwyheeatRome_std_scaler.bin'
                      ),
              
    'Middle Fork Salmon at Middle Fork Lodge':("https://waterservices.usgs.gov/nwis/iv/?format=json&sites=13309220&period=P10D&parameterCd=00060&siteStatus=all",
                                               "https://api.weather.gov/gridpoints/BOI/169,112/forecast", ## Banner Summit SNOTEL
                                               44.723362,
                                               -115.015526,
                                               'Middle Fork Salmon at Middle Fork Lodge',
                                               'models/MiddleForkSalmonatMiddleForkLodge_LSTM.h5',
                                               'models/MiddleForkSalmonatMiddleForkLodge_std_scaler.bin'
                                                  ),
              
      'South Fork Salmon at Krassel':("https://waterservices.usgs.gov/nwis/iv/?format=json&sites=13310700&period=P10D&parameterCd=00060&siteStatus=all",
                                      'https://api.weather.gov/gridpoints/BOI/158,145/forecast', ## Need to update this to Big creek summit - its' Krassel right now
                                      44.982159,
                                      -115.725846,
                                      'South Fork Salmon at Krassel',
                                      'models/SouthSalmon_LSTM_model.h5',
                                      'models/SouthSalmon_std_scaler.bin'
                                       ),
      'White Salmon at Underwood':("https://waterservices.usgs.gov/nwis/iv/?format=json&sites=14123500&period=P10D&parameterCd=00060&siteStatus=all",
                                   'https://api.weather.gov/gridpoints/PQR/151,106/forecast', ## I used Surprise Lakes SNOTEL data, but this forecast is for Underwood
                                   45.751834,
                                   -121.527002,
                                   'White Salmon at Underwood' ,
                                   'models/WhiteSalmon_LSTM_model.h5',
                                   'models/WhiteSalmon_std_scaler.bin'
                                   ),
                                               
              }


def build_prev_flow_dataframe(river):

    response = requests.get(river[0])
    payload = response.json()

    #building an empty dataframe
    prev_flow_df = pd.DataFrame({
                    'Observation': [],
                    'date': [],
                    'lat':[],
                    'lon':[],
                    'station':[],
                    'Forecast':[]
                    })
    
    # this parses the USGS JSON response
    for i in range(len(payload['value']['timeSeries'][0]['values'][0]['value'])):
        cfs = float(payload['value']['timeSeries'][0]['values'][0]['value'][i]['value'])
        date = payload['value']['timeSeries'][0]['values'][0]['value'][i]['dateTime']
        date = str(date)[:-6]
        # date = pd.to_datetime(date)
        lat = river[2]
        lon = river[3]
        station = river[4]
        new_row = {'Observation':cfs, 'date':date, 'lat':lat, 'lon':lon, 'station':station}
        prev_flow_df = prev_flow_df.append(new_row, ignore_index=True)
    
    return prev_flow_df



def get_weather_forecast(weather_gov_api_url):
    '''
    To get the right API URL, plug in lat and lon into this URL:
    https://api.weather.gov/points/{latitude},{longitude}
    For example: https://api.weather.gov/points/39.7456,-97.0892

    This will return the grid endpoint in the "forecast" property.
    '''

    response = requests.get(weather_gov_api_url)
    print(response)
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

def build_LSTM_1_day_model_inputs(future_weather_df, current_flow, days_ahead):

    '''
    These are the inputs needed to calculate the next days' flow forecast

    Returns array [['TMAX','TMIN','DAY_OF_YEAR','STREAMFLOW']]
    '''

    # random forest model inputs
    #['TMAX','TMIN','DAY_OF_YEAR','STREAMFLOW']


    tomorrows_forecast = future_weather_df[future_weather_df['date']==pd.to_datetime(str(datetime.now()+ timedelta(days=days_ahead))[:10])]

    day_of_year = current_MDT.timetuple().tm_yday

    # print(previous_flow_dataframe['cfs'][:-1])

    input_array = [
                    current_flow,
                    tomorrows_forecast['max_temp'],
                    tomorrows_forecast['min_temp'],
                    day_of_year+days_ahead,
                    ]
    
    return input_array

def LSTM_prediction(array_of_inputs,model,scaler):

    ## notice the extra brackets as I make it an array
    array_of_inputs = np.array([array_of_inputs], dtype=object)
    # ensure all data is float
    array_of_inputs = array_of_inputs.astype('float32')

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

def build_LSTM_7Day_forecast(river, current_flow):

  #building an empty dataframe
  forecast_flow_df = pd.DataFrame({
                    'Observation': [],
                    'date': [],
                    'lat':[],
                    'lon':[],
                    'station':[],
                    'Forecast':[]
                    })

  ## Gather the weather forecast for the next 7 days
  weather_forecast_df = get_weather_forecast(river[1])

  ## Import the saved model and scaler
  # model = keras.models.load_model("/content/LSTM_model.h5")
  # weights_path = get_file(
  #           'MiddleForkSalmonatMiddleForkLodge_LSTM.h5',
  #           'https://github.com/willstauffernorris/streamflow_predictions/blob/master/models')

# print(weights_path)
  model = keras.models.load_model(river[5])
  # model = keras.models.load_model(weights_path)


  # scaler=load('/content/std_scaler.bin')
  scaler=load(river[6])

  ## Range of days I'm making a prediction for
  ## Change the last number in range for different set of days
  for i in range(0,7):
      if i == 0:
        forecast_cfs = current_flow
      else:
        current_flow = forecast_flow_df['Forecast'].iloc[-1]
        model_inputs = build_LSTM_1_day_model_inputs(weather_forecast_df, current_flow, days_ahead=i)
        forecast_cfs = LSTM_prediction(model_inputs,model,scaler)


      ## for each day's prediction, add the relevant metadata
      date = current_MDT + timedelta(days=i)
      date = pd.to_datetime(date)
      lat = river[2]
      lon = river[3]
      station = river[4]
      new_row = {'Forecast':forecast_cfs, 'date':date, 'lat':lat, 'lon':lon, 'station':station}
      forecast_flow_df = forecast_flow_df.append(new_row, ignore_index=True)
  return forecast_flow_df

mapping_flow_df = pd.DataFrame({
                    'Observation': [],
                    'date': [],
                    'lat':[],
                    'lon':[],
                    'station':[],
                    'Forecast':[]
                    })

for river in river_dict:
  print(f"Generating data for {river}...")

  ## all USGS data for the last 10 days
  prev_flow_df = build_prev_flow_dataframe(river_dict[river])
#   print(prev_flow_df.tail(20))
#   exit()
  ## flow at time of data import
  current_flow = prev_flow_df['Observation'].iloc[-1]

  # future flows
  ## uncomment this out for future flows- weather.gov API isn't working
  forecast_flow_df = build_LSTM_7Day_forecast(river_dict[river], current_flow)

  ## Big dataframe that puts all the information together
  mapping_flow_df = mapping_flow_df.append(prev_flow_df, ignore_index=True)
  mapping_flow_df = mapping_flow_df.append(forecast_flow_df, ignore_index=True)

print(mapping_flow_df.tail(10))

# mapping_flow_df.to_csv('data/generated_latest_flows.csv')
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

def delete_existing_and_execute_values(conn, df, table):
    """
    Using psycopg2.extras.execute_values() to insert the dataframe
    """
    # Create a list of tupples from the dataframe values
    tuples = [tuple(x) for x in df.to_numpy()]
    # Comma-separated dataframe columns
    cols = ','.join(list(df.columns))
    # SQL quert to execute
    query  = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
    cursor = conn.cursor()

    cursor.execute(f"DELETE FROM {table}")
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    print("execute_values() done")
    cursor.close()


# calling the function
delete_existing_and_execute_values(conn, mapping_flow_df, 'flow')