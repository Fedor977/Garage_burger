import requests
from locations import *
from configs import *
from check import *


def get_category_menu(token):
    url = F"https://joinposter.com/api/menu.getCategories?token={token}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        # Дальнейшая обработка полученных данных
        return data
    else:
        return "Ошибка при выполнении запроса. Код статуса:", response.status_code


def get_category_products(id, token):
    url = 'https://joinposter.com/api/menu.getProducts'
    params = {
        'token': token,
        'category_id': f"{id}",
    }

    response = requests.get(url, params=params)
    data = response.json()

    return data


def get_product(product_id, token):
    url = "https://joinposter.com/api/menu.getProduct"
    params = {
        'token': token,
        'product_id': f"{product_id}",
    }
    response = requests.get(url, params=params)

    data = response.json()

    return data


def post_new_order(latitude, longitude, data):
    filial = check_spot(latitude, longitude)

    # spot_id
    if filial == "filial_1_urgench":
        data["spot_id"] = 1
        url = f"https://joinposter.com/api/incomingOrders.createIncomingOrder?token={poster_token}"
        response = requests.post(url, json=data)
        return response.json()

    elif filial == "filial_2_urgench":
        data["spot_id"] = 2
        response_2 = requests.get(f"https://joinposter.com/api/menu.getProducts?token={poster_token}")
        all_products = response_2.json().get("response", [])

        items_data = data["products"]
        counter = 0

        for product in items_data:
            product_id = product['product_id']
            response_1 = requests.get(
                f"https://joinposter.com/api/menu.getProduct?token={poster_token}&product_id={product_id}")
            if response_1.status_code == 200:
                product_data = response_1.json().get("response")
                product_name = product_data["product_name"].rstrip()

                for product_2 in all_products:
                    product_name_2 = product_2["product_name"]
                    if product_name_2 == (product_name + ".") or product_name_2 == (product_name + ". "):
                        data["products"][counter]["product_id"] = product_2.get("product_id",
                                                                            "Unknown Product")
                        data["products"][counter]["product_name"] = product_2.get("product_name",
                                                                              "Unknown Product")

            counter += 1

        url = f"https://joinposter.com/api/incomingOrders.createIncomingOrder?token={poster_token}"
        response = requests.post(url, json=data)
        return response.json()

    elif filial == "filial_3_xiva":

        response_2 = requests.get(f"https://joinposter.com/api/menu.getProducts?token={poster_token_xiva}")
        all_products = response_2.json().get("response", [])

        # Use safer access methods and error handling
        counter = 0
        items_data = data["products"]
        for product in items_data:
            product_id = product["product_id"]
            response_1 = requests.get(
                f"https://joinposter.com/api/menu.getProduct?token={poster_token}&product_id={product_id}")

            if response_1.status_code == 200:
                product_data = response_1.json().get("response")
                if product_data and isinstance(product_data, dict):
                    product_name = product_data.get("product_name", "Unknown Product")

                    for product_2 in all_products:
                        product_name_2 = product_2.get("product_name", "Unknown Product")

                        if product_name == product_name_2:
                            data["products"][counter]["product_id"] = product_2.get("product_id",
                                                                                    "Unknown Product")

            counter += 1

        url = f"https://joinposter.com/api/incomingOrders.createIncomingOrder?token={poster_token_xiva}"
        response = requests.post(url, json=data)
        return response.json()


def get_category_data(token):
    data = get_category_menu(token)

    categories = [(category['category_id'], category['category_name']) for category in data['response']]

    return categories


def get_products_data(token, category_id):
    data = get_category_products(category_id, token)

    products = [(category['product_id'], category['product_name']) for category in data['response']]

    return products
