# Power BI dashboard

This folder contains a version-controlled Power BI project entry point, the
business measures, and an import-ready analytics dataset.

## Refresh the report data

```bash
python -m src.generate_data --rows 25000
python -m src.local_pipeline
python powerbi/export_dataset.py
```

The final command creates `powerbi/route_daily_performance.csv`. In Power BI
Desktop, choose **Get data > Text/CSV**, select that file, and name the table
`route_daily_performance`.

## Report layout

### Page 1: Network overview

- KPI cards: Total Passengers, On-Time Performance %, Average Delay Minutes,
  Cancellation Rate %, and Average Occupancy %.
- Line chart: `service_date` against `On-Time Performance %`.
- Bar chart: `route_name` against `Total Passengers`.

### Page 2: Route reliability

- Matrix: route, scheduled trips, cancelled trips, average delay, and on-time percentage.
- Bar chart sorted by the lowest on-time percentage to surface problem routes.
- Date and route slicers.

### Page 3: Capacity utilization

- Scatter chart: Average Occupancy % against Average Delay Minutes by route.
- Conditional formatting: red above 90% occupancy, amber above 75%, green otherwise.

The measures in `measures.dax` are ready to paste into Power BI. The report is
deliberately output-focused; an input form would not add value to this analytics
use case.
