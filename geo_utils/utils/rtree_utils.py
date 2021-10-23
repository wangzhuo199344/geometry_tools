import datetime

from rtree import index
from shapely import wkt
from element.map.zone_dict import ZoneDict
from element.graph.node import NodeWithGPSAndTypeAndNeighborSetAndBelonging
from element.map.zone import Zone
from shapely.geometry import Point, LineString
import shapely.geometry as geometry
import geopandas as gpd


def init_zone_rtree(zone_dict):
    """
       建立交通小区集合rtree索引
       Args:
           zone_dict: 通小区集合

       Returns:
           zone_rtree_index:交通小区集合rtree索引

    """
    from rtree.index import Index
    zone_rtree_index = Index()
    zone_index = 0
    for zone_id in zone_dict:
        zone_rtree_index.insert(zone_index, list(zone_dict[zone_id].get_polygon().bounds), obj=zone_dict[zone_id])
        zone_index = zone_index + 1
    return zone_rtree_index


def get_neighbour_zone_id_list(zone, zone_rtree_index):
    """
    获取zone临近区域ID列表
    Args:
        zone: 交通小区集合
        zone_rtree_index: 交通小区集合rtree

    Returns:
        zone区域临近区域ID列表

    """

    zone_results = list(zone_rtree_index.nearest(list(zone.get_polygon().bounds), objects=True))
    adjacent_zone_id_list = []
    for adjacent_zone in zone_results:
        if adjacent_zone.object.get_id() != zone.get_id() and gpd.GeoSeries([zone.get_polygon()]).touches(
                gpd.GeoSeries([adjacent_zone.object.get_polygon()]).values[0]).bool():
            adjacent_zone_id_list.append(adjacent_zone.object.get_id())
    return adjacent_zone_id_list


def init_zone_and_edge_rtree(zone_dict, edge_dict):
    """
    建立交通小区集合与边集合的rtree索引
    Args:
        zone_dict:
        edge_dict:

    Returns:
        zone_and_edge_index :通小区集合与边集合的rtree索引

    """
    from rtree import index
    zone_and_edge_index = index.Index()
    zone_index = 0
    for zone_id in zone_dict:
        zone_and_edge_index.insert(id=zone_index, coordinates=list(zone_dict[zone_id].get_polygon().bounds),
                                   obj=zone_dict[zone_id])
        zone_index = zone_index + 1

    walk_edge_node_index = 0
    for edge_id in edge_dict:

        for line_string_point in list(LineString(edge_dict[edge_id].get_geometry()).coords):
            walk_edge_node = NodeWithGPSAndTypeAndNeighborSetAndBelonging(node_id=walk_edge_node_index,
                                                                          node_coord=line_string_point,
                                                                          node_name=None,
                                                                          node_type='Walk',
                                                                          neighbor_node_id_set=None,
                                                                          belong_element_id_dict=None)
            zone_and_edge_index.insert(id=(len(zone_dict) + walk_edge_node_index),
                                       coordinates=Point(walk_edge_node.get_lon(), walk_edge_node.get_lat()).bounds,
                                       obj=edge_dict[edge_id])
            walk_edge_node_index = walk_edge_node_index + 1


    return zone_and_edge_index


def get_zone_inner_edge_id_list(zone, zone_and_edge_index):
    """
    索引交通小区内部及相交的edge id列表
    Args:
        zone: 交通小区
        zone_and_edge_index: 交通小区集合与边结合Rtree

    Returns:
        inner_edge_id_list: 通小区内部及相交的edge id列表

    """
    # 索引区域内不包含edge
    inner_edge_results = list(zone_and_edge_index.contains(list(zone.get_polygon().bounds), objects=True))
    inner_edge_id_list = []
    for edge in inner_edge_results:
        if type(edge.object) is not Zone:
            inner_edge_id_list.append(edge.object.get_id())
    # 索引区域相交edge
    intersect_edge_results = list(zone_and_edge_index.intersection(list(zone.get_polygon().bounds), objects=True))
    intersect_edge_id_list = []
    for edge in intersect_edge_results:
        if type(edge.object) is not Zone:
            intersect_edge_id_list.append(edge.object.get_id())
    # 合并
    inner_edge_id_list = inner_edge_id_list + intersect_edge_id_list
    # 去重
    inner_edge_id_list = list(set(inner_edge_id_list))
    return inner_edge_id_list


