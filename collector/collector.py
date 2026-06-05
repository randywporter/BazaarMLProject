'''
Machine learning and data analytics project
Collects data from the Hypixel skyblock Bazaar
and then is trained on good flips in order to,
eventually, recommend good flips within a dashboard
interface, probably a web interface.
'''

import requests
import os
import time
import psycopg
import traceback

DATABASE_URL = os.environ["DATABASE_URL"]

POLL_INTERVAL = 60

API_URL = "https://api.hypixel.net/v2/skyblock/bazaar"

def get_db_connection():
    return psycopg.connect(DATABASE_URL)

def insert_snapshot(conn, product):
    cursor = conn.cursor()

    item_id = product['product_id']

    buy_summary = product.get("buy_summary", [])
    sell_summary = product.get("sell_summary", [])

    if buy_summary:
        best_buy_price = buy_summary[0]["pricePerUnit"]
    else:
        best_buy_price = None

    if sell_summary:
        best_sell_price = sell_summary[0]["pricePerUnit"]
    else:
        best_sell_price = None

    if best_buy_price and best_sell_price:
        exact_delta_price = best_buy_price - best_sell_price
    else:
        exact_delta_price = None

    quick_status = product.get('quick_status', {})

    cursor.execute(
        """
        INSERT INTO market_snapshots(
            time,
            source,
            item_id,
            buy_summary,
            sell_summary,
            exact_delta_price,
            buy_price,
            sell_price,
            delta_price,
            buy_volume,
            sell_volume,
            delta_volume,
            buy_moving_week,
            sell_moving_week,
            delta_moving_week,
            raw
        )
        VALUES (
            NOW(),
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """,
        (
            "hypixel_bazaar",
            item_id,
            psycopg.types.json.Jsonb(buy_summary),
            psycopg.types.json.Jsonb(sell_summary),
            exact_delta_price,
            quick_status["buyPrice"],
            quick_status["sellPrice"],
            (quick_status["buyPrice"] - quick_status["sellPrice"]),
            quick_status["buyVolume"],
            quick_status["sellVolume"],
            (quick_status["buyVolume"] - quick_status["sellVolume"]),
            quick_status["buyMovingWeek"],
            quick_status["sellMovingWeek"],
            (quick_status["buyMovingWeek"] - quick_status["sellMovingWeek"]),
            psycopg.types.json.Jsonb(product)
        ))

def collect():
    print("collecting data...")

    conn = get_db_connection()

    while True:
        try:
            response = requests.get(API_URL, timeout=30)

            response.raise_for_status()

            data = response.json()

            products = data["products"]

            count = 0

            for item_id, product in products.items():
                product["product_id"] = item_id
                insert_snapshot(conn, product)
                count += 1

            conn.commit()

            print(f"collected {count} products")


        except Exception:

            traceback.print_exc()

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    collect()
