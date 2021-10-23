from shapely.geometry import Point


class Node(object):

    def __init__(self, node_id):
        self.__node_id = str(node_id)

    def get_id(self): return self.__node_id

    def __repr__(self):
        return "\n<Node>\nID:{}".format(self.get_id())

    def get_json_string(self):
        return {
            "node_id": self.get_id(),
        }


class NodeWithGPS(Node):

    def __init__(self, node_id, node_coord):
        super().__init__(node_id)
        self.__lon, self.__lat = node_coord

    def __repr__(self):
        return Node.__repr__(self) + "\nGPS:{}".format(self.get_GPS())

    def get_lon(self):
        return self.__lon

    def get_lat(self):
        return self.__lat

    def get_GPS(self):
        return self.__lon, self.__lat

    def is_in_polygon(self, polygon):
        return True if Point(self.get_GPS()).within(polygon) else False

    def get_json_string(self):
        return {**Node.get_json_string(self), **{
            "node_coord": self.get_GPS(),
        }}


class NodeWithGPSAndName(NodeWithGPS):

    def __init__(self, node_id, node_coord, node_name):
        super().__init__(node_id, node_coord)
        self.__node_name = node_name

    def __repr__(self):
        return NodeWithGPS.__repr__(self) + "\nName:{}".format(
            self.get_node_name()
        )

    def get_node_name(self):
        return self.__node_name

    def get_json_string(self):
        return {**NodeWithGPS.get_json_string(self), **{
            "node_name": self.get_node_name(),
        }}


class NodeWithGPSAndSpecificType(NodeWithGPSAndName):

    def __init__(self, node_id, node_coord, node_name, node_type):
        super().__init__(node_id, node_coord, node_name)
        self.__node_type = node_type

    def get_node_type(self): return self.__node_type

    def __repr__(self):
        return NodeWithGPSAndName.__repr__(self) + "\nNodeType:{}".format(
            self.get_node_type()
        )

    def get_json_string(self):
        return {**NodeWithGPSAndName.get_json_string(self), **{
            "node_type": self.get_node_type(),
        }}


class NodeWithGPSAndTypeAndNeighborSet(NodeWithGPSAndSpecificType):

    def __init__(self, node_id, node_coord, node_name, node_type, neighbor_node_id_set=None):
        super().__init__(node_id, node_coord, node_name, node_type)
        if neighbor_node_id_set:
            self.__neighbor_node_id_set = eval(str(neighbor_node_id_set))
        else:
            self.__neighbor_node_id_set = set()

    def get_neighbor_node_id_set(self):
        return self.__neighbor_node_id_set

    def add_neighbor_node_id_set(self, element_id):
        # if self.__neighbor_node_id_set:
        #     set(self.__neighbor_node_id_set).add(element_id)
        # else:

        self.__neighbor_node_id_set.add(element_id)

    def __repr__(self):
        return NodeWithGPSAndSpecificType.__repr__(self) + "\nNeighborNodeIdSet:{}".format(
            self.get_neighbor_node_id_set()
        )

    def get_json_string(self):
        return {**NodeWithGPSAndSpecificType.get_json_string(self), **{
            "neighbor_node_id_set": str(self.get_neighbor_node_id_set()),
        }}


class NodeWithGPSAndTypeAndNeighborSetAndBelonging(NodeWithGPSAndTypeAndNeighborSet):

    def __init__(self, node_id, node_coord, node_name, node_type, neighbor_node_id_set=None,
                 belong_element_id_dict=None):
        super().__init__(node_id, node_coord, node_name, node_type, neighbor_node_id_set)
        if belong_element_id_dict:
            self.belong_element_id_dict = belong_element_id_dict
        else:
            self.belong_element_id_dict = dict()

    def get_belong_element_id_dict(self):
        return self.belong_element_id_dict

    def add_belong_element(self, element_dict_name, element_id):
        if element_dict_name not in self.belong_element_id_dict:
            self.belong_element_id_dict[element_dict_name] = [element_id]
        else:
            self.belong_element_id_dict[element_dict_name].append(element_id)

    def __repr__(self):
        return NodeWithGPSAndTypeAndNeighborSet.__repr__(self) + "\nBelongElementIdDict:{}".format(
            self.get_belong_element_id_dict()
        )

    def get_json_string(self):
        return {**NodeWithGPSAndTypeAndNeighborSet.get_json_string(self), **{
            "belong_element_id_dict": self.get_belong_element_id_dict(),
        }}


if __name__ == '__main__':
    from shapely.geometry import Polygon

    coords = Polygon([(114.27, 22.60),
                      (114.27, 22.58),
                      (114.24, 22.58),
                      (114.24, 22.60),
                      (114.27, 22.60)])
    poly = Polygon(coords)
    node = NodeWithGPS('a', (114.25, 22.59))
    print(node.is_in_polygon(poly))
