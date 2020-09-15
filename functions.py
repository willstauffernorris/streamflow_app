import plotly.express as px
from datetime import datetime  
from datetime import timedelta
import requests
import pandas as pd



## Eventually, in order to make more graphs, I'll build out this structure
river_dict = {

    'South Fork Payette at Lowman': 'https://waterservices.usgs.gov/nwis/iv/?format=json&sites=13235000&period=P10D&parameterCd=00060&siteStatus=all',
    'Owyhee at Rome':'https://waterservices.usgs.gov/nwis/iv/?format=json&sites=13181000&period=P10D&parameterCd=00060&siteStatus=all'
}




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

def get_weather_forecast():

    response = requests.get("https://api.weather.gov/gridpoints/BOI/169,112/forecast")
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
                    # line_shape='spline',
                    # line_shape='linear'
                    # width=700
                )

    # Add image
    fig.add_layout_image(
        dict(
            source="/assets/circle-cropped.png",
            xref="paper", yref="paper",
            x=0.04, y=0.92,
            sizex=0.3, sizey=0.3,
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
                text="4-10 Day <br> Forecast")
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
