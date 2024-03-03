from copy import deepcopy
from typing import List, Dict
from Data import Data
from settings import Settings


done = 0
left = 1
COURSES_TYPES = Settings.get_instance().COURSES_TYPES
COURSES_NUM_PER_SUBTYPES = Settings.get_instance().COURSES_NUM_PER_SUBTYPES

class State:
    # COURSES_TYPES = Settings.get_instance().COURSES_TYPES

    def __init__(self, completed_courses_id: List[str], requirements_credit_points: Dict):
        self.completed_courses = {course_type: [] for course_type in COURSES_TYPES}
        self.degree_requirements = {course_type: (0, requirements_credit_points[course_type]) for course_type in
                                    COURSES_TYPES}
        self.scientific_chains = {}  # example: ( ביולוגיה':( [ 134058, 134020 ], (2,0)'
        data = Data.get_instance()
        self.update_completed_courses(completed_courses_id)
        # for course_id in completed_courses_id:
        #     course = data.courses_dict[course_id]
        #     self.completed_courses[course.get_type()].append(course_id)
        #     # template of requirement is: (done,left)
        #     req = self.degree_requirements[course.get_type()]
        #     req_done = float(req[0]) + float(course.get_credit_points())
        #     req_left = float(req[1]) - float(course.get_credit_points())
        #     self.degree_requirements[course.get_type()] = (req_done, req_left)
        #     if course.get_is_project():  # !!! only if project is (0,1)
        #         # project requirement is (0,1) and if the student has done at least one course that "is project" = true
        #         # we change the requirement to (1,0) and it won't be updated again.
        #         self.degree_requirements[COURSES_TYPES[8]] = (1, 0)

    def get_str_courses_list(self) -> List[str]:
        lst = []
        for courses in self.completed_courses.values():
            lst.extend(courses)
        return lst

    def is_graduate(self, requirements=None) -> bool:
        if requirements is None:
            requirements = self.degree_requirements

        for course_type in requirements:
            if requirements[course_type][left] > 0:
                return False
        return True

    def is_graduate_with_a_given_semester(self, semester: List[str]) -> bool:
        new_state = deepcopy(self)
        new_state.update_completed_courses(semester)
        return new_state.is_graduate()

    def get_sub_type_of_scientific_course(self, course_id: str):
        sub_type = ''
        course = Data.get_instance().courses_dict[course_id]
        sub_types = list(course.get_subtype())
        if len(sub_types) == 0:
            return ''
        if len(sub_types) > 1:
            # if there is more than one sub type choose the one that already chosen
            for i in sub_types:
                if i in self.scientific_chains.keys():
                    sub_type = i
                    return sub_type
            # if there is no chosen one, choose the first
            if sub_type == '':
                if len(self.scientific_chains) == 2:  # it means that 2 chains already opened,Shouldn't happen
                    return '-1'
                sub_type = sub_types[0]
        else:
            if len(self.scientific_chains) == 2 and \
                    sub_types[0] not in list(
                self.scientific_chains.keys()):  # it means that 2 chains already opened,Shouldn't happen
                return '-1'
            sub_type = sub_types[0]
        return sub_type

    def update_completed_courses(self, courses: List[str]):
        # !for every change in the logic here, check if in is_it_irrelevant_course func need to change also
        for course_id in courses:
            course = Data.get_instance().courses_dict[course_id]
            course_type = course.get_type()
            if course_id in self.completed_courses[course_type]:
                continue
            # if the student finish the requirement of A list, all the courses of type A list will count as B list
            if course_type == COURSES_TYPES[6] and self.degree_requirements[course_type][1] <= 0:
                course_type = COURSES_TYPES[7]
            self.completed_courses[course_type].append(course_id)
            req = self.degree_requirements[course_type]
            req_done = float(req[done]) + float(course.get_credit_points())
            req_left = float(req[left]) - float(course.get_credit_points())
            self.degree_requirements[course_type] = (req_done, req_left)
            if course.get_is_project():
                # project requirement is (0,1) and if the student has done at least one course that "is project" = true
                # we chacne the requirment to (1,0) and it won't be updated again.
                self.degree_requirements[COURSES_TYPES[8]] = (1, 0)
            # if its a scientific course, we need to update the relevant chain
            if course_type == COURSES_TYPES[4]:
                # sub type is a set
                sub_type = self.get_sub_type_of_scientific_course(course_id)
                if sub_type == '-1':
                    print('Error: Can not open more than 2 scientific chains')
                if sub_type == '':
                    continue
                if not self.scientific_chains.get(sub_type):
                    self.scientific_chains[sub_type] = ([], (0, COURSES_NUM_PER_SUBTYPES[sub_type]))
                self.scientific_chains[sub_type][0].append(course_id)
                dn = self.scientific_chains[sub_type][1][0]
                lft = self.scientific_chains[sub_type][1][1]
                dn = int(dn) + 1
                lft = int(lft) - 1
                lst = self.scientific_chains[sub_type][0]
                self.scientific_chains[sub_type] = (lst, (dn, lft))
                if lft <= 0:
                    self.degree_requirements[COURSES_TYPES[9]] = (1, 0)

                # if the student finish scientific courses it will count as B list
                if self.degree_requirements[course_type][1] < 0 and self.degree_requirements[COURSES_TYPES[7]][1] > 0:
                    scien_left = self.degree_requirements[course_type][1]  # negative value
                    self.degree_requirements[course_type] = (self.degree_requirements[course_type][0], 0)
                    b_list_left = self.degree_requirements[COURSES_TYPES[7]][1]
                    b_list_left = int(b_list_left) - abs(scien_left)
                    self.degree_requirements[COURSES_TYPES[7]] = (self.degree_requirements[COURSES_TYPES[7]][0], b_list_left)


    def is_it_irrelevant_course(self, course_type: str, course_id: str) -> bool:
        if self.degree_requirements[course_type][left] > 0 and course_type != COURSES_TYPES[4]:
            return False
        # if the student finish the requirement of A list, all the courses of type A list will count as B list
        if course_type == COURSES_TYPES[6] and self.degree_requirements[COURSES_TYPES[7]][left] > 0:
            return False
        # if its a project course and the student hasn't done yet a project course its not an irrelevant course
        if Data.get_instance().courses_dict[course_id].get_is_project() \
                and self.degree_requirements[COURSES_TYPES[8]][left] > 0:
            return False
        # if its a scientific course and the student already open 2 chains we dont need the course
        if course_type == COURSES_TYPES[4]:
            if self.degree_requirements[COURSES_TYPES[4]][left] <= 0 and \
                    self.degree_requirements[COURSES_TYPES[9]][left] == 0:
                return True
            # if he still didn't open a scientific chain, all the scientific courses are relevant
            if len(self.scientific_chains) == 0:
                if not self.get_sub_type_of_scientific_course(course_id):
                    return True
                else:
                    return False
            course = Data.get_instance().courses_dict[course_id]
            if len(self.scientific_chains) == 2 \
                    and all(x not in self.scientific_chains.keys() for x in list(course.get_subtype())):
                return True
            else:
                if not self.get_sub_type_of_scientific_course(course_id):
                    # if in the total scientific chain left 4 points and still didnt finish 1 scientific chain,
                    # we don't want courses without subtype
                    if self.degree_requirements[COURSES_TYPES[4]][left] <= 4 and \
                            self.degree_requirements[COURSES_TYPES[9]][left] == 1:
                        return True
                return False
        return True

    def check_scientific_courses(self, scientific_courses: [str]):
        chains = {}
        for course_id in scientific_courses:
            sub_type = self.get_sub_type_of_scientific_course(course_id)
            if sub_type == '-1':
                return False
            if sub_type == '':  # no sub type
                continue
            if chains.get(sub_type):
                chains[sub_type] = int(chains[sub_type]) + 1
            else:
                chains[sub_type] = 1
        if len(chains) > 2:
            return False
        else:
            num = len(chains)
            for i in self.scientific_chains.keys():
                if i not in chains:
                    num = num + 1
            if num > 2:
                return False
        return True

    def is_project_allowed(self) -> bool:
        return '234124' in self.completed_courses[COURSES_TYPES[0]]

    def is_seminar_allowed(self) -> bool:
        # if the student compleerd more than 70% of the degree requirements of COURSES_TYPES[0]
        # he can take a seminar course
        completed_mandatory_courses = self.degree_requirements[COURSES_TYPES[0]][done]
        left_mandatory_courses = self.degree_requirements[COURSES_TYPES[0]][left]
        return completed_mandatory_courses / (completed_mandatory_courses + left_mandatory_courses) >= 0.7

    def is_advanced_allowed(self) -> bool:
        return '234218' in self.completed_courses[COURSES_TYPES[0]]

    def is_course_completed(self, course_id: str):
        ret = course_id in self.get_str_courses_list()
        return ret

    def get_uncompleted_req(self) -> List:
        uncompleted_req = []
        for req in self.degree_requirements:
            if self.degree_requirements[req][left] > 0:
                uncompleted_req.append(req)
        # sort by left field
        uncompleted_req.sort(key=lambda x: self.degree_requirements[x][left], reverse=True)
        return uncompleted_req

    def get_remaining_points(self):
        total_left_points = 0
        for typ in self.degree_requirements:
            remainder = self.degree_requirements[typ][1]
            if typ == COURSES_TYPES[0]:
                if remainder > 0:
                    total_left_points += remainder
            elif typ == COURSES_TYPES[1]:
                if remainder > 0:
                    total_left_points += remainder
            elif typ == COURSES_TYPES[2]:
                if remainder > 0:
                    total_left_points += remainder
            elif typ == COURSES_TYPES[3]:
                if remainder > 0:
                    total_left_points += remainder
            elif typ == COURSES_TYPES[4]:
                if remainder >= 0:
                    total_left_points += remainder
                else:
                    if self.degree_requirements[COURSES_TYPES[9]][1] == 1:
                        total_left_points += 3.5
            elif typ == COURSES_TYPES[5]:
                if remainder > 0:
                    total_left_points += remainder
            elif typ == COURSES_TYPES[6]:
                if remainder >= 0:
                    total_left_points += remainder
                else:
                    if self.degree_requirements[COURSES_TYPES[8]][1] == 1:
                        total_left_points += 3
            elif typ == COURSES_TYPES[7]:
                if remainder > 0:
                    total_left_points += remainder
        return total_left_points

    def get_remaining_points_per_req(self):
        s = ''
        for typ in self.degree_requirements:
            s += typ + ': ' + str(self.degree_requirements[typ][1]) + '\n'
        return s

