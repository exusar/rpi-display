from zeroseg import get_response_json
import requests
import threading
from constants import *

temperature = 0
feelslike = 0

eur = 0
usd = 0

followers = 0


def update_weather():
    try:
        data = get_response_json(url=URL_WEATHER)
    except requests.exceptions.RequestException as e:
        print(e)
    else:
        global temperature, feelslike
        temperature = int(round(data["current_observation"]["temp_c"]))
        feelslike = int(round(float(data["current_observation"]["feelslike_c"])))
        print("Weather updated")

    threading.Timer(UPDATE_RATE_WEATHER, update_weather).start()


def update_currency():
    try:
        data_eur = get_response_json(url=URL_EUR)
        data_usd = get_response_json(url=URL_USD)
    except requests.exceptions.RequestException as e:
        print(e)
    else:
        global eur, usd
        eur = int(round(data_eur["rates"][0]["mid"], 2) * 100)
        usd = int(round(data_usd["rates"][0]["mid"], 2) * 100)
        print("Currency updated")

    threading.Timer(UPDATE_RATE_CURRENCY, update_currency).start()


def update_instagram():
    try:
        data = get_response_json(url=URL_IG)
    except requests.exceptions.RequestException as e:
        print(e)
    else:
        global followers
        followers = data["user"]["followed_by"]["count"]
        print("Instagram followers updated")

    threading.Timer(UPDATE_RATE_IG, update_instagram).start()


def update_all_modes():
    update_weather()
    update_currency()
    update_instagram()
