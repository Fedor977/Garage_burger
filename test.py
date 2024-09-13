import requests
from configs import *

response_2 = requests.get(f"https://joinposter.com/api/menu.getProducts?token={poster_token}")
all_products = response_2.json().get("response", [])


items_data = [{'product_id': 41, 'count': 1}]
counter = 0


for product in items_data:
    product_id =product['product_id']
    response_1 = requests.get(
        f"https://joinposter.com/api/menu.getProduct?token={poster_token}&product_id={product_id}")
    if response_1.status_code == 200:
        product_data = response_1.json().get("response")
        product_name = product_data["product_name"].rstrip()
        print(product_name)
        for product_2 in all_products:
            product_name_2 = product_2["product_name"]
            if product_name_2 == (product_name + ".") or product_name_2 == (product_name+". "):
                print(product_name_2)







