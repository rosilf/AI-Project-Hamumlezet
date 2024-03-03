import time
import datetime
from typing import Optional, Any
from CatalogParser import CatalogParser
from settings import Settings


from settings import *
from TimeTableClasess import *
from typing import List, Dict, Set, Tuple

SEASON = Settings.get_instance().SEASON
GENERIC_COURSES = Settings.get_instance().GENERIC_COURSES
COURSES_SUBTYPES = Settings.get_instance().COURSES_SUBTYPES
COURSES_TYPES = Settings.get_instance().COURSES_TYPES

class Course:
    def __init__(self, id: str, name: str, credit_points: float,
                 prerequisites_courses: List[List[str]] = None,
                 linked_courses: List[str] = None, overlapping_courses: List[str] = None,
                 incorporated_courses: List[str] = None, given_in_semester: Dict = None,
                 time_table: List[Dict] = None,
                 exam_dates: Dict = None):
        self.__id = id
        self.__name = name
        self.__credit_points = float(credit_points)
        self.__type = None
        self.__subtype = set()
        self.__prerequisites_courses = prerequisites_courses
        self.__linked_courses = linked_courses
        self.__overlapping_courses = overlapping_courses
        self.__incorporated_courses = incorporated_courses
        self.__given_in_semester = given_in_semester
        self.__time_table = time_table
        self.__lectures_times = self.__extract_classes_times_by_type('הרצאה')
        self.__tutorials_times = self.__extract_classes_times_by_type('תרגול')
        self.__laboratory_times = self.__extract_classes_times_by_type('מעבדה')
        self.__project_times = self.__extract_classes_times_by_type('פרויקט')
        self.__exam_dates = exam_dates
        self.__is_project = True if "פרויקט " in self.__name else False
        self.__is_seminar = True if "סמינר " in self.__name else False
        self.__contains = {self.__id}
        self.__is_seminar = True if "סמינר" in self.__name else False
        self.__is_advanced = True if "נושאים מתקדמים " in self.__name else False
        self.__importance = 0

    def __extract_classes_times_by_type(self, typ: str) -> List[List[Dict]] or None:
        if not self.__time_table:
            return None
        lst = list()
        for registering_group in self.__time_table:
            for group in registering_group.get_groups():
                if all(c.get_type() == typ for c in group.get_classes()):
                    if group.get_classes() not in lst:
                        lst.append(group.get_classes())
        if not lst:
            return None
        final = []
        if typ == 'הרצאה':
            t = 'lec'
        if typ == 'תרגול':
            t = 'tut'
        if typ == 'מעבדה':
            t = 'lab'
        if typ == 'פרויקט':
            t = 'pro'
        for x in lst:
            m = []
            num = len(x)
            for l in x:
                m.append((l.get_id(), l.get_day(), l.get_start_time(), l.get_end_time(), t, num, self.__id))
            final.append(m)
        return final

    def get_name(self) -> str:
        return self.__name

    def get_id(self) -> str:
        return self.__id

    def get_type(self) -> COURSES_TYPES:
        return self.__type

    def set_type(self, typ: COURSES_TYPES):
        self.__type = typ

    def get_subtype(self) -> COURSES_SUBTYPES:
        return self.__subtype

    def set_subtype(self, subtype_list: List):
        self.__subtype.update(subtype_list)

    def get_is_project(self) -> bool:
        return self.__is_project

    def get_is_seminar(self) -> bool:
        return self.__is_seminar

    def get_is_advanced(self) -> bool:
        return self.__is_advanced

    def get_credit_points(self) -> float:
        return self.__credit_points

    def get_prerequisites_courses(self) -> List[List[str]]:
        return self.__prerequisites_courses

    def set_prerequisites_courses(self, prerequisites_courses: List[List[str]]):
        self.__prerequisites_courses = prerequisites_courses

    def get_num_of_prerequisites_courses(self):
        if not self.__prerequisites_courses or self.__prerequisites_courses == [[]]:
            return 0
        return len(self.__prerequisites_courses)

    def get_num_of_linked_courses(self):
        if not self.__linked_courses or self.__linked_courses == []:
            return 0
        return len(self.__linked_courses)

    def get_linked_courses(self) -> List[str]:
        return self.__linked_courses

    def set_linked_courses(self, linked_courses: List[str]):
        self.__linked_courses = linked_courses

    def get_given_in_semester(self) -> Dict:
        return self.__given_in_semester

    def is_given_in_semester(self, sem: str):
        if self.__id in GENERIC_COURSES:
            return True
        if not self.__given_in_semester:
            return False
        if sem in self.__given_in_semester.keys():
            return self.__given_in_semester[sem]
        return False

    def get_exam_dates(self):
        return self.__exam_dates

    def get_contains_courses(self) -> Set[str]:
        return self.__contains

    def get_overlapping_courses(self) -> List[str]:
        return self.__overlapping_courses

    def get_incorporated_courses(self) -> List[str]:
        return self.__incorporated_courses

    def get_time_table(self) -> List[Dict]:
        return self.__time_table

    def get_lectures_times(self) -> Optional[List[List[Tuple[Any, Any, Any, Any, str, int, str]]]]:
        return self.__lectures_times

    def get_tutorials_times(self) -> Optional[List[List[Tuple[Any, Any, Any, Any, str, int, str]]]]:
        return self.__tutorials_times

    def get_laboratory_times(self) -> Optional[List[List[Tuple[Any, Any, Any, Any, str, int, str]]]]:
        return self.__laboratory_times

    def get_project_times(self) -> Optional[List[List[Tuple[Any, Any, Any, Any, str, int, str]]]]:
        return self.__project_times

    def insert_contains(self, course_id: str):
        self.__contains.add(course_id)

    def set_contains(self, courses: Set[str]):
        self.__contains = courses

    def is_union(self) -> bool:
        return len(self.__contains) > 1

    def get_importance(self) -> int:
        return self.__importance

    def set_importance(self, importance: int):
        self.__importance = importance

    def create_json_course(self):
        string = '{'
        for v, k in self.__dict__.items():
            string += f'"{v}": "{k}",'
        string = string[:-1] + '}'
        return string

