import click
import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm


dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64",
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
]


@click.command()
@click.option("--csv-path", default=None, help="Path or URL to the CSV file to ingest. If omitted, reads from stdin.")
@click.option("--pg-user", default="root", help="Postgres user")
@click.option("--pg-pass", default="root", help="Postgres password")
@click.option("--pg-host", default="localhost", help="Postgres host")
@click.option("--pg-port", default=5432, type=int, help="Postgres port")
@click.option("--pg-db", default="ny_taxi", help="Postgres database name")
@click.option("--target-table", default="yellow_taxi_trips", help="Target table name in Postgres")
@click.option("--chunksize", default=100000, type=int, help="Number of rows per chunk when reading CSV")
def main(csv_path, pg_user, pg_pass, pg_host, pg_port, pg_db, target_table, chunksize):
    """Simple CSV -> Postgres ingestion using pandas and SQLAlchemy.

    Example:
      python ingest_data.py --csv-path data.csv --pg-user root --pg-pass root --pg-host localhost \
          --pg-port 5432 --pg-db ny_taxi --target-table yellow_taxi_trips
    """

    engine = None
    if pg_host and pg_db:
        url = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
        try:
            engine = create_engine(url)
        except Exception as exc:
            click.echo(f"Warning: could not create engine: {exc}")

    if csv_path:
        reader = pd.read_csv(csv_path, dtype=dtype, parse_dates=parse_dates, chunksize=chunksize)
    else:
        # read from stdin
        reader = pd.read_csv(click.open_file("-"), dtype=dtype, parse_dates=parse_dates, chunksize=chunksize)

    first_chunk = True
    for chunk in tqdm(reader, desc="ingest"):
        # ensure dtypes for nullable ints
        for col, col_dtype in dtype.items():
            if col in chunk.columns:
                try:
                    chunk[col] = chunk[col].astype(col_dtype)
                except Exception:
                    pass

        if engine is not None:
            try:
                chunk.to_sql(name=target_table, con=engine, if_exists=("replace" if first_chunk else "append"), index=False)
            except Exception as exc:
                click.echo(f"Error writing chunk to Postgres: {exc}")
                raise
        else:
            # fallback: write to parquet files locally
            out_name = f"{target_table}_{int(pd.Timestamp.now().timestamp())}.parquet"
            chunk.to_parquet(out_name)
            click.echo(f"Wrote chunk to {out_name}")

        first_chunk = False


if __name__ == "__main__":
    main()