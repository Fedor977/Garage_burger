import geocoder
from configs import *
from check import *


def get_location_name(latitude, longitude):
    location = geocoder.osm([latitude, longitude], method='reverse')
    return location.address


def get_group_with_location(latitude, longitude):
    filial = check_spot(latitude, longitude)

    if filial == "filial_1_urgench":
        return group_filial_1
    elif filial == "filial_2_urgench":
        return group_filial_2
    elif filial == "filial_3_xiva":
        return group_filial_3




