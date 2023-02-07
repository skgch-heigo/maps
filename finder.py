import math
from io import BytesIO

import requests
from PIL import Image


API_KEY = "40d1649f-0493-4b70-98ba-98533de7710b"
org_api = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
search_api_server = "https://search-maps.yandex.ru/v1/"
map_api_server = "http://static-maps.yandex.ru/1.x/"


def lonlat_distance(a, b):

    degree_to_meters_factor = 111 * 1000 # 111 километров в метрах
    a_lon, a_lat = a
    b_lon, b_lat = b

    # Берем среднюю по широте точку и считаем коэффициент для нее.
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    # Вычисляем смещения в метрах по вертикали и горизонтали.
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    # Вычисляем расстояние между точками.
    distance = math.sqrt(dx * dx + dy * dy)

    return distance


def geocode(address):
    geocoder_request = "http://geocode-maps.yandex.ru/1.x/"
    params = {"apikey": API_KEY, "geocode": address, "format": "json"}

    response = requests.get(geocoder_request, params=params)

    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()
        for i in json_response["response"]["GeoObjectCollection"]["featureMember"]:
            toponym = i["GeoObject"]
            return toponym
        return None
    else:
        print("Ошибка выполнения запроса:")
        print(geocoder_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        return None


def get_address(town, index):
    toponym = geocode(town)
    toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["Components"]
    return toponym_address[index]["name"]


def get_coords(town):
    toponym = geocode(town)
    coords = toponym["Point"]["pos"]
    return map(float, coords.split())


def get_org(text, where, num):
    search_params = {
        "apikey": org_api,
        "text": text,
        "lang": "ru_RU",
        "ll": ",".join(map(str, where)),
        "type": "biz"
    }

    response = requests.get(search_api_server, params=search_params)
    if not response:
        print("Ошибка выполнения запроса:")
        print(search_params)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        return None
    else:
        json_response = response.json()
        # Получаем первую найденную организацию.
        orgs = json_response["features"][:num]
        answer = []
        for i in orgs:
            organization = i
            # Название организации.
            org_name = organization["properties"]["CompanyMetaData"]["name"]
            # Адрес организации.
            org_address = organization["properties"]["CompanyMetaData"]["address"]

            # Получаем координаты ответа.
            point = organization["geometry"]["coordinates"]
            org_point = f"{point[0]},{point[1]}"
            answer.append((org_name, org_address, org_point, organization["properties"]["CompanyMetaData"]))
        return answer


def get_map(ll, span, points=None):
    map_params = {
        # позиционируем карту центром на наш исходный адрес
        "ll": ll,
        "spn": span,
        "l": "map",
        "size": "650,450",
    }
    if points:
        ans = []
        for i in points:
            ans.append(str(i[0]) + "," + i[1])
        map_params["pt"] = "~".join(ans)
    response = requests.get(map_api_server, params=map_params)
    if not response:
        print("Ошибка выполнения запроса.")
        print("Http статус:", response.status_code, "(", response.reason, ")")
        return None
    else:
        return response


def get_postal_code(address):
    toponym = geocode(address)
    toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]
    code = toponym_address['postal_code']
    return code


def get_ll_span(address):
    toponym = geocode(address)
    if toponym:
        long, latt = toponym["Point"]["pos"].split(" ")
        ll = ",".join([long, latt])
        envelope = toponym["boundedBy"]["Envelope"]
        l, b = envelope["lowerCorner"].split(" ")
        r, t = envelope["upperCorner"].split(" ")
        dx = abs(float(l) - float(r)) / 2.0
        dy = abs(float(t) - float(b)) / 2.0
        span = f"{dx},{dy}"
        return ll, span
    else:
        return (None, None)