import copy

from element.element_dict import ElementDict
from element.graph.node import NodeWithGPSAndTypeAndNeighborSet

class NodeDict(ElementDict):

    def __init__(self, name=''):
        if name:
            super().__init__('NodeDict_'+name)
        else:
            super().__init__('NodeDict')

    def add_node(self, node):
        self[node.get_id()] = node

    def select_by_polygon(self, polygon):
        selected_dict = copy.deepcopy(self)
        if polygon:
            for node_id, node in self.items():
                if node.is_in_polygon(polygon):
                    pass
                    # print(node_id)
                else:
                    del selected_dict[node_id]
            return selected_dict
        else:
            return selected_dict

    def select_not_in_polygon(self, polygon):
        inside_polygon_node_dict = self.select_by_polygon(polygon)
        return {i:j for i, j in self.items() if i not in inside_polygon_node_dict}

    def select_candidate_node_dict_by_zone_dict_and_polygon(self, zone_dict, polygon):
        from shapely.geometry import LineString
        selected_candidate_node_dict = NodeDict()
        for zone_id, zone in zone_dict.items():
            if LineString(zone.get_polygon().exterior.coords).intersects(LineString(polygon.exterior.coords)):
                inner_element_list = zone.get_inner_element_set()['node_dict']
                for e in inner_element_list:
                    selected_candidate_node_dict.add_node(self[e])
        print('[{}][Info] select {} candidate nodes'.format(__name__.split('.')[-1], len(selected_candidate_node_dict)))
        return selected_candidate_node_dict


    def select_candidate_node_dict_by_zone_dict_and_multi_points(self, zone_dict, multipoint):
        selected_candidate_node_dict = NodeDict()
        for zone_id, zone in zone_dict.items():
            for point in multipoint:
                if zone.get_polygon().contains(point):
                    for e in zone.get_inner_element_set()['node_dict']:
                        selected_candidate_node_dict.add_node(self[e])
                    break

        print('[{}][Info] select {} candidate nodes'.format(__name__.split('.')[-1], len(selected_candidate_node_dict)))
        return selected_candidate_node_dict


    def select_by_request_dict(self, request_dict):
        select_node_dict = NodeDict()
        for request_id, request in request_dict.items():
            pickup_node_id = request.get_pickup_node_id()
            delivery_node_id = request.get_delivery_node_id()
            if pickup_node_id in select_node_dict:
                pass
            else:
                select_node_dict.add_node(self[pickup_node_id])
            if delivery_node_id in select_node_dict:
                pass
            else:
                select_node_dict.add_node(self[delivery_node_id])
        return select_node_dict

    # @lru_cache(50)
    def cal_convex_hull_exterior(self):
        from shapely.geometry import MultiPoint
        return MultiPoint([n.get_GPS() for n in self.values()]).convex_hull.exterior

    # @lru_cache(50)
    def get_id_by_coord(self, coord):
        for n in self.values():
            if n.get_GPS() == coord:
                return n.get_id()
    # def save_to_json(self, json_path):
    #     json_dict = {"Nodes": []}
    #     for node_id, node in self.items():
    #         json_dict['Nodes'].append(node.get_json_string())
    #     self.dict_2_json(json_dict, json_path)
    #
    # def load_from_json(self, json_path):
    #     json_dict = self.json_2_dict(json_path)
    #     for node in json_dict['Nodes']:
    #         new_node = NodeWithGPSAndSpecificType(**node)
    #         self.add_node(new_node)
    def save_to_df(self):
        import pandas as pd
        node_data = []
        for node_id, node in self.items():
            node_data.append({'node_id':node_id,
                              'lat':node.get_lat(),
                              'lon':node.get_lon(),
                              'belong_zone_id':node.get_belong_element_id_dict()['zone_node_dict'][0]})
        df = pd.DataFrame(node_data)
        return df


if __name__ == '__main__':
    # 初始化节点字典接
    node_dict = NodeDict()
    # 初始化node类，加入节点字典集合
    node_dict.add_node(NodeWithGPSAndTypeAndNeighborSet(node_id='e1',node_coord=(1,2),node_name='ed2',node_type=None,neighbor_node_id_set=['1','2']))
    node_dict.add_node(NodeWithGPSAndTypeAndNeighborSet(node_id='e2',node_coord=(3,4),node_name='ed2',node_type=None,neighbor_node_id_set=['1','2']))
    # 保存为json数据
    node_dict.save_to_json('../../res/json/node.json')
    # 读取静态json数据
    new_node_dict = NodeDict()
    new_node_dict.load_from_json('../../res/json/test_node.json')
    print(new_node_dict)
