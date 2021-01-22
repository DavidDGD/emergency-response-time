import json
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import dash_table
import dash_bootstrap_components as dbc
from flask_caching import Cache

## https://ops.fhwa.dot.gov/publications/weatherempirical/sect2.htm
## https://ops.fhwa.dot.gov/weather/q1_roadimpact.htm
## https://downloads.hindawi.com/journals/jat/2019/8203081.pdf

RAINY_DELAY_FACTOR = 1.13
SNOWY_FACTOR = 1.23
HEAVY_SNOW_DELAY_FACTOR = 1.4
ICY_DELAY_FACTOR = 1.5
LOW_VISIBILITY_DARK_FACTOR = 1.12

BUSY_DELAY_FACTOR = 1.47
AVG_DAY_TRAFFIC_FACTOR = 1.25
AVG_EVENING_TRAFFIC_FACTOR = 1.13

## Read data
df = pd.read_csv('data/main.csv', sep=',')
df_climb = pd.read_csv('data/climb.csv')
df_walk = pd.read_csv('data/hor_climb.csv')
df_mapboxes = pd.read_csv('data/firestation_mapboxes.csv')
df_fire_stations = pd.read_csv('data/fire_stations_with_statistics.csv')
with open('temp/polygons_geo.json') as json_file:
    fire_stations_geojson = json.load(json_file)

# df = df.sample(1000)  # @todo: remove this line
# df_climb = df_climb.sample(1000)  # @todo: remove this line
# df_walk = df_walk.sample(1000)  # @todo: remove this line

df_for_export = df.head(5)
total_samples = len(df)

available_indicators = ["Response Time (s)", "Notification Time (s)", "Travel Time (s)",
                        "Climbing Time (s)", "Walking Time, indoors (s)", "Walking Time, outdoors (s)",
                        'Post Arrival Time (s)']



app = dash.Dash(__name__)
app.title = "Response Time 🔥"
server = app.server
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': './Dashboard/cache'
})

