from Calculators.CalculatorInterface import CalculatorInterface


class AggregatingTimeCalculator(CalculatorInterface):

    def __init__(self, properties):
        self.properties = properties

    def calculate(self):
        self.properties['response_time'] = self.properties['notification_time'] + self.properties['travel_time'] + \
                                           self.properties['post_arrival_time']
        self.properties['intervention_time'] = self.properties['response_time'] + self.properties['post_arrival_time']

        return self.properties
