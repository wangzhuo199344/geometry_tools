import json
import time
from collections import deque
from pathlib import Path

import geohash
from shapely import wkt, geometry
from shapely.geometry import LineString, Point, MultiLineString
from shapely.ops import nearest_points
import numpy as np

from element.map.zone_dict import ZoneDict
from element.map.zone import Zone
from utils.geo_hash_utils import GeoHashUtils


class Matching(object):
    """
    地图匹配
    """

    @staticmethod
    def match_point_to_nearest_edge(node_gps, geo_hash_zone_dict, edge_dict):
        """
        node节点匹配至最近的步行边上
        Args:
           node_gps: 带匹配的node节点坐標
            geo_hash_zone_dict: 全市geo_hash小区
            edge_dict: 全市步行边

        Returns:
            nearest_edge_id :最近步行边ID

        """
        longitude = float(node_gps.split(';')[0])
        latitude = float(node_gps.split(';')[1])
        point = Point(longitude, latitude)
        belong_zone_id = geohash.encode(latitude, longitude,
                                        precision=6)

        try:
            zone = geo_hash_zone_dict[belong_zone_id]
            if 'inner_link_edge' in zone.get_inner_element_set().keys():
                inner_edge_id_list = zone.get_inner_element_set()['inner_link_edge']
                min_distance_edge_id_dict = Matching.find_nearest_edge(point, inner_edge_id_list, edge_dict)
            else:

                inner_edge_id_set = Matching.search_zone_inner_edge_id(zone_id_set={belong_zone_id},
                                                                          zone_dict=geo_hash_zone_dict)
                min_distance_edge_id_dict = Matching.find_nearest_edge(point, inner_edge_id_set, edge_dict)
            return min_distance_edge_id_dict
        except KeyError:
            pass

    @staticmethod
    def match_point_to_nearest_edge_(node_gps, edge_dict):
        # 判断edge类型
        if edge_dict[list(edge_dict.keys())[0]].get_edge_type() in {'car'}:
            geo_hash_zone_dict_file = "../../../../res/json/geo_hash_box_zone_inner_road_edges.json"
        else:
            geo_hash_zone_dict_file = "../../../../res/json/geo_hash_box_zone_edges.json"
        # 静态文件存在
        if Path(geo_hash_zone_dict_file).exists():
            geo_hash_box_zone_dict = ZoneDict.load_from_json(ZoneDict(), geo_hash_zone_dict_file)
        else:
            geo_hash_box_zone_dict = GeoHashUtils.init_geo_hash_box_zone_dict(edge_dict, geo_hash_code_precision=6)
            geo_hash_box_zone_dict.save_to_json(geo_hash_box_zone_dict)
        return Matching.match_point_to_nearest_edge(node_gps, geo_hash_box_zone_dict, edge_dict)

    @staticmethod
    def find_nearest_edge(point, inner_edge_id_list, edge_dict):
        """
        point节点匹配至最近的步行边上
        Args:
            point: 节点
            inner_edge_id_list: 节点所属郊区内部的步行边ID列表
            edge_dict: 全市步行边集合
        Returns:
            min_distance_edge_id_dict：最近步行边ID及距离，投影坐标

        """
        min_distance_edge_id_dict = {}
        # 去掉反向edge，减少搜索edge数量
        single_inner_edge_id_list = []
        for edge_id_list in inner_edge_id_list:
            if [edge_id_list[1], edge_id_list[0]] not in single_inner_edge_id_list:
                single_inner_edge_id_list.append(edge_id_list)
        for edge_id_list in single_inner_edge_id_list:
            edge_id = (edge_id_list[0], edge_id_list[1])
            line = wkt.loads(edge_dict[edge_id].get_geometry())
            # Point
            distance = point.distance(line)
            if 'min_distance' in min_distance_edge_id_dict.keys():
                history_distance = min_distance_edge_id_dict['min_distance']
                if distance <= history_distance:
                    min_distance_edge_id_dict['min_distance'] = distance
                    min_distance_edge_id_dict['min_distance_edge_id'] = edge_id
                    polate_point = list(nearest_points(line, point)[0].coords)
                    min_distance_edge_id_dict['polate_point'] = tuple(
                        [round(polate_point[0][0], 7), round(polate_point[0][1], 7)])
            else:
                min_distance_edge_id_dict['min_distance'] = distance
                min_distance_edge_id_dict['min_distance_edge_id'] = edge_id
                polate_point = list(nearest_points(line, point)[0].coords)
                min_distance_edge_id_dict['polate_point'] = tuple(
                    [round(polate_point[0][0], 7), round(polate_point[0][1], 7)])
        return min_distance_edge_id_dict

    @staticmethod
    def get_polate_point(point, line):
        """
           计算point在line上的投影坐标
           Args:
               point: 点
               line: 线

           Returns:
               point_list：投影坐标
           """
        x = np.array(point.coords[0])
        u = np.array(line.coords[0])
        v = np.array(line.coords[len(line.coords) - 1])
        n = v - u
        n /= np.linalg.norm(n, 2)
        point_list = u + n * np.dot(x - u, n)
        return point_list

    @staticmethod
    def search_zone_inner_edge_id(zone_id_set, zone_dict):
        """
        广度优先搜索zone中的edge_id
        Args:
            zone_id_set:
            zone_dict:
        Returns:

        """
        # 创建一个队列
        search_queue = deque()
        inner_edge_id_set = set()
        inner_edge_id_list = []
        searched_zone_id_set = zone_id_set
        while not inner_edge_id_set:
            # 将起始节点的邻居都加入到这个搜索队列中
            for zone_id in zone_id_set:
                # if zone_id in zone_dict.keys():
                search_queue += {i for i in zone_dict[zone_id].get_inner_element_set()['neighbour_zone_id_list'] if
                                 i not in searched_zone_id_set and i not in list(search_queue)}
            # 用于记录检查过的区域，避免重复检查
            zone_id_set = set(list(search_queue))
            while search_queue:
                zone_node_id = search_queue.popleft()
                if zone_node_id not in searched_zone_id_set:
                    try:
                        zone = zone_dict[zone_node_id]
                        if 'inner_link_edge' in zone.get_inner_element_set().keys():
                            for edge_id in zone.get_inner_element_set()['inner_link_edge']:
                                inner_edge_id_list.append(tuple([edge_id[0], edge_id[1]]))
                        searched_zone_id_set = searched_zone_id_set.union({zone_node_id})
                    except KeyError:
                        pass
                else:
                    search_queue += [zone_id for zone_id in
                                     zone_dict[zone_node_id].get_inner_element_set()['neighbour_zone_id_list']]
            inner_edge_id_set = set(inner_edge_id_list)
        return inner_edge_id_set

    @staticmethod
    def search_point_belong_to_zone(node_gps, geohash_box_zone_dict, zone_dict):
        longitude = float(node_gps.split(',')[0])
        latitude = float(node_gps.split(',')[1])
        zone_hash_zone_id = geohash.encode(latitude, longitude, precision=6)
        # geo_hash_zone = geohash_box_zone_dict.get(zone_hash_zone_id, None)
        if not geohash_box_zone_dict.get(zone_hash_zone_id, None):
            return None
        else:
            if 'belong_zone_id' in geohash_box_zone_dict[zone_hash_zone_id].get_inner_element_set().keys():
                zone_id_list = \
                    geohash_box_zone_dict[zone_hash_zone_id].get_inner_element_set()[
                        'belong_zone_id']
                if zone_id_list:
                    for zone_id in zone_id_list:
                        if geometry.Point(longitude, latitude).within(geometry.shape(zone_dict[zone_id].get_polygon())):
                            return zone_id
                else:
                    return None
            else:
                return None
