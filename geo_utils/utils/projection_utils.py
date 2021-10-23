#!/usr/bin/python3.7
# coding: utf-8

"""
@file   : projection_utils.py
@date   : 2021/5/18
@author : zhuyuanqi@sutpc.com
"""
import math


class CoordinateTransfer:
    """ 地理坐标转化工具，提供3种主要功能
    1 wgs84转火星
    2 火星转wgs84
    3 计算两点的haversine距离
    """

    def __init__(self):
        self.x_pi = 3.14159265358979324 * 3000.0 / 180.0
        self.pi = 3.1415926535897932384626  # π
        self.a = 6378245.0  # 长半轴
        self.ee = 0.00669342162296594323  # 扁率

    def wgs84togcj02(self, lng, lat):
        """WGS84转GCJ02(火星坐标系)

        Args:
            lng: WGS84坐标系的经度
            lat: WGS84坐标系的纬度

        Returns:
            火星坐标系的经度、纬度
        """
        if self.wgs84_out_of_china(lng, lat):  # 判断是否在国内
            Warning("WARNING: WGS Coord ({},{}) is out of china!".format(lng, lat))
        dlat = self.transformlat(lng - 105.0, lat - 35.0)
        dlng = self.transformlng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * self.pi
        magic = math.sin(radlat)
        magic = 1 - self.ee * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((self.a * (1 - self.ee)) / (magic * sqrtmagic) * self.pi)
        dlng = (dlng * 180.0) / ((self.a / sqrtmagic * math.cos(radlat) * (self.pi)))
        mglat = lat + dlat
        mglng = lng + dlng
        return mglng, mglat

    def gcj02towgs84(self, lng, lat):
        """GCJ02(火星坐标系)转GPS84

        Args:
            lng: 火星坐标系的经度
            lat: 火星坐标系纬度

        Returns:
            WGS84坐标系的经度、纬度
        """

        dlat = self.transformlat(lng - 105.0, lat - 35.0)
        dlng = self.transformlng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * self.pi
        magic = math.sin(radlat)
        magic = 1 - self.ee * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((self.a * (1 - self.ee)) / (magic * sqrtmagic) * self.pi)
        dlng = (dlng * 180.0) / (self.a / sqrtmagic * math.cos(radlat) * self.pi)
        mglat = lat + dlat
        mglng = lng + dlng
        if self.wgs84_out_of_china(lng * 2 - mglng, lat * 2 - mglat):
            Warning("WARNING: GCJ02 Coord ({},{}) is out of china!".format(lng, lat))
        return lng * 2 - mglng, lat * 2 - mglat

    def transformlat(self, lng, lat):
        ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
              0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
        ret += (20.0 * math.sin(6.0 * lng * self.pi) + 20.0 *
                math.sin(2.0 * lng * self.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lat * self.pi) + 40.0 *
                math.sin(lat / 3.0 * self.pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(lat / 12.0 * self.pi) + 320 *
                math.sin(lat * self.pi / 30.0)) * 2.0 / 3.0
        return ret

    def transformlng(self, lng, lat):
        ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
              0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
        ret += (20.0 * math.sin(6.0 * lng * self.pi) + 20.0 *
                math.sin(2.0 * lng * self.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lng * self.pi) + 40.0 *
                math.sin(lng / 3.0 * self.pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(lng / 12.0 * self.pi) + 300.0 *
                math.sin(lng / 30.0 * self.pi)) * 2.0 / 3.0
        return ret

    def wgs84_out_of_china(self, lng, lat):
        """粗略判断坐标是否在国内，不在国内不做偏移

        Args:
            lng:坐标经度
            lat:坐标纬度

        Returns:
            布尔值，如果在中国境内返回False,否则Navigation返回True
        """
        if lng < 72.004 or lng > 137.8347:
            return True
        if lat < 0.8293 or lat > 55.8271:
            return True
        return False

    def haversine(self, lon1, lat1, lon2, lat2):
        """ Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)

        Args:
            lon1:第一个坐标的经度
            lat1:第一个坐标的纬度
            lon2:第二个坐标的经度
            lat2:第二个坐标的纬度

        Returns:
            两个坐标之间的Haversine距离
        """
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        r = self.a  # Radius of earth in kilometers. Use 3956 for miles
        return c * r

    @staticmethod
    def wgs84_to_web_mercator(lon, lat):
        x = lon * 20037508.342789 / 180
        y = math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180)
        y = y * 20037508.34789 / 180
        return x, y

    @staticmethod
    def web_mercator_to_wgs84(x, y):
        lon = x / 20037508.34 * 180
        lat = y / 20037508.34 * 180
        lat = 180 / math.pi * (2 * math.atan(math.exp(lat * math.pi / 180)) - math.pi / 2)
        return lon, lat
