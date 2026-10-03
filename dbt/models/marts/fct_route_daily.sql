select
    service_date,
    route_name,
    count(*) as scheduled_trips,
    sum(cast(cancelled as integer)) as cancelled_trips,
    round(avg(delay_minutes), 2) as average_delay_minutes,
    round(100 * avg(on_time_flag), 2) as on_time_pct,
    sum(passengers) as passengers,
    round(100 * avg(occupancy_rate), 2) as average_occupancy_pct
from {{ ref('stg_trips') }}
group by 1, 2

