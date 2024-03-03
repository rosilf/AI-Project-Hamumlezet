# -*- coding: utf-8 -*-
from datetime import datetime
from settings import Settings
from typing import List

DAYS = Settings.get_instance().DAYS

class Class:
    def __init__(self, room: str, building: str, start_time: datetime.time,
                 end_time: datetime.time, day: DAYS, lecturer: str, type_class: str, class_id: str):
        if room == 'לא ידוע':
            self.__room = None
        else:
            self.__room = room
        if building == 'לא ידוע':
            self.__building = None
        else:
            self.__building = building
        if start_time == 'לא ידוע':
            self.__start_time = None
        else:
            self.__start_time = start_time
        if end_time == 'לא ידוע':
            self.__end_time = None
        else:
            self.__end_time = end_time
        if day == 'לא ידוע':
            self.__day = None
        else:
            self.__day = day
        if lecturer == 'לא ידוע':
            self.__lecturer = None
        else:
            self.__lecturer = lecturer
        if type_class == 'לא ידוע':
            self.__type = None
        else:
            self.__type = type_class
        if id == 'לא ידוע':
            self.__id = None
        else:
            self.__id = class_id

    def __eq__(self, other):
        return self.__room == other.get_room() and self.__building == other.get_building() and \
               self.__start_time == other.get_start_time() and self.__end_time == other.get_end_time() and \
               self.__day == other.get_day() and self.__lecturer == other.get_lecturer() and \
               self.__type == other.get_type()

    def get_room(self):
        return self.__room

    def get_building(self):
        return self.__building

    def get_start_time(self):
        return self.__start_time

    def get_end_time(self):
        return self.__end_time

    def get_day(self):
        return self.__day

    def get_lecturer(self):
        return self.__lecturer

    def get_type(self):
        return self.__type

    def get_id(self):
        return self.__id


class Group:
    def __init__(self, group_number: int, classes: List[Class]):
        self.__id = group_number
        self.__classes = classes

    def get_id(self):
        return self.__id

    def get_classes(self):
        return self.__classes


class RegisteringGroup:
    def __init__(self, group_number: int, groups: List[Group]):
        self.__id = group_number
        self.__groups = groups

    def get_id(self):
        return self.__id

    def get_groups(self):
        return self.__groups
