from faker import Faker
import pandas as pd
import uuid
import random
from datetime import datetime
import os

fake = Faker()

event_types = ["page_view", "add_to_cart", "checkout", "purchase"]

def generate_event():
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": random.choice(event_types),
        "event_timestamp": fake.date_time_between(
            start_date="-3y",
            end_date="now"
        ).isoformat(),  # ✅ important
        "user_id": fake.uuid4(),
        "session_id": str(uuid.uuid4()),
        "product_id": random.randint(1000, 1100),
        "price": round(random.uniform(10, 500), 2)
    }

def generate_events(n=5000):  # increase volume
    events = [generate_event() for _ in range(n)]
    return pd.DataFrame(events)

if __name__ == "__main__":
    df = generate_events(5000)

    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", "raw_events.csv")
    df.to_csv(output_path, index=False)

    print("Multi-year events generated successfully!")