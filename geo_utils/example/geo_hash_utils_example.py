from element.graph.edge_dict import EdgeDict
from element.graph.node_dict import NodeDict
from element.map.zone_dict import ZoneDict
from match_node_to_edge.matching_node import Matching
from utils.geo_hash_utils import GeoHashUtils


def match_node_to_nearest_edge_example():
    """
    将节点匹配至最近边
    :return: min_distance_edge_id_dict：
    匹配后的信息字典：min_distance_edge_id
                      polate_point
                      min_distance


    """
    # 读取edge集合
    road_edge_dict = EdgeDict.load_from_json(EdgeDict(), '../res/json/test_edges.json')
    # 对edge进行编码
    geo_hash_box_zone_dict = GeoHashUtils.init_geo_hash_box_zone_dict(road_edge_dict, geo_hash_code_precision=6)
    # 得到geohash矩形区域包含和相交的edge_id (耗时较长，初始化后可存为静态数据)
    GeoHashUtils.add_edge_dict_geo_hash_code_data(road_edge_dict, geo_hash_box_zone_dict, geo_hash_code_precision=6)
    # 将geo_hash_box_zone保存为静态数据（下次匹配可通过load_from_json加载z）
    # geo_hash_box_zone_dict.save_to_json('../../../res/json/test.json')
    # geo_hash_box_zone_dict = ZoneDict.load_from_json(ZoneDict(), '../../../res/json/geo_hash_box_zone_edges.json')
    # 地图匹配
    node_gsp = '114.29404;22.717104'
    min_distance_edge_id_dict = Matching.match_point_to_nearest_edge(node_gsp,
                                                                     geo_hash_zone_dict=geo_hash_box_zone_dict,
                                                                     edge_dict=road_edge_dict)
    return min_distance_edge_id_dict


if __name__ == '__main__':
    print(match_node_to_nearest_edge_example())
