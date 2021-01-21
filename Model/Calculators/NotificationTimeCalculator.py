from Calculators.CalculatorInterface import CalculatorInterface


class NotificationTimeCalculator(CalculatorInterface):
    # Constants are in seconds and were obtained from
    # https://opendata.cbs.nl/statline/#/CBS/nl/dataset/83123NED/table?ts=1608449866799
    T1 = 42
    T2 = 90
    T3 = 120

    def __init__(self, properties):
        self.properties = properties

    def calculate(self):
        """
        Notification time is defined as the sum of the dispatch time, turnout out and @TODO
        """

        self.properties['notification_time'] = self.T1 + self.T2 + self.T3

        return self.properties
