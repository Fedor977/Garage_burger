import math


def haversine(lat1, lon1, lat2, lon2):
    # Радиус Земли в километрах
    R = 6371.0

    # Перевод координат в радианы
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Разница в координатах
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Формула гаверсинуса
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Расстояние
    distance = R * c
    return distance


def check_spot(latitude, longitude):
    # Координаты филиалов
    filial_1_urgench = [41.561680, 60.630551]
    filial_2_urgench = [41.563037, 60.599731]
    filial_3_xiva = [41.391633, 60.364280]

    # Словарь с филиалами и их координатами
    filials = {
        "filial_1_urgench": filial_1_urgench,
        "filial_2_urgench": filial_2_urgench,
        "filial_3_xiva": filial_3_xiva
    }

    # Поиск филиала с минимальным расстоянием
    closest_filial = None
    min_distance = float('inf')

    for filial, coords in filials.items():
        distance = haversine(latitude, longitude, coords[0], coords[1])
        if distance < min_distance:
            min_distance = distance
            closest_filial = filial

    return closest_filial


