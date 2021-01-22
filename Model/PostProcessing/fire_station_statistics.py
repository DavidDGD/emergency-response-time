import pandas as pd
import math as m


def get_firestation_statistics():
    stations = pd.read_csv('Model/Data/firestations.csv')

    df = pd.read_csv('Model/Data/main.csv')

    rows = []
    for i, station in stations.iterrows():
        subdf = df.loc[df['firestation_name'] == station['LOC_NAAM']]
        if (len(subdf) <= 0):
            continue

        mean_response_time = subdf['Response Time (s)'].mean()
        stdev_response_time = subdf['Response Time (s)'].std()
        max_response_time = subdf['Response Time (s)'].max()
        formatted_mean_resp = str(m.floor(mean_response_time / 60)) + 'm ' + str(
            round((mean_response_time % 1) * 60)) + 's'
        formatted_stdev = str(m.floor(stdev_response_time / 60)) + 'm ' + str(
            round((stdev_response_time % 1) * 60)) + 's'
        formatted_max_time = str(m.floor(max_response_time / 60)) + 'm ' + str(
            round((max_response_time % 1) * 60)) + 's'
        max_response_time_address = subdf.loc[subdf['Response Time (s)'] == max_response_time].iloc[0]['Address']

        print(mean_response_time, formatted_mean_resp)

        rows.append(
            [station['LOC_NAAM'], station['latitude'], station['longitude'], round(mean_response_time, 1),
             round(stdev_response_time, 1),
             round(max_response_time, 1), max_response_time_address, formatted_mean_resp, formatted_stdev,
             formatted_max_time])

    to_save = pd.DataFrame(rows,
                           columns=['LOC_NAAM', 'latitude', 'longitude', 'mean_response_time', 'response_time_stdev',
                                    'max_response_time',
                                    'max_response_time_address', 'formatted_mean_resp', 'formatted_stdev',
                                    'formatted_max_time'])
    to_save.rename({'LOC_NAAM': 'name', 'latitude': 'lat', 'longitude': 'lon'}, inplace=True)

    to_save.to_csv('Model/Data/fire_stations_with_statistics.csv', index=False)