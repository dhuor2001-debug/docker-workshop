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
@click.option(
    "--file-path",
    required=True,
    help="Path to CSV or Parquet file"
)
@click.option("--pg-user", default="root", help="Postgres user")
@click.option("--pg-pass", default="root", help="Postgres password")
@click.option("--pg-host", default="localhost", help="Postgres host")
@click.option("--pg-port", default=5432, type=int, help="Postgres port")
@click.option("--pg-db", default="ny_taxi", help="Postgres database name")
@click.option(
    "--target-table",
    default="yellow_taxi_trips",
    help="Target table name"
)
@click.option(
    "--chunksize",
    default=100000,
    type=int,
    help="CSV chunk size"
)
def main(
    file_path,
    pg_user,
    pg_pass,
    pg_host,
    pg_port,
    pg_db,
    target_table,
    chunksize,
):

    url = (
        f"postgresql://{pg_user}:{pg_pass}"
        f"@{pg_host}:{pg_port}/{pg_db}"
    )

    engine = create_engine(url)

    # PARQUET FILES
    if file_path.endswith(".parquet"):

        click.echo("Reading parquet file...")

        df = pd.read_parquet(file_path)

        click.echo(
            f"Loading {len(df):,} rows into {target_table}..."
        )

        df.to_sql(
            name=target_table,
            con=engine,
            if_exists="replace",
            index=False,
            chunksize=10000,
        )

        click.echo("Done!")
        return

    # CSV FILES
    reader = pd.read_csv(
        file_path,
        dtype=dtype,
        parse_dates=parse_dates,
        chunksize=chunksize,
    )

    first_chunk = True

    for chunk in tqdm(reader, desc="ingest"):

        for col, col_dtype in dtype.items():
            if col in chunk.columns:
                try:
                    chunk[col] = chunk[col].astype(col_dtype)
                except Exception:
                    pass

        chunk.to_sql(
            name=target_table,
            con=engine,
            if_exists="replace" if first_chunk else "append",
            index=False,
        )

        first_chunk = False

    click.echo("Done!")


if __name__ == "__main__":
    main()