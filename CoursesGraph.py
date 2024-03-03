import networkx as nx
from Course import Course
from Data import Data
from copy import deepcopy
from typing import List, Tuple

course_type = str
course_id = str
first = str
second = str
points = float


class CoursesGraph:
    __instance = None

    # my google colab for playing around with the graph :
    # https://colab.research.google.com/drive/1r9YgAEoncKxEpqaoAFPTc5CPcD1q_hX6#scrollTo=3Z9p4hegLA2U

    def __init__(self):
        self.graph = None
        self.sorted_courses = None
        if CoursesGraph.__instance is None:
            CoursesGraph.__instance = self
        else:
            raise Exception("Courses Graph instance already exists")

    @staticmethod
    def get_instance():
        if CoursesGraph.__instance is None:
            raise Exception("Courses Graph instance does not exist")
        return CoursesGraph.__instance

    def remove_cycles(self):
        """remove cycles from the graph before the toplogical sort
        since the relationship between courses represents pre-requisites the graph should be a DAG
        if there is a cycle in the graph - the student can't graduate
        we noticed that when tha faculty wants to enforce the student to learn two courses in the same semester
        they create a cycle in the graph - i.e IOT and IOT project
        we will handle this case by combinig the two courses into one course
        and we will remove the cycle from the graph"""
        cycles = list(nx.simple_cycles(self.graph))
        for cycle in cycles:
            if len(cycle) == 2:
                if self.graph.edges[cycle[0], cycle[1]]['linked'] == False:
                    raise Exception("can't handle cycle that is not linked")
                new_course_id, new_course = self.combine_courses(cycle[0], cycle[1])
                Data.get_instance().add_to_courses_dict(new_course_id, new_course)
                self.graph.add_node(new_course_id, dummy=False, legacy=False)
                for c in cycle:
                    for edge in self.graph.in_edges(c):
                        if edge[0] in cycle:
                            continue
                        self.graph.add_edge(edge[0], new_course_id,
                                            mandatory=self.graph.edges[edge[0], edge[1]]['mandatory'],
                                            linked=self.graph.edges[edge[0], edge[1]]['linked'])
                    for edge in self.graph.out_edges(c):
                        if edge[1] in cycle:
                            continue
                        self.graph.add_edge(new_course_id, edge[1],
                                            mandatory=self.graph.edges[edge[0], edge[1]]['mandatory'],
                                            linked=self.graph.edges[edge[0], edge[1]]['linked'])
                self.graph.remove_node(cycle[0])
                self.graph.remove_node(cycle[1])
            else:
                raise Exception("can't handle cycles with more than two courses")

    def merge_course_lists(self, l1, l2)->List[str]:
        list1 = l1 if l1 else []
        list2 = l2 if l2 else []
        return list1 + list2 if list1 != [] and list2 != [] else None

    def combine_courses(self, c1, c2):
        """find the two courses in the course dict combine them into one course
        return the new course id"""
        course1 = Data.get_instance().courses_dict[c1]
        course2 = Data.get_instance().courses_dict[c2]
        id = course1.get_id() +'###'+ course2.get_id()
        name = course1.get_name() + '###' + course2.get_name()
        credit_points = course1.get_credit_points() + course2.get_credit_points()
        if course1.get_type() != course2.get_type():
            raise Exception("can't combine courses with different types")
        type = course1.get_type()
        prerequisites_courses = course1.get_prerequisites_courses() + course2.get_prerequisites_courses()
        linked_courses = self.merge_course_lists(course1.get_linked_courses(),course2.get_linked_courses())
        overlapping_courses = self.merge_course_lists(course1.get_overlapping_courses(), course2.get_overlapping_courses())
        incorporated_courses = self.merge_course_lists(course1.get_incorporated_courses(), course2.get_incorporated_courses())
        if course1.get_given_in_semester() != course2.get_given_in_semester():
            raise Exception("can't combine courses with different given in semester")
        given_in_semester = course1.get_given_in_semester()
        time_table = None
        exam_dates = None
        new_course = Course(id, name, credit_points, prerequisites_courses, linked_courses, overlapping_courses,
               incorporated_courses, given_in_semester, time_table, exam_dates)
        new_course.set_type(type)
        new_course.insert_contains(c1)
        new_course.insert_contains(c2)
        return id, new_course

    def select_cs_pre_courses(self,id , pre_courses: List[List[str]]) -> List[str]:
        relevant_pre_courses = []
        if len(pre_courses) > 1:
            for pre in pre_courses:
                if all(c in Data.get_instance().courses_dict for c in pre):
                    relevant_pre_courses.append(pre)
            if len(relevant_pre_courses) == 0:
                # print("no cs pre for:"+id)
                return []
            return relevant_pre_courses[0]
        else:
            if all (c == -1 for c in pre_courses[0]):
                return []
            return pre_courses[0]

    def create_graph(self) -> None:
        courses = Data.get_instance().courses_dict.values()
        # courses = [Course("probability", "1", 1, "COURSES_TYPES[0]"),
        #            Course("mtm", "2", 2, "COURSES_TYPES[0]"),
        #            Course("combinatorics", "3", 3, "COURSES_TYPES[0]"),
        #            Course("data structures", "4", 4, "COURSES_TYPES[0]",
        #                   [["mtm", "combinatorics"]], ["probability"])
        #            ]
        G = nx.DiGraph()
        if courses:
            courses_ids = list(map(lambda c: c.get_id(), courses))
            G.add_nodes_from(courses_ids, dummy=False, legacy=False)
            for c in courses:
                # if c.get_id() in Data.get_instance().get_no_cs_pre():
                #     continue
                pre_courses_num = c.get_num_of_prerequisites_courses()
                if pre_courses_num > 0:
                    pre_courses = deepcopy(self.select_cs_pre_courses(c.get_id(),c.get_prerequisites_courses()))
                    for pre in pre_courses:
                        if pre not in courses_ids:
                            G.add_node(pre,dummy=False, legacy=True)
                        G.add_edge(pre, c.get_id(), mandatory=True, linked=False)
                if c.get_linked_courses():
                    for l in c.get_linked_courses():
                        if l not in courses_ids:
                            G.add_node(l,dummy=False, legacy=True)
                        G.add_edge(l, c.get_id(), linked=True, mandatory=False)
        self.graph = G
        self.remove_cycles()
        self.sorted_courses = list(nx.topological_sort(self.graph))
        for node in self.sorted_courses:
            self.graph.nodes[node]['importance']= self.calculate_importance(node)
            if self.graph.nodes[node]["legacy"]:
                continue
            Data.get_instance().courses_dict[node].set_importance(self.graph.nodes[node]['importance'])
        # print("graph: ", self.graph.nodes.data())

    def get_valid_courses(self, current_state: List[course_id]) -> (List[course_id], List[Tuple]):
        # print("sorted courses: ", self.sorted_courses)
        valid_courses = []
        linked_courses = []
        dummies = []
        for c in self.sorted_courses:
            if c not in current_state:
                is_required = False
                if len(valid_courses) == 0:
                    valid_courses.append(c)
                else:
                    current_linked_courses = []
                    for v in valid_courses:
                        # print("v: ", v)
                        # print("c: ", c)
                        # print("edge: ", self.graph.has_edge(v, c))
                        if self.graph.has_edge(v, c):
                            # print("linked: ", str(self.graph.edges[v, c]['linked']))
                            # print("mandatory: ", str(self.graph.edges[v, c]['mandatory']))
                            if self.graph.edges[v, c]['linked'] == True:
                                current_linked_courses.append((v, c))
                            if self.graph.edges[v, c]['mandatory'] == True:
                                is_required = True
                            if self.graph.nodes[c]['dummy'] == True:
                                dummies.append(c)
                                is_required = True
                            for d in dummies:
                                if self.graph.has_edge(d, c):
                                    if self.graph.edges[d, c]['mandatory'] == False:
                                        is_required = True
                        elif nx.has_path(self.graph, v, c):
                            is_required = True
                    if not is_required:
                        valid_courses.append(c)
                        linked_courses.extend(current_linked_courses)
                    # print("valid courses: ", valid_courses)
                    # for c in valid_courses:
                    # print("course: ", c, "dummy: ", self.graph.nodes[c]['dummy'], "legacy: ", self.graph.nodes[c]['legacy'])
                    # valid_courses = list(filter(lambda c: self.graph.nodes[c]['dummy'] == False and self.graph.nodes[c]['legacy'] == False,
                    #                    valid_courses))
                    # return valid_courses, linked_courses
        final_linked_courses = list(filter(lambda c: self.graph.nodes[c[1]]['dummy'] == False and
                                                     self.graph.nodes[c[1]]['legacy'] == False and
                                                     self.graph.nodes[c[0]]['dummy'] == False and
                                                        self.graph.nodes[c[0]]['legacy'] == False,  linked_courses))
        final_valid_list = list(
            filter(lambda c: self.graph.nodes[c]['dummy'] == False and self.graph.nodes[c]['legacy'] == False,
                   valid_courses))
        # linked_lst = None
                # for id in final_valid_list:
                #     linked_lst = Data.get_instance().linked_dict.get(id)
                #     if linked_lst:
                #         final_valid_list.extend(linked_lst)
                #         for i in linked_lst:
                #             linked_courses.append((id, i))
        return final_valid_list, linked_courses

    def calculate_importance(self, course_id: str) -> int:
        descendants = nx.descendants(self.graph, course_id)
        return len(descendants)
#
    # def get_course_info_by_id(self, str) -> (type, points):
    #     pass
