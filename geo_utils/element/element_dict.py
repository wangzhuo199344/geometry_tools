from random import sample, seed
from json import dump, load
import json
from element.graph.edge import EdgeWithResCostAndFixCostAndEdgeTypeAndRouteIDAndRouteName, \
    EdgeWithResCostAndFixCostAndEdgeTypeAndRouteID, EdgeWithResCostAndFixCostAndEdgeType, \
    EdgeWithResCostAndFixCost  # noqa
from element.graph.node import NodeWithGPSAndTypeAndNeighborSetAndBelonging, \
    NodeWithGPSAndTypeAndNeighborSet, \
    NodeWithGPSAndSpecificType  # noqa
from element.map.zone import Zone  # noqa



class ElementDict(dict):
    """
    Collection 类继承dict，是辅助各类算法实现的排序、索引、统计工具，
    针对不同类型的对象集合，设计高效、统一的筛选方法，能减少算法的代码冗余。

    Parameter:
    ----------

    """

    def __init__(self, name):
        super().__init__()
        self.__name = name

    def get_name(self):
        return self.__name

    def sorted_values(self):
        return sorted(self, key=lambda x: self[x])

    def add_element(self, element):
        self[element.get_id()] = element

    def merge_element_dict(self, element_dict):
        for k, v in element_dict.items():
            if k not in self:
                self[k] = v

    def random_select_one_element(self, random_seed=None):
        if random_seed:
            seed(random_seed)
        return sample(set(self.values()), 1)[0]

    def show_one_example(self):
        print(self.random_select_one_element())

    def random_select_k_element(self, k=5, random_seed=None):
        if random_seed:
            seed(random_seed)
        return sample(set(self.values()), k)

    def show_k_example(self, k=5):
        for element in self.random_select_k_element(k):
            print(element)

    def __repr__(self):
        return "{}(Size={})".format(self.get_name(), len(self))

    @staticmethod
    def dict_2_json(dict_, json_path):
        dump(dict_, open(json_path, 'w'))

    @staticmethod
    def json_2_dict(json_path):
        with open(json_path, 'r') as f:
            return load(f)

    @staticmethod
    def json_to_dict(json_string):
        return json.loads(json_string)

    @staticmethod
    def dict_to_json(dict_data):
        return json.dumps(dict_data)

    def to_dict(self):
        json_dict = {}
        for element_id, element in self.items():
            element_class_name = type(element).__name__
            if element_class_name in json_dict:
                json_dict[element_class_name].append(element.get_json_string())
            else:
                json_dict[element_class_name] = [element.get_json_string()]
        return json_dict

    def save_to_json(self, json_path):
        self.dict_2_json(self.to_dict(), json_path)

    def load_from_json(self, json_path):
        json_dict = self.json_2_dict(json_path)
        self.load_from_dict(json_dict)
        return self

    def load_from_json_data(self, json_string):
        json_dict = self.json_to_dict(json_string)
        self.load_from_dict(json_dict)
        return self

    def load_from_dict(self, json_dict):
        for element_class_name, element_list in json_dict.items():
            class_func = eval(element_class_name)
            for element in element_list:
                new_element = class_func(**element)
                self.add_element(new_element)
        print('[{}][Info] {} was read from json file'.format(__name__.split('.')[-1], self))
        return self

    def select_by_id_list(self, id_list):
        import copy
        selected_dict = copy.deepcopy(self)
        id_dict = {i: None for i in id_list}
        for element_id, element in self.items():
            if element_id in id_dict:
                pass
            else:
                del selected_dict[element_id]
        return selected_dict

    # def merge_element_dict(self, element_dict_set):
    #     import copy
    #     combined_dict = copy.deepcopy(self)
    #     for element_dict in element_dict_set.values():
    #         for element in element_dict.values():
    #             if element.get_id() not in combined_dict:
    #                 combined_dict.add_element(element)
    #     return combined_dict


if __name__ == '__main__':
    vrp_elements_collection = ElementDict('vrp')
    print(vrp_elements_collection['edge_collection'])
