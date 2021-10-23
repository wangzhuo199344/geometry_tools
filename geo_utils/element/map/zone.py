import copy

from shapely import wkt
from shapely.geometry import Polygon


class Zone(object):
    """
    区域
    """

    def __init__(self, zone_id, inner_elements_index_dict=None, zone_type=None, polygon=None):
        """

        Args:
            zone_id:
            inner_elements:
            zone_type:
            polygon:
        """
        self.__zone_id = str(zone_id)
        self.__zone_type = zone_type

        self.__polygon = polygon

        if inner_elements_index_dict:
            self.inner_elements_index_dict = inner_elements_index_dict
        else:
            self.inner_elements_index_dict = dict()

    def __repr__(self):
        return "\n<Zone>\nID:{}\nZoneType:{}\nPolygon:{}\nInnerElement:{}".format(
            self.get_id(),
            self.get_zone_type(),
            self.get_exterior_xy(),
            self.get_inner_element_set()
        )

    def get_polygon(self):
        if isinstance(self.__polygon, str):
            return wkt.loads(self.__polygon)
        elif isinstance(self.__polygon, list):
            return Polygon(self.__polygon)
        else:
            return self.__polygon

    def get_polygon_string(self):
        return str(self.__polygon.exterior.xy)

    def get_polygon_coord_list_str(self):
        return list(self.get_polygon().coords)

    def get_id(self):
        return self.__zone_id

    def get_zone_type(self):
        return self.__zone_type

    def get_inner_element_set(self):
        return self.inner_elements_index_dict

    def add_inner_element(self, element_dict_name, element_id):
        if element_dict_name not in self.inner_elements_index_dict:
            self.inner_elements_index_dict[element_dict_name] = [element_id]
        else:
            self.inner_elements_index_dict[element_dict_name].append(element_id)

    def add_inner_element_list(self, element_dict_name, element_id_list):
        if element_dict_name not in self.inner_elements_index_dict:
            self.inner_elements_index_dict[element_dict_name] = element_id_list
        else:
            self.inner_elements_index_dict[element_dict_name].extend(element_id_list)

    def reset_inner_element_id_dict(self):
        self.inner_elements_index_dict = {}

    def update_inner_element_list(self, element_dict_name, element_id_list):
        self.inner_elements_index_dict[element_dict_name] = element_id_list

    def reset_inner_element_id_dict_value(self, element_dict_name):
        if element_dict_name not in self.inner_elements_index_dict:
            pass
        else:
            self.inner_elements_index_dict.pop(element_dict_name)

    def get_exterior(self):
        return self.__polygon.exterior

    def get_exterior_xy(self):
        return list(self.__polygon.exterior.coords)

    def update_element_by_polygon(self, node_dict):
        zone = copy.deepcopy(self)
        for ele_type, ele_id_set in self.inner_elements_index_dict.items():
            ele_id_list = list({ele_id for ele_id in ele_id_set if ele_id in node_dict})
            zone.inner_elements_index_dict[ele_type] = ele_id_list
        return zone

    def has_element(self):
        for element_id_set in self.inner_elements_index_dict.values():
            if element_id_set:
                return True
        return False

    def get_json_string(self):
        return {
            "zone_id": self.get_id(),
            "inner_elements_index_dict": self.get_inner_element_set(),
            "zone_type": self.get_zone_type(),
            'polygon': str(self.get_polygon())
        }
