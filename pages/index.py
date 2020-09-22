# Imports from 3rd party libraries
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from datetime import datetime  
from datetime import timedelta
import numpy as np

# Imports from this application
from app import app

import os.path, time


mapping_df = pd.read_csv("data/latest_flows.csv")
# print("Last modified: %s" % time.ctime(os.path.getmtime("test.txt")))

dt=os.path.getmtime('data/latest_flows.csv')
# print(datetime.fromtimestamp(dt))
utc_time = datetime.utcfromtimestamp(dt)

current_MDT = utc_time - timedelta(hours=6)

# print(current_MDT)


mapping_df['date'] = pd.to_datetime(mapping_df['date'])



## create map fig##############
fig = px.scatter_mapbox(mapping_df, lat="lat", lon="lon", hover_name="station", 
                        hover_data={"lat":False, "lon":False,"Observation":False,"Forecast":False},
                            color_discrete_sequence=["DodgerBlue"], zoom=5, height=300,
                        
                                        )
fig.update_layout(
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
# fig.update_layout(mapbox_style="outdoors")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.update_traces(customdata=mapping_df['station'])
#########


column1 = dbc.Col(
    [


        dcc.Markdown(
            f"""
            **Hover over a gauge to see its past and predicted flow. Double click to reset the map.**
            
            """
        ),


        dcc.Graph(
            id='crossfilter-indicator-scatter',
            figure = fig,
            hoverData={'points': [{'customdata': 'South Fork Payette at Lowman'}]}),
        dcc.Graph(id='x-time-series'),
        # dcc.Graph(figure=map_fig, style={"border":"1px black solid", 'padding': 0}),
        # dcc.Graph(figure=fig, style={"border":"1px black solid", 'padding': 0}),

        dcc.Markdown(
            f"""
            Forecast created: {str(current_MDT)[:-3]} MDT. \n
            **Note:** Forecasts only take into consideration the maximum and minimum temperature, day of year, and previous day's flow. Better models coming soon.
            """
        ),


        # html.Div(children=[dcc.Graph(figure=fig)], style={"border":"2px black solid"})


    
    ]
)


def create_time_series(df,title='Flow',x='date',y=['Observation','Forecast']):

    fig = px.scatter(df, x=x, y=y)
    fig = px.line(
                    df,
                    x=x,
                    y=y,
                    # line_shape='hvh',
                    # line_shape='linear'
                    # width=700
                )


    # fig.update_traces(mode='lines+markers')
    fig.update_layout(height=400, margin={'l': 20, 'b': 30, 'r': 10, 't': 10})

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

## This line scales the y axis so when a prediction is made that's 
# significantly higher or lower than the current flow, it looks good in chart 
    fig.update_yaxes(range=[min(np.nanmin(df[y[0]]),np.nanmin(df[y[1]]))*.5, max(np.nanmax(df[y[0]]),np.nanmax(df[y[1]]))*2])

    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
    fig.update_yaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
    fig.update_xaxes(nticks=18)


    fig.add_annotation(
                x=datetime.now() + timedelta(days=1.5),
                y=min(min(df[y[0]]),min(df[y[1]]))*.5,
                text="1-3 Day <br> Forecast")
    fig.add_annotation(
                x=datetime.now() + timedelta(days=4.5),
                y=min(min(df[y[0]]),min(df[y[1]]))*.5,
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
                x0=current_MDT,
                y0=0,
                x1=current_MDT + timedelta(days=3),
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
                x0=current_MDT + timedelta(days=3),
                y0=0,
                x1=current_MDT + timedelta(days=7),
                y1=1,
                fillcolor="LightPink",
                opacity=0.2,
                layer="below",
                line_width=0,
            ),
        ]
    )
    


    return fig



@app.callback(
    dash.dependencies.Output('x-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
    ])
def update_y_timeseries(hoverData):
    df = mapping_df

    city_name = hoverData['points'][0]['customdata']

    df = df[df['station']== city_name]
 
    return create_time_series(df)


layout = dbc.Row([column1])
