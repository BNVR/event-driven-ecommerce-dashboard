from google.cloud import bigquery
import pandas as pd

# Initialize BigQuery client
client = bigquery.Client()

# Read processed events
df = pd.read_csv("data/processed_events.csv")

# project ID
project_id = "event-data-pipeline-488104"

# Target table
table_id = f"{project_id}.event_pipeline.processed_events"

# Load job configuration
job_config = bigquery.LoadJobConfig(
    write_disposition="WRITE_APPEND",  # Append new data
    autodetect=True
)

# Load data
job = client.load_table_from_dataframe(df, table_id, job_config=job_config)

job.result()

print(f"Loaded {job.output_rows} rows into BigQuery.")