app.layout = html.Div(children=[

    html.Div(className="row",
             children=[
                 html.Div(
                     className="twelve columns div-user-controls",
                     children=[
                         html.H1("Fire Incidents Response Time"),
                         html.Div(
                             children=[
                                 html.P(children=[
                                     html.Span('''Time of notification''',
                                               style={'color': '#bb5b67', 'letter-spacing': '2px'}),
                                     html.Span(''' + ''', style={'margin-left': '15px', 'margin-right': '15px'}),
                                     html.Span('''Travel time''', style={'color': '#d8a1a7', 'letter-spacing': '2px'}),
                                     html.Span(''' + ''', style={'margin-left': '15px', 'margin-right': '15px'}),
                                     html.Span(''' Post-arrival time needed to actually start extinguishing a fire''',
                                               style={'color': '#bb5b67', 'letter-spacing': '2px'}),
                                 ],
                                     className='formula1'
                                 ),
                                 html.P(children=[
                                     html.Span('''Fixed 4:12''', style={'color': '#bb5b67', 'letter-spacing': '2px'}),
                                     html.Span(''' + ''', style={'margin-left': '6px', 'margin-right': '6px'}),
                                     html.Span('''Travel time to reach individual property''',
                                               style={'color': '#d8a1a7', 'letter-spacing': '2px'}),
                                     html.Span(''' + ''', style={'margin-left': '6px', 'margin-right': '6px'}),
                                     html.Span('''Walking outdoors (fixed 0:16) + Climbing + Walking indoors''',
                                               style={'color': '#bb5b67', 'letter-spacing': '2px'}),
                                 ],
                                     className='formula2'),
                             ],
                             style={'display': 'inline-block', 'text-align': 'center'}),

                     ])]),

    html.Div(className="row",
             children=[
                 html.Div(
                     className="five columns div-user-controls",
                     children=[
                         html.P('About', style={'font-size': '24px', 'font-weight': '600', 'widht': '100%',
                                                'text-align': 'center'}),
                         html.P(
                             '''This dashboard provides insights to the response times of the fire department for commercial properties in Amsterdam, in case a fire incidents occurs. By navigating through the dashboard, you can discover how different elements vary the response time, as well as getting detailed information about commercial addresses and fire stations in Amsterdam. '''),
                     ]),

                 html.Div(
                     className="seven columns div-user-controls2",
                     children=[
                         html.P('Features', style={'font-size': '24px', 'font-weight': '600', 'widht': '100%',
                                                   'text-align': 'center'}),
                         html.Div(
                             html.Ul(id='my-list',
                                     children=[
                                         html.Li('Different  response time components overview', className='li-new'),
                                         html.Li('Weather settings', className='li-new'),
                                         html.Li('Traffic settings', className='li-new'),
                                         html.Li('Specific property related information', className='li-new'),
                                         html.Li('Fire district information', className='li-new'),
                                         html.Li('Dark and Street map style for vieweing', className='li-new'),
                                         html.Li('Export list of properties to CSV', className='li-new'),
                                     ],
                                     style={'text-align':'center'}),
                         ),
                         html.P('How to use?', style={'font-size': '24px', 'font-weight': '600', 'widht': '100%',
                                                      'text-align': 'center'}),

                         html.Div(children=[
                              html.Details([
                              html.Summary(children=[
                                  html.Span('''Instructions: '''),
                                  html.Span('''(can be expanded and collapsed by clicking on this row):''', style={'opacity':'0.4'})],
                                  className='summary'),
                              html.Ul(id='instructions-visible',
                                     children=[
                                         html.Li('Select the response time component of interest from the dropdown'),
                                         html.Li('Change Weather and Traffic settings to see how they affect "Response Time" and "Travel Time"'),
                                         html.Li('Hover on one of the addresses to see information about its response time in detail'),
                                         html.Li('Hover on a white dot (firestation) to see information about the fire station district'),
                                         html.Li('Toggle between map style views to find the convenient one'),
                                         html.Li('Filter the number of addresses to be shown on the map and to be displayed in the table below'),
                                         html.Li('Export the selected number of addresses with the longest response times to a CSV file.'),
                                     ],
                                     ),
])           
                             
                         ]),
                     ]),

             ]),


    html.Hr(),

    html.Div(
        className="row",
        children=[
            html.Div(
                className="three columns div-user-controls",
                children=[

                    html.H2("Dashboard Settings"),
                    html.P(
                        """"""
                    ),
                    ## Change background color

                    html.Div(
                        className="div-for-category",
                        children=[
                            ## Input: variable to show
                            html.Div([
                                html.P('Response time variable', className="pfilter"),
                                dcc.Dropdown(
                                    id='indicators-column',
                                    options=[{'label': "Response Time", 'value': "Response Time (s)"},
                                             #  {'label': "- Notification Time", 'value': "Notification Time (s)"},  hidden, because all properties have he same value
                                             {'label': "- Travel Time", 'value': "Travel Time (s)"},
                                             {'label': "- Post Arrival Time", 'value': "Post Arrival Time (s)"},
                                             {'label': "- - Climbing Time", 'value': "Climbing Time (s)"},
                                             {'label': "- - Walking Time, indoors",
                                              'value': "Walking Time, indoors (s)"},
                                             # {'label': "- - Walking Time, outdoors", 'value': "Walking Time, outdoors (s)"}     hidden, because all properties have he same value
                                             ],
                                    value="Response Time (s)",
                                    searchable=False,
                                    clearable=False,
                                    className="dropdown",
                                    style={ 'width':'100%', 'margin-left':'5px' }
                                ),
                            ]),

                            html.Hr(),
                            html.P('Number of entries to be shown in the table and the map.'),
                            dcc.Input(
                             id="table-entries",
                             type="number",
                             placeholder="Number of entries to show",
                             value=len(df),
                             min=0,
                             max=total_samples,
                             style={"width":"200px","margin-left":"10px", "height":"30px",
                                      'display': 'inline-block',
                                      'background-color': '#722f37',
                                      'border-color': 'white',
                                      'color': '#722f37'}

                            ),

                            html.Hr(),
                            ## Input: Weather setting
                            html.Div(
                                children=[
                                    html.P(
                                        'Weather and traffic filters are only available in combination with "Response Time" or "Travel Time".',
                                        className="pwarning", id='visibility-dependent-element1',
                                        style={'display': 'none'}),
                                    html.P('Weather settings', className="pfilter-weather",
                                           id='visibility-dependent-element2'),
                                    dbc.RadioItems(

                                        options=[
                                            ## Use this as implementation basis https://www.researchgate.net/publication/328133914_Impact_of_adverse_winter_weather_on_traffic_flow/figures?lo=1 (table 3)
                                            {'label': 'Sunny', 'value': 'sunny'},  # factor = 1 for travel time
                                            {'label': 'Rainy️', 'value': 'rainy'},  # factor = 1 / 0.846
                                            {'label': 'Snowy️', 'value': 'snowy'},
                                            {'label': 'Heavy Snow️', 'value': 'heavy snow'},  # factor = 1 / 0.769
                                            {'label': 'Icy️', 'value': 'icy'},
                                            {'label': 'Low visibility️', 'value': 'low visibility'},
                                        ],
                                        value='sunny',
                                        id='weather-checklist',
                                        ## or use this https://core.ac.uk/download/pdf/81158446.pdf (table 2)
                                        labelClassName="radio-group-labels",
                                        labelCheckedClassName="radio-group-labels-checked",
                                        className="button-container",
                                        style={"display": "grid"}
                                    ),
                                ]),

                            ## Input: Traffic setting
                            html.Div([
                                html.P('Traffic settings', className="pfilter"),
                                dbc.RadioItems(
                                    id='traffic-checklist',  ## Not sure how to implement this yet
                                    options=[
                                        {'label': '️No traffic', 'value': 'no-traffic'},  # factor = 1
                                        {'label': 'Day time', 'value': 'normal-day'},  # factor = 1 / 0.846
                                        {'label': 'Late evening', 'value': 'normal-evening'},  # factor = 1 / 0.846
                                        {'label': 'Rush hour', 'value': 'busy'},  # factor = 1 / 0.769
                                    ],
                                    value='no-traffic',
                                    labelClassName="radio-group-labels",
                                    labelCheckedClassName="radio-group-labels-checked",
                                    className="button-container",
                                    style={"display": "grid"}
                                ),
                            ]),
                            html.Hr(),

                            html.Div([
                                html.P('Map color setting', className="pfilter"),
                                dbc.RadioItems(
                                    id='background',
                                    options=[{'label': 'Dark Mode', 'value': 'black'},  # factor = 1 for travel time
                                             {'label': 'Street Map Style', 'value': 'streetmap'}],
                                    value='black',
                                    labelClassName="radio-group-labels",
                                    labelCheckedClassName="radio-group-labels-checked",
                                    className="button-container"
                                ),
                            ]),

                        ],
                    ),

                ],
            ),
            # Column for app graphs and plots
            html.Div(
                className="nine columns div-for-charts bg-grey",
                children=[
                    dcc.Loading(
                        id="loading-1",
                        children=[
                            html.Div(
                                dcc.Graph(
                                    id='indicator-graphic',
                                    config={
                                        'displayModeBar': False
                                    },

                                ))],
                        type="dot",
                        color='#d8d8d8',
                    ),
                ],
            ),
        ],
    ),

    html.Div(className="row",
             children=[
                 html.Div(
                     className="twelve columns div-table-export",
                     children=[
                         html.Hr(),
                         html.H2('Properties with the longest response time'),


                         dcc.Loading(
                             id="loading-2",
                             children=[
                                 dash_table.DataTable(
                                     id='table',
                                     data=[],
                                     style_header={'backgroundColor': 'rgb(30, 30, 30)'},
                                     style_cell={
                                         'backgroundColor': 'rgb(50, 50, 50)',
                                         'color': 'white',
                                         'textAlign': 'center',
                                         'fontFamily': 'Arial',
                                         'fontSize': '16px',
                                         'lineHeight':'25px',
                                     },
                                     export_format="csv",
                                     page_size=15,
                                 )
                             ],
                             type="dot",
                             color='#d8d8d8',
                         ),
                     ],
                 ),
             ],
             ),
])


