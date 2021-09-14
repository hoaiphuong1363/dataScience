# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
from pandas.core.algorithms import value_counts
import plotly.express as px


# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()


def get_data(df):

    data = pd.DataFrame(spacex_df.groupby('Launch Site').sum()[
        'class']/spacex_df.groupby('Launch Site').count()['class']).reset_index()
    data['Fail'] = 1 - data['class']
    data.columns = ['Launch Site', 'Success', 'Fail']
    return data


data_df = get_data(spacex_df)

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='side-dropdown',
                                             options=[{'label': 'All Sites', 'value': 'All'},
                                                      {'label': 'CCAFS LC-40',
                                                          'value': '0'},
                                                      {'label': 'VAFB SLC-4E',
                                                          'value': '1'},
                                                      {'label': 'KSC LC-39A',
                                                          'value': '2'},
                                                      {'label': 'CCAFS SLC-40', 'value': '3'}],
                                             placeholder='Select a Launch Site here',

                                             searchable=True
                                             ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),

                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider', min=0, max=10000,
                                    step=1000,
                                    marks={
                                        0: "0",
                                        2500: "2500",
                                        5000: "5000",
                                        7500: "7500",
                                        10000: "10000"
                                    }, value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(
                                    dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output


@app.callback(Output('success-pie-chart', 'figure'),
              Input(component_id='side-dropdown', component_property='value'))
def get_graph(value):
    if value == 'All':
        fig = px.pie(data_df, values='Success', names='Launch Site',
                     title='Total Success Launches By Site')
    else:
        data = pd.DataFrame(data_df.iloc[int(value)]).reset_index()
        title = f'Total Success Launches By {data.iloc[0, 1]}'
        fig = px.pie(data, values=int(value), names='index',
                     title=title)
    return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
# Run the app
@app.callback(Output('success-payload-scatter-chart', 'figure'),
              [Input(component_id='side-dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value')]
              )
def get_graph(type, value):
    print(type, value)
    if type == 'All':
        fig = px.scatter(y=spacex_df['class'], x=spacex_df['Payload Mass (kg)'],
                         color=spacex_df['Booster Version Category'])
    else:
        launch_site = ['CCAFS LC-40', 'VAFB SLC-4E',
                       'KSC LC-39A', 'CCAFS SLC-40']

        df = spacex_df[(spacex_df['Launch Site'] == launch_site[int(
            type)]) & ((spacex_df['Payload Mass (kg)'] > float(value[0])) & spacex_df['Payload Mass (kg)'] < float(value[1]))]
        fig = px.scatter(df, y='class', x='Payload Mass (kg)',
                         color='Booster Version Category')

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
