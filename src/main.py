import time
from data_fetcher import fetch_data  # Your existing fetcher
from database import DatabaseManager

db = DatabaseManager()

def run_pipeline():
    print("Pipeline started, ctrl+C to stop.")
    while True:
        try:
            data = fetch_data()[0]
            if data and data.get('success'):
                db.insert_batch(data['products'])
                print(f"[{time.ctime()}] Successfully logged {len(data['products'])} items.")

            # Sleep for 60s (Bazaar Refresh Rate)
            time.sleep(60)

        except Exception as e:
            print(f"Error encountered: {e}. Retrying in 10s...")
            time.sleep(10)


if __name__ == "__main__":
    run_pipeline()