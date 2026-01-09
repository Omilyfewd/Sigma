import sqlite3


class DatabaseManager:
    def __init__(self, db_path="../data/bazaar.db"):
        self.db_path = db_path
        self.con = sqlite3.connect(self.db_path)
        self.cur = self.con.cursor()
        self._setup_table()


    def _setup_table(self):
        self.cur.execute("""
                     CREATE TABLE IF NOT EXISTS bazaar_updates
                     (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         product_id TEXT,
                         buy_price REAL,
                         sell_price REAL,
                         buy_volume INTEGER,
                         sell_volume INTEGER,
                         timestamp INTEGER
                     )
                     """)

        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_product_time ON bazaar_updates (product_id, timestamp)")

    def insert_batch(self, products_dict, last_update_time=None):
        data_to_insert = []

        for p_id, info in products_dict.items():
            status = info.get('quick_status', {})
            data_to_insert.append((
                p_id,
                status.get('buyPrice'),
                status.get('sellPrice'),
                status.get('buyVolume'),
                status.get('sellVolume'),
                last_update_time
            ))

        query = "INSERT INTO bazaar_updates (product_id, buy_price, sell_price, buy_volume, sell_volume, timestamp) VALUES (?, ?, ?, ?, ?, ?)"
        self.cur.executemany(query, data_to_insert)
        self.con.commit()