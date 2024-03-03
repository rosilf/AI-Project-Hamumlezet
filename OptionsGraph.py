import networkx as nx
# import matplotlib.pyplot as plt
from copy import deepcopy
import math
from Course import Course
from State import State
from Data import Data
from datetime import timedelta
from CoursesGraph import CoursesGraph
from settings import Settings
from itertools import product
import random
from typing import List, Set


class OptionsGraph:
    __instance = None

    # student = None
    # options_graph = None
    # __semesters = []
    # __available_courses_list = []

    def __init__(self):
        self.options_graph = None
        self.settings = Settings.get_instance()
        self.__semesters = {self.settings.MIN_POINTS_PER_SEMESTER: set()}
        self.__available_courses_list = []
        self.__seminars = []
        self.linked_courses_dict = {}
        self.cache_schedules = {}
        self.__shortest_path_length = 15
        #  for test
        self.__cut_counter = 0
        self.options_counter = {}
        if OptionsGraph.__instance is None:
            OptionsGraph.__instance = self
        else:
            raise Exception("Options Graph instance already exists")

    @staticmethod
    def get_instance():
        if OptionsGraph.__instance is None:
            raise Exception("Options Graph instance does not exist")
        return OptionsGraph.__instance

    def get_number_of_nodes(self):
        return self.options_graph.number_of_nodes()

    def get_number_of_edges(self):
        return self.options_graph.number_of_edges()

    def get_cut_counter(self):
        return self.__cut_counter

    def get_options_counter(self):
        return self.options_counter

    @staticmethod
    def get_semester_size(semester: [str]):
        return sum([Data.get_instance().courses_dict[course_id].get_credit_points() for course_id in semester])

    def get_next_season(self, current: str):
        if current == self.settings.SEASON[0]:
            return self.settings.SEASON[1]
        elif current == self.settings.SEASON[1]:
            return self.settings.SEASON[0]
        # elif current == self.settings.SEASON[2]:
        #    return self.settings.SEASON[0]

        return ""

    def __gen(self, index: int, comb_size: float, comb: List[str], state: State) -> None:
        if comb_size > self.settings.MAX_POINTS_PER_SEMESTER:
            return

        semester = deepcopy(comb)
        key = comb_size
        # if comb_size >= self.settings.MIN_POINTS_PER_SEMESTER:
        #     key = self.settings.MIN_POINTS_PER_SEMESTER
        if not self.__semesters.get(comb_size):
            self.__semesters[comb_size] = set()
        self.__semesters[key].add(tuple(semester))

        i = index
        new_state = deepcopy(state)
        while i < len(self.__available_courses_list):
            course_id = self.__available_courses_list[i]
            course = Data.get_instance().courses_dict[course_id]
            # if not new_state.is_it_irrelevant_course(course.get_type(), course_id):
            if not comb:
                comb = [course_id]
            else:
                comb.append(course_id)

            self.__gen(i + 1, comb_size + course.get_credit_points(), comb, new_state)
            comb.remove(course_id)
            i = i + 1

    def get_the_most_relevant_courses(self, courses: {}, state: State) -> [str]:
        final_relevant_courses = []
        left_points_per_type = {}
        total_left_points = 0
        total_points = 0
        for typ in courses:
            if typ != self.settings.COURSES_TYPES[8] and typ != self.settings.COURSES_TYPES[9]:
                left_points = state.degree_requirements[typ][1]
                if left_points > 0:
                    left_points_per_type[typ] = left_points
                    total_left_points += left_points
        if self.settings.COURSES_TYPES[0] in left_points_per_type.keys():
            if left_points_per_type[self.settings.COURSES_TYPES[0]] >= (73.5 - self.settings.MANDATORY_COURSES_POINTS):
                final_relevant_courses.extend(courses[self.settings.COURSES_TYPES[0]][:self.settings.MAX_AVAILABLE_COURSES - 1])
                if len(courses[self.settings.COURSES_TYPES[0]]) < self.settings.MAX_AVAILABLE_COURSES:
                    total_points += len(courses[self.settings.COURSES_TYPES[0]])
                    del courses[self.settings.COURSES_TYPES[0]]
                else:
                    return final_relevant_courses

        # if the student finish A list but not a project
        if state.degree_requirements[self.settings.COURSES_TYPES[6]][1] <= 0 and state.degree_requirements[self.settings.COURSES_TYPES[8]][1] == 1:
            if courses.get(self.settings.COURSES_TYPES[6]):
                for c_id in courses[self.settings.COURSES_TYPES[6]]:
                    if Data.get_instance().courses_dict[c_id].get_is_project():
                        final_relevant_courses.append(c_id)
                        total_points += 1
                        del courses[self.settings.COURSES_TYPES[6]]
                        break

        if state.degree_requirements[self.settings.COURSES_TYPES[4]][1] <= 0 and state.degree_requirements[self.settings.COURSES_TYPES[9]][1] == 1:
            total_left_points += 3
            left_points_per_type[self.settings.COURSES_TYPES[4]] = 3

        remaining_courses = []
        for typ in courses:
            if typ not in left_points_per_type.keys():  # if the student finish A list but not B list courses contains A list courses that can be counted as B list
                continue  # instead of continue we can add the courses to the B list courses in courses and sort again by importance
            total_per_type = 0
            percentage_points = (left_points_per_type[typ] / total_left_points) * self.settings.MAX_AVAILABLE_COURSES
            if 0 < percentage_points < 1:
                percentage_points = 1
            else:
                percentage_points = round(percentage_points)
            for i in range(len(courses[typ])):
                if total_per_type + 1 > percentage_points:
                    if i < len(courses[typ]):
                        remaining_courses.extend(courses[typ][i:])
                    break
                else:
                    final_relevant_courses.append(courses[typ][i])
                    total_points += 1
                    total_per_type += 1
            if total_points >= self.settings.MAX_AVAILABLE_COURSES:
                break

        i = 0
        while total_points < self.settings.MAX_AVAILABLE_COURSES and i < len(remaining_courses):
            final_relevant_courses.append(remaining_courses[i])
            i += 1
            total_points += 1

        return final_relevant_courses

    def select_random_courses(self, courses):
        rnd = []
        c = 0
        p = 0
        if '234114' in courses:
            rnd.append('234114')
            courses.remove('234114')
            c = 1
            p = 4
        while True:
            if len(courses) < 7:
                print('new courses selected: ')
                for course in courses:
                    print(Data.get_instance().courses_dict[course].get_id())
                print('total points: ', sum([Data.get_instance().courses_dict[course].get_credit_points() for course in courses]))
                print('courses names: ', [Data.get_instance().courses_dict[course].get_name() for course in courses])
                return courses
            num_courses = random.randint(5 - c , 7 - c)  # Randomly select the number of courses
            selected_courses = random.sample(courses, num_courses)  # Randomly select the courses
            if (18 - p) <= sum([Data.get_instance().courses_dict[course].get_credit_points() for course in selected_courses]) <= (23 - p):  # Check if the sum of the selected courses is within the desired range
                selected_courses = selected_courses + rnd
                print('new courses selected: ')
                for course in selected_courses:
                    print(Data.get_instance().courses_dict[course].get_id())
                print('total points: ', sum([Data.get_instance().courses_dict[course].get_credit_points() for course in selected_courses]))
                print('courses names: ', [Data.get_instance().courses_dict[course].get_name() for course in selected_courses])
                return selected_courses + rnd

    def remove_unrelevant_courses(self, state: State, available_courses, semester: str):
        relevant_courses = {}
        relevant_seminars = []
        # remove projects if the student did not take mtm - 234124
        # remove seminars if the student did not complete at least 70% of the חובה

        # init sorted by importance with the course list, override if the settings appropriate FLAG is on
        sorted_by_importance = available_courses

        # #create a dictionary of the avavilable courses by course type
        if self.settings.DEVELOP_OPTIONS_GRAPH_BY_PRIORITY:
            sorted_by_importance = sorted(available_courses,
                                          key=lambda x: Data.get_instance().courses_dict[x].get_importance(),
                                          reverse=True)
        for course_id in sorted_by_importance:
            course = Data.get_instance().courses_dict[course_id]
            if state.is_it_irrelevant_course(course.get_type(), course_id):
                continue
            # if not course.is_given_in_semester(semester):  # NOTE IT WHEN USING COURSES FROM TEST
            #     continue
            if course.get_is_project():
                if not state.is_project_allowed():
                    continue
            if course.get_is_seminar():
                if state.is_seminar_allowed():
                    relevant_seminars.append(course_id)
                continue
            if course.get_is_advanced():
                if not state.is_advanced_allowed():
                    continue
            if relevant_courses.get(course.get_type()):
                relevant_courses[course.get_type()].append(course_id)
            else:
                relevant_courses[course.get_type()] = [course_id]
        # union all the courses that are in relevant courses and the courses that are in the relevant seminars.
        # create random students
        # list_to_random = []
        # for course_type in relevant_courses.keys():
        #     list_to_random.extend(relevant_courses[course_type])
        # list_to_random.extend(relevant_seminars)
        # return self.select_random_courses(list_to_random)


        self.__seminars = relevant_seminars
        if len(self.__seminars) > 0:
            if 'seminar' in Data.get_instance().courses_dict.keys():
                Data.get_instance().courses_dict['000004'].set_type(self.settings.COURSES_TYPES[6])
                Data.get_instance().courses_dict['000004'].set_contains(relevant_seminars)
            else:
                Data.get_instance().courses_dict['000004'] = Course('000004', 'סמינר', 2)
                Data.get_instance().courses_dict['000004'].set_type(self.settings.COURSES_TYPES[6])
                Data.get_instance().courses_dict['000004'].set_contains(relevant_seminars)
            if relevant_courses.get(self.settings.COURSES_TYPES[6]):
                relevant_courses[self.settings.COURSES_TYPES[6]].append('000004')
            else:
                relevant_courses[self.settings.COURSES_TYPES[6]] = ['000004']

        # here the courses are already sorted by importance
        all_courses = []
        sum_courses = 0
        for typ in relevant_courses:
            all_courses.extend(relevant_courses[typ])
            sum_courses += len(relevant_courses[typ])
            if sum_courses > self.settings.MAX_AVAILABLE_COURSES:
                break
        if sum_courses <= self.settings.MAX_AVAILABLE_COURSES:
            return all_courses
        # insert flag to know if we need to remove courses from the list using the self.settings.MAX_AVAILABLE_COURSES
        if self.settings.LIMIT_AVAILABLE_COURSES:
            return self.get_the_most_relevant_courses(relevant_courses, state)
        else:
            return all_courses

    def convert_ids_to_name(self, semester) -> str:
        # sem = semester.split(",")
        name = ""
        for id in semester:
            if id not in ["__DONE__"]:
                name += Data.get_instance().courses_dict[id].get_name() + "\n "
        # return name[::-1]
        return name[::]

    def convert_ids_to_name_reversed(self, semester) -> str:
        # sem = semester.split(",")
        name = ""
        for id in semester:
            if id not in ["__DONE__"]:
                name += Data.get_instance().courses_dict[id].get_name() + "\n "
        return name[::-1]

    def calculate_weight(self, semester: ()):
        weight = 0
        for course_id in semester:
            if course_id not in ["__DONE__"]:
                weight += Data.get_instance().courses_dict[course_id].get_credit_points()
        return weight

    def calculate_heuristic(self, state: State, semester: str) -> int:
        """
        Calculates the heuristic value of a semester
        :param state: the current state of the student
        :param semester: the semester to calculate the heuristic value for
        :return: the heuristic value of the semester
        """
        # if semester contains __DONE__ then return 0

        if '__DONE__' in semester:
            return 0
        semester_as_list = list(filter(lambda c: c != "__DONE__", list(semester)))
        new_state = deepcopy(state)
        new_state.update_completed_courses(semester_as_list)
        heuristic = 0
        for req in new_state.degree_requirements.values():
            if req[1] > 0:
                heuristic += req[1]
        return heuristic

    def get_heuristic(self, u):
        return self.options_graph.nodes[u]['h']

    def has_irrelevant_courses(self, state: State, semester: [str]):
        new_state = deepcopy(state)
        scientific_courses = []
        for course_id in semester:
            if new_state.is_it_irrelevant_course(Data.get_instance().courses_dict[course_id].get_type(), course_id):
                return True
            else:
                if Data.get_instance().courses_dict[course_id].get_type() == self.settings.COURSES_TYPES[4]:
                    scientific_courses.append(course_id)
        if scientific_courses:
            if not new_state.check_scientific_courses(scientific_courses):
                return True
        return False

    def check_tests_dates(self, semester: List[str]):
        dates = []
        for course_id in semester:
            course = Data.get_instance().courses_dict[course_id]
            # get the exam date of moed A
            if course.get_exam_dates():
                if course.get_exam_dates()['א']['Date']:
                    dates.append(course.get_exam_dates()['א']['Date'])

        study_days = timedelta(days=self.settings.DAYS_BETWEEN_TESTS)
        dates = sorted(dates)
        for i in range(len(dates) - 2):
            delta = dates[i + 1] - dates[i]
            if delta < study_days:
                return False
        return True

    def is_linked_courses_legal(self, state: State, semester: [str]):
        completed_courses = state.get_str_courses_list()
        for course_id in semester:
            # we need that at least one of the courses on linked_dict[course_id] has already been completed
            at_least_one = False
            course = Data.get_instance().courses_dict[course_id]
            if course.get_linked_courses():
                for c in course.get_linked_courses():
                    if c in semester or c in completed_courses:
                        at_least_one = True
                        break
                if not at_least_one:
                    return False
            # if Data.get_instance().linked_dict.get(course_id):
            #     for linked_id in Data.get_instance().linked_dict[course_id]:
            #         if linked_id in semester or linked_id in completed_courses:
            #             at_least_one = True
            #             break
        return True

    def get_requirments_of_courses(self, sem: [str]):
        req = {}
        at_least_one = False
        courses_with_times = set()
        for course_id in sem:
            dic = {'lec': None,
                   'tut': None,
                   'lab': None,
                   'pro': None}
            course = Data.get_instance().courses_dict[course_id]
            if course.get_lectures_times():
                at_least_one = True
                courses_with_times.add(course_id)
                dic['lec'] = False
            if course.get_tutorials_times():
                at_least_one = True
                courses_with_times.add(course_id)
                dic['tut'] = False
            if course.get_laboratory_times():
                at_least_one = True
                courses_with_times.add(course_id)
                dic['lab'] = False
            if course.get_project_times():
                at_least_one = True
                courses_with_times.add(course_id)
                dic['pro'] = False
            req[course_id] = deepcopy(dic)
        if not at_least_one or len(courses_with_times) == 1:
            return {}
        return req

    def is_it_fit(self, schedule: {}, comb: [()]):
        # i contain tuple of lec,tut,lab and project, each of them optional and its a list that contian tuples
        # like this: (id, day, start_time, end_time, type, num of meetings in a week, course_id)
        original_sched = deepcopy(schedule)
        for i in comb:
            for j in i:
                schedule[j[1]] = sorted(schedule[j[1]], key=lambda x: (x[2], x[3]))
                for k in schedule[j[1]]:
                    # if there is a class that starts before/with me and ends with/after me its conflict
                    # or if there is a class that starts after me but before i finished
                    # or if there is a class that starts before me but finished after i start
                    if (k[2] <= j[2] and k[3] >= j[3]) or (j[2] < k[2] < j[3]) or (k[2] < j[2] < k[3]):
                        schedule.update(original_sched)
                        return False
                    #Strong
                # there is no conflicts -> add to schedule
                schedule[j[1]].append(j)
        return True

    def check_if_there_is_valid_comb(self, index: int, schedule: {}, combinations: {}):
        if not combinations:
            return True
        if index == len(combinations.keys()) - 1:  # we're in the last course so check all the combs of this course
            course_id = list(combinations.keys())[index]
            for comb in combinations[course_id]:
                # check if the combinations is ok with current schedule
                if self.is_it_fit(schedule, comb):
                    return True
            return False
        else:  # not in the last course
            course_id = list(combinations.keys())[index]
            for comb in combinations[course_id]:
                # check if the combinations is ok with current schedule, and if its ok - add to schedule
                original_sched = deepcopy(schedule)
                if self.is_it_fit(schedule, comb):
                    if self.check_if_there_is_valid_comb(index + 1, schedule, combinations):
                        return True
                    else:
                        schedule.update(original_sched)
                        continue  # try the next combination of this course

            return False

    def check_courses_without_conflicts(self, sem: List[str], requirements: {}, real_sched: {}):
        schedule = {}
        for d in self.settings.DAYS:
            schedule[d] = []

        for course_id in sem:
            course = Data.get_instance().courses_dict[course_id]
            lectures = course.get_lectures_times()
            if lectures:
                for lec in lectures:
                    num = len(lec)
                    # add lec to schedule for each lecture can be more than one meeting per week
                    for i in lec:
                        schedule[i[1]].append(i)
                        # (i.get_start_time(), i.get_end_time(), course_id, 'lec', i.get_id(), num))
            tutorials = course.get_tutorials_times()
            if tutorials:
                for tut in tutorials:
                    num = len(tut)
                    for t in tut:
                        schedule[t[1]].append(t)
                        # (t.get_start_time(), t.get_end_time(), course_id, 'tut', t.get_id(), num))

            labs = course.get_laboratory_times()
            if labs:
                for lab in labs:
                    num = len(lab)
                    for j in lab:
                        schedule[j[1]].append(j)
                        #  (j.get_start_time(), j.get_end_time(), course_id, 'lab', j.get_id(), num))

            projects = course.get_project_times()
            if projects:
                for project in projects:
                    num = len(project)
                    for k in project:
                        schedule[k[1]].append(k)
                        # (k.get_start_time(), k.get_end_time(), course_id, 'pro', k.get_id(), num))

        # more_than_one = deepcopy(requirements)
        # for course_id in sem:
        #     more_than_one = {}
        # sort by start date
        for d in self.settings.DAYS:
            schedule[d] = sorted(schedule[d], key=lambda x: (x[2], x[3]))
            for i in range(len(schedule[d])):
                if i == 0:  # first meeting of the day
                    # if i'm alone or if i'm ending before the next is starting, no conflict
                    if len(schedule[d]) == 1 or schedule[d][i][3] <= schedule[d][i + 1][2]:
                        course_id = schedule[d][i][6]
                        meeting_type = schedule[d][i][4]
                        if schedule[d][i][5] == 1:  # one week meeting
                            if requirements[course_id][meeting_type] is False:
                                real_sched[d].append(schedule[d][i])
                                requirements[course_id][meeting_type] = True
                        else:  # more than one meeting per week
                            pass
                            # more_than_one[course_id]
                            # לוותר או לעדכן רשימה שבid עבור הקורס הזה יש 1
                            # ואחד להגדיל ובסוף לבדוק אם בid המסוים יש לפי הכמות ברשימה המקורית
                elif i == len(schedule[d]) - 1:  # last meeting of the day
                    # if the previous is ending before I start, no conflict
                    if schedule[d][i - 1][3] <= schedule[d][i][2]:
                        course_id = schedule[d][i][6]
                        meeting_type = schedule[d][i][4]
                        if schedule[d][i][5] == 1:  # one week meeting
                            if requirements[course_id][meeting_type] is False:
                                real_sched[d].append(schedule[d][i])
                                requirements[course_id][meeting_type] = True
                        else:  # more than one meeting per week
                            pass
                else:
                    # if i start after the previous one finished and finished before the next one start, no conflicts
                    if schedule[d][i - 1][3] <= schedule[d][i][2] and schedule[d][i][3] <= schedule[d][i + 1][2]:
                        course_id = schedule[d][i][6]
                        meeting_type = schedule[d][i][4]
                        if schedule[d][i][5] == 1:  # one week meeting
                            if requirements[course_id][meeting_type] is False:
                                real_sched[d].append(schedule[d][i])
                                requirements[course_id][meeting_type] = True
                        else:  # more than one meeting per week
                            pass

    def get_list_of_courses_that_need_to_be_scheduled(self, req: {}):
        lst = []
        for course_id in req.keys():
            if all([x is None for x in req[course_id].values()]):
                continue
            else:
                lst.append(course_id)
        return lst

    def is_semester_can_be_scheduled(self, sem: [str]):
        requirements = self.get_requirments_of_courses(sem)
        if requirements == {}:  # if there is no times for all courses or there is times only for one course
            return True
        # check if we already checked this semester
        courses = self.get_list_of_courses_that_need_to_be_scheduled(requirements)
        key = ','.join(sorted(courses))
        if self.cache_schedules.get(key):
            return self.cache_schedules[key]
        else:
            # if there is a semester that those courses are part of him and this semester can be scheduled->no conflicts
            for x in self.cache_schedules.keys():
                if all(i in x for i in courses) and self.cache_schedules[x] is True:
                    self.cache_schedules[key] = True
                    return True
        schedule = {}
        for d in self.settings.DAYS:
            schedule[d] = []
        # check for courses without any conflicts and update in the requirements
        # for now it checks only for meeting with one per week
        self.check_courses_without_conflicts(sem, requirements, schedule)

        # combine for each course all the possible combinations
        combinations = {}
        for course_id in sem:
            lst = []
            course = Data.get_instance().courses_dict[course_id]
            if requirements[course_id]['lec'] is False:
                lst.append(course.get_lectures_times())
            if requirements[course_id]['tut'] is False:
                lst.append(course.get_tutorials_times())
            if requirements[course_id]['lab'] is False:
                lst.append(course.get_laboratory_times())
            if requirements[course_id]['pro'] is False:
                lst.append(course.get_project_times())
            if lst:
                # here I need to check if there is tut in the same time parallel left only one
                comb = list(product(*lst))
                combinations[course_id] = comb

        # save to cache
        self.cache_schedules[key] = self.check_if_there_is_valid_comb(0, schedule, combinations)
        return self.cache_schedules[key]

    def generate_semesters(self, state: State) -> Set[str]:
        is_intro_cs_done = state.is_course_completed('234114')
        self.__semesters = {self.settings.MIN_POINTS_PER_SEMESTER: set()}
        self.__gen(0, 0, [], state)

        optional_semesters = set()
        local_min_points = self.settings.MIN_POINTS_PER_SEMESTER
        sorted_keys = sorted(self.__semesters.keys(), reverse=True)
        semesters_to_filter = []
        for k in sorted_keys:
            if k < local_min_points:
                break
            semesters_to_filter.extend(deepcopy(self.__semesters[k]))
            del self.__semesters[k]
        semesters_to_filter = set(semesters_to_filter)

        while optional_semesters == set():
            semesters_to_sort = deepcopy(semesters_to_filter)
            semesters_to_filter = []
            for u in semesters_to_sort:
                importance_sum = 0
                for course_id in u:
                    if course_id == "__DONE__":
                        continue
                    importance_sum += Data.get_instance().courses_dict[course_id].get_importance()
                semesters_to_filter.append((importance_sum, u))
            semesters_to_sort.clear()

            if self.settings.DEVELOP_OPTIONS_GRAPH_BY_PRIORITY:
                semesters_to_filter.sort(key=lambda x: x[0], reverse=True)

            semesters_to_filter = set(semesters_to_filter)

            for sem in semesters_to_filter:
                sem = list(sem[1])  # Convert sem from a tuple to a list
                if not is_intro_cs_done and '234114' not in sem:
                    continue
                if self.has_irrelevant_courses(state, sem):
                    continue
                if not self.is_linked_courses_legal(state, sem):
                    continue
                # insert flag for seperate tests
                if self.settings.TESTS_CONFLICTS and not self.check_tests_dates(sem):
                    continue
                # insert flag for schedule conflict optimization
                if self.settings.TIME_TABLE_CONFLICTS and not self.is_semester_can_be_scheduled(sem):
                    continue
                if state.is_graduate_with_a_given_semester(sem):
                    sem.append('__DONE__')
                optional_semesters.add(tuple(sem))

            if optional_semesters == set() and self.__semesters != dict():
                max_size = max(self.__semesters.keys())
                semesters_to_filter = deepcopy(self.__semesters[max_size])
                del self.__semesters[max_size]
            else:
                break

        return optional_semesters

    def is_it_a_promising_path(self, state: State, length: int):
        # if we divide the remaining points to semesters and in each semesters we put the max possible points and
        # still the length to finish the degree is longest from the one that found until now, we don't want to keep
        # calculate this path its worthless -> the A* will never choose this path
        remaining_points = state.get_remaining_points()
        minimum_possible_length = math.ceil(remaining_points / self.settings.MAX_POINTS_PER_SEMESTER) + length
        if minimum_possible_length > self.__shortest_path_length:
            self.__cut_counter += 1
            return False
        return True

    def add_optional_semesters_from_current_state(self, origin_node: (), state: State, season: str, length: int):
        semester_as_list = list(origin_node[0])
        new_state = deepcopy(state)
        new_state.update_completed_courses(semester_as_list)
        if new_state.is_graduate():
            return

        # insert flag for pruning
        if self.settings.PRUNING and not self.is_it_a_promising_path(new_state, length):
            return

        available_and_linked_courses = CoursesGraph.get_instance().get_valid_courses(new_state.get_str_courses_list())
        available_courses = available_and_linked_courses[0]
        # self.linked_courses_dict = {}
        # # convert the tuples list to dict(the value is what the student has to take with the key)
        # for linked in available_and_linked_courses[1]:
        #     self.linked_courses_dict[linked[1]] = linked[0]
        self.__available_courses_list = self.remove_unrelevant_courses(new_state, available_courses, season)
        # print id from available courses and convert to name
        # print(self.__available_courses_list)
        # print(self.convert_ids_to_name(self.__available_courses_list))
        # print('Number of courses: ', len(self.__available_courses_list))
        # if len(self.__available_courses_list) == 0:
        #     print('0 courses is available')
        if self.__available_courses_list:
            optional_semesters_set = self.generate_semesters(new_state)
            # self.options_graph.add_nodes_from(optional_semesters_set)
            if not self.options_counter.get(length) or (self.options_counter[length] < len(optional_semesters_set)):
                self.options_counter[length] = len(optional_semesters_set)
            next_season = self.get_next_season(season)
            length += 1
            for x in optional_semesters_set:
                node = (x, self.options_graph.number_of_nodes())
                self.options_graph.add_node(node)
                self.options_graph.add_edge(origin_node, node, weight=self.calculate_weight(x), zero=0,
                                            inverse_weight=1 / self.calculate_weight(x))
                # print('semester: ', x, 'num of semester: ', length)
                # print('name: ', self.convert_ids_to_name(x))
                # print('-------------------------------------------------------------------------')
                self.options_graph.nodes[node]["h"] = self.calculate_heuristic(new_state, x)
                if '__DONE__' not in x:
                    self.add_optional_semesters_from_current_state(node, new_state, next_season, length)
                else:
                    if length < self.__shortest_path_length:
                        self.__shortest_path_length = length
                    self.options_graph.add_edge(node, "end", weight=0, zero=0, inverse_weight=0)

    def create_graph(self) -> None:
        state = Data.get_instance().get_student().get_state()
        self.options_graph = nx.DiGraph()
        available_and_linked_courses = CoursesGraph.get_instance().get_valid_courses(state.get_str_courses_list())
        available_courses = available_and_linked_courses[0]
        # print available_courses like this (for loop): [('1', 'מבוא למדעי המחשב'), \n, (2, 'מבוא למדעי המחשב'), \n, (3, 'מבוא למדעי המחשב')]
        # convert the tuples list to dict(the value is what the student has to take with the key)
        for linked in available_and_linked_courses[1]:
            self.linked_courses_dict[linked[1]] = linked[0]
        if available_courses:
            self.options_graph.add_node("start")
            self.options_graph.add_node("end")
            first_season = self.settings.SEASON[0]  # start calculate from semester A --> the student will enter this detail?
            self.__available_courses_list = self.remove_unrelevant_courses(state, available_courses, first_season)
            # print(self.__available_courses_list)
            # print(self.convert_ids_to_name(self.__available_courses_list))
            optional_semesters_set = self.generate_semesters(state)
            # print('Number of courses: ', len(self.__available_courses_list))
            self.options_counter[1] = len(optional_semesters_set)
            if len(self.__available_courses_list) == 0:
                print('kk')
            # self.options_graph.add_nodes_from(optional_semesters_set)
            next_season = self.get_next_season(first_season)
            length = 1
            for semester in optional_semesters_set:
                node = (semester, self.options_graph.number_of_nodes())
                self.options_graph.add_node(node)
                self.options_graph.add_edge("start", node, weight=self.calculate_weight(semester), zero=0,
                                            inverse_weight=1 / self.calculate_weight(semester))
                # print('semester: ', semester)
                # print('name: ', self.convert_ids_to_name(semester))
                # print('-------------------------------------------------------------------------')
                # if '000004' in semester:
                #     self.options_graph.nodes[semester]["seminars"] = self.__seminars
                self.options_graph.nodes[node]["h"] = self.calculate_heuristic(state, semester)
                if '__DONE__' not in semester:
                    self.add_optional_semesters_from_current_state(node, state, next_season, length)
                else:
                    if length < self.__shortest_path_length:
                        self.__shortest_path_length = length
                    self.options_graph.add_edge(node, "end", weight=0, zero=0, inverse_weight=0)

        for node in self.options_graph.nodes:
            if node != 'start' and node != 'end':
                self.options_graph.nodes[node]["data"] = self.convert_ids_to_name_reversed(node[0])
            else:
                self.options_graph.nodes[node]["data"] = node
        # labels = nx.get_node_attributes(self.options_graph, "data")
        # color_map = ['red' if node == "start" or node == "end" else 'blue' for node in self.options_graph]
        # pos = nx.spring_layout(self.options_graph, seed=10396953)
        # nx.draw_networkx_nodes(self.options_graph, pos, node_size=1000, node_color=color_map)
        # nx.draw_networkx_edges(self.options_graph, pos, arrowsize=13, arrowstyle="->",node_size=1000)
        # nx.draw_networkx_labels(self.options_graph, pos, labels=labels)
        # plt.show()

        # import pydot
        # from networkx.drawing.nx_pydot import graphviz_layout
        # #
        # # labels = nx.get_node_attributes(self.options_graph, "data")
        # pos = graphviz_layout(self.options_graph, prog="dot")
        # color_map = ['red' if node == "start" or node == "end" else 'grey' for node in self.options_graph]
        # nx.draw_networkx_nodes(self.options_graph, pos, node_size=1000, node_color=color_map)
        # nx.draw_networkx_edges(self.options_graph, pos, arrowsize=13, arrowstyle="->", node_size=1000)
        # # nx.draw_networkx_labels(self.options_graph, pos, labels=labels, font_size=10)
        # nx.draw(self.options_graph, pos)
        # #change the size of the figure
        # plt.gcf().set_size_inches(17, 17)
        # #space between the nodes
        # plt.margins(0.01, 0.01)
        # plt.show()
        # print number of nodes and edges
        # print("------------------------------options graph------------------------------")
        # print("number of nodes: ", self.options_graph.number_of_nodes())
        # print("number of edges: ", self.options_graph.number_of_edges())
        # print('cut counter: ', self.__cut_counter)
        # for i in self.options_counter:
        #     print('length: ', i, 'num of options: ', self.options_counter[i])
        # nx.write_gexf(self.options_graph, "test.gexf")
        # nx.write(self.options_graph, "test.gexf")
