# Imports from 3rd party libraries
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from datetime import datetime  
from datetime import timedelta
import os.path, time
# import datetime


## database imports
import os
import psycopg2
import psycopg2.extras as extras


# Imports from this application
from app import app



# from index import *
# from index import mapping_df

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

## This line always fucks up 
    # fig.update_yaxes(range=[min(df[y])/2,max(df[y])*2])
    # fig.update_yaxes(range=[min(df), max(df)])
    fig.update_yaxes(range=[min(min(df[y[0]]),min(df[y[1]]))*.5, max(max(df[y[0]]),max(df[y[1]]))*2])

    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
    fig.update_yaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
    fig.update_xaxes(nticks=21)


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
    


    return fig

# Connecting to database
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
sql = "select * from flow;"
database_df = pd.read_sql_query(sql, conn)
conn = None

database_df = database_df.rename(columns={"observation":"Observation", "forecast":"Forecast"})
database_df = database_df.drop(columns="id")
mapping_df = database_df
mapping_df['date'] = pd.to_datetime(mapping_df['date'])


payette_df = mapping_df[mapping_df['station']=='South Fork Payette at Lowman']

fig = create_time_series(payette_df,title='South Fork Payette at Lowman')

dt=os.path.getmtime('data/latest_flows.csv')
# print(datetime.fromtimestamp(dt))
utc_time = datetime.utcfromtimestamp(dt)

current_MDT = utc_time - timedelta(hours=6)

# print(current_MDT)

# 1 column layout
# https://dash-bootstrap-components.opensource.faculty.ai/l/components/layout
column1 = dbc.Col(
    [
        dcc.Markdown(
            """
        
            # **How rivers.fyi works**

            This website uses machine learning to predict a river's flow. Predictions are currently generated once every 10 minutes.

            This very simple looking web app has a lot going on behind the scenes! Here are the steps I used to create rivers.fyi.

            ### Gather historical flow and climate data
            I gathered flow data from the period 1912-2020 from the USGS, although most stations have consistent data from the late 80's onward. I merged this dataset with climate data from NRCS SNOTEL stations, which generally starts around 1980. This typically 30+ year dataset is used to train my model.
            

            ### Create a model
            I used an LSTM neural network to create models with R^2 between .90 and .98 for a forecast one day in advance. Read more about how the model was created [here.](https://towardsdatascience.com/predicting-the-flow-of-the-south-fork-payette-river-using-an-lstm-neural-network-65292eadf6a6) 
            I will report R^2 and mean average error for each river in the future.

            Currently, I'm using a time window of one day for the LSTM model, but I will likely increase this window at least for some of the models where the gauge is far downstream of the SNOTEL station such as the Owyhee River.
            
            My current method of prediction is to predict one day out, then use the result of that prediction as inputs for the next day (along with weather predictions). This is quite prone to errors multiplying rapidly, so I will experiement with forecasting more days out. Ideally I would blend longer-term forecasts with my current house-of-cards model for more accuracy.
            
            Finally, I save the model and associated data transformations like scalers to use in predictions.
            

            ### Import current flow and weather data
            The model is trained on historical data, but I want to make predictions on live data.
            To gather this information, I interface with the USGS and NOAA APIs.

            I pull in the last 10 days of flow data from the USGS, and the next seven days of forecasted weather from NOAA. 
            These data are used as inputs to the LSTM neural network.

            ### Generate predictions
            Predictions are generated once every 10 minutes using a one-off Heroku dyno.
            I tried to have predictions run on demand on the same Heroku dyno the app is hosted on, but after strugging mightily with deploying Tensorflow on Heroku, I realized that the 500MB of RAM allotted was only sufficient to run one day of neural network prediction.
            Using the one-off dyno allows a task to run at scheduled intervals, but not run constantly or every single time a user visits the site. 
            
            The data from the scheduled prediction generator are stored in a Heroku PostgreSQL database.
            The app refreshes the displayed data every 10 minutes.
            
            ### Display the data
            I used Plotly Dash to create a clean-looking data visualization.
            I really like navigating through data in a spatial way (huge mapping nerd), so I wrestled with various Plotly frameworks until I figured out how to display time series graphs by simply hovering over a point.
            The hover features is nice because data is displayed in a snappy way, with a minimum of user input.
            I think this is the best way for a user to navigate, becuase when I'm looking at flows, I first want to know what's going on closest to me, then move farther out if I'm interested.
            It's also easier to see spatial trends, like where storms are hitting.
            
            For plotting the time series data, I was heavily inspired by the NOAA river forecast centers. I tried to mimic the style of their plots (see **Comparing Models** below).
            
            ### Deploy

            I used Heroku for ease of use, although as mentioned above, deploying neural networks is anything but easy.
            I'm happier with the current setup, because the app boots faster now that it's mainly a data dashboard (as Plotly is designed to be).
            I'm using the Hobby tier, which costs $7/month. 


            ### Next steps
            There are many, many ways to improve this app. The features I'd like to add are:

            - Integrations with precipitation data. This is tough because I have to parse the NOAA forecast text to get actual precipitation amounts. This feature doens't make a huge difference right now (fall) in the Rocky Mountain rivers, but it's one of the most important features for the Cascade mountain rivers (White Salmon).

            - Incorporating Google Earth Engine data into model. This would help the model determine if it's a wet or dry year. Right now, I think the Owyhee model is trying to go up to get closer to the historical mean, but it's low because it's a drought year in that basin.

            - Increase LSTM time window

            - Report error metrics

            - Use difference in flow each day as target, instead of cfs. This dramatically decreases the R^2 metric, and turns my data into a stationary time series. Read more [here.](https://otexts.com/fpp2/stationarity.html)

            - Model interpretability - run a parallel random forest model and log feature importances

            - Include Wind River at Stabler, WA (not currently served by NWRFC - WA State runs the gauge)

            - Include Little White Salmon at Willard, WA (currently ungauged, but has historically been gauged)

            - Incorporate NOAA river forecast data into plots, so users can see the difference with my model

            """
        ),

        dcc.Markdown(
            """
        
            ### Comparing Models
            It's helpful to gut-check my model against the current public standard, the NOAA forecast center models.
            Below you can see the two plots compared.

            ### This is the model that I created from a neural nework 👇
            """
        ), 

        dcc.Graph(figure=fig, style={"border":"1px black solid", 'padding': 0, 'width':700}),

        dcc.Markdown(
            f"""
            Forecast created: {str(current_MDT)[:-3]} MDT. \n

            ### And this is the Northwest River Forecast Center model 👇

            """
        ),     

        ## This is the live link
        html.Img(src='https://www.nwrfc.noaa.gov/station/flowplot/hydroPlot.php?id=PRLI1&pe=HG&v=1599087455/hydroPlot.png', className='img-fluid'),
    
        dcc.Markdown(
            f"""
            .\n


            ### Thanks for reading!
            Check out my [portfolio site,](https://www.willstauffer.com) and feel free to [reach out](will@willstauffernorris.com) if you have questions or comments about the project.

            """
        ),     

    ],
)







layout = dbc.Row([column1])