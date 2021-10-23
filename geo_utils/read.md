功能说明：
geo_hash_utils - 节点、线匹空间配工具
geometry_utils - 线型打断工具
projection_utils - 坐标转换工具
rtree_utils - 节点、区域匹配工具

环境依赖：
  python3.8

公共库依赖：
  shapely
  rtree
  python-geohash
  geopandas

自定义类说明：
1. element.graph.node
Node # 自定义节点类
  Format:
		Node:
      - node_id: string # 节点ID
        node_coord: string # 节点坐标
        node_name: string # 节点名称
        node_type: string# 节点类型
        neighbor_node_id_set: set # 相邻节点ID集合
        belong_element_id_dict:
          belong_zone_id:
            - string # 所属区域ID
          route_id:
            - string # 所属线路ID
2. element.graph.edge
Edge # 自定义边类
  Format:
		Edge:
      - edge_id: string # 默认使用 (from_node_id, to_node_id)
        from_node_id: string # 起点id
        to_node_id: string # 终点id
        geometry: string # GEO_WKT
        res_cost_dict:
          distance: string # 路段行驶距离
          time: string # 路段行驶时间
        fix_res_cost:
          wgs_84_distance_in_meter: string # wgs84投影球面距离
3. element.map.zone
Zone # 自定义区域类
  Format:
		Zone:
      - zone_id: string # 区域ID
        zone_type: string # 区域类型
        polygon: string # 区域边界坐标GEO_WKT
        inner_elements_index_dict:
          neighbour_zone_id_list:
            - list # 相邻区域ID列表

一、空间关系判定工具说明：
1.点、区域空间关系判定 rtree_utils
实现原理：构建点、区域空间搜索树（Rtree）计算点、区域空间关系
1.1计算点所属区域(get_point_belong_to_zone_example())
Input:
  node_dict: dict # 节点数据字典 
    - key:string # 节点ID
	- value:Node # 自定义节点类

  zone_dict: dict # 区域数据字典 
    - key:string # 节点ID
	- value:Zone # 自定义区域类

Return:
      belong_zone_id: string # 所属区域ID
	  
	  
1.2 计算区域包含节点ID(get_zone_inner_point_id_list_example())
Input:
  node_dict: dict # 节点数据字典 
    - key:string # 节点ID
	- value:Node # 自定义节点类
  zone_dict: dict # 区域数据字典 
    - key:string # 节点ID
	- value:Zone # 自定义区域类

Return:
      zone_inner_node_id_list: list # 区域包含节点ID列表

1.3 计算区域相邻区域ID(get_neighbour_zone_id_list_example())
Input:
  zone_dict: dict # 区域数据字典 
    - key:string # 节点ID
	- value:Zone # 自定义区域类

Return:
      neighbour_zone_id_list: list # 相邻区域ID列表
      
1.4 计算节点相邻节点ID(get_node_nearest_node_example())
Input:
  node_dict: dict # 节点数据字典 
    - key:string # 节点ID
	- value:Node # 自定义节点类

Return:
      nearest_node_id_list: list # 最近邻节点ID列表
      
2.点、线空间匹配 geo_hash_utils
实现原理：对线型数据进行geo_hash编码，得到geohash区域包含和相交的边id,对匹配点进行geohash编码，利用广度优先搜索将点匹配至最近的边
1.5 点、线空间匹配 match_node_to_nearest_edge_example()
Input:
  node_gsp：string 带匹配的node节点坐标字符串 '114.073143;22.606761'
  edge_dict: dict # 边数据字典
    - key:tuple # 边ID
	- value:edge # 自定义edge

Return:
      min_distance_edge_id_dict: dict # 匹配结果字典
	    min_distance：float # 点与最近边投影距离
		min_distance_edge_id：string# 点匹配最近边ID
		polate_point：tuple# 匹配投影后的节点坐标
		
二、lineString边打断 geometry_utils

2.1 按固定长度打断边 cut_edge_with_fix_length()
Input: 
  line: LineString # 待打断线型数据
  distance：打断固长度参数（单位：米）
Return:
  cut_line_list：list # 打断后的线型列表

2.2 按固定点打断边 cut_line_segment_with_point()
Input: 
  line: LineString # 待打断线型数据
  break_point：Point 打断点
Return:
  cut_line_list：list # 打断后的线型列表
  
三、坐标转换 projection_utils

3.1 84转火星 wgs84togcj02()
Input: 
  longitude: float # 经度
  latitude： float # 纬度
Return:
  mars_longitude: float # 火星坐标系经度
  mars_latitude： float # 火星坐标系纬度 
  
3.2 火星转84 gcj02towgs84()
Input: 
  longitude: float # 经度
  latitude： float # 纬度
Return:
  wgs_longitude: float # 84坐标系经度
  wgs_latitude： float # 84坐标系纬度
3.3 84转墨卡托 wgs84_to_web_mercator()
Input: 
  longitude: float # 经度
  latitude： float # 纬度
Return:
  x: float # 墨卡托坐标系横轴
  y：float # 墨卡托坐标系纵轴 
  
3.4 墨卡托84 web_mercator_to_wgs84()
Input: 
  x: float # 墨卡托坐标系横轴
  y：float # 墨卡托坐标系纵轴
Return:
  wgs_longitude: float # 84坐标系经度
  wgs_latitude： float # 84坐标系纬度
3.5 计算两个坐标点球面距离：haversine()
Input: 
  lon1: float #第一个坐标的经度
  lat1: float #第一个坐标的纬度
  lon2: float #第二个坐标的经度
  lat2: float #第二个坐标的纬度
Return:
  distance: float # 球面直线距离（单位：米）
