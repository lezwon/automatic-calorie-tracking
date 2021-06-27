import requests
import copy
import time
from datetime import datetime
import json
import os
from dotenv import load_dotenv

load_dotenv()


headers = {
    "Authorization": os.environ['API_KEY'],
    "Content-Length": "378",
    "Content-Type": "application/json; charset=utf-8",
    "Connection": "Keep-Alive",
    "Host": "api.healthifyme.com",
    "User-Agent": "okhttp/4.9.0",
}

params = (
    ("vc", os.environ['VC']),
    ("auth_user_id", os.environ['USER_ID']),
)

data = {
    "install_id": "162079231866135970",
    "sync_token": "1.621529742997383E9",
    "food_logs": [
        {
            "local_id": 5052,
            "server_id": -1,
            "food_id": 21519,
            "quantity": 200,
            "calorie_value": 238,
            "measure_weight": 200,
            "entry_time": "2021-05-20",
            "meal_type": "D",
            "food_measure_to_weight_map_id": 73245,
            "food_name": "Cooked Chicken Breast",
            "isdeleted": 0,
            "source": "N",
            "log_source": "0",
            "device_log_time": 1621529874,
        }
    ],
}


try:
    with open("foods.json") as file:
        FOOD_ITEMS = json.load(file)
except:
    FOOD_ITEMS = {}


def update_food_dict(food_name, data):
    with open("foods.json", "w+") as file:
        for measure in data["food_measures"]:
            if measure["measure_name_weight"] == "grams (1 gms)":
                FOOD_ITEMS[food_name] = {
                    "food_id": measure["food_id"],
                    "food_measure_to_weight_map_id": measure["measure_id"],
                    "food_name": food_name,
                    "calorie": measure["calorie"],
                }
                json.dump(FOOD_ITEMS, file)


def create_payload(food_name, weight):
    new_data = copy.deepcopy(data)
    try:
        food_data = FOOD_ITEMS[food_name]
    except KeyError:
        food_id = search_food(food_name)
        if food_id:
            food_data = fetch_details(food_id)
            if food_data:
                update_food_dict(food_name, food_data)

        food_data = FOOD_ITEMS[food_name]

    new_data["food_logs"][0].update(food_data)
    meal_type = "B"
    now = datetime.now()
    hour = now.hour

    if 7 <= hour < 11:
        meal_type = "B"
    elif 12 <= hour < 15:
        meal_type = "L"
    elif 19 <= hour < 22:
        meal_type = "D"

    new_data["food_logs"][0].update(
        {
            "quantity": int(weight),
            "calorie_value": weight * food_data["calorie"],
            "measure_weight": int(weight),
            "entry_time": now.strftime("%Y-%m-%d"),
            "meal_type": meal_type,
            "device_log_time": int(time.time()),
        }
    )
    return json.dumps(new_data)


def make_request(data):
    return requests.post(
        "https://api.healthifyme.com/api/v1/foodlog/foodlog_sync/",
        headers=headers,
        params=params,
        data=data,
    )


def log(food_name, weight):
    data = create_payload(food_name, weight)
    response = make_request(data)
    return response


def search_food(food_name):
    params = (
        ("query", food_name),
        ("meal_type", "D"),
        ("country_code", "US"),
        ("vc", "816"),
        ("auth_user_id", "17794667"),
    )

    response = requests.get(
        "https://api.healthifyme.com/search-food/api/v1/",
        headers=headers,
        params=params,
    )
    data = response.json()
    if data:
        return data[0]["food_id"]
    else:
        return None


def fetch_details(food_id):
    params = (
        ("food_id", food_id),
        ("vc", "816"),
        ("auth_user_id", "17794667"),
    )

    response = requests.get(
        "https://api.healthifyme.com/api/v2/food/details",
        headers=headers,
        params=params,
    )
    data = response.json()
    return data


if __name__ == "__main__":
    log("Veg Salad", 187)
