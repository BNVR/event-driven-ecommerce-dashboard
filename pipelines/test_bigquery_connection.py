from google.cloud import bigquery

client = bigquery.Client()

print("Connected to BigQuery successfully!")
print("Project:", client.project)