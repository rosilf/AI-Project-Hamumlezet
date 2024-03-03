# -*- coding: utf-8 -*-
from settings import Settings
from CatalogParser import CatalogParser
from SupporterGraduateParser import *
from JsonParser import JsonParser
from CoursesTest import CoursesTest
from typing import Dict, List

COURSES_TYPES = Settings.get_instance().COURSES_TYPES
COURSES_SUBTYPES = Settings.get_instance().COURSES_SUBTYPES

class GraduateParser:
    __instance = None

    @staticmethod
    def __create_json_courses(courses_dict):
        json_data = '{"Courses":['
        for c in courses_dict.values():
            json_data += c.create_json_course() + ','
        json_data = json_data[:-1] + ']}'
        json_file = open("courses.json", "w")
        json_file.write(json_data)
        json_file.close()

    def __find_type(self, course_id: str) -> COURSES_TYPES:
        for course_type in self.__catalog_parser.get_id_courses_sorted_by_courses_type().keys():
            for id in self.__catalog_parser.get_id_courses_sorted_by_courses_type()[course_type]:
                if id == course_id:
                    return course_type

    def __find_subtype(self, course_id: str) -> COURSES_SUBTYPES:
        lst = []
        for course_key_type in self.__catalog_parser.get_id_courses_sorted_by_courses_subtype().keys():
            for course_subtype in self.__catalog_parser.get_id_courses_sorted_by_courses_subtype()[ \
                    course_key_type].keys():
                for id in self.__catalog_parser.get_id_courses_sorted_by_courses_subtype()[course_key_type][ \
                        course_subtype]:
                    if id == course_id:
                        lst.append(course_subtype)
        return lst

    def __create_courses(self, json_courses_dct: Dict or None, is_courses_test: bool, internet_access: bool) -> Dict:
        courses_dict = {}
        if is_courses_test and not json_courses_dct and not internet_access:
            # if json file doesn't exist and not internet
            courses_test = CoursesTest()
            for course in courses_test.get_lst():
                courses_dict[course.get_id()] = course
                course.set_type(self.__find_type(course.get_id()))
                course.set_subtype(self.__find_subtype(course.get_id()))
                courses_dict.update({course.get_id(): course})
            return courses_dict
        elif not is_courses_test and json_courses_dct and not internet_access:  # if json file exists
            for c in json_courses_dct['Courses']:
                courses_dict[c['_Course__id']] = Course(c['_Course__id'], c['_Course__name'],
                                                        c['_Course__credit_points'],
                                                        c['_Course__prerequisites_courses'],
                                                        c['_Course__linked_courses'],
                                                        c['_Course__overlapping_courses'],
                                                        c['_Course__incorporated_courses'],
                                                        c['_Course__given_in_semester'],
                                                        c['_Course__time_table_to_semester'],
                                                        c['_Course__exam_dates'])
                courses_dict[c['_Course__id']].set_type(c['_Course__type'])
                courses_dict[c['_Course__id']].set_subtype(c['_Course__subtype'])
        elif not json_courses_dct and not is_courses_test:  # create courses from catalog (read from graduate site)
            for id in self.__courses_id:
                if id not in courses_dict.keys():
                    courses_dict[id] = None
            del_list_id = []
            for id_key in courses_dict.keys():
                if internet_access is False:
                    course = create_course(id_key)
                else:
                    course = create_course(id_key, "HTML Courses/" + id_key + ".html")
                if course is None:
                    del_list_id.append(id_key)
                    continue
                course.set_type(self.__find_type(id_key))
                course.set_subtype(self.__find_subtype(id_key))
                courses_dict.update({id_key: course})
            for id in del_list_id:
                del self.__courses_dict[id]
            # add ספורט courses to courses_dict:
            sport_course_1 = Course("000011", "ספורט 1", 1, None, None, None, None, None, None, None)
            sport_course_1.set_type(self.__find_type('000011'))
            sport_course_1.set_subtype(self.__find_subtype('000011'))
            courses_dict['000011'] = sport_course_1
            sport_course_2 = Course("000012", "ספורט 2", 1, [['000011']], None, None, None, None, None, None)
            sport_course_2.set_type(self.__find_type('000012'))
            sport_course_2.set_subtype(self.__find_subtype('000012'))
            courses_dict['000012'] = sport_course_2
            # add העשרה courses to courses_dict:
            haashara_course_1 = Course("000021", "העשרה 1", 2, None, None, None, None, None, None, None)
            haashara_course_1.set_type(self.__find_type('000021'))
            haashara_course_1.set_subtype(self.__find_subtype('000021'))
            courses_dict['000021'] = haashara_course_1
            haashara_course_2 = Course("000022", "העשרה 2", 2, None, None, None, None, None, None, None)
            haashara_course_2.set_type(self.__find_type('000022'))
            haashara_course_2.set_subtype(self.__find_subtype('000022'))
            courses_dict['000022'] = haashara_course_2
            haashara_course_3 = Course("000023", "העשרה 3", 2, [['000021']], None, None, None, None, None, None)
            haashara_course_3.set_type(self.__find_type('000023'))
            haashara_course_3.set_subtype(self.__find_subtype('000023'))
            courses_dict['000023'] = haashara_course_3
            # add בחירה חופשית course:
            hofshit_course = Course("000031", "חופשית 1", 2, None, None, None, None, None, None, None)
            hofshit_course.set_type(self.__find_type('000031'))
            hofshit_course.set_subtype(self.__find_subtype('000031'))
            courses_dict['000031'] = hofshit_course
            # self.__create_json_courses(courses_dict)

        return courses_dict

    def __create_linked_dict(self):
        linked_dict = {}
        for course_id in self.__courses_dict:
            linked_lst = self.__courses_dict[course_id].get_linked_courses()
            if linked_lst:
                for linked_id in linked_lst:
                    is_exist = linked_dict.get(linked_id)
                    if is_exist:
                        linked_dict[linked_id].append(course_id)
                    else:
                        linked_dict[linked_id] = [course_id]
        return linked_dict

    def __new__(cls, catalog_parser=None, json_file_path=None, courses_test=False, internet_access=bool):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__courses_dict = None
            cls.__instance.__linked_courses_dict = None
            return cls.__instance
        else:
            raise Exception("GraduateParser instance already exists")

    def __init__(self, json_file_path: str or None, catalog_parser: CatalogParser or None,
                 is_courses_test=False, internet=bool):
        if catalog_parser and is_courses_test and not json_file_path:  # create courses from CoursesTest
            self.__catalog_parser = catalog_parser
            self.__courses_dict = self.__create_courses(None, True, False)
            self.__linked_courses_dict = self.__create_linked_dict()
        elif catalog_parser and not is_courses_test and not json_file_path:  # create courses from graduate site
            self.__courses_id = catalog_parser.get_id_list()
            self.__catalog_parser = catalog_parser
            if not internet:
                self.__courses_dict = self.__create_courses(None, False, True)
            else:
                self.__courses_dict = self.__create_courses(None, False, False)
            self.__linked_courses_dict = self.__create_linked_dict()
        elif not catalog_parser and not is_courses_test and json_file_path:  # create courses from json file
            self.__courses_dict = self.__create_courses(JsonParser(json_file_path).get_courses_dict(), False, False)
            self.__linked_courses_dict = self.__create_linked_dict()
        else:
            raise Exception("Wrong arguments! The optional for right arguments is: \n(1) (None, <CatalogParser_obj>,"
                            " True) - arguments for extracting courses from CoursesTest \n(2) ('<json_path>', None,"
                            " False) - arguments for extracting courses from json file \n(3) (None, "
                            "<CatalogParser_obj>, False) - arguments for extracting courses from graduate site")
        if GraduateParser.__instance is not None:
            GraduateParser.__instance = self

    @staticmethod
    def get_instance():
        if GraduateParser.__instance is None:
            raise Exception("GraduateParser instance does not exist")
        return GraduateParser.__instance

    def get_courses_dict(self):
        return self.__courses_dict

    def get_courses_lst(self):
        return self.__courses_dict.values()

    def get_courses_dict_by_type(self) -> Dict[str, List[Course]]:
        courses_dict_type = {}
        for course in self.__courses_dict.values():
            if course.get_type() not in courses_dict_type.keys():
                courses_dict_type[course.get_type()] = []
            courses_dict_type[course.get_type()].append(course)
        return courses_dict_type

    def get_linked_dict(self):
        return self.__linked_courses_dict
