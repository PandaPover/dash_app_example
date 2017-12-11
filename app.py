
# coding: utf-8

# # Final Project
# 
# #step1: download the csv and get it running local (with pd.read)
# #step2: upload the data to github and access the data through the web
# 
# Create a Dashboard taking data from [Eurostat, GDP and main components (output, expenditure and income)](http://ec.europa.eu/eurostat/web/products-datasets/-/nama_10_gdp). 
# The dashboard will have two graphs: 
# 
# * The first one will be a scatterplot with two DropDown boxes for the different indicators. It will have also a slide for the different years in the data. 
# * The other graph will be a line chart with two DropDown boxes, one for the country and the other for selecting one of the indicators. (hint use Scatter object using mode = 'lines' [(more here)](https://plot.ly/python/line-charts/) 
# 
# 

# In[1]:


# imports
import dash
# from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd


# In[2]:


# load the dataframe
df = pd.read_csv('nama_10_gdp_1_Data.csv')
# inspect the dataframe
print(df)


# In[31]:


# to make the Year-Slider work properly, make sure TIME-column is of int type
# df['TIME'] = df['TIME'].astype('int64')


# In[3]:


# build the dashboard

app = dash.Dash(__name__)
server = app.server

app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

available_indicators = df['NA_ITEM'].unique()
available_units = df['UNIT'].unique()
available_locations = df['GEO'].unique()

