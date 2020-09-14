# Imports from 3rd party libraries
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Imports from this application
from app import app

# 2 column layout. 1st column width = 4/12
# https://dash-bootstrap-components.opensource.faculty.ai/l/components/layout
column1 = dbc.Col(
    [
        dcc.Markdown(
            """
        
            ## What's the future flow of the river?

            This website uses machine learning to predict a river's flow.

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


gapminder = px.data.gapminder()
fig = px.scatter(gapminder.query("year==2007"), x="gdpPercap", y="lifeExp", size="pop", color="continent",
           hover_name="country", log_x=True, size_max=60)



d = {
    'date': ['2020-09-04','2020-09-05','2020-09-06','2020-09-07', '2020-09-08','2020-09-09','2020-09-10','2020-09-11','2020-09-12','2020-09-13','2020-09-14','2020-09-15','2020-09-16','2020-09-17','2020-09-18','2020-09-19','2020-09-20','2020-09-21','2020-09-22','2020-09-23','2020-09-24','2020-09-25'],
    'Observation': [364,364,364,364,365,369,366,362,358,358,361,np.nan, np.nan, np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan],
    'Forecast': [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 361, 359, 355, 350, 350, 350, 390, 350, 350, 350, 350,350]
     }
df = pd.DataFrame(data=d)


fig = px.line(
                df,
                x='date',
                y=['Observation','Forecast'],
                line_shape='spline',
                
                
            )

# Add image
fig.add_layout_image(
    dict(
        source="/assets/circle-cropped.png",
        xref="paper", yref="paper",
        x=0.04, y=0.94,
        sizex=0.3, sizey=0.3,
        xanchor="left",
        yanchor="top",
        opacity=0.6,
        layer="below"
    )
)

fig.add_layout_image(
        dict(
            source="https://images.plot.ly/language-icons/api-home/python-logo.png",
            xref="x",
            yref="y",
            x=0,
            y=500,
            sizex=20,
            sizey=20,
            sizing="stretch",
            opacity=0.9,
            layer="above")
)
fig.update_yaxes(range=[200, 900])

fig.update_layout({
                    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                })

fig.update_layout(
    title="<b>South Fork Payette at Lowman</b>",
    xaxis_title="<b>Day of Month </b>",
    yaxis_title="<b>Discharge, cfs </b>",
    legend_title="",
    # showlegend=False,
    font=dict(
        # family="Courier New, monospace",
        size=14,
        color="BLACK",
    )
)

fig.update_layout(
    title={
        # 'text': "Plot Title",
        # 'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})

fig.update_layout(legend=dict(
    orientation="h",
    yanchor="top",
    y=.96,
    xanchor="right",
    x=0.98,
    bgcolor="White",
    bordercolor="Black",
    borderwidth=1
))

fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

fig.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
fig.update_yaxes(showline=True, linewidth=1, linecolor='black', mirror=True)



# fig.add_trace(go.Scatter(x=[-100,400],y= [400,400],fill='tozeroy'),row=1, col=1)

fig.add_annotation(
            x='2020-09-16',
            y=200,
            text="1-3 Day <br> Forecast")
fig.add_annotation(
            x='2020-09-22',
            y=200,
            text="4-10 Day <br> Forecast")
# fig.add_annotation(
#             x=4,
#             y=4,
#             text="dict Text 2")

fig.update_annotations(dict(
            xref="x",
            yref="y",
            # showarrow=True,
            # arrowhead=7,
            ax=0,
            # ay=-40
))





import plotly.graph_objects as go

# fig = go.Figure()

# # Add scatter trace for line
# fig.add_trace(go.Scatter(
#     x=df['date'],
#     y=df['observed cfs','predicted cfs'],
#     mode="lines",
#     name="temperature"
# ))

# Add shape regions
fig.update_layout(
    shapes=[
        # 1st highlight during Feb 4 - Feb 6
        dict(
            type="rect",
            # x-reference is assigned to the x-values
            xref="x",
            # y-reference is assigned to the plot paper [0,1]
            yref="paper",
            x0='2020-09-14',
            y0=0,
            x1='2020-09-18',
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
            x0='2020-09-18',
            y0=0,
            x1='2020-09-25',
            y1=1,
            fillcolor="LightPink",
            opacity=0.2,
            layer="below",
            line_width=0,
        ),
        # # 2nd highlight during Feb 20 - Feb 23
        # dict(
        #     type="rect",
        #     xref="x",
        #     yref="paper",
        #     x0="2015-02-20",
        #     y0=0,
        #     x1="2015-02-22",
        #     y1=1,
        #     fillcolor="LightSalmon",
        #     opacity=0.5,
        #     layer="below",
        #     line_width=0,
        # )
    ]
)


fig.update_layout(
    # title = 'Time Series with Custom Date-Time Format',
    xaxis_tickformat = '%d'
)

fig.update_xaxes(nticks=len(df['date']))





column2 = dbc.Col(
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
        # html.Img(src='https://www.nwrfc.noaa.gov/station/flowplot/hydroPlot.php?id=PRLI1&pe=HG&v=1599087455/hydroPlot.png', className='img-fluid'),

        ## Placeholder image
        html.Img(src='/assets/hydroPlot.png', className='img-fluid'),
    ]
)

layout = dbc.Row([column1, column2])