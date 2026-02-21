import pandas as pd
import os

RAW_PATH = "data/raw_events.csv"
PROCESSED_PATH = "data/processed_events.csv"

def load_raw_events():
    return pd.read_csv(RAW_PATH)

def load_processed_events():
    if os.path.exists(PROCESSED_PATH):
        return pd.read_csv(PROCESSED_PATH)
    else:
        return pd.DataFrame()

def incremental_process():
    raw_df = load_raw_events()
    processed_df = load_processed_events()

    if processed_df.empty:
        new_events = raw_df
    else:
        new_events = raw_df[~raw_df["event_id"].isin(processed_df["event_id"])]

    if new_events.empty:
        print("No new events to process.")
        return

    # Example transformation
    new_events["event_timestamp"] = pd.to_datetime(new_events["event_timestamp"])

    # Append to processed
    final_df = pd.concat([processed_df, new_events], ignore_index=True)
    final_df.to_csv(PROCESSED_PATH, index=False)

    print(f"{len(new_events)} new events processed.")

if __name__ == "__main__":
    incremental_process()