def init_zone_and_node_rtree(zone_dict, node_dict):
    """
    建立交通小区集合与节点集合的rtree索引
    Args:
        zone_dict: 交通小区集合
        node_dict: 节点集合

    Returns:

    """
    from rtree import index
    zone_and_node_rtree_index = index.Index()
    zone_index = 0
    for zone_id in zone_dict:
        zone_and_node_rtree_index.insert(id=zone_index, coordinates=list(zone_dict[zone_id].get_polygon().bounds),
                                         obj=zone_dict[zone_id])
        zone_index = zone_index + 1
    node_index = 0
    for node_id in node_dict:
        zone_and_node_rtree_index.insert(id=(len(zone_dict) + node_index),
                                         coordinates=list(
                                             Point(node_dict[node_id].get_lon(), node_dict[node_id].get_lat()).bounds),
                                         obj=node_dict[node_id])
        node_index = node_index + 1
    return zone_and_node_rtree_index


def get_zone_inner_point_id_list(zone_and_node_rtree_index, zone):
    """
    查询区域内部节点
    Args:
        zone_and_node_rtree_index: 交通小区与节点建立的rtree索引
        zone: 交通小区

    Returns:
        交通小区内部节点ID列表

    """
    inner_results = list(zone_and_node_rtree_index.contains(list(zone.get_polygon().bounds), objects=True))
    # print(inner_results)
    inner_point_id_list = []
    for node in inner_results:
        if not isinstance(zone, type(node.object)):
            # print(node.object)
            if geometry.Point(node.object.get_lon(), node.object.get_lat()).within(geometry.shape(zone.get_polygon())):
                inner_point_id_list.append(node.object.get_id())
    return inner_point_id_list


def get_point_belong_to_zone(zone_and_node_rtree_index, node):
    belong_zone_results = list(
        zone_and_node_rtree_index.intersection(list(Point(node.get_lon(), node.get_lat()).bounds), objects=True))
    belong_zone_id = None
    for zone in belong_zone_results:
        if not isinstance(node, type(zone.object)):
            if geometry.Point(node.get_lon(), node.get_lat()).within(geometry.shape(zone.object.get_polygon())):
                return zone.object.get_id()
            else:
                continue
    return belong_zone_id


def get_coords_belong_to_zone(zone_and_node_rtree_index, coords):
    belong_zone_results = list(
        zone_and_node_rtree_index.intersection(
            list(Point(float(coords.split(',')[0]), float(coords.split(',')[1])).bounds), objects=True))
    belong_zone_id = None
    for zone in belong_zone_results:
        if not isinstance(coords, type(zone.object)):
            if geometry.Point(float(coords.split(',')[0]), float(coords.split(',')[1])).within(
                    geometry.shape(zone.object.get_polygon())):
                return zone.object.get_id()
            else:
                continue
    return belong_zone_id


def init_node_rtree(node_dict):
    """
    生成node集合Rtree
    Args:
        node_dict: 节点集合

    Returns:
        node集合Rtree

    """
    from rtree import index
    node_rtree_index = index.Index()
    node_index = 0
    for node_id in node_dict:
        node_rtree_index.insert(id=node_index,
                                coordinates=list(
                                    Point(node_dict[node_id].get_lon(), node_dict[node_id].get_lat()).bounds),
                                obj=node_dict[node_id])
        node_index = node_index + 1
    return node_rtree_index


