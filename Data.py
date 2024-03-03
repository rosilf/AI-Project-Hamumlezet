# -*- coding: utf-8 -*-
from settings import Settings

SPECIAL_PREREQUISITES_COURSES = Settings.get_instance().SPECIAL_PREREQUISITES_COURSES

class Data:
    __instance = None

    def __init__(self):
        self.courses_dict = None
        self.linked_dict = None
        self.__student = None
        if Data.__instance is None:
            Data.__instance = self
        else:
            raise Exception("Data instance already exists")

    @staticmethod
    def get_instance():
        if Data.__instance is None:
            raise Exception("Data instance does not exist")
        return Data.__instance

    def get_student(self):
        return self.__student

    def set_student(self, student):
        self.__student = student

    def set_courses_dict(self, dct):
        self.courses_dict = dct
        self.convert_to_cs_pre_courses()
        self.delete_no_cs_pre_courses()
        self.convert_to_cs_linked_courses()

    def add_to_courses_dict(self, key, value):
        self.courses_dict[key] = value

    def set_linked_dict(self, dct):
        self.linked_dict = dct

    def get_cs_course(self, course_id) -> str:
        for course in self.courses_dict:
            overlap = self.courses_dict[course].get_overlapping_courses()
            if overlap is None:
                continue
            for c in overlap:
                if c == course_id:
                    return course
        return -1

    def convert_to_cs_linked_courses(self):
        # print('-----------------convert_to_cs_linked_courses-----------------')
        for course in self.courses_dict:
            # special case
            if course == '134020':
                self.courses_dict[course].set_linked_courses(None)
                continue
            # check if there is no linked courses from cs.
            relevant_linked_courses = []
            linked_courses = self.courses_dict[course].get_linked_courses()
            if self.courses_dict[course].get_num_of_linked_courses() == 0:
                continue
            else:
                if all(l not in self.courses_dict.keys() for l in linked_courses):
                    for l in linked_courses:
                        l_cs = self.get_cs_course(l)
                        relevant_linked_courses.append(l_cs)
                    self.courses_dict[course].set_linked_courses(relevant_linked_courses)
                    # print('Name: ', self.courses_dict[course].get_name(), 'ID: ', self.courses_dict[course].get_id(), 'Linked courses: ',
                    #       self.courses_dict[course].get_linked_courses())
                    if all(l == -1 for l in relevant_linked_courses):
                        # print('Error: all -1')
                        self.courses_dict[course].set_linked_courses([])
            for l in self.courses_dict[course].get_linked_courses():
                if l in self.courses_dict.keys():
                    self.courses_dict[course].set_linked_courses([l])
                    # print('Name: ', self.courses_dict[course].get_name(), 'ID: ', self.courses_dict[course].get_id(),
                    #       'Linked courses: ',
                    #       self.courses_dict[course].get_linked_courses())
                    continue

    def convert_to_cs_pre_courses(self):
        no_cs_pre_courses = []
        for course in self.courses_dict:
            # check if there is no pre courses from cs.
            relevant_pre_courses = []
            pre_courses = self.courses_dict[course].get_prerequisites_courses()
            # delete from list of list all the courses in another list.
            if self.courses_dict[course].get_num_of_prerequisites_courses() == 0:
                continue
            else:
                for pre in pre_courses:
                    for c in pre:
                        if c not in Data.get_instance().courses_dict.keys():
                            break
                        else:
                            relevant_pre_courses.append(pre)
                if len(relevant_pre_courses) == 0:
                    # print("no cs pre for:"+id)
                    no_cs_pre_courses.append(course)
        for course in no_cs_pre_courses:
            new_pre_courses = []
            pre_courses = self.courses_dict[course].get_prerequisites_courses()
            # delete from list of list all the courses in another list.
            if self.courses_dict[course].get_num_of_prerequisites_courses() == 0:
                continue
            else:
                for pre in pre_courses:
                    new_pre = []
                    replace_pre = []
                    for c in pre:
                        if c not in self.courses_dict.keys():
                            if c in SPECIAL_PREREQUISITES_COURSES:  # get all the sivugim.
                                continue
                            cs_course = self.get_cs_course(c)
                            replace_pre.append(cs_course)
                        else:
                            new_pre.append(c)
                    for c in replace_pre:
                        new_pre.append(c)
                    new_pre_courses.append(new_pre)
            self.courses_dict[course].set_prerequisites_courses(new_pre_courses)

    def delete_no_cs_pre_courses(self):
        to_delete = []
        for course in self.courses_dict:
            if self.courses_dict[course].get_type() == 'חובה':
                continue
            all_pre_is_cs_courses = False
            pre_courses = self.courses_dict[course].get_prerequisites_courses()
            if pre_courses:
                for pre in pre_courses:
                    if all(c != -1 for c in pre):
                        all_pre_is_cs_courses = True
                        break
                if all_pre_is_cs_courses:
                    continue
                else:
                    to_delete.append(course)
        for course in to_delete:
            # print('delete ', course)
            del self.courses_dict[course]
