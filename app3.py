import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from datetime import datetime  
from datetime import timedelta

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# us_cities = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv")


# mapping_data = {
#     'date': ['7-19', '7-19','7-20','7-20'],
#     'lat': [42.838680, 44.082420,42.838680,44.082420, ],
#     'lon': [-117.629028,-115.613130,-117.629028,-115.613130],
#     'station':['Owyhee at Rome','SF Payette at Lowman','Owyhee at Rome','SF Payette at Lowman'],
#     "flow":[777, 222,888,333],
#      }


# mapping_df = pd.DataFrame(data=mapping_data)

mapping_df = pd.read_csv("data/latest_flows.csv")


mapping_df['date'] = pd.to_datetime(mapping_df['date'])



## create map fig 2##############
fig = px.scatter_mapbox(mapping_df, lat="lat", lon="lon", hover_name="station", 
                        # hover_data=["State", "Population"],
                            color_discrete_sequence=["fuchsia"], zoom=3, height=300)
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
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.update_traces(customdata=mapping_df['station'])
#########


# ##### create map fig
# fig = px.scatter_mapbox(us_cities, lat="lat", lon="lon", hover_name="City", 
#                         # hover_data=["State", "Population"],
#                             color_discrete_sequence=["fuchsia"], zoom=3, height=300)
# fig.update_layout(
#             mapbox_style="white-bg",
#             mapbox_layers=[
#             {
#                 "below": 'traces',
#                 "sourcetype": "raster",
#                 "sourceattribution": "United States Geological Survey",
#                 "source": [
#                     "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
#                 ]
#             }
#             ])
# fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
# fig.update_traces(customdata=us_cities['City'])
# #######





app.layout = html.Div([

    html.Div([
        dcc.Graph(
            id='crossfilter-indicator-scatter',
            figure = fig,
            hoverData={'points': [{'customdata': 'South Fork Payette at Lowman'}]}
            
        )
    ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
    html.Div([
        dcc.Graph(id='x-time-series'),
        #   
    ], style={'display': 'inline-block', 'width': '49%'}),

])


def create_time_series(df,title='test',x='date',y=['Observation','Forecast']):

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
    fig.update_layout(height=225, margin={'l': 20, 'b': 30, 'r': 10, 't': 10})

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
    fig.update_yaxes(range=[min(df), max(df)])

    
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


if __name__ == '__main__':
    app.run_server(debug=True)