class Edge(object):
    """
    边
    """

    def __init__(self, from_node_id, to_node_id, geometry=None):
        self.__from_node_id = str(from_node_id)
        self.__to_node_id = str(to_node_id)
        self.__edge_id = (self.__from_node_id, self.__to_node_id)
        self.__geometry = None
        self.set_geometry(geometry)

    def __repr__(self):
        return "\n<Edge>\nID:{}\nGeometry:{}".format((self.get_from_node_id(), self.get_to_node_id()),
                                                     self.get_geometry())

    def get_id(self):
        return self.__edge_id

    def get_vnode_tuple(self):
        return self.__from_node_id, self.__to_node_id

    def get_from_node_id(self):
        return self.__from_node_id

    def get_to_node_id(self):
        return self.__to_node_id

    def get_geometry(self):
        return self.__geometry

    def set_geometry(self, geometry):
        if not geometry:
            self.__geometry = []
        else:
            self.__geometry = geometry

    def is_in_node_dict(self, node_dict):
        if ((self.get_from_node_id() in node_dict) and (self.get_to_node_id() in node_dict)):
            return True
        else:
            return False

    def get_json_string(self):
        return {
            "from_node_id": self.get_from_node_id(),
            "to_node_id": self.get_to_node_id(),
            "geometry": self.get_geometry()
        }


class EdgeWithResCost(Edge):

    def __init__(self, from_node_id, to_node_id, geometry=None, res_cost_dict=None):
        super().__init__(from_node_id, to_node_id, geometry)
        if not res_cost_dict:
            self.__res_cost_dict = {}
        else:
            self.__res_cost_dict = res_cost_dict

    def __repr__(self):
        return Edge.__repr__(self) + "\nResCost:{}".format(self.get_res_cost())

    def get_res_cost(self):
        return self.__res_cost_dict

    def view_res_cost(self):
        print(self.__res_cost_dict)

    def get_typical_res_cost(self, res_type):
        return self.__res_cost_dict[res_type]

    def set_typical_res_cost(self, res_type, res_cost):
        self.__res_cost_dict[res_type] = res_cost

    def get_res_cost_types(self):
        return set(self.__res_cost_dict)

    def get_json_string(self):
        return {**Edge.get_json_string(self), **{
            "res_cost_dict": self.get_res_cost(),
        }}


class EdgeWithResCostAndFixCost(EdgeWithResCost):

    def __init__(self, from_node_id, to_node_id, geometry=None, res_cost_dict=None, fix_res_cost=None):
        super().__init__(from_node_id, to_node_id, geometry, res_cost_dict)
        if not fix_res_cost:
            self.__fix_cost_dict = {}
        else:
            self.__fix_cost_dict = fix_res_cost

    def __repr__(self):
        return EdgeWithResCost.__repr__(self) + "\nFixCost:{}".format(self.get_fix_cost())

    def get_fix_cost(self):
        return self.__fix_cost_dict

    def get_typical_fix_cost(self, res_type):
        return self.__fix_cost_dict[res_type]

    def set_typical_fix_cost(self, res_type, res_cost):
        self.__fix_cost_dict[res_type] = res_cost

    def get_json_string(self):
        return {**EdgeWithResCost.get_json_string(self), **{
            "fix_res_cost": self.get_fix_cost()
        }}


class EdgeWithResCostAndFixCostAndEdgeType(EdgeWithResCostAndFixCost):

    def __init__(self, from_node_id, to_node_id, geometry=None, res_cost_dict=None, fix_res_cost=None, edge_type=None):
        super().__init__(from_node_id, to_node_id, geometry, res_cost_dict, fix_res_cost)
        self.__edge_type = edge_type

    def get_edge_type(self): return self.__edge_type

    def __repr__(self):
        return EdgeWithResCostAndFixCost.__repr__(self) + "\nEdgeType:{}".format(self.get_edge_type())

    def get_json_string(self):
        return {**EdgeWithResCostAndFixCost.get_json_string(self), **{
            "edge_type": self.get_edge_type()
        }}


class EdgeWithResCostAndFixCostAndEdgeTypeAndRouteID(EdgeWithResCostAndFixCostAndEdgeType):

    def __init__(self, from_node_id, to_node_id, geometry=None, res_cost_dict=None, fix_res_cost=None, edge_type=None,
                 edge_belong_route_id=None):
        super().__init__(from_node_id, to_node_id, geometry, res_cost_dict, fix_res_cost, edge_type)

        self.__edge_belong_route_id = edge_belong_route_id

    def get_edge_belong_route_id(self): return self.__edge_belong_route_id

    def __repr__(self):
        return EdgeWithResCostAndFixCostAndEdgeType.__repr__(self) + "\nEdgeBelongRouteID:{}".format(
            self.get_edge_belong_route_id())

    def get_json_string(self):
        return {**EdgeWithResCostAndFixCostAndEdgeType.get_json_string(self), **{
            "edge_belong_route_id": self.get_edge_belong_route_id()
        }}


class EdgeWithResCostAndFixCostAndEdgeTypeAndRouteIDAndRoutePriority(EdgeWithResCostAndFixCostAndEdgeTypeAndRouteID):

    def __init__(self, from_node_id, to_node_id, geometry=None, res_cost_dict=None, fix_res_cost=None, edge_type=None,
                 edge_belong_route_id=None, edge_priority=None):
        super().__init__(from_node_id, to_node_id, geometry, res_cost_dict, fix_res_cost, edge_type,
                         edge_belong_route_id)

        self.__edge_priority = edge_priority

    def get_edge_priority(self): return self.__edge_priority

    def __repr__(self):
        return EdgeWithResCostAndFixCostAndEdgeTypeAndRouteID.__repr__(self) + "\nEdgePriority:{}".format(
            self.get_edge_priority())

    def get_json_string(self):
        return {**EdgeWithResCostAndFixCostAndEdgeTypeAndRouteID.get_json_string(self), **{
            "edge_priority": self.get_edge_priority()
        }}


class EdgeWithResCostAndFixCostAndEdgeTypeAndRouteIDAndRouteName(EdgeWithResCostAndFixCostAndEdgeTypeAndRouteID):

    def __init__(self, from_node_id, to_node_id, geometry=None, res_cost_dict=None, fix_res_cost=None, edge_type=None,
                 edge_belong_route_id=None, edge_belong_route_name=None):
        super().__init__(from_node_id, to_node_id, geometry, res_cost_dict, fix_res_cost, edge_type,
                         edge_belong_route_id)

        self.__edge_belong_route_name = edge_belong_route_name

    def get_edge_belong_route_name(self): return self.__edge_belong_route_id

    def __repr__(self):
        return EdgeWithResCostAndFixCostAndEdgeTypeAndRouteID.__repr__(self) + "\nEdgeBelongRouteName:{}".format(
            self.get_edge_belong_route_name())

    def get_json_string(self):
        return {**EdgeWithResCostAndFixCostAndEdgeTypeAndRouteID.get_json_string(self), **{
            "edge_belong_route_name": self.get_edge_belong_route_name()
        }}
