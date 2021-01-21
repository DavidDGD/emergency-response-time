import ast
from turfpy.measurement import boolean_point_in_polygon
# from geojson import Feature
import pandas as pd
from geojson import Polygon, Feature, MultiPolygon
# from shapely.geometry import Point, Polygon
from shapely.geometry import Point

fire_stations = pd.read_csv('Model/Data/firestations.csv')

fire_stations['polygon'] = fire_stations['area'].apply(ast.literal_eval)

polygons = {}
for i, station in fire_stations.iterrows():

    polygons[station['LOC_NAAM']] = Polygon([station['polygon']])

def match(properties):
    print('Matching properties to fire stations \n--This may take a minute')
    # properties['fire_station'] = is_inside_polygon(properties)

    properties['firestation_name'] = properties.apply(lambda x: get_station(x['lat'], x['lon']), axis=1)

    print('Finished Matching properties\n\n')
    return properties


def get_station(lat, lon):
    point = Feature(geometry=Point((lat, lon)))

    for name, polygon in polygons.items():
        # print(polygon)
        if boolean_point_in_polygon(point, polygon):
            return name

    return 'no_station'


# def is_inside_polygon(dataset):
#     global result
#     result = []
#     for a, b in zip(dataset.lat, dataset.lon):
#         point = Feature(geometry=Point((a, b)))
#
#         for name, polygon in polygons.items():
#             # print(polygon)
#             if boolean_point_in_polygon(point, polygon):
#                 result.append(name)
#         result.append('no_station')
#
#     return result
#
# commercial_properties.fire_station[(commercial_properties.fire_station == 'no_station') & (
#     commercial_properties['subsubcity name'] == 'Bedrijventerrein Sloterdijk')] = 'GBA/GALWIN'
# commercial_properties.fire_station[(commercial_properties.fire_station == 'no_station') & (
#     commercial_properties['subsubcity name'] == 'Westelijk Havengebied')] = 'GBA/GALWIN'
#
# commercial_properties[commercial_properties.fire_station == 'no_station']

# def match_fire_station(row):
#     for a, station in fire_stations.iterrows():
#         return station['LOC_NAAM'], station['latitude'], station['longitude']
#
# # # @TODO:fix this
# #     point = Point(row['lat'], row['lon'])
# #
# #     for i, station in fire_stations.iterrows():
# #         print(len(station['area']))
# #         polygon = Polygon(list(station['area']))
# #         print(type(polygon))
# #         exit()
# #
# #         if polygon.contains(point):
# #             print('station found')
# #             return station['LOC_NAAM'], station['latitude'], station['longitude']
# #
# #         print('No station found')
# #
# #     return 0, 0, 0
#
#
# def match(df):
#
#
#     df['firestation_name'], df['firestation_lat'], df['firestation_lon'] = zip(
#         *df.apply(lambda row: match_fire_station(row), axis=1))
#
#     return df
