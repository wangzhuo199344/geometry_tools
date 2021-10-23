from shapely import wkt
from shapely.geometry import LineString, Point, Polygon
from collections import deque

from element.graph.edge_dict import EdgeDict
from utils.projection_utils import CoordinateTransfer
from element.graph.node import NodeWithGPSAndTypeAndNeighborSetAndBelonging
from element.graph.node_dict import NodeDict
from element.map.zone import Zone
from element.map.zone_dict import ZoneDict

"""
@File  :geometry_utils.py
@Author: 王卓
@Date  : ${2021-5-17} ${16:50}
"""


class GeometryUtils(object):
    @staticmethod
    def split(line_string, point):
        coords = list(line_string.coords)
        j = None
        for i in range(len(coords) - 1):
            if LineString(coords[i:i + 2]).intersects(point):
                j = i
                break
        assert j is not None
        if Point(coords[j + 1:j + 2]).equals(point):
            return coords[:j + 2], coords[j + 1:]
        else:
            return coords[:j + 1], coords[j + 1:]

    @staticmethod
    def cut_edge_with_distance(line: LineString, distance: float) -> list:
        """
        以固定距离切分edge
        Args:
            line: edge线性（LineString）
            distance: 定长参数（单位：米）

        Returns:

        """
        # Cuts a line in two at a distance from its starting point
        # 坐标投影
        global after_line
        cut_line_list = []
        line = LineString([CoordinateTransfer.wgs84_to_web_mercator(coord[0], coord[1]) for coord in list(line.coords)])
        if distance <= 0.0 or distance >= line.length:
            return [line]
        else:
            while 0.0 < distance < line.length:
                coords = list(line.coords)
                for i, p in enumerate(coords):
                    pd = line.project(Point(p))
                    if pd == distance:
                        pre_line = LineString(
                            [CoordinateTransfer.web_mercator_to_wgs84(coord[0], coord[1]) for coord in coords[:i + 1]])
                        after_line = LineString([(coord[0], coord[1]) for coord in coords[i:]])
                        cut_line_list.append(pre_line)
                        if after_line.length <= distance:
                            cut_line_list.append(LineString(
                                [CoordinateTransfer.web_mercator_to_wgs84(coord[0], coord[1]) for coord in coords[i:]]))

                        break
                    if pd > distance:
                        cp = line.interpolate(distance)

                        pre_line = LineString([CoordinateTransfer.web_mercator_to_wgs84(coord[0], coord[1]) for coord in
                                               (coords[:i] + [(cp.x, cp.y)])])
                        after_line = LineString([(coord[0], coord[1]) for coord in
                                                 ([(cp.x, cp.y)] + coords[i:])])
                        cut_line_list.append(pre_line)
                        if after_line.length <= distance:
                            cut_line_list.append(
                                LineString([CoordinateTransfer.web_mercator_to_wgs84(coord[0], coord[1]) for coord in
                                            ([(cp.x, cp.y)] + coords[i:])]))
                        break
                line = after_line
        return cut_line_list

    @staticmethod
    def cut_line_segment_with_point(line_string: LineString, break_point: Point):
        """
        基于点将线段打断
        Args:
            line_string: 线段
            break_point: 打断点

        Returns:

        """
        geo_loc = line_string.coords
        point_loc = list(break_point.coords)
        j = None

        if len(list(geo_loc)) == 2:
            return [geo_loc[0], point_loc[0]], [point_loc[0], geo_loc[1]]
        else:
            for i in range(len(geo_loc) - 1):
                if LineString(geo_loc[i:i + 2]).intersects(break_point):
                    j = i
                    break
            if j:
                if Point(geo_loc[j + 1:j + 2]).equals(break_point):
                    return geo_loc[:j + 2], geo_loc[j + 1:] + geo_loc[j + 1:j + 2]
                else:
                    return geo_loc[:j + 1], geo_loc[j:]
            else:
                if geo_loc[0][0] < geo_loc[-1][0]:
                    for n in range(len(geo_loc) - 1):
                        if geo_loc[n][0] <= point_loc[0][0] <= geo_loc[n + 1][0]:
                            j = n
                            break
                    return geo_loc[:j + 1] + point_loc + point_loc, point_loc + point_loc + geo_loc[j + 1:]
                else:
                    for n in range(len(geo_loc) - 1):
                        if geo_loc[n][0] >= point_loc[0][0] >= geo_loc[n + 1][0]:
                            j = n
                            break
                    return geo_loc[:j + 1] + point_loc + point_loc, point_loc + point_loc + geo_loc[j + 1:]

    @staticmethod
    def transfer_edge_to_line_string(line_data):
        if isinstance(line_data, str):
            return wkt.loads(line_data)
        elif isinstance(line_data, list):
            return LineString(line_data)
        else:
            return line_data

    @staticmethod
    def transfer_zone_to_line_polygon(zone_data):
        if isinstance(zone_data, str):
            return wkt.loads(zone_data)
        elif isinstance(zone_data, list):
            return Polygon(zone_data)
        else:
            return zone_data


if __name__ == "__main__":
    network_edges_dict = EdgeDict.load_from_json(EdgeDict(), '../../../res/json/walk_edges.json')
    edge_id = ('1739', '3159')
    print(network_edges_dict[edge_id])
    # GridGraphGeneration.cut_edge_with_limit_distance(edge, dist=50)
