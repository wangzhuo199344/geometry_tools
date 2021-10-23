from element.element_dict import ElementDict
from element.graph.edge import EdgeWithResCostAndFixCost
from element.graph.node_dict import NodeDict
from element.graph.node import NodeWithGPSAndTypeAndNeighborSet
import shapely.wkt
class EdgeDict(ElementDict):
    """
    边字典集合
    """

    def __init__(self, name=''):
        if name:
            super().__init__('_'.join(['EdgeDict', name]))
        else:
            super().__init__('EdgeDict')

    def add_edge(self, edge):
        self[edge.get_id()] = edge

    def select_by_node_dict(self, node_dict):
        import copy
        selected_dict = copy.deepcopy(self)
        for edge_id, edge in self.items():
            if edge.is_in_node_dict(node_dict):
                pass
            else:
                del selected_dict[edge_id]
        return selected_dict

    def cal_all_nodes_id(self):
        nodes = set()
        for e in self:
            nodes.update(set(e))
        return nodes
        # return {k:v for k, v in selected_dict.items() if v.is_in_node_dict(node_dict)}

    # def save_to_json(self, edge_json_path):
    #     json_dict = {"Edges": []}
    #     for edge_id, edge in self.items():
    #         json_dict['Edges'].append(edge.get_json_string())
    #     self.dict_2_json(json_dict, edge_json_path)
    #
    # def load_from_json(self, edge_json_path):
    #     json_dict = self.json_2_dict(edge_json_path)
    #     for edge in json_dict['Edges']:
    #         new_edge = EdgeWithResCostAndFixCost(**edge)
    #         self.add_edge(new_edge)


if __name__ == '__main__':
    # # 初始化edge集合
    # edge_dict = EdgeDict()
    # # 将edge加入edge集合
    # edge_dict.add_edge(
    #     EdgeWithResCostAndFixCost(from_node_id='eo1', to_node_id='ed2',geometry =None, res_cost_dict=None))
    # edge_dict.add_edge(
    #     EdgeWithResCostAndFixCost( from_node_id='eo2', to_node_id='ed2', res_cost_dict=None))
    # # 保存为静态json数据
    # edge_dict.save_to_json('../../res/edge.json')

    # 读取静态数据
    new_edge_dict = EdgeDict()
    new_edge_dict.load_from_json('../../res/json/test_edges.json')

