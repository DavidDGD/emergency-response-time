from Calculators.CalculatorInterface import CalculatorInterface
import numpy as np


class SetupTimeCalculator(CalculatorInterface):
    # estimated constants in seconds
    CLIMBING_TIME = 21  # seconds per floor
    INDOOR_WALKING_SPEED = 2.78  # meters/second = 10 km/hr
    TRAVEL_FROM_PARKING_TIME = 16 # seconds

    def __init__(self, properties):
        self.properties = properties

    def calculate(self):
        """Set up time is defined as the sum of indoor walking time, climbing time
        and the time it takes to prepare and start walking to the building once arriving
        at the property"""

        # preperation time
        self.properties['travel_from_parking_time'] = self.TRAVEL_FROM_PARKING_TIME

        # Indoor walking time: assuming square buildings, calculate time needed to reach the center
        self.properties['indoor_walking_distance'] = 0.5 * np.sqrt(
            2 * self.properties['internal_area'])  # Using Pythagoras Theorem
        self.properties['horizontal_climbing_time'] = self.properties[
                                                          'indoor_walking_distance'] / self.INDOOR_WALKING_SPEED
        self.properties['horizontal_climbing_time'] = self.properties['horizontal_climbing_time'].round(1)

        # climbing time
        self.properties['climbing_time'] = self.properties.apply(lambda x: self.get_climbing_time(x.number_of_layers),
                                                                 axis=1)
        self.properties['climbing_time'] = self.properties['climbing_time'].round(1)
        self.properties['post_arrival_time'] = self.properties['travel_from_parking_time'] + self.properties[
            'climbing_time'] + self.properties['horizontal_climbing_time']

        return self.properties

    def get_climbing_time(self, layers):
        if layers > 1.0:
            return self.CLIMBING_TIME * layers
        else:
            return 0
