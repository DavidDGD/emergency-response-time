from Calculators.CalculatorInterface import CalculatorInterface
import pandas as pd  ## 1.1.5
import numpy as np  ## 1.19.4
# import matplotlib.pyplot as plt
import networkx as nx  ## 2.5
# import geopandas as gpd    ## 0.8.1
# import os
import osmnx as ox
import math as m
import pickle


class TravelTimeCalculator(CalculatorInterface):
    with open('Model/Data/calamity_roads', 'rb') as fp:
        calamity_roads = pickle.load(fp)
    CALAMITY_ROAD_SPEED_INCREASE = 25  # km/hour
    CALAMITY_ROAD_STREET_NAMES = calamity_roads

    def __init__(self, properties):
        self.properties = properties

        print('Gathering data from OSM \n---This may take a while')
        amsterdam = ox.graph_from_bbox(52.216863, 52.448686, 5.082550, 4.671936, network_type='drive_service')

        print('Converting OSM network')
        self.new_g, self.edges_df = self.prepare_graph(amsterdam)

        self.firestations = pd.read_csv('Model/Data/firestations.csv')
        self.fire_districts = self.firestations['LOC_NAAM'].tolist()

    def prepare_graph(self, g):
        """Takes in a graph, add speed and travel times, updates travel times per edge
            Input:
                graph
            Output:
                graph
        """
        new_g = ox.add_edge_speeds(g)
        new_g = ox.add_edge_bearings(new_g)
        edges_g = ox.graph_to_gdfs(new_g, nodes=False)  # Graph edges DF
        nodes_g = ox.graph_to_gdfs(new_g, edges=False)  # Graph nodes DF
        edges_g_updated = self.update_speed_in_edges(edges_g)  # change the speed for calamity roads
        edges_g_updated['travel_time2'] = edges_g_updated.apply(lambda x: self.travel_time_recalc(x), axis=1)
        new_graph = ox.graph_from_gdfs(nodes_g, edges_g_updated)  ## Putting the DF back to the graph

        return new_graph, edges_g_updated

    def increase_calamity_routes_speed(self, row):
        if row['name'] in self.CALAMITY_ROAD_STREET_NAMES and row['speed_kph'] != 0:
            return row['speed_kph'] + self.CALAMITY_ROAD_SPEED_INCREASE

        return row['speed_kph']  # remove 2

    def update_speed_in_edges(self, edges):
        edges['updated_speed'] = edges.apply(lambda row: self.increase_calamity_routes_speed(row), axis=1)

        return edges

    def travel_time_recalc(self, df):
        """
        This function calculated the edge travel time based on its length, and speed allowed there.
        Deceleration is considered to be a mirrored version of acceleration.

        The base of this is formula Distance = Speed*time + acceleration*time^2/2
        a = 0.889m/s^2   (Fire truck average acceleration 0.9m/s^2. https://www.rosenbauer.com/en/int/rosenbauer-world/vehicles/arff-vehicles/the-new-panther)
        u = 2.78m/s   (assuming fire truck always at 10km/h speed when reaching a turn of right after the turn
                      (the start and end node also uses the initial speed, which is not correct, but the expected
                      difference is likely to be marginal).

        Inputs:
            dataframe (Pandas or Geopandas)
        Outputs:
            travel time (float)
        """

        a = 0.889
        u = 2.78
        speed_kph = df['updated_speed']
        if speed_kph <= 100:  ##Assuming trucks can speed 10% above the speed limit
            speed_kph *= 1.1

        length = df['length']
        speed_ms_full = speed_kph * 1000 / 3600  ## what is the max speed of the truck in the selected edge. Using speed_kph, because maxseepd is not always available.
        speed_ms_acc = speed_ms_full - u  ## speed difference available for acceleration/decceleration, assuming truck starts from u km/h speed
        t = speed_ms_acc / a  ## how much time it takes to accelerate until the maximum speed
        d = u * t + a * m.pow(t,
                              2) / 2  ## what is the distance that can be covered with the truck starting with u km/h reaching maximum speed for edge
        travel_time = 0

        if length > 2 * d:  ## if the edge is longer than the distance where the truck will accelerate and decellerate, then
            travel_time = ((
                                   length - 2 * d) / speed_ms_full) + 2 * t  ## travel time is acceleration and decceleration times + traveltime with the max speed
        else:
            travel_time = 2 * (m.sqrt((length / a) + m.pow(u / a,
                                                           2)) - u / a)  ##doubling the time for acceleration/deceleration, when the turck doesn't reach max speed
        return travel_time

    def calculate(self):

        self.properties['travel_time'] = 0  # @TODO

        # Calculate traveltimes for each route, save the lengh, travel time and route
        main_df_cols = self.properties.columns.tolist()
        main_df_cols.extend(['route_length', 'travel_time_raw', 'route'])
        main_df = pd.DataFrame(columns=main_df_cols)

        print('Calculating initial travel times')
        for fire_station in self.fire_districts:
            district = self.properties[self.properties['firestation_name'] == fire_station]
            station_row = self.firestations[self.firestations['LOC_NAAM'] == fire_station].squeeze()
            district_station = (station_row['latitude'], station_row['longitude'])
            main_df = self.travel_time_for_district(district_station, district, self.new_g, 'travel_time2', main_df)

        # Since each edge has a separate travel time, which assumes a slow down and speed up, it distors the travelling time on
        # those roads, that are generally straight but consist of many edges (for example, a main rroad with many side roads).
        # The following functions take the route of each addressand checks if the subsequent edges belong to the same road, if so,
        # they are grouped together, and travel time for them is recalulated (essentially, the unnecessary slow downs are removed).

        # Create a cropped copy of edges dataframe to work with
        print('Detecting corners')
        edges_to_upd = self.edges_df.copy()
        edges_pd = pd.DataFrame(edges_to_upd[['name', 'length', 'bearing', 'u', 'v', 'updated_speed', 'travel_time2']])

        # Some edges do not have a bearing. In this case a unique value is assigned to such edge bearing, to treat it as a unique edge, that doesn't belong to any straight road (edges without bearing will always take in acceleration/ decelaration into account).
        edges_pd['bearing'].isnull().sum()
        nan_index = edges_pd[edges_pd['bearing'].isnull()].index
        edges_pd.loc[
            nan_index, 'bearing'] = nan_index.to_series() * 11  ## multiplied by 11 so that for sure no edge would be within +-10 range from each other in respect to bearing

        # removing unsuccessful calculations
        main_df_notnull = main_df[main_df['route'].notnull()].copy()
        main_df_notnull['route'].apply(lambda cell: pd.Series(self.adjust_travel_time(cell, edges_pd), index=['travel_time']))

        return main_df_notnull

        # # Split the addresses DF to many smaller ones to ease up calculation
        # n = 54
        # dfs = np.array_split(main_df_notnull, n)
        #
        # # Recalculate the travel times and save to csv
        # for df in dfs:
        #     new_df = pd.concat((
        #         df,
        #         df['route'].apply(
        #             lambda cell: pd.Series(self.adjust_travel_time(cell, edges_pd), index=['travel_time']))), axis=1)
        #     with open('amsterdam-properties-response-time.csv', 'a', encoding='utf-8') as f:
        #         new_df.to_csv(f, header=f.tell() == 0, index=False)
        #
        # print('Finished travel time calculations')
        # print(new_df.columns.tolist())
        # print(new_df.head())
        # exit()
        # return new_df

        # return self.properties

    def travel_time_for_district(self, station, district, G, weight_column, main_df):
        ## station - tuple of firestatin coordinates
        ## district - dataframe with district buildings' details. must have lat lon columns
        ## G - city grapgh

        source = ox.get_nearest_node(G, station)
        district['nearest_node'] = ''
        district['nearest_node'] = district.apply(self.nearest_node, args=(G,), axis=1)
        new_df = pd.concat((
            district,
            district['nearest_node'].apply(
                lambda cell: pd.Series(self.get_travel_time(G, source, cell, weight_column),
                                       index=['route_length', 'travel_time_raw', 'route']))), axis=1)
        # lambda cell: pd.Series(get_travel_time(G,source,cell,weight_column,edges_g), index=['route_length','travel_time','travel_time_adjusted','route']))), axis = 1)
        new_df.drop(['nearest_node'], axis=1, inplace=True)
        main_df = main_df.append(new_df)

        return main_df

    def nearest_node(self, df, G):
        ## df - district addresses for wchich the nearest node is needed
        ## G - city graph
        return ox.get_nearest_node(G, (df['lat'], df['lon']))

    def get_travel_time(self, G, source, destination, weight_column):
        ## G - city grapgh
        ## source - firestation address
        ## district - district with the addresses
        try:
            route = nx.shortest_path(G, source, destination, weight=weight_column)
        except:
            route_length = None
            route_duration = None
            return route_length, route_duration, np.nan
        else:
            route_length = int(sum(ox.utils_graph.get_route_edge_attributes(G, route, 'length')))
            # route_duration_adjusted = adjust_travel_time(route,edges_g)
            route_duration = int(sum(ox.utils_graph.get_route_edge_attributes(G, route, weight_column)))
            return route_length, route_duration, route  # route_duration_adjusted,

    def adjust_travel_time(self, route, edges_df):

        '''
        Function takes the route and adjusts its traveltime based on how many of the edges
        are actually likely belonging to the same road.

        If the road has less than 3 edges, travel time or a sum of two edges is returned without recalculation.
        Else, the function checks if the subsequent edge bearing is within +-10, and if the speed allowed on that
        edge is within the range of the current edge speed +-3km/h. (Intially the street name was ment to be used,
        but there are too many NaN streets.). If two subsequent edges have similar bearing and speed, they get
        the same grouping factor (the street name and bearing first digit. If street name was NaN, grouping factor is
        speed on that edge and bearing's first digit.

        Input:
            route (list)
            edges_df (pandas dataframe), containing the lenght, speed, bearing, u and v IDs
        Output:
            travel_ time(float)
        '''

        no_nodes = len(route)

        edges_subset = edges_df[(edges_df['u'].isin(route)) & (edges_df['v'].isin(route))]
        edges = pd.DataFrame(columns=edges_subset.columns)
        for i in range(0, no_nodes - 1):
            ith_edge = edges_subset[(edges_subset['u'] == route[i]) & (edges_subset['v'] == route[i + 1])]
            edges = edges.append(ith_edge)

        if no_nodes <= 2:
            return edges['travel_time2'].sum()
        else:
            edges = edges[['name', 'length', 'updated_speed', 'bearing']].copy().reset_index(drop=True)
            edges['grouping_factor'] = ''
            end_index = edges.shape[0] - 1

            for i in range(0, end_index + 1):
                if str(edges.iloc[i, 0]) == 'nan':
                    name = str(edges.iloc[i, 2])
                else:
                    name = str(edges.iloc[i, 0])
                condition1 = (i == 0) and ((edges.iloc[i, 3] >= edges.iloc[i + 1, 3] - 10) and (
                        edges.iloc[i, 3] <= edges.iloc[i + 1, 3] + 10) and (
                                                   edges.iloc[i, 2] <= edges.iloc[i + 1, 2] + 3) and (
                                                   edges.iloc[i, 2] >= edges.iloc[i + 1, 2] - 3))
                condition2 = (i == end_index) and (((edges.iloc[i, 3] >= edges.iloc[i - 1, 3] - 10) or (
                        edges.iloc[i, 3] <= edges.iloc[i - 1, 3] + 10)) and (
                                                           (edges.iloc[i, 2] <= edges.iloc[i - 1, 2] + 3) and (
                                                           edges.iloc[i, 2] >= edges.iloc[i - 1, 2] - 3)))
                condition3 = ((i > 0) and (i < end_index)) and (((edges.iloc[i, 3] > edges.iloc[i + 1, 3] - 10) and (
                        edges.iloc[i, 3] < edges.iloc[i + 1, 3] + 10) and ((edges.iloc[i, 2] <= edges.iloc[
                    i + 1, 2] + 3) and (edges.iloc[i, 2] >= edges.iloc[i + 1, 2] - 3)))
                                                                or ((edges.iloc[i, 3] >
                                                                     edges.iloc[
                                                                         i - 1, 3] - 10) and (
                                                                            edges.iloc[
                                                                                i, 3] <
                                                                            edges.iloc[
                                                                                i - 1, 3] + 10) and (
                                                                            (edges.iloc[
                                                                                 i, 2] <=
                                                                             edges.iloc[
                                                                                 i - 1, 2] + 3) and (
                                                                                    edges.iloc[
                                                                                        i, 2] >=
                                                                                    edges.iloc[
                                                                                        i - 1, 2] - 3))))
                if condition1 or condition2 or condition3:
                    edges.iloc[i, 4] = name + str(m.floor(edges.iloc[i, 3] / 100.0) * 100)
                else:
                    edges.iloc[i, 4] = name + edges.iloc[i, 3].astype(str)

            edges = edges[['length', 'updated_speed', 'grouping_factor']]
            edges = edges.groupby(['grouping_factor', 'updated_speed']).sum().reset_index()
            edges['travel_time2'] = edges.apply(lambda x: self.travel_time_recalc(x), axis=1)
            travel_time = edges['travel_time2'].sum()

            return travel_time
