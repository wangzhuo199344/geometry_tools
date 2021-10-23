from element.graph.node_dict import NodeDict
from element.map.zone_dict import ZoneDict
from utils.rtree_utils import init_zone_rtree, get_neighbour_zone_id_list, init_zone_and_node_rtree, \
    get_zone_inner_point_id_list, get_point_belong_to_zone, init_node_rtree, get_node_near_point_id_list


def get_neighbour_zone_id_list_example():
    """
    计算区域临接区域ID列表
    :return: 区域临接区域ID列表
    """
    # 可根据自定义数据生成zone类
    zone_dict = ZoneDict.load_from_json(ZoneDict(), '../res/json/zones.json')
    # 初始化zone_rtree
    zone_rtree_index = init_zone_rtree(zone_dict)
    zone = zone_dict['672646']
    # 获取区域临近区域id
    neighbour_zone_id_list = get_neighbour_zone_id_list(zone, zone_rtree_index)
    return neighbour_zone_id_list


def get_zone_inner_point_id_list_example():
    """
    计算区域内部包含节点ID列表
    :return: 域内部包含节点ID列表
    """
    # 可根据自定义数据生成zone类 node
    zone_dict = ZoneDict.load_from_json(ZoneDict(), '../res/json/zones.json')
    node_dict = NodeDict.load_from_json(NodeDict(), '../res/json/nodes.json')
    # 初始化zone_and_node_rtree
    zone_and_node_rtree_index = init_zone_and_node_rtree(zone_dict, node_dict)
    zone = zone_dict['702680']
    zone_inner_node_id_list = get_zone_inner_point_id_list(zone_and_node_rtree_index, zone)
    return zone_inner_node_id_list


def get_point_belong_to_zone_example():
    """
    计算节点所属区域
    :return: 节点所属区域ID
    """
    # 可根据自定义数据生成zone类 node
    zone_dict = ZoneDict.load_from_json(ZoneDict(), '../res/json/zones.json')
    node_dict = NodeDict.load_from_json(NodeDict(), '../res/json/nodes.json')
    # 初始化zone_and_node_rtree
    zone_and_node_rtree_index = init_zone_and_node_rtree(zone_dict, node_dict)
    node = node_dict['f93e08392192f5bc71747e399025f554_0ed8d27bf5bc6fb7ebbce2409a32b58e']
    belong_zone_id = get_point_belong_to_zone(zone_and_node_rtree_index, node)
    return belong_zone_id


def get_node_nearest_node_example():
    """
    计算节点临近节点ID
    :return: 节点临近节点ID列表
    """
    node_dict = NodeDict.load_from_json(NodeDict(), '../res/json/nodes.json')
    # 初始化node_rtree
    node_rtree_index = init_node_rtree(node_dict)
    node = node_dict['705699']
    # 计算节点临近节点ID
    nearest_node_id_list = get_node_near_point_id_list(node_rtree_index, node, num_results=2)
    return nearest_node_id_list


if __name__ == '__main__':
    get_neighbour_zone_id_list_example()
    get_zone_inner_point_id_list_example()
    get_point_belong_to_zone_example()
    get_node_nearest_node_example()
