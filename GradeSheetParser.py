from typing import List
class GradeSheetParser:
    __instance = None

    def __init__(self, grade_sheet_path: str):
        sheet = open(grade_sheet_path, "r")
        lines = sheet.readlines()
        for i in range(len(lines)):
            if '\n' in lines[i]:
                lines[i] = lines[i].replace("\n", "")
        self.__name = lines[1]
        self.__id = lines[3]
        self.__catalog_type = lines[5]
        self.__degree_type = lines[7]
        self.__courses_completed = [line for line in lines[9:]]

        if GradeSheetParser.__instance is None:
            GradeSheetParser.__instance = self
        else:
            raise Exception("GradeSheetParser instance already exists")

    @staticmethod
    def get_instance():
        if GradeSheetParser.__instance is None:
            raise Exception("GradeSheetParser instance does not exist")
        return GradeSheetParser.__instance

    def get_name(self):
        return self.__name

    def get_id(self):
        return self.__id

    def get_completed_courses_id(self) -> List[str]:
        return self.__courses_completed

    def get_catalog_type(self):
        return self.__catalog_type

    def get_degree_type(self):
        return self.__degree_type