def get_node_near_point_id_list(node_rtree_index, node, num_results):
    """
    索引距离node节点最近的节点
    Args:
        node_rtree_index: node集合Rtree
        node: 节点
        num_results ：最近节点数量参数，默认为1 返回距离最近点

    Returns:
        near_point_id_list：离node节点最近的节点id列表

    """
    near_node_results = list(
        node_rtree_index.nearest(list(Point(node.get_lon(), node.get_lat()).bounds), num_results=num_results, objects=True))
    near_point_id_list = []
    for near_node in near_node_results:
        if near_node.object.get_id() != node.get_id():
            near_point_id_list.append(near_node.object.get_id())
    return near_point_id_list


def init_edge_rtree(edge_dict):
    """
    生成edge集合Rtree
    Args:
        edge_dict: edge集合

    Returns:
        edge_rtree_index：edge集合Rtree

    """
    from rtree import index
    edge_rtree_index = index.Index()
    edge_index = 0
    walk_edge_node_index = 0
    for edge_id in edge_dict:
        for line_string_point in list(LineString(edge_dict[edge_id].get_geometry()).coords):
            walk_edge_node = NodeWithGPSAndTypeAndNeighborSetAndBelonging(node_id=walk_edge_node_index,
                                                                          node_coord=line_string_point,
                                                                          node_name=None,
                                                                          node_type='Walk',
                                                                          neighbor_node_id_set=None,
                                                                          belong_element_id_dict=None)
            edge_rtree_index.insert(id=walk_edge_node_index,
                                    coordinates=Point(walk_edge_node.get_lon(), walk_edge_node.get_lat()).bounds,
                                    obj=edge_dict[edge_id])
            walk_edge_node_index = walk_edge_node_index + 1
        edge_index = edge_index + 1
    return edge_rtree_index


def get_min_and_max_coords_list(minimum_rotated_rectangle_coords_list):
    longitude_data_list = []
    latitude_data_list = []
    for coords in minimum_rotated_rectangle_coords_list:
        longitude_data_list.append(coords[0])
        latitude_data_list.append(coords[1])
    max_longitude = max(longitude_data_list)
    max_latitude = max(latitude_data_list)
    min_longitude = min(longitude_data_list)
    min_latitude = min(latitude_data_list)
    return [min_longitude, min_latitude, max_longitude, max_latitude]


def get_node_nearest_edge_id_list(node, edge_rtree_index):
    """
    索引距离节点node最近的edge边
    Args:
        node: 节点
        edge_rtree_index: edge集合Rtree

    Returns:据
        near_edge_id_list：距离节点node最近的edge边id列表

    """
    start_time = datetime.datetime.now()
    edge_rtree_index.insert(id=9999999,
                            coordinates=list(Point(node.get_lon(), node.get_lat()).bounds),
                            obj=node)
    near_edge_results = list(
        edge_rtree_index.nearest(list(Point(node.get_lon(), node.get_lat()).bounds), num_results=2, objects=True))
    near_edge_id_list = []
    for near_edge in near_edge_results:
        if near_edge.object.get_id() != node.get_id():
            near_edge_id_list.append(near_edge.object.get_id())
    edge_rtree_index.delete(id=9999999, coordinates=list(Point(node.get_lon(), node.get_lat()).bounds))
    end_time = datetime.datetime.now()
    print('索引Rtree', (end_time - start_time).microseconds / 1000)
    return near_edge_id_list


class JSONIndex(index.Index):

    def dumps(self, obj):
        # This import is nested so that the doctest doesn't
        # require simplejson.
        import simplejson
        return simplejson.dumps(obj).encode('ascii')

    def loads(self, string):
        import simplejson
        return simplejson.loads(string.decode('ascii'))


if __name__ == '__main__':
    total_start_time = datetime.datetime.now()
    zone_dict = ZoneDict.load_from_json(ZoneDict(), '../res/json/zones.json')
    init_zone_rtree(zone_dict)
