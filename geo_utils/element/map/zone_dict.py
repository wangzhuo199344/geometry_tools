
from element.element_dict import ElementDict
from element.map.zone import Zone
from shapely.geometry import Polygon, Point


class ZoneDict(ElementDict):
    """
    区域集合
    """

    def __init__(self, name=''):
        if name:
            super().__init__('_'.join(['ZoneDict', name]))
        else:
            super().__init__('ZoneDict')

    def add_zone(self, zone):
        self[zone.get_id()] = zone

    def select_by_node_dict(self, node_dict):
        import copy
        selected_dict = copy.deepcopy(self)
        for zone_id, zone in self.items():
            zone = zone.update_element_by_polygon(node_dict)
            if zone.has_element():
                selected_dict[zone_id] = zone
            else:
                del selected_dict[zone_id]
        return selected_dict

    def select_by_route_dict(self, route_dict, node_dict):
        import copy
        selected_dict = ZoneDict()
        for route_id, route in route_dict.items():
            route_stop_id_list = route.get_node_id_list()
            for i in route_stop_id_list:
                belong_zone_id = node_dict[i].get_belong_element_id_dict()['zone_node_dict'][0]
                if belong_zone_id not in selected_dict:
                    selected_dict.add_zone(self[belong_zone_id])
        return selected_dict

        # zone_dict = copy.deepcopy(self)
        # zone_dict = {zone_id: zone.update_element_by_polygon(node_dict) for zone_id, zone in zone_dict.items()}        
        # selected_zone_dict = {zone_id: zone for zone_id, zone in zone_dict.items() if zone.has_element()}
        # return selected_zone_dict

    def select_zone_by_coor(self, coor):
        for zone_id, zone in self.items():
            if zone.get_polygon().contains(Point(coor)):
                return zone

    def save_to_df(self, request_dict=None, node_dict=None):
        from geodaisy import GeoObject
        from shapely.geometry import Polygon
        import pandas as pd
        zone_data_dict = {}
        for zone_id, zone in self.items():
            geo_obj = GeoObject(Polygon(zone.get_polygon()))
            wkt_format = geo_obj.wkt()
            zone_data_dict[zone_id] = {'zone_id': zone_id,
                                       'polygon': wkt_format,
                                       'total_demand': 0,
                                       'production': 0,
                                       'attraction': 0}
        if request_dict:
            for request in request_dict.values():
                pickup_node = node_dict[request.get_pickup_node_id()]
                delivery_node = node_dict[request.get_delivery_node_id()]
                pickup_zone_id = pickup_node.get_belong_element_id_dict()['zone_node_dict'][0]
                delivery_zone_id = delivery_node.get_belong_element_id_dict()['zone_node_dict'][0]
                demand = request.get_res_cost()['demand']
                if pickup_zone_id in zone_data_dict:
                    zone_data_dict[pickup_zone_id]['total_demand'] += demand
                    zone_data_dict[pickup_zone_id]['production'] += demand
                if delivery_zone_id in zone_data_dict:
                    zone_data_dict[delivery_zone_id]['total_demand'] += demand
                    zone_data_dict[delivery_zone_id]['attraction'] += demand
        zone_data = list(zone_data_dict.values())
        df = pd.DataFrame(zone_data)
        return df


if __name__ == '__main__':
    from shapely.geometry import Polygon

    polygon = Polygon([(114.27, 22.60), (114.27, 22.58), (114.27, 22.60)])
    zone_dict = ZoneDict()
    zone_dict.add_zone(
        Zone(zone_id='e1', inner_elements_index_dict=None, zone_type=None, polygon=polygon))
    zone_dict.add_zone(
        Zone(zone_id='e2', inner_elements_index_dict=None, zone_type=None, polygon=polygon))
    zone_dict.save_to_json('../../res/json/test_zones.json')

    new_zone_dict = ZoneDict()
    new_zone_dict.load_from_json('../../res/json/zones.json')

