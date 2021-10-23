import json
import sys
from datetime import datetime

import geopandas as gpd
import geohash
from shapely import geometry, wkt
from shapely.geometry import Polygon, Point

from element.graph.edge_dict import EdgeDict
from element.graph.node_dict import NodeDict
from element.map.zone import Zone
from element.map.zone_dict import ZoneDict


class GeoHashUtils(object):

    @staticmethod
    def get_polygon_min_box(polygon):
        """
        返回多边形最小外接矩形坐标
        Args:
            polygon:

        Returns:

        """
        return list(polygon.bounds)

    @staticmethod
    def is_rectangle_overlap(rec1: list, rec2: list) -> bool:
        """
        判断矩形是否相交
        Args:
            rec1: 矩形1
            rec2: 矩形2

        Returns:

        """
        if rec1[0] == rec1[2] or rec1[1] == rec1[3] or rec2[0] == rec2[2] or rec2[1] == rec2[3]:
            return False
        return not (rec1[2] <= rec2[0] or  # left
                    rec1[3] <= rec2[1] or  # bottom
                    rec1[0] >= rec2[2] or  # right
                    rec1[1] >= rec2[3])  # top

    @staticmethod
    def init_column_geo_hash_code_list(start_geohash_code, end_geohash_code):
        left_start_geo_hash_code_list = []
        mid_geohash_code = start_geohash_code
        left_start_geo_hash_code_list.append(mid_geohash_code)
        while mid_geohash_code != end_geohash_code:
            mid_geohash_code = geohash.neighbors(mid_geohash_code)[5]
            left_start_geo_hash_code_list.append(mid_geohash_code)
        return left_start_geo_hash_code_list

    @staticmethod
    def init_row_geo_hash_code_list(start_geohash_code, end_geohash_code):
        left_start_geo_hash_code_list = []
        mid_geohash_code = start_geohash_code
        left_start_geo_hash_code_list.append(mid_geohash_code)
        while mid_geohash_code != end_geohash_code:
            mid_geohash_code = geohash.neighbors(mid_geohash_code)[1]
            left_start_geo_hash_code_list.append(mid_geohash_code)
        return left_start_geo_hash_code_list

    @staticmethod
    def init_rectangle_geo_hash_code_list(rectangle_list, geo_hash_code_precision=6):
        rectangle_geo_hash_code_list = []
        # 左下
        lower_left_geohash_code = geohash.encode(rectangle_list[1], rectangle_list[0],
                                                 precision=geo_hash_code_precision)
        # 左上
        upper_left_geohash_code = geohash.encode(rectangle_list[3], rectangle_list[0],
                                                 precision=geo_hash_code_precision)
        # 右下
        lower_right_geohash_code = geohash.encode(rectangle_list[1], rectangle_list[2],
                                                  precision=geo_hash_code_precision)
        # 右上
        upper_right_geohash_code = geohash.encode(rectangle_list[3], rectangle_list[2],
                                                  precision=geo_hash_code_precision)
        lower_left_to_upper_left_geo_hash_list = GeoHashUtils.init_column_geo_hash_code_list(
            start_geohash_code=lower_left_geohash_code,
            end_geohash_code=upper_left_geohash_code)
        lower_right_to_upper_right_geo_hash_list = GeoHashUtils.init_column_geo_hash_code_list(
            start_geohash_code=lower_right_geohash_code,
            end_geohash_code=upper_right_geohash_code)
        for i in range(0, len(lower_left_to_upper_left_geo_hash_list)):
            rectangle_geo_hash_code_list = rectangle_geo_hash_code_list + GeoHashUtils.init_row_geo_hash_code_list(
                start_geohash_code=lower_left_to_upper_left_geo_hash_list[i],
                end_geohash_code=lower_right_to_upper_right_geo_hash_list[i])
        return rectangle_geo_hash_code_list

    @staticmethod
    def init_geo_hash_code_rectangle_polygon(geo_hash_code):
        """
        生成geohash code 矩形polygon
        Args:
            geo_hash_code: geohash 字符转

        Returns:
            矩形polygon

        """
        box_coords_dict = geohash.bbox(geo_hash_code)
        return Polygon([(box_coords_dict['w'], box_coords_dict['s']), (box_coords_dict['e'], box_coords_dict['s']),
                        (box_coords_dict['e'], box_coords_dict['n']), (box_coords_dict['w'], box_coords_dict['n']),
                        (box_coords_dict['w'], box_coords_dict['s'])])

    @staticmethod
    def is_intersects(polygon, other_polygon):
        """
            判断polygon是否相交
            :param  polygon:区域一
            :param  other_polygon:区域二
            :return:if touch return true
            """
        return gpd.GeoSeries([polygon]).intersects(gpd.GeoSeries([other_polygon]).values[0]).bool()

    @staticmethod
    def is_contains(polygon, other_polygon):
        return gpd.GeoSeries([polygon]).contains(gpd.GeoSeries([other_polygon]).values[0]).bool()

    @staticmethod
    def is_within(polygon, other_polygon):
        return gpd.GeoSeries([polygon]).within(gpd.GeoSeries([other_polygon]).values[0]).bool()

    @staticmethod
    def get_overlap_geo_hash_code_list(rectangle_geo_hash_code_list, zone_polygon):
        zone_contains_geo_hash_code_list = []
        zone_intersects_geo_hash_code_list = []
        for i in range(0, len(rectangle_geo_hash_code_list)):
            rectangle_polygon = GeoHashUtils.init_geo_hash_code_rectangle_polygon(rectangle_geo_hash_code_list[i])
            if GeoHashUtils.is_contains(zone_polygon, rectangle_polygon):
                zone_contains_geo_hash_code_list.append(rectangle_geo_hash_code_list[i])
            elif GeoHashUtils.is_intersects(zone_polygon, rectangle_polygon):
                zone_intersects_geo_hash_code_list.append(rectangle_geo_hash_code_list[i])
            elif GeoHashUtils.is_within(zone_polygon, rectangle_polygon):
                zone_intersects_geo_hash_code_list.append(rectangle_geo_hash_code_list[i])
            else:
                pass
        return {'zone_contains_geo_hash_code': zone_contains_geo_hash_code_list,
                'zone_intersects_geo_hash_code': zone_intersects_geo_hash_code_list}

    @staticmethod
    def get_edge_overlap_geo_hash_code_list(rectangle_geo_hash_code_list, edge_line_string):
        edge_within_geo_hash_code_list = []
        edge_intersects_geo_hash_code_list = []
        for i in range(0, len(rectangle_geo_hash_code_list)):
            rectangle_polygon = GeoHashUtils.init_geo_hash_code_rectangle_polygon(rectangle_geo_hash_code_list[i])
            if GeoHashUtils.is_intersects(edge_line_string, rectangle_polygon):
                edge_intersects_geo_hash_code_list.append(rectangle_geo_hash_code_list[i])
            elif GeoHashUtils.is_within(edge_line_string, rectangle_polygon):
                edge_within_geo_hash_code_list.append(rectangle_geo_hash_code_list[i])
            else:
                pass
        return {'edge_within_geo_hash_code_code': edge_within_geo_hash_code_list,
                'edge_intersects_geo_hash_code': edge_intersects_geo_hash_code_list}

    @staticmethod
    def generate_geohash_shape_file(zone_contains_geo_hash_code_list):
        geo_df = gpd.GeoDataFrame()
        index = 0
        for geohash_code in zone_contains_geo_hash_code_list:
            geo_df.loc[index, 'id'] = geohash_code
            geo_df.loc[index, 'geometry'] = GeoHashUtils.init_geo_hash_code_rectangle_polygon(geohash_code)
            index = index + 1
        return geo_df

    @staticmethod
    def generate_polygon_shape_file(zone):
        geo_df = gpd.GeoDataFrame()
        index = 0
        geo_df.loc[index, 'id'] = zone.get_id()
        geo_df.loc[index, 'geometry'] = zone.get_polygon()
        return geo_df

    @staticmethod
    def add_zone_geo_hash_code_data(zone, geo_hash_code_precision=6):
        """
        区域geo_hash编码
        Args:
            zone: 区域
            geo_hash_code_precision: 编码精度

        Returns:

        """
        rectangle_list = GeoHashUtils.get_polygon_min_box(zone.get_polygon())
        rectangle_geo_hash_code_list = GeoHashUtils.init_rectangle_geo_hash_code_list(rectangle_list,
                                                                                      geo_hash_code_precision=geo_hash_code_precision)
        zone_contains_geo_hash_code_dict = GeoHashUtils.get_overlap_geo_hash_code_list(rectangle_geo_hash_code_list,
                                                                                       zone.get_polygon())
        zone.add_inner_element_list('zone_contains_geo_hash_code',
                                    zone_contains_geo_hash_code_dict['zone_contains_geo_hash_code'])
        zone.add_inner_element_list('zone_intersects_geo_hash_code',
                                    zone_contains_geo_hash_code_dict['zone_intersects_geo_hash_code'])
        return zone

    @staticmethod
    def add_edge_geo_hash_code_data(edge, geo_hash_zone_dict, geo_hash_code_precision=6):
        """
        将edge匹配至geo_hash_box
        Args:
            edge: 边
            geo_hash_zone_dict: geo_hash_box 集合
            geo_hash_code_precision: 编码精度

        Returns:
            geo_hash_zone_dict：包含edge_id geo_hash_box 集合

        """

        rectangle_list = list(wkt.loads(edge.get_geometry()).bounds)
        # edge 最小外接矩形geohash
        rectangle_geo_hash_code_list = GeoHashUtils.init_rectangle_geo_hash_code_list(rectangle_list,
                                                                                      geo_hash_code_precision=geo_hash_code_precision)

        edge_contains_geo_hash_code_dict = GeoHashUtils.get_edge_overlap_geo_hash_code_list(
            rectangle_geo_hash_code_list,
            wkt.loads(edge.get_geometry()))
        for geo_hash_zone_id in (
                edge_contains_geo_hash_code_dict['edge_within_geo_hash_code_code'] +
                edge_contains_geo_hash_code_dict['edge_intersects_geo_hash_code']):
            geo_hash_zone_dict[geo_hash_zone_id].add_inner_element('inner_link_edge', edge.get_id())
        return geo_hash_zone_dict

    @staticmethod
    def find_max_and_min_coords(line_string_list):
        """
        根据线网数据集合得到外接矩形
        Args:
            line_string_list: 深圳市路网数据列表

        Returns:
            最大经纬度，最小经纬度

        """
        longitude_data_list = []
        latitude_data_list = []
        for line_string_data in line_string_list:
            from_node = line_string_data.coords[0]
            to_node = line_string_data.coords[len(line_string_data.coords) - 1]
            longitude_data_list.append(from_node[0])
            longitude_data_list.append(to_node[0])
            latitude_data_list.append(from_node[1])
            latitude_data_list.append(to_node[1])
        longitude_data_list = list(set(longitude_data_list))
        latitude_data_list = list(set(latitude_data_list))
        max_longitude = max(longitude_data_list)
        max_latitude = max(latitude_data_list)
        min_longitude = min(longitude_data_list)
        min_latitude = min(latitude_data_list)

        return [min_longitude, min_latitude, max_longitude, max_latitude]

    @staticmethod
    def init_geo_hash_box_zone_dict(edge_dict, geo_hash_code_precision):
        """
        根据edge集合生成geo_hash_zone
        Args:
            edge_dict:
            geo_hash_code_precision:

        Returns:
            geo_hash_box_zone_dict：geo_hash_zone 集合

        """
        print('[{}][{}()][Info] init_geo_hash_box_zone_dict...'.format(__file__.split('/')[-1],
                                                                       sys._getframe().f_code.co_name))
        geo_hash_box_zone_dict = ZoneDict()
        rectangle_list = GeoHashUtils.find_max_and_min_coords(
            line_string_list=[wkt.loads(edge_dict[edge_id].get_geometry()) for edge_id in edge_dict.keys()])
        geo_hash_code_list = GeoHashUtils.init_rectangle_geo_hash_code_list(rectangle_list,
                                                                            geo_hash_code_precision=geo_hash_code_precision)
        for geo_hash_code in geo_hash_code_list:
            geohash_box_zone = Zone(
                zone_id=geo_hash_code,
                inner_elements_index_dict=None,
                zone_type='geo_hash_box',
                polygon=GeoHashUtils.init_geo_hash_code_rectangle_polygon(geo_hash_code))
            geohash_box_zone.add_inner_element_list('neighbour_zone_id_list',
                                                    [geohash_code for geohash_code in geohash.neighbors(geo_hash_code)
                                                     if
                                                     geohash_code in geo_hash_code_list])
            geo_hash_box_zone_dict.add_zone(geohash_box_zone)
        print('[{}][{}()][Info] init_geo_hash_box_zone_dict finished'.format(__file__.split('/')[-1],
                                                                             sys._getframe().f_code.co_name))
        return geo_hash_box_zone_dict

    @staticmethod
    def add_zone_dict_geo_hash_code_data(zone_dict, geo_hash_code_precision):
        for zone_id in zone_dict:
            zone_dict[zone_id] = GeoHashUtils.add_zone_geo_hash_code_data(zone_dict[zone_id],
                                                                          geo_hash_code_precision=geo_hash_code_precision)
        return zone_dict

    @staticmethod
    def add_edge_dict_geo_hash_code_data(edge_dict, geo_hash_zone_dict, geo_hash_code_precision):
        for edge_id in edge_dict:
            GeoHashUtils.add_edge_geo_hash_code_data(edge_dict[edge_id], geo_hash_zone_dict,
                                                     geo_hash_code_precision=geo_hash_code_precision)
        return geo_hash_zone_dict

    @staticmethod
    def add_node_geo_hash_code_data(node, geo_hash_code_precision=6):
        node.add_belong_element('geo_hash_code', geohash.encode(node.get_lat(), node.get_lon(),
                                                                precision=geo_hash_code_precision))

        return node

    @staticmethod
    def add_node_dict_geo_hash_code_data(node_dict, geo_hash_code_precision):
        for node_id in node_dict:
            node_dict[node_id] = GeoHashUtils.add_node_geo_hash_code_data(node_dict[node_id],
                                                                          geo_hash_code_precision=geo_hash_code_precision)
        return node_dict

    @staticmethod
    def init_geohash_box_zone_dict(zone_dict):
        geohash_box_zone_dict = ZoneDict()
        for zone_id in zone_dict:
            zone_contains_geo_hash_code_list = zone_dict[zone_id].get_inner_element_set()['zone_contains_geo_hash_code']
            zone_intersects_geo_hash_code_list = zone_dict[zone_id].get_inner_element_set()[
                'zone_intersects_geo_hash_code']
            for geohash_code in zone_contains_geo_hash_code_list:
                geohash_box_zone = Zone(
                    zone_id=geohash_code,
                    inner_elements_index_dict=None,
                    zone_type='geo_hash_box',
                    polygon=GeoHashUtils.init_geo_hash_code_rectangle_polygon(geohash_code))
                geohash_box_zone.add_inner_element('belong_zone_id', zone_id)
                geohash_box_zone_dict.add_zone(geohash_box_zone)
            for geohash_code in zone_intersects_geo_hash_code_list:
                if geohash_code in geohash_box_zone_dict.keys():
                    geohash_box_zone_dict[geohash_code].add_inner_element('belong_zone_id', zone_id)
                else:
                    geohash_box_zone = Zone(
                        zone_id=geohash_code,
                        inner_elements_index_dict=None,
                        zone_type='geo_hash_box',
                        polygon=GeoHashUtils.init_geo_hash_code_rectangle_polygon(geohash_code))
                    geohash_box_zone.add_inner_element('belong_zone_id', zone_id)
                    geohash_box_zone_dict.add_zone(geohash_box_zone)
        return geohash_box_zone_dict

    @staticmethod
    def search_zone_inner_node(zone, node_dict):
        zone_contains_geo_hash_code_list = zone.get_inner_element_set()['zone_contains_geo_hash_code']
        zone_intersects_geo_hash_code_list = zone.get_inner_element_set()['zone_intersects_geo_hash_code']
        zone_lower_pre_geo_hash_code_list = list(
            set([geo_hash_code[0:len(geo_hash_code) - 2] for geo_hash_code in zone_contains_geo_hash_code_list])) + \
                                            list(set([geo_hash_code[0:len(geo_hash_code) - 2] for geo_hash_code in
                                                      zone_intersects_geo_hash_code_list]))
        node_dict_ = {node_id: node_dict[node_id] for node_id in node_dict if
                      node_dict[node_id].get_belong_element_id_dict()['geo_hash_code'][0][
                      0:len(zone_intersects_geo_hash_code_list[0]) - 2] in zone_lower_pre_geo_hash_code_list}
        return [node_id for node_id in node_dict_
                if
                node_dict[node_id].get_belong_element_id_dict()['geo_hash_code'][
                    0] in zone_contains_geo_hash_code_list or
                (node_dict[node_id].get_belong_element_id_dict()['geo_hash_code'][
                     0] in zone_intersects_geo_hash_code_list and
                 GeoHashUtils.point_in_polygon(node_dict[node_id].get_lon(), node_dict[node_id].get_lat(),
                                               zone.get_polygon()))]

    @staticmethod
    def search_node_belong_to_zone(node, geohash_box_zone_dict, zone_dict):
        if 'belong_zone_id' in geohash_box_zone_dict[
            node.get_belong_element_id_dict()['geo_hash_code'][0]].get_inner_element_set().keys():
            zone_id_list = \
                geohash_box_zone_dict[node.get_belong_element_id_dict()['geo_hash_code'][0]].get_inner_element_set()[
                    'belong_zone_id']
            if zone_id_list:
                if len(zone_id_list) == 1:
                    return zone_id_list[0]
                else:
                    for zone_id in zone_id_list:
                        if GeoHashUtils.point_in_polygon(node.get_lon(), node.get_lat(),
                                                         zone_dict[zone_id].get_polygon()):
                            return zone_id
            else:
                return None
        else:
            return None

    @staticmethod
    def point_in_polygon(longitude, latitude, polygon):
        """
            判断点是否在多边形内
            :param longitude:
            :param latitude:
            :param polygon:
            :return:
            """
        return geometry.Point(longitude, latitude).within(geometry.shape(polygon)).__bool__()

    @staticmethod
    def search_zone_inner_node_(zone, geohash_box_zone_dict, node_dict):
        zone_inner_node_id_list = []
        zone_contains_geo_hash_code_list = zone.get_inner_element_set()['zone_contains_geo_hash_code']
        zone_intersects_geo_hash_code_list = zone.get_inner_element_set()['zone_intersects_geo_hash_code']
        for zone_contains_geo_hash_code in zone_contains_geo_hash_code_list:
            if 'inner_node_id' in geohash_box_zone_dict[zone_contains_geo_hash_code].get_inner_element_set():
                zone_inner_node_id_list = zone_inner_node_id_list + \
                                          geohash_box_zone_dict[zone_contains_geo_hash_code].get_inner_element_set()[
                                              'inner_node_id']
        for zone_intersects_geo_hash_code in zone_intersects_geo_hash_code_list:
            if 'inner_node_id' in geohash_box_zone_dict[zone_intersects_geo_hash_code].get_inner_element_set():
                zone_inner_node_id_list = zone_inner_node_id_list + [node_id for node_id in geohash_box_zone_dict[
                    zone_intersects_geo_hash_code].get_inner_element_set()[
                    'inner_node_id'] if GeoHashUtils.point_in_polygon(node_dict[node_id].get_lon(),
                                                                      node_dict[node_id].get_lat(),
                                                                      zone.get_polygon())]
        return zone_inner_node_id_list

    @staticmethod
    def search_node_neighbour_nodes(node, node_dict, geohash_box_zone_dict, distance_limit):
        """
        查询节点附近的节点
        Args:
            node: 节点
            node_dict: 节点集合
            geohash_box_zone_dict: 矩形区域集合
            distance_limit: 距离范围

        Returns:

        """
        node_circle_zone = Zone(
            zone_id=node.get_id() + '_' + 'circle',
            inner_elements_index_dict=None,
            zone_type=None,
            polygon=Point([node.get_lon(), node.get_lat()]).buffer(distance_limit / 100000))
        node_circle_zone = GeoHashUtils.add_zone_geo_hash_code_data(node_circle_zone,
                                                                    geo_hash_code_precision=6)
        zone_contains_geo_hash_code_list = node_circle_zone.get_inner_element_set()['zone_contains_geo_hash_code']
        zone_intersects_geo_hash_code_list = node_circle_zone.get_inner_element_set()['zone_intersects_geo_hash_code']

        for geohash_code in zone_contains_geo_hash_code_list:
            geohash_box_zone_dict[geohash_code].add_inner_element('belong_zone_id', node_circle_zone.get_id())
        for geohash_code in zone_intersects_geo_hash_code_list:
            if geohash_code in geohash_box_zone_dict.keys():
                geohash_box_zone_dict[geohash_code].add_inner_element('belong_zone_id', node_circle_zone.get_id())
            else:
                geohash_box_zone = Zone(
                    zone_id=geohash_code,
                    inner_elements_index_dict=None,
                    zone_type='geo_hash_box',
                    polygon=GeoHashUtils.init_geo_hash_code_rectangle_polygon(geohash_code))
                geohash_box_zone.add_inner_element('belong_zone_id', node_circle_zone.get_id())
                geohash_box_zone_dict.add_zone(geohash_box_zone)
        return GeoHashUtils.search_zone_inner_node_(node_circle_zone, geohash_box_zone_dict, node_dict)

    @staticmethod
    def find(zone_dict, node_dict):
        for node_id in node_dict.keys():
            for zone_id in zone_dict.keys():
                if GeoHashUtils.point_in_polygon(node_dict[node_id].get_lon(), node_dict[node_id].get_lat(),
                                                 zone_dict[zone_id].get_polygon()):
                    break
        return node_dict

    @staticmethod
    def add_node_belong_to_zone(physical_node_dict, zone_dict):
        """
        节点区域匹配
        Args:
            physical_node_dict: 物理站点集合
            zone_dict: 区域集合

        Returns:
            包含所属区域ID的物理站点集合

        """
        zone_and_node_rtree_index = GeoHashUtils.init_zone_and_node_rtree(zone_dict, physical_node_dict)
        for node_id in physical_node_dict.keys():
            belong_zone_id = GeoHashUtils.get_point_belong_to_zone(zone_and_node_rtree_index,
                                                                   physical_node_dict[node_id])
            physical_node_dict[node_id].add_belong_element('belong_zone_id', belong_zone_id)

        return physical_node_dict

    @staticmethod
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
                                                 Point(node_dict[node_id].get_lon(),
                                                       node_dict[node_id].get_lat()).bounds),
                                             obj=node_dict[node_id])
            node_index = node_index + 1
        return zone_and_node_rtree_index

    @staticmethod
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


