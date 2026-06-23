# End-to-End Local Modern Data Stack — NYC Taxi Pipeline
Author: Abraham Makur Dhuor

## Project summary
This repository demonstrates a fully containerized Modern Data Stack that runs locally. The pipeline ingests NYC Yellow Taxi trip Parquet files, loads raw data into a PostgreSQL warehouse, transforms the data with dbt to produce analytics-ready models, and exposes results for BI consumption (Power BI). The entire workflow is orchestrated with Kestra so each step runs isolated inside Docker while sharing the same Docker network.

## Architecture & tech stack
- Orchestration: Kestra (runs containerized tasks)
- Ingestion: Python (pandas, pyarrow, SQLAlchemy)
- Warehouse: PostgreSQL
- Transformations: dbt (Postgres adapter)
- BI: Power BI (desktop/dashboard)
- Containers: python:3.9, dbt-postgres, postgres, etc.

## Repository layout
Assumes files are mounted into Kestra under a consistent namespace so dbt and Python can access them.

local.data.warehouse (Kestra namespace)
├── ny_taxi_models/                # dbt project root
│   ├── models/
│   │   ├── stg_taxi_trips.sql         # staging view over raw table
│   │   ├── core_passenger_revenue.sql # passenger-level revenue aggregates
│   │   └── mrt_trip_performance.sql   # tipping & trip-volume metrics
│   ├── dbt_project.yml            # dbt project configuration
│   └── .gitignore
├── profiles.yml                   # dbt connection credentials for Postgres
└── ingest_data.py                 # Python script that downloads and loads Parquet data

## Pipeline stages

1. Extract & Load (Python)
- A python:3.9 container downloads a Parquet file from the TLC Trip Record Data distribution and streams it into the `ingest_data.py` loader.
- The loader uses pandas + SQLAlchemy to chunk and write data into `yellow_taxi_trips_automated` in Postgres, handling types with pyarrow where appropriate.

2. Transform (dbt)
- A dbt-postgres container connects to the local Postgres using `profiles.yml`.
- Staging model `stg_taxi_trips` casts and normalizes raw fields.
- Downstream models (`core_passenger_revenue`, `mrt_trip_performance`) compute aggregated metrics:
  - total_trips, total_revenue, average_tip, average_tip_pct grouped by passenger_count and other dimensions.
- Models are materialized as tables in the `public` schema for BI consumption.

3. Orchestration (Kestra)
- A YAML flow defines sequential shell tasks that run the ingestion, run dbt, and optionally run checks. Each task runs its own container but joins a shared Docker network (e.g., `pg-network`) so containers can reach Postgres at `host=postgres` (or `localhost` when mapped).

## Visualization & dashboards
The dbt tables are built to be loaded directly into Power BI Desktop. Connection settings used during development:
- Host: localhost
- Port: 5432
- Database: ny_taxi
- Credentials: provided through local Docker environment variables or the mounted `profiles.yml` (for dbt).

Key dashboard insights to build:
- Average Tip % by Passenger Count — highlights generosity by group size (use "Don't summarize" for pre-aggregated values in Power BI).
- Trip Volume Curves — total trips by passenger_count and time-of-day.
- Revenue summaries and tipping behavior across boroughs / time windows.

## Screenshots (descriptions)
Below are the images included in this folder with plain-language descriptions you can use as alt text or captions.

1. image.png
   - Caption: Power BI overview dashboard.
   - Description: A landing view with KPI cards (Total Trips, Total Revenue, Average Tip %) at the top and a time series chart below showing trip volume over time. Filters (date range, passenger_count) appear on the left. This screen is intended to show executive-level metrics and quick filters.

2. image-1.png
   - Caption: Average Tip % by Passenger Count.
   - Description: A bar chart comparing average tip percentage for each passenger_count (1, 2, 3, 4+). The visualization emphasizes that the metric is calculated in dbt and should not be re-aggregated by Power BI; the "Don't summarize" rule is applied to preserve pre-computed averages.

3. image-2.png
   - Caption: Trip volume curves by passenger count.
   - Description: A multi-series line or area chart that maps total_trips across time with separate series for passenger_count buckets. Useful to spot peaks in demand and compare utilization across group sizes.

4. image-3.png
   - Caption: dbt model graph and run preview.
   - Description: dbt Cloud/Desktop or CLI results showing the model graph (staging → core models) and a small preview of the `core_passenger_revenue` table (column names, sample row counts). This screenshot demonstrates successful model runs and lineage between staging and marts.

5. image-4.png
   - Caption: Raw table preview in Postgres / ingestion verification.
   - Description: A table preview (from pgAdmin/psql or a data preview tool) showing `yellow_taxi_trips_automated` with sample rows and key columns (pickup_datetime, dropoff_datetime, passenger_count, fare_amount, tip_amount). This verifies successful ingestion and correct schemas.

## Quick run notes
- Ingest:
  - Run the loader container or run locally: `python ingest_data.py --file <path-to-parquet> --db-url "postgresql://user:pass@localhost:5432/ny_taxi"`
- dbt:
  - From the `ny_taxi_models` directory: `dbt run --profiles-dir ..`
- Kestra:
  - Deploy the flow YAML in Kestra and trigger the execution (flows run containers that call the ingestion and dbt tasks).

## Tips & troubleshooting
- Ensure the Postgres container is reachable on the same Docker network as ingestion/dbt containers.
- Use NUMERIC types in dbt models for monetary columns to avoid floating-point rounding issues.
- When connecting Power BI to the dbt-built tables, disable automatic aggregation on pre-computed metrics.

## Contact
For questions about the pipeline, reach out to the author listed at the top.
