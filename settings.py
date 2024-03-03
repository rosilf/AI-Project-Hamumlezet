###
#  General settings
#   Add jason
###
# -*- coding: utf-8 -*-
class Settings:
    __instance = None
    def __init__(self):

        self.DAYS = ['א', 'ב', 'ג', 'ד', 'ה', 'ו']
        self.SEASON = ['א', 'ב', 'ג']
        # !!!!IMPORTANT: DO NOT CHANGE THE TYPES ORDER IN COURSES_TYPES, YOU CAN ADD NEW TYPES ONLY IN THE END OF THE LIST!!

        # UNIVERSAL ID -
        # '4' - סמינר קורס (איחוד של סמינרים)
        self.COURSES_TYPES = ["חובה",  # 0
                         "בחירה חופשית",  # 1
                         "העשרה",  # 2
                         "מתמטי נוסף",  # 3
                         "שרשרת מדעית",  # 4
                         "ספורט",  # 5
                         "רשימה א",  # 6
                         "רשימה ב",  # 7
                         "פרויקט",  # 8
                         "תת שרשרת מדעית"  # 9
                         ]

        self.COURSES_SUBTYPES = [
            "פיזיקה 1",  # 0
            "פיזיקה 2",  # 1
            "ביולוגיה",  # 2
            "כימיה 1",  # 3
            "כימיה 2",  # 4
            "פיזיקה-כימיה"  # 5
        ]
        self.COURSES_NUM_PER_SUBTYPES = {
            "פיזיקה 1": 1,  # 0
            "פיזיקה 2": 2,  # 1
            "ביולוגיה": 2,  # 2
            "כימיה 1": 2,  # 3
            "כימיה 2": 2,  # 4
            "פיזיקה-כימיה": 2  # 5

        }
        self.DAYS_BETWEEN_TESTS = 2
        self.TOTAL_POINTS_A_B_LIST = 24.5
        self.MIN_POINTS_PER_SEMESTER = 18
        self.MAX_POINTS_PER_SEMESTER = 23
        self.MAX_AVAILABLE_COURSES = None
        self.MAX_AVAILABLE_COURSES_UP_TO_30_POINTS = 12
        self.MAX_AVAILABLE_COURSES_31_TO_45_POINTS = 9
        self.MAX_AVAILABLE_COURSES_46_TO_60_POINTS = 8
        self.MAX_AVAILABLE_COURSES_FROM_61_POINTS = 7

        self.STUDY_PLAN = ["3 years - Computer Science",  # 0
                      "4 years - Computer Science",  # 1
                      "Software Engineering",  # 2
                      "Computer Engineering"]  # 3

        self.CATALOG_TYPES = ["2019-2020",  # 0
                         "2020-2021",  # 1
                         "2021-2022",  # 2
                         "2022-2023"]  # 3

        self.GENERIC_COURSES = ["000011", "000012", "000021", "000022", "000023", "000031"]

        self.SPECIAL_PREREQUISITES_COURSES = ['113014', '113013', '123015']
        # Optimizations flags:
        self.LIMIT_AVAILABLE_COURSES = True
        self.TESTS_CONFLICTS = True
        self.TIME_TABLE_CONFLICTS = True
        self.PRUNING = True
        self.DEVELOP_OPTIONS_GRAPH_BY_PRIORITY = True
        self.MANDATORY_COURSES_POINTS = 42
        if Settings.__instance is None:
            Settings.__instance = self
        else:
            raise Exception("Settings instance already exists")

    @staticmethod
    def get_instance():
        if Settings.__instance is None:
            raise Exception("Settings instance does not exist")
        return Settings.__instance

    def config_settings(self, flags: dict, remaining_points: float):
        for flag in flags.keys():
            if flag == "time table conflicts":
                self.TIME_TABLE_CONFLICTS = flags[flag]
            if flag == "tests conflicts":
                self.TESTS_CONFLICTS = flags[flag]
            if flag == "pruning":
                self.PRUNING = flags[flag]
            if flag == "limit available courses":
                self.LIMIT_AVAILABLE_COURSES = flags[flag]
            if flag == "develop options graph by priority":
                self.DEVELOP_OPTIONS_GRAPH_BY_PRIORITY = flags[flag]
            if flag == "max available courses":
                if flags[flag] == "default":
                    if remaining_points <= 30.5:
                        self.MAX_AVAILABLE_COURSES = self.MAX_AVAILABLE_COURSES_UP_TO_30_POINTS
                    elif 31 <= remaining_points <= 45.5:
                        self.MAX_AVAILABLE_COURSES = self.MAX_AVAILABLE_COURSES_31_TO_45_POINTS
                    elif 46 <= remaining_points <= 60.5:
                        self.MAX_AVAILABLE_COURSES = self.MAX_AVAILABLE_COURSES_46_TO_60_POINTS
                    elif remaining_points >= 61:
                        self.MAX_AVAILABLE_COURSES = self.MAX_AVAILABLE_COURSES_FROM_61_POINTS
                else:
                    self.MAX_AVAILABLE_COURSES = int(flags[flag])
                    print("max available courses: " + str(self.MAX_AVAILABLE_COURSES))
                    pass
