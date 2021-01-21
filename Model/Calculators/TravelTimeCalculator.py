from Calculators.CalculatorInterface import CalculatorInterface
import pickle
# import osmnx as ox         ## 0.16.2
# import numpy as np         ## 1.19.4
# import networkx as nx      ## 2.5
# import math as m


class TravelTimeCalculator(CalculatorInterface):
    with open('Model/Data/calamity_roads', 'rb') as fp:
        calamity_roads = pickle.load(fp)
    CALAMITY_ROAD_SPEED_INCREASE = 25  # km/hour
    CALAMITY_ROAD_STREET_NAMES = calamity_roads


    def __init__(self, properties):
        self.properties = properties

        # self.data = self.prepare()

    def calculate(self):

        self.properties['travel_time'] = 0  # @TODO



        return self.properties
    #
    # def prepare(self):
    #     ## Load Amsterdam graph http://bboxfinder.com/#52.216863,4.671936,52.448686,5.082550
    #     amsterdam = ox.graph_from_bbox(52.216863, 52.448686, 5.082550, 4.671936, network_type='drive_service')
    #
    #     new_g = amsterdam
    #     new_g = ox.add_edge_speeds(new_g)
    #     new_g = ox.add_edge_bearings(new_g)
    #     edges_g = ox.graph_to_gdfs(new_g, nodes=False)  # Graph edges DF
    #     nodes_g = ox.graph_to_gdfs(new_g, edges=False)  # Graph nodes DF
    #
    #     edges_g_updated = self.update_speed_in_edges(edges_g)  # change the speed for calamity roads
    #     edges_g_updated['travel_time2'] = edges_g_updated.apply(lambda x: self.travel_time_recalc_1(x), axis=1)
    #     new_g1 = ox.graph_from_gdfs(nodes_g, edges_g_updated)  ## Putting the DF back to the graph
    #
    # def increase_calamity_routes_speed(self, row):
    #     if row['name'] in self.CALAMITY_ROAD_STREET_NAMES and row['speed_kph'] != 0:
    #         return row['speed_kph'] + self.CALAMITY_ROAD_SPEED_INCREASE
    #
    #     return row['speed_kph']  # remove 2
    #
    # def update_speed_in_edges(self, edges):
    #     edges['updated_speed'] = edges.apply(lambda row: self.increase_calamity_routes_speed(row), axis=1)
    #
    #     return edges
    #
    # def get_travel_time(G, source, destination, weight_column):
    #     '''
    #     Returns travel time based on the hiven weight column.
    #     Inputs:
    #         G (graph)
    #         source (tuple)
    #         destination (tuple)
    #         weight_columns (string)
    #     Outputs:
    #         route_length (float)
    #         route_duration (float)
    #         route (list)
    #     '''
    #
    #     try:
    #         route = nx.shortest_path(G, source, destination, weight=weight_column)
    #     except:
    #         route_length = None
    #         route_duration = None
    #         return route_length, route_duration, np.nan
    #     else:
    #         route_length = int(sum(ox.utils_graph.get_route_edge_attributes(G, route, 'length')))
    #         route_duration = int(sum(ox.utils_graph.get_route_edge_attributes(G, route, weight_column)))
    #         return route_length, route_duration, route
    #
    # def nearest_node(df, G):
    #     '''
    #     Returns the nearest node for the given lat/lon combination.
    #     Inputs:
    #         dataframe
    #         G (graph)
    #     Outputs:
    #         node ID
    #     '''
    #     return ox.get_nearest_node(G,(df['lat'],df['lon']))
    #
    #
    # def travel_time_for_district(station, district, G, weight_column, main_df):
    #     '''
    #     Calculates the travel times for addresses within a certain district.
    #     Input:
    #         station (tuple)
    #         district (Pandas Datarame)
    #         G (graph)
    #         weight_column (string)
    #         main_df (Pandas dataframe)
    #     Output:
    #         dataframe (Pandas)
    #     '''
    #
    #     source = ox.get_nearest_node(G, station)
    #     district['nearest_node'] = ''
    #     district['nearest_node'] = district.apply(nearest_node, args=(G,), axis=1)
    #     new_df = pd.concat((
    #         district,
    #         district['nearest_node'].apply(
    #             lambda cell: pd.Series(get_travel_time(G, source, cell, weight_column),
    #                                    index=['route_length', 'travel_time', 'route']))), axis=1)
    #     new_df.drop(['nearest_node'], axis=1, inplace=True)
    #     main_df = main_df.append(new_df)
    #     return main_df
    #
    #
    #
    #
    # def travel_time_recalc_1(df):
    #
    #     '''
    #     Function takes the route and adjusts its traveltime based on how many of the edges
    #     are actually likely belonging to the same road.
    #
    #     If the road has less than 3 edges, travel time or a sum of two edges is returned without recalculation.
    #     Else, the function checks if the subsequent edge bearing is within +-10, and if the speed allowed on that
    #     edge is within the range of the current edge speed +-3km/h. (Intially the street name was ment to be used,
    #     but there are too many NaN streets.). If two subsequent edges have similar bearing and speed, they get
    #     the same grouping factor (the street name and bearing first digit. If street name was NaN, grouping factor is
    #     speed on that edge and bearing's first digit.
    #
    #     Input:
    #         route (list)
    #         edges_df (pandas dataframe), containing the lenght, speed, bearing, u and v IDs
    #     Output:
    #         travel_ time(float)
    #     '''
    #
    #     a = 0.889
    #     u = 2.78
    #     speed_kph = df['updated_speed']  ## The updated speed - could be a calamity route
    #     regular_speed = df['speed_kph']
    #
    #     if speed_kph == regular_speed:
    #         a = 0.809
    #     else:
    #         a = 0.889  ## incentivizing the acceleration on calamity routes
    #     u = 2.78
    #
    #     length = df['length']
    #     speed_ms_full = speed_kph * 1000 / 3600  ## what is the speed of the truck in the selected edge. using speed_kph, because maxseepd is not always available.
    #     speed_ms_acc = speed_ms_full - u  ## speed difference available for acceleration/decceleration, assuming truck starts from u km/h speed
    #     t = speed_ms_acc / a  ## how much time it takes to accelerate until the maximum speed
    #     d = u * t + a * m.pow(t,
    #                           2) / 2  ## what is the distance that can be covered with the truck starting with u km/h reaching maximum speed for edge
    #     travel_time = 0
    #
    #     if length > 2 * d:  ## if the edge is longer than the distance where the truck will accelerate and decellerate, then
    #         travel_time = ((
    #                                    length - 2 * d) / speed_ms_full) + 2 * t  ## travel time is acceleration and decceleration times + traveltime with the max speed
    #     else:
    #         travel_time = 2 * (m.sqrt((length / a) + m.pow(u / a,
    #                                                        2)) - u / a)  ##doubling the time for acceleration/deceleration, when the turck doesn't reach max speed
    #     return travel_time