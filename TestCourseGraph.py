import networkx as nx
# import matplotlib.pyplot as plt

from CoursesGraph import CoursesGraph


# this is the test class for the CourseGraph class
class TestCourseGraph:
    # draw the graph func for testing
    def __init__(self):
        self.course_graph = CoursesGraph()

    # def draw_graph(self):
    #     nx.draw(self.course_graph, with_labels=True, node_color="green", node_size=3000, font_weight = 'bold')
    #     plt.margins(0.2) #בעבר היה margin
    #     plt.show()

    # test scenario: create a graph and check if the graph is correct
    def test_create_graph(self):
        self.course_graph.create_graph()
        assert self.course_graph.graph is not None
        #assert len(self.course_graph.graph.nodes) == 37
        # self.draw_graph()

    def test_remove_cyles(self):

        self.course_graph.create_graph()
        self.course_graph.remove_cycles()

    # test scenario: get_valid_courses
    # test goal: check if get valid courses is working as expected
    def test_get_valid_courses(self):
        #test 1 & 2 & 3 : check if the function return the correct  valid courses
        #         lst = [Course("1", "1", 1, COURSES_TYPES[0]),
        #                Course("2", "2", 2, COURSES_TYPES[0], [["1"]]),
        #                Course("3", "3", 3, COURSES_TYPES[0], [["2"]]),
        #                Course("4", "4", 4, COURSES_TYPES[0])
        #                ]
        self.course_graph.create_graph()
        print(self.course_graph.sorted_courses)
        #test1:
        print("test1: input : 1")
        valid_courses, linked_courses = self.course_graph.get_valid_courses(['1'])
        print("valid courses: ", valid_courses)
        print("linked courses: ",linked_courses)
        #test2: no more valid courses
        print("test2: input : 1,2,3,4")
        valid_courses, linked_courses = self.course_graph.get_valid_courses(['1', '2', '3', '4'])
        print("valid courses: ", valid_courses)
        print("linked courses: ",linked_courses)
        #test3: no initial courses
        print("test3: input : []")
        valid_courses, linked_courses = self.course_graph.get_valid_courses([])
        print("valid courses: ", valid_courses)
        print("linked courses: ",linked_courses)
        #test4&5: more complicated graph and some linked courses
        # lst = [Course("1", "1", 1, COURSES_TYPES[0]),
        #        Course("2", "2", 2, COURSES_TYPES[0], [["1","4"]]),
        #        Course("3", "3", 3, COURSES_TYPES[0], None, [["2"]]),
        #        Course("4", "4", 4, COURSES_TYPES[0])
        #        ]
        #test 4 : two dependencies
        print("test4: input : 1")
        valid_courses, linked_courses = self.course_graph.get_valid_courses(['1'])
        print("valid courses: ", valid_courses)
        print("linked courses: ",linked_courses)
        #test 5 : linked courses
        print("test5: input : 1,4")
        valid_courses, linked_courses = self.course_graph.get_valid_courses(['1', '4'])
        print("valid courses: ", valid_courses)
        print("linked courses: ",linked_courses)
        #test 6&7&8 : dummy test
        # lst = [Course("probability", "1", 1, "COURSES_TYPES[0]"),
        #        Course("mtm", "2", 2, "COURSES_TYPES[0]"),
        #        Course("combinatorics", "3", 3, "COURSES_TYPES[0]"),
        #        Course("data structures", "4", 4, "COURSES_TYPES[0]",
        #        [["mtm", "combinatorics"],["mtm","combinatorics2"]], ["probability"])
        #        ]
        # test 6 : regular courses
        print("test6: input : mtm, combinatorics")
        valid_courses, linked_courses = self.course_graph.get_valid_courses(['mtm', 'combinatorics'])
        print("valid courses: ", valid_courses)
        print("linked courses: ",linked_courses)
        # test 7 : special pre courses
        print("test7: input : mtm, combinatorics2")
        valid_courses, linked_courses = self.course_graph.get_valid_courses(['mtm', 'combinatorics2'])
        print("valid courses: ", valid_courses)
        print("linked courses: ",linked_courses)
        # test 8 : special pre courses and linked already taken courses
        print("test8: input : mtm, combinatorics2, probability")
        valid_courses, linked_courses = self.course_graph.get_valid_courses(['mtm', 'combinatorics2', 'probability'])
        print("valid courses: ", valid_courses)
        print("linked courses: ",linked_courses)

