from Properties.preprocess_properties import preprocess
from Properties.match_properties import match
from Calculators.TravelTimeCalculator import TravelTimeCalculator
from Calculators.NotificationTimeCalculator import NotificationTimeCalculator
from Calculators.SetupTimeCalculator import SetupTimeCalculator
from Calculators.AggregatingTimeCalculator import AggregatingTimeCalculator
from PostProcessing.post_process import post_process

# Gather all relevant properties
properties = preprocess()

# Assign fire stations to each properties
matched_properties = match(properties)

# Calculate Intervention times for each property
# Notification time
notification_timer = NotificationTimeCalculator(matched_properties)
properties = notification_timer.calculate()

# Travel Time
travel_timer = TravelTimeCalculator(properties)
properties = travel_timer.calculate()

# Post arrival time
setup_timer = SetupTimeCalculator(properties)
properties = setup_timer.calculate()

# Aggregates
aggregating_timer = AggregatingTimeCalculator(properties)
properties = aggregating_timer.calculate()

# Export results
properties.to_csv('Model/Data/results.csv', index=False)

# Post process and save data so it can be used in dashboard
formatted_results = post_process(properties)
