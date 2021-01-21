from PostProcessing.fire_station_statistics import get_firestation_statistics

# Store response times in minutes
def format_time(time_in_seconds):
    minutes, seconds = divmod(time_in_seconds, 60)

    formatted_seconds = str(int(round(seconds, 0)))
    if len(formatted_seconds) == 1:
        formatted_seconds = '0' + formatted_seconds

    formatted_minutes = str(int(round(minutes, 0)))
    if len(formatted_minutes) == 1:
        formatted_minutes = '0' + formatted_minutes

    return formatted_minutes + ':' + formatted_seconds

def post_process_properties(properties):
    ## add street names
    properties['street_number_additional_letter'].fillna('', inplace=True)
    properties['street_number_addition'].fillna('', inplace=True)
    properties['Address'] = properties['streetname'] + ' ' + properties['street_number'].astype(str) + ' ' + properties[
        'street_number_additional_letter'] + ' ' + properties['street_number_addition']

    ## Translate/Rename
    available_indicators = ['response_time', 'notification_time', 'travel_time', 'post_arrival_time', 'climbing_time',
                            'horizontal_climbing_time', 'fetch_water_time', 'travel_from_parking_time']
    conversion_map_dutch = {"response_time": "Reactie Tijd (s)", "notification_time": "Notificatie Tijd (s)",
                            "travel_time": "Reis Tijd (s)",
                            "climbing_time": "Klim Tijd (s)", "horizontal_climbing_time": "Loop Tijd, Binnen (s)",
                            "travel_from_parking_time": "Loop Tijd, Buiten (s)",
                            "fetch_water_time": "Water Haal Tijd (s)"}
    conversion_map_english = {"response_time": "Response Time (s)", "notification_time": "Notification Time (s)",
                              "travel_time": "Travel Time (s)",
                              "climbing_time": "Climbing Time (s)",
                              "horizontal_climbing_time": "Walking Time, indoors (s)",
                              'post_arrival_time': 'Post Arrival Time (s)',
                              "travel_from_parking_time": "Walking Time, outdoors (s)", 'fire_station': 'Fire Station'}

    properties_english = properties.rename(columns=conversion_map_english)
    # properties_dutch = properties.rename(columns=conversion_map_dutch)
    properties = properties_english

    # Format seconds to mm:ss
    for indicator in conversion_map_english.values():
        if indicator != 'Fire Station':
            properties[indicator.replace('(s)', '(min)')] = properties.apply(lambda x: format_time(x[indicator]), axis=1)

    return properties


def deduplicate(df):
    # Duplicates sorting on response_time
    df_main = df.sort_values('Response Time (s)', ascending=False).drop_duplicates(['lat', 'lon'])

    # Duplicates sorting on climbing_time
    df_climb = df.sort_values('Climbing Time (s)', ascending=False).drop_duplicates(['lat', 'lon'])

    # Duplicates sorting on horizontal_climbing_time
    df_hor_climb = df.sort_values('Walking Time, indoors (s)', ascending=False).drop_duplicates(['lat', 'lon'])

    return df_main, df_climb, df_hor_climb


def post_process(properties):
    # format values for dashboard
    properties = post_process_properties(properties)

    # remove duplicate values while keeping maximum value
    df_main, df_climb, df_hor_climb = deduplicate(properties)

    # write results to file
    write_formatted_results(df_main, df_climb, df_hor_climb)

    # Calculate statistics per fire station and write results to file
    get_firestation_statistics()


def write_formatted_results(df_main, df_climb, df_hor_climb):
    df_main.to_csv('Model/Data/main.csv', index=False)
    df_climb.to_csv('Model/Data/climb.csv', index=False)
    df_hor_climb.to_csv('Model/Data/hor_climb.csv', index=False)