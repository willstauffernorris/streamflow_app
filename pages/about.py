# Imports from 3rd party libraries
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Imports from this application
from app import app

# 1 column layout
# https://dash-bootstrap-components.opensource.faculty.ai/l/components/layout
column1 = dbc.Col(
    [
        dcc.Markdown(
            """
        
            ## **River Prediction**

            This website uses machine learning to predict a river's flow. 
            Read more about how the model was created [here.](https://towardsdatascience.com/predicting-the-flow-of-the-south-fork-payette-river-using-an-lstm-neural-network-65292eadf6a6)


            
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

        ## This is the live link
        html.Img(src='https://www.nwrfc.noaa.gov/station/flowplot/hydroPlot.php?id=PRLI1&pe=HG&v=1599087455/hydroPlot.png', className='img-fluid'),
    
        dcc.Markdown(
            """
        
            ### Northwest River Forecast Center model ☝️

            Compare this against current model
            """
        ),   

    ],
)

layout = dbc.Row([column1])