if __name__ == '__main__':
    road_edge_dict = EdgeDict.load_from_json(EdgeDict(), '../res/json/test_edges.json')
    road_node_dict = NodeDict.load_from_json(NodeDict(), '../res/json/test_nodes.json')
    start_time = datetime.now()
    #
    geo_hash_box_zone_dict = GeoHashUtils.init_geo_hash_box_zone_dict(road_edge_dict, geo_hash_code_precision=6)
    GeoHashUtils.add_edge_dict_geo_hash_code_data(road_edge_dict, geo_hash_box_zone_dict, geo_hash_code_precision=6)
    geo_hash_box_zone_dict.save_to_json('../../../res/json/test.json')
    end_time = datetime.now()
    print((end_time - start_time).total_seconds())
    geo_hash_box_zone_dict = ZoneDict.load_from_json(ZoneDict(), '../../../res/json/geo_hash_box_zone_edges.json')
    # 地图匹配
    node_gsp = '114.073143;22.606761'
    start_time = datetime.now()
    min_distance_edge_id_dict = MapMatching.match_point_to_nearest_edge(node_gsp,
                                                                        geo_hash_zone_dict=geo_hash_box_zone_dict,
                                                                        edge_dict=road_edge_dict)
    end_time = datetime.now()
    print('地图匹配耗时：', (end_time - start_time).total_seconds())
    # 线条基于打断点打断
    # line = LineString(
    #         [(114.300495, 22.593601), (114.300364, 22.593370999999998), (114.30018799999999, 22.593152999999997),
    #          (114.299882, 22.592897999999998), (114.299264, 22.592384), (114.29906, 22.592076),
    #          (114.298947, 22.591421999999998)])
    # # cut_line_list = GeometryUtils.cut_edge_with_distance(line, distance=50)
    # cut_line_list = GeometryUtils.cut_line_segment_with_point(LineString([(114.07034, 22.610956),
    #                                                                       (114.070168, 22.610584),
    #                                                                       (114.069561, 22.609683),
    #                                                                       (114.06915, 22.60922)]),Point(114.069561, 22.609683))
    # from ...algorithm.graph_generation.graph_generation import GridGraphGeneration
    # from ...algorithm.graph_generation.graph_generation import read_json
    #
    # # 匹配打断
    # stations_json_data = read_json('../../../res/json/t_bus_info_stop_data.json')
    # search_nodes_id_list = list(
    #     set([str(row['stop_id']) for row in json.loads(stations_json_data)['t_bus_info_stop_data']]))
    # search_nodes_gps_list = list(set([str(row['lon']) + ';' + str(row['lat']) for row in
    #                                   json.loads(stations_json_data)['t_bus_info_stop_data']]))
    # print(len(search_nodes_id_list))
    # zone = geo_hash_box_zone_dict['ws13vt']
    # geo_def = geopandas.GeoDataFrame()
    # print(zone.get_polygon())
    # geo_def['geometry'] = [Polygon(zone.get_polygon())]
    # geo_def['id'] = [1]
    # geo_def.to_file( "C:\\Users\\lenovo\\Desktop\\GIS数据\\深圳路网\\84\\new\\zone.shp")
    start_time = datetime.now()
    new_walk_edge_dict, new_walk_node_dict = GridGraphGeneration.add_cut_walk_edge_and_node(
        search_nodes_id_list=search_nodes_id_list,
        search_nodes_gps_list=search_nodes_gps_list,
        edge_dict=walk_edge_dict, node_dict=walk_node_dict)
    print(len(new_walk_edge_dict), len(new_walk_node_dict))
    end_time = datetime.now()
    print('全市站点地图匹配打断耗时：', (end_time - start_time).total_seconds())