app.layout = html.Div([
    # Create Selection Items
    html.Div([
        #Create Dropdown for selecting the unit of meaurement
        html.Div([
            html.H2(children='Please select unit'),
            dcc.Dropdown(
                id='unit',
                options=[{'label': i, 'value': i} for i in available_units],
                value='Chain linked volumes, index 2010=100'
            )]),
    
        #Create Selectors for X-Axis
        html.Div([
            #Header
            html.H2(children='Select X-Axis Indicator'),
            #Dropdown for X-Axis Indicator
            dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Gross domestic product at market prices'
            ),
            #Radioitems for X-Axis Type
            dcc.RadioItems(
                id='xaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
         ],
         style={'width': '48%', 'display': 'inline-block'}),
    
        # Create Selectors for Y-Axis
        html.Div([
            #Header
            html.H2(children='Select Y-Axis Indicator'),
            #Dropdown for Y-Axis Indicator
            dcc.Dropdown(
                id='yaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Value added, gross'
            ),
            #Radioitems for Y-Axis Type
            dcc.RadioItems(
                id='yaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),
    
    # Create Main Graph (Upper Scatter)
     html.Div([
        dcc.Graph(
            id='indicator-scatter',
            hoverData={'points': [{'customdata': 'Spain'}]}
        )
    ], style={'width': '100%', 'display': 'inline-block', 'padding': '0 20'}),    
    
    # Create the Year-Slider
    html.Div(dcc.Slider(
        id='year-slider',
        min=df['TIME'].min(),
        max=df['TIME'].max(),
        value=df['TIME'].max(),
        step=None,
        marks={str(year): str(year) for year in df['TIME'].unique()}
    ), style={'width': '100%', 'padding': '0px 20px 20px 20px'}),
    
    #Create left bottom graph (X-Axis Values and Time Series)
    html.Div([
        dcc.Graph(id='x-time')
    ], style={'display': 'inline-block', 'width': '49%'}),
    
    #Create Right bottom graph (Y-Axis and Time-Series)
    html.Div([
        dcc.Graph(id='y-time')
        ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})

])

# Select dependencies of the Main Graph (Upper Scatter)
@app.callback(
    dash.dependencies.Output('indicator-scatter', 'figure'),
    [dash.dependencies.Input('xaxis-column', 'value'),
     dash.dependencies.Input('yaxis-column', 'value'),
     dash.dependencies.Input('xaxis-type', 'value'),
     dash.dependencies.Input('yaxis-type', 'value'),
     dash.dependencies.Input('year-slider', 'value'),
     dash.dependencies.Input('unit', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type,
                 year_value, unit_value):
    dff = df[df['TIME'] == year_value]
    dff = dff[dff['UNIT'] == unit_value]
    
    return {
        'data': [go.Scatter(
            x=dff[dff['NA_ITEM'] == xaxis_column_name]['Value'],
            y=dff[dff['NA_ITEM'] == yaxis_column_name]['Value'],
            text=dff[dff['NA_ITEM'] == yaxis_column_name]['GEO'],
            customdata=dff[dff['NA_ITEM'] == yaxis_column_name]['GEO'],
            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': go.Layout(
            xaxis={
                'title': xaxis_column_name,
                'type': 'linear' if xaxis_type == 'Linear' else 'log'
            },
            yaxis={
                'title': yaxis_column_name,
                'type': 'linear' if yaxis_type == 'Linear' else 'log'
            },
            margin={'l': 40, 'b': 30, 't': 10, 'r': 0},
            hovermode='closest'
        )
    }

# Create Return-Function for both bottom Graphs
def create_time_series(dff, axis_type, title):
    return {
        'data': [go.Scatter(
            x=dff['TIME'],
            y=dff['Value'],
            mode='lines+markers'
        )],
        'layout': {
            'height': 225,
            'margin': {'l': 20, 'b': 30, 'r': 10, 't': 10},
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': title
            }],
            'yaxis': {'type': 'linear' if axis_type == 'Linear' else 'log'},
            'xaxis': {'showgrid': False}
        }
    }


# Select dependencies for right bottom graph
@app.callback(
    dash.dependencies.Output('x-time', 'figure'),
    [dash.dependencies.Input('indicator-scatter', 'hoverData'),
     dash.dependencies.Input('xaxis-column', 'value'),
     dash.dependencies.Input('xaxis-type', 'value'),
     dash.dependencies.Input('unit', 'value')])
def update_y_timeseries(hoverData, xaxis_column_name, axis_type, unit_value):
    country_name = hoverData['points'][0]['customdata']
    dff = df[df['GEO'] == country_name]
    dff = dff[dff['UNIT'] == unit_value]
    dff = dff[dff['NA_ITEM'] == xaxis_column_name]
    title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
    return create_time_series(dff, axis_type, title)

# Select dependencies for left bottom graph
@app.callback(
    dash.dependencies.Output('y-time', 'figure'),
    [dash.dependencies.Input('indicator-scatter', 'hoverData'),
     dash.dependencies.Input('yaxis-column', 'value'),
     dash.dependencies.Input('yaxis-type', 'value'),
     dash.dependencies.Input('unit', 'value')])
def update_x_timeseries(hoverData, yaxis_column_name, axis_type, unit_value):
    dff = df[df['GEO'] == hoverData['points'][0]['customdata']]
    dff = dff[dff['UNIT'] == unit_value]
    dff = dff[dff['NA_ITEM'] == yaxis_column_name]
    return create_time_series(dff, axis_type, yaxis_column_name)


if __name__ == '__main__':
    app.run_server()
    
"""        
        html.Div([
            dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Gross domestic product at market prices'
            )
        ],
        style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='yaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Value added, gross'
            )
        ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
        
        
    ]),
    
    dcc.Graph(id='indicator-graphic'),

    dcc.Slider(
        id='year--slider',
        min=df['TIME'].min(),
        max=df['TIME'].max(),
        value=df['TIME'].max(),
        step=None,
        marks={str(year): str(year) for year in df['TIME'].unique()}
    )
])

@app.callback(
    dash.dependencies.Output('indicator-graphic', 'figure'),
    [dash.dependencies.Input('xaxis-column', 'value'),
     dash.dependencies.Input('yaxis-column', 'value'),
     dash.dependencies.Input('year--slider', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name, year_value):
    dff = df[df['TIME'] == year_value]
    
    return {
        'data': [go.Scatter(
            x=dff[dff['NA_ITEM'] == xaxis_column_name]['Value'],
            y=dff[dff['NA_ITEM'] == yaxis_column_name]['Value'],
            text=dff[dff['NA_ITEM'] == yaxis_column_name]['Value'],
            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': go.Layout(
            xaxis={
                'title': xaxis_column_name,
                'type': 'linear' if xaxis_type == 'Linear' else 'log'
            },
            yaxis={
                'title': yaxis_column_name,
                'type': 'linear' if yaxis_type == 'Linear' else 'log'
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )
    }

if __name__ == '__main__':
    app.run_server()
    
"""

