from shapely import wkt

from element.graph.edge_dict import EdgeDict
from utils.geometry_utils import GeometryUtils


def cut_edge_with_fix_length():
    """
    将LineString线型按照固定长度打断
    :return: 返回固定长度的线形列表
    """
    network_edges_dict = EdgeDict.load_from_json(EdgeDict(), '../res/json/road_edges.json')
    edge_id = ('1', '2')
    edge = network_edges_dict[edge_id]
    # 固定长度打断
    cut_line_list = GeometryUtils.cut_edge_with_distance(line=wkt.loads(edge.get_geometry()), distance=50)
    return cut_line_list


if __name__ == '__main__':
    print(cut_edge_with_fix_length())
