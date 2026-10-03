select
    trip_id,
    cast(event_ts as timestamp) as event_ts,
    cast(service_date as date) as service_date,
    route_name,
    vehicle_id,
    delay_minutes,
    passengers,
    capacity,
    weather,
    cancelled,
    occupancy_rate,
    on_time_flag
from clean_trips