def format_time(time_in_seconds):
    minutes, seconds = divmod(time_in_seconds, 60)

    formatted_seconds = str(int(round(seconds, 0)))
    if len(formatted_seconds) == 1:
        formatted_seconds = '0' + formatted_seconds

    formatted_minutes = str(int(round(minutes, 0)))
    if len(formatted_minutes) == 1:
        formatted_minutes = '0' + formatted_minutes

    return formatted_minutes + ':' + formatted_seconds


@app.callback(
    Output('indicator-graphic', 'figure'),
    Output('table', 'data'),
    Output('table', 'columns'),
    Output('visibility-dependent-element1', 'style'),
    Output('weather-checklist', 'options'),
    Output('traffic-checklist', 'options'),
    Input('indicators-column', 'value'),
    Input('background', 'value'),
    Input('weather-checklist', 'value'),
    Input('traffic-checklist', 'value'),
    Input('table-entries', 'value'),
    Input('indicator-graphic', 'clickData'))
@cache.memoize(timeout=3600 * 24)  # in seconds
def update_graph(variable_to_show, background, weather_checklist, traffic, table_entries, click_data):
    if variable_to_show == "Climbing Time (s)":
        df_copy = df_climb.copy()
    elif variable_to_show == "Walking Time, indoors (s)":
        df_copy = df_walk.copy()
    else:
        df_copy = df.copy()

    ## Hide filters if not relevant - maybe will reuse
    if (variable_to_show == 'Response Time (s)') or (variable_to_show == "Travel Time (s)"):
        style = {'display': 'none'}
        weather_options = [{'label': 'Sunny', 'value': 'sunny'},  # factor = 1 for travel time
                           {'label': 'Rainy️', 'value': 'rainy'},  # factor = 1 / 0.846
                           {'label': 'Snowy️', 'value': 'snowy'},
                           {'label': 'Heavy Snow️', 'value': 'heavy snow'},  # factor = 1 / 0.769
                           {'label': 'Icy️', 'value': 'icy'},
                           {'label': 'Low visibility️', 'value': 'low visibility'}]
        traffic_options = [{'label': '️No traffic', 'value': 'no-traffic'},  # factor = 1
                           {'label': 'Day time', 'value': 'normal-day'},  # factor = 1 / 0.846
                           {'label': 'Late evening', 'value': 'normal-evening'},  # factor = 1 / 0.846
                           {'label': 'Rush hour', 'value': 'busy'}]
    else:
        style = {'display': 'inline-block'}
        weather_options = [{'label': 'Sunny', 'disabled': 'True'},  # factor = 1 for travel time
                           {'label': 'Rainy️', 'disabled': 'True'},  # factor = 1 / 0.846
                           {'label': 'Snowy️', 'disabled': 'True'},
                           {'label': 'Heavy Snow️', 'disabled': 'True'},  # factor = 1 / 0.769
                           {'label': 'Icy️', 'disabled': 'True'},
                           {'label': 'Low visibility️', 'disabled': 'True'}]
        traffic_options = [{'label': '️No traffic', 'disabled': 'True'},  # factor = 1
                           {'label': 'Day time', 'disabled': 'True'},  # factor = 1 / 0.846
                           {'label': 'Late evening', 'disabled': 'True'},  # factor = 1 / 0.846
                           {'label': 'Rush hour', 'disabled': 'busy'}]

    ## Select weather
    if weather_checklist == 'rainy':
        df_copy['Travel Time (s)'] = df_copy['Travel Time (s)'] * RAINY_DELAY_FACTOR
    elif weather_checklist == 'snowy':
        df_copy['Travel Time (s)'] = df_copy['Travel Time (s)'] * SNOWY_FACTOR
    elif weather_checklist == 'heavy snow':
        df_copy['Travel Time (s)'] = df_copy['Travel Time (s)'] * HEAVY_SNOW_DELAY_FACTOR
    elif weather_checklist == 'icy':
        df_copy['Travel Time (s)'] = df_copy['Travel Time (s)'] * ICY_DELAY_FACTOR
    elif weather_checklist == 'low visibility':
        df_copy['Travel Time (s)'] = df_copy['Travel Time (s)'] * LOW_VISIBILITY_DARK_FACTOR

    ## Select traffic
    if traffic == 'busy':
        df_copy['Travel Time (s)'] = df_copy['Travel Time (s)'] * BUSY_DELAY_FACTOR
    elif traffic == 'no-traffic':
        df_copy['Travel Time (s)'] = df_copy['Travel Time (s)']
    elif traffic == 'normal-day':
        df_copy['Travel Time (s)'] = df_copy['Travel Time (s)'] * AVG_DAY_TRAFFIC_FACTOR
    elif traffic == 'normal-evening':
        df_copy['Travel Time (s)'] = df_copy['Travel Time (s)'] * AVG_EVENING_TRAFFIC_FACTOR

    ## Recalculate and reformat Travel/Response time
    df_copy['Response Time (s)'] = df_copy['Notification Time (s)'] + df_copy['Travel Time (s)'] + df_copy[
        'Post Arrival Time (s)']

    df_copy['Response Time (min)'] = df_copy.apply(lambda x: format_time(x['Response Time (s)']), axis=1)
    df_copy['Travel Time (min)'] = df_copy.apply(lambda x: format_time(x['Travel Time (s)']), axis=1)

    # n_largest = int(total_samples * percentile_limit / 100)
    n_largest = int(total_samples)
    filtered_df = df_copy.nlargest(n_largest, variable_to_show)

    #  Update map
    hover_data = {
        'Fire Station': True,
        'lat': False,
        'lon': False,
        variable_to_show: False
    }
    for indicator in available_indicators:
        hover_data[indicator.replace('(s)', '(min)')] = True

    fig = px.scatter_mapbox(filtered_df, lat="lat", lon="lon", hover_name="Address",
                            hover_data=hover_data,
                            color_discrete_sequence=["fuchsia"], zoom=10.8, color=variable_to_show,
                            height=800,
                            center=dict(lat=52.370216, lon=4.895168),

                            )  # TODO: now manually set height, but should size to fit window

    # configure background map style: Options are: 'open-street-map', 'white-bg', 'carto-positron', 'carto-darkmatter', 'stamen- terrain', 'stamen-toner', 'stamen-watercolor'.
    if background == 'black':
        fig.update_layout(mapbox_style="carto-darkmatter")
    elif background == 'streetmap':
        fig.update_layout(mapbox_style="open-street-map")

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.update_yaxes(automargin=True)
    #    fig.update_layout(uirevision=percentile_limit)  # this prevents zoom from resetting
    # fig.update_layout(legend_title="Legend Title")

    # add firestations
    fig.add_scattermapbox(lat=df_fire_stations['lat'], lon=df_fire_stations['lon'], mode='markers',
                          hovertemplate='<b>%{text}</b>',
                          text='<b> Fire Station: ' + df_fire_stations['name'] + '</b>' +
                               '<br><br><i>Avgerage response time</i>: ' + df_fire_stations['formatted_mean_resp'] +
                               '<br><i>Response time standard deviation</i>: ' + df_fire_stations['formatted_stdev'] +
                               '<br><i>Max response time</i>: ' + df_fire_stations['formatted_max_time'] +
                               ', ' + df_fire_stations['max_response_time_address'] +
                               '<extra></extra>',
                          showlegend=False,

                          marker=dict(symbol='circle', size=15,
                                      color='white'))  # @TODO: different symbols seem not supported, but I would like to use something like a flame symbol

    # draw district polygons
    fig.add_scattermapbox(
        mode='lines',
        line={'color': 'white', 'width': 1},
        # fill="toself", # seems to block out all other stuff no matter the opacity
        fill="none",
        fillcolor="white",
        opacity=1,
        lon=df_mapboxes['lons'], lat=df_mapboxes['lats'],
        showlegend=False,
        hoverinfo="skip"
    )

    max_val = df_copy[variable_to_show].quantile(
        0.995)  ## Taking the 99.5 quantile, because of the outliers in the response times
    min_val = df[variable_to_show].min()
    fig.update_coloraxes(colorscale='Jet', cmin=min_val, cmax=max_val)

    if click_data is not None and 'hovertext' in click_data['points'][0]:
        name = click_data['points'][0]['hovertext']
        clicked_row = df[df['Address'] == name]
        if len(clicked_row) >= 1:

            fig.add_scattermapbox(
                mode='lines',
                line={'color': 'white', 'width': 2},
                fill="none",
                opacity=0.95,
                lon=df_copy['route_lons'], lat=df['route_lats'],
                showlegend=False,
                hoverinfo="skip"
            )

    #  Update table
    export_df_full = filtered_df[['Address', variable_to_show]]
    export_df = export_df_full.nlargest(table_entries, variable_to_show)
    export_df = export_df.round(2)
    data = export_df.to_dict("records")

    if table_entries != len(filtered_df):
        fig = px.scatter_mapbox(filtered_df[:table_entries], lat="lat", lon="lon", hover_name="Address",
                                hover_data=hover_data,
                                color_discrete_sequence=["fuchsia"], zoom=10.8, color=variable_to_show,
                                height=800,
                                center=dict(lat=52.370216, lon=4.895168),

                                )  # TODO: now manually set height, but should size to fit window
        # configure background map style: Options are: 'open-street-map', 'white-bg', 'carto-positron', 'carto-darkmatter', 'stamen- terrain', 'stamen-toner', 'stamen-watercolor'.
        if background == 'black':
            fig.update_layout(mapbox_style="carto-darkmatter")
        elif background == 'streetmap':
            fig.update_layout(mapbox_style="open-street-map")

        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        fig.update_yaxes(automargin=True)
        #       fig.update_layout(uirevision=percentile_limit)  # this prevents zoom from resetting
        # fig.update_layout(legend_title="Legend Title")

        # add firestations
        fig.add_scattermapbox(lat=df_fire_stations['lat'], lon=df_fire_stations['lon'], mode='markers',
                              hovertemplate='<b>%{text}</b>',
                              text='<b>' + df_fire_stations['name'] + ' Fire Station: </b>' +
                                   '<br><br><i>Avgerage response time</i>: ' + df_fire_stations['formatted_mean_resp'] +
                                   '<br><i>Response time standard deviation</i>: ' + df_fire_stations[
                                       'formatted_stdev'] +
                                   '<br><i>Max response time</i>: ' + df_fire_stations['formatted_max_time'] +
                                   ', ' + df_fire_stations['max_response_time_address'] +
                                   '<extra></extra>',
                              showlegend=False,

                              marker=dict(symbol='circle', size=15,
                                          color='white'))  # @TODO: different symbols seem not supported, but I would like to use something like a flame symbol

        # draw district polygons
        fig.add_scattermapbox(
            mode='lines',
            line={'color': 'white', 'width': 1},
            # fill="toself", # seems to block out all other stuff no matter the opacity
            fill="none",
            fillcolor="gray",
            opacity=1,
            lon=df_mapboxes['lons'], lat=df_mapboxes['lats'],
            showlegend=False,
            hoverinfo="skip"
        )

        max_val = df_copy[variable_to_show].quantile(
            0.995)  ## Taking the 99.5 quantile, because of the outliers in the response times
        min_val = df[variable_to_show].min()
        fig.update_coloraxes(colorscale='Jet', cmin=min_val, cmax=max_val)

    columns = [{"name": i, "id": i} for i in export_df.columns]

    return fig, data, columns, style, weather_options, traffic_options


if __name__ == '__main__':
    app.run_server(debug=True, port=8051)


@app.callback(
    Output('instructions-hidden', 'style'),
    Input('toggle', 'value'))
def toggle_container(toggle_value):
    if toggle_value == 'Show':
        return {'display': 'block'}
    else:
        return {'display': 'none'}
    
    
    
## TODOs
# round numbers in legend
# fix size of divs as portions of the screen instead of number of pixels

# optional
# add dutch/english filter
# add page for table with filtering options
# update table on zoom
# add fire icon for properties as shown in table


