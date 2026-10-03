# Power BI dashboard

This folder is a tested Power BI starter package containing an import-ready
analytics dataset, documented business measures, and a three-page report
blueprint. It does not claim to include a finished `.pbix` or `.pbip` report;
those binary/project artifacts must be created and saved by Power BI Desktop.

## Refresh the report data

```bash
python -m src.generate_data --rows 25000
python -m src.local_pipeline
python powerbi/export_dataset.py
```

The final command creates `powerbi/route_daily_performance.csv`. In Power BI
Desktop, choose **Get data > Text/CSV**, select that file, and name the table
`route_daily_performance`.

After building the pages below, choose **File > Save As** in Power BI Desktop.
Save as `.pbix` for the simplest portable report, or enable Power BI Project
format and save as `.pbip` if you want source-controlled report and semantic
model folders. A real PBIP contains both `.Report` and `.SemanticModel`
directories; a pointer file by itself is not a valid report.

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

Format `On-Time Performance %`, `Cancellation Rate %`, and `Average Occupancy %`
as **Percentage** with one decimal place. Format `Average Delay Minutes` as a
decimal number with one decimal place. The CSV percentage columns contain values
from 0 to 100; the DAX measures convert them to Power BI's 0-to-1 percentage scale.
