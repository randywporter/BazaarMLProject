'''
Machine learning and data analytics project
Collects data from the Hypixel skyblock Bazaar
and then is trained on good flips in order to,
eventually, recommend good flips within a dashboard
interface, probably a web interface.
'''

import requests
import json

TEMP_API_KEY = "987e1ef7-c4f1-4452-b764-215167242fd5"
API_URL = "https://api.hypixel.net/v2/skyblock/bazaar"


print("hello world!")

def fetch_bz_data():
    print("getting data...")
    headers = {"API-Key": TEMP_API_KEY}
    resp = requests.get(API_URL, headers=headers, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    if not data.get("success", False):
        print("issue with getting data!")
        raise RuntimeError(f"Hypixel API returned success=false: {json.dumps(data)[:500]}")

    print("data got!")

    return data

def extract_products(data):
    print("extracting products...")
    products = data.get("products", {})
    if not products:
        print("issue getting products!")
        raise RuntimeError(f"Hypixel API returned no products: {json.dumps(data)[:500]}")
    print("products got!")
    return products

# THIS IS FOR SPECIFIC CHECKS ON ONE ITEM
# in reality, a 'for item in dict' loop will probably
# be used, instead of looking at specific, user defined
# single items
def extract_product(products, item_id):
    print("extracting product...")
    product = products.get(item_id)
    if not product:
        print("issue getting product!")
        raise RuntimeError(f"Hypixel API returned no product: {item_id}")
    print("product got!")
    return product

def format_product_quick_status(product):
    print("formatting product...")
    quick_status = product.get("quick_status", {})
    if not quick_status:
        print("issue getting quick status!")
        raise RuntimeError(f"Hypixel API returned no quick status: {json.dumps(product)[:500]}")
    print("quick status got! formatting...")
    return {
        "productId": quick_status.get("productId"),
        "sellPrice": quick_status.get("sellPrice"),
        "buyPrice": quick_status.get("buyPrice"),
        "sellVolume": quick_status.get("sellVolume"),
        "buyVolume": quick_status.get("buyVolume"),
        "sellOrders": quick_status.get("sellOrders"),
        "buyOrders": quick_status.get("buyOrders"),
        "buyMovingWeek": quick_status.get("buyMovingWeek"),
        "sellMovingWeek": quick_status.get("sellMovingWeek"),
    }

def clean_product_data(product_quick_status):
    print("cleaning product data...")
    print('''
        Positive deltaPrice means that the insta Buy is greater than insta Sell (rarely ever NOT the case).
        Positive deltaVolume means that there are more total items in orders to sell than there are items in orders to
            buy.
        Positive deltaOrders means there are more orders to buy a number of items than to sell a number of items.
    ''')
    return {
        "productId": product_quick_status.get("productId"),
        "sellPrice": product_quick_status.get("sellPrice"),
        "buyPrice": product_quick_status.get("buyPrice"),
        "deltaPrice": product_quick_status.get("buyPrice") - product_quick_status.get("sellPrice"),
        "sellVolume": product_quick_status.get("sellVolume"),
        "buyVolume": product_quick_status.get("buyVolume"),
        "deltaVolume": product_quick_status.get("buyVolume") - product_quick_status.get("sellVolume"),
        "sellOrders": product_quick_status.get("sellOrders"),
        "buyOrders": product_quick_status.get("buyOrders"),
        "deltaOrders": product_quick_status.get("buyOrders") - product_quick_status.get("sellOrders"),
    }

print(clean_product_data(format_product_quick_status(extract_product(extract_products(fetch_bz_data()), "ENCHANTED_DIAMOND"))))