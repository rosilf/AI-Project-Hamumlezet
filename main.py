# -*- coding: utf-8 -*-
import networkx as nx
# import matplotlib.pyplot as plt
from JsonParser import JsonParser
import ast
from Create_students import *
from settings import Settings
Settings()
import Astar
from Data import Data
from State import State
from Student import Student
from CoursesGraph import CoursesGraph
from OptionsGraph import OptionsGraph
from GradeSheetParser import GradeSheetParser
from CatalogParser import CatalogParser
from GraduateParser import GraduateParser
import argparse
import time
from HtmlDownloader import download_html
import time
import json
import csv
import itertools
import os


def initialization(experiments_dict):
    academic_bg = experiments_dict["academic background"]
    # print('------------------------------Student------------------------------')
    file_path = "students_examples/" + academic_bg + ".txt"
    grade_sheet = GradeSheetParser(file_path)
    #print the name of file.
    # print('file name: ' + (file_path.split('/')[1]))
    catalog = CatalogParser()
    # courses_obj = GraduateParser(None, catalog, True, False) # arguments for extracting courses from CoursesTest
    # courses_obj = GraduateParser('courses.json', None, False, False) # arguments for extracting courses from json file
    # courses_obj = GraduateParser(None, CatalogParser, False, True)  # arguments for extracting courses from graduate with internet access
    # site with internet access
    courses_obj = GraduateParser(None, catalog, False, False)  # arguments for extracting courses from graduate site without internet access
    # without internet access
    Data()
    Data.get_instance().set_courses_dict(courses_obj.get_courses_dict())
    Data.get_instance().set_linked_dict(courses_obj.get_linked_dict())
    state = State(grade_sheet.get_completed_courses_id(),
                  catalog.get_three_year_degree_requirements_credit_points())
    student = Student(grade_sheet.get_name(), grade_sheet.get_id(),
                      grade_sheet.get_catalog_type(), grade_sheet.get_degree_type(), state)
    Data.get_instance().set_student(student)
    # print which courses the student has completed, id and name
    completed_courses = GradeSheetParser.get_instance().get_completed_courses_id()
    credits_left = state.get_remaining_points()
    Settings.get_instance().config_settings(experiments_dict, credits_left)
    # print("max available set to: " + str(Settings.get_instance().MAX_AVAILABLE_COURSES))
    # print('completed courses:')
    completed_courses_names = ''
    for course in completed_courses:
        # print(Data.get_instance().courses_dict[course].get_name() + ' : ' + Data.get_instance().courses_dict[course].get_id())
        completed_courses_names += Data.get_instance().courses_dict[course].get_name() + ' : ' + Data.get_instance().courses_dict[course].get_id() + '\n'
    # print("credits left for graduation: " + str(state.get_remaining_points()))
    # print(state.get_remaining_points_per_req())
    return completed_courses_names, str(state.get_remaining_points()), state.get_remaining_points_per_req()

def heuristic_points_to_graduation(u, v):
    """ u and v are nodes in the graph. v is the goal node(end) """
    if u == "end":
        return 0
    return OptionsGraph.get_instance().get_heuristic(u)

def heuristic_importance(u, v):
    """ u and v are nodes in the graph. v is the goal node(end) """
    if u == "end":
        return 0
    importance_sum = 0
    #iterate over courses in the node tuple and sum their importance
    for course_id in u[0]:
        if course_id == "__DONE__":
            continue
        importance_sum += Data.get_instance().courses_dict[course_id].get_importance()
    importance_factor = 1/importance_sum if importance_sum > 0 else 1
    return importance_factor

def create_exp_config_files():
    # Delete all files in the experiments/config/ directory
    config_dir = "experiments/config/"
    for file_name in os.listdir(config_dir):
        file_path = os.path.join(config_dir, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)

    exp_id = create_tuning_exp_config_files() # Continuous index counter, starts from the last tuning exp index + 1

    # Define the possible values for each flag
    flags = [
        "time table conflicts",
        "tests conflicts",
        "pruning",
        "limit available courses",
        "develop options graph by priority",
    ]

    # Generate all possible combinations of the flags
    flag_combinations = list(itertools.product([True, False], repeat=len(flags)))

    # Get the list of academic background files
    academic_files_path = "students_examples/"
    academic_files = [file for file in os.listdir(academic_files_path) if file.endswith(".txt")]

    # Create experiment configuration files for each academic background
    for academic_file in academic_files:
        academic_background = os.path.splitext(academic_file)[0]

        # Create a JSON file for each flag combination
        for index, combination in enumerate(flag_combinations):
            # Create the description string with flag names separated by '&'
            flag_names = [flags[i] for i, flag_value in enumerate(combination) if flag_value]
            description = " & ".join(flag_names)

            # Create the experiment configuration dictionary
            exp_dict = {
                "id": str(exp_id),
                "description": description,
                "academic background": academic_background,
                "max available courses": "default"
            }
            exp_dict.update(dict(zip(flags, combination)))

            # Write the experiment configuration to a JSON file
            filename = f"experiments/config/{exp_id}_{academic_background}_{index + 1}.json"
            with open(filename, 'w') as file:
                json.dump(exp_dict, file, indent=4)

            # print(f"Created JSON file: {filename}")

            exp_id += 1  # Increment the counter for the next file

def create_tuning_exp_config_files() -> int:
    # Delete all files in the experiments/config/ directory
    config_dir = "experiments/config/"
    for file_name in os.listdir(config_dir):
        file_path = os.path.join(config_dir, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Define the possible values for the "max available courses" flag
    max_available_courses_values = [6,7,8,9,10,11,12,13,14,15]

    # Get the list of academic background files
    academic_files_path = "students_examples/"
    academic_files = [file for file in os.listdir(academic_files_path) if file.endswith(".txt")]

    # Create experiment configuration files for each academic background
    counter = 1  # Continuous index counter
    for academic_file in academic_files:
        academic_background = os.path.splitext(academic_file)[0]

        # Create a JSON file for each "max available courses" value
        for max_courses in max_available_courses_values:
            # Create the experiment configuration dictionary
            exp_dict = {
                "id": str(counter),
                "description": "tuning max available courses value = " + str(max_courses),
                "academic background": academic_background,
                "max available courses": max_courses,
                "time table conflicts": True,
                "tests conflicts": True,
                "pruning": True,
                "limit available courses": True,
                "develop options graph by priority": True
            }

            # Write the experiment configuration to a JSON file
            filename = f"experiments/config/{counter}_tuning_{academic_background}_{max_courses}.json"
            with open(filename, 'w') as file:
                json.dump(exp_dict, file, indent=4)

            # print(f"Created JSON file: {filename}")

            counter += 1  # Increment the counter for the next file
    return counter


def create_results_csv(file_name, exp_dict, completed_courses_names, credit_left, credit_left_per_typ, total_time,
                           initialization_total_time, courses_graph_total_time, options_graph_total_time, nodes, edges,
                           cut_counter, options_counter, a_star_results):
    # Create the results CSV file
    data = {
        "id": exp_dict["id"],
        "description": exp_dict["description"],
        "academic background": exp_dict["academic background"],
        "max available courses": exp_dict["max available courses"],
        "time table conflicts": exp_dict["time table conflicts"],
        "tests conflicts": exp_dict["tests conflicts"],
        "pruning": exp_dict["pruning"],
        "limit available courses": exp_dict["limit available courses"],
        "develop options graph by priority": exp_dict["develop options graph by priority"],
        "completed courses": completed_courses_names,
        "credit left": credit_left,
        "credit left by type": credit_left_per_typ,
        "MAX_VALUE": Settings.get_instance().MAX_AVAILABLE_COURSES,
        "total time": round(total_time,3),
        "initialization total time": round(initialization_total_time,3),
        "courses graph total time": round(courses_graph_total_time,3),
        "options graph total time": round(options_graph_total_time,3),
        "nodes": nodes,
        "edges": edges,
        "cut counter": cut_counter,
    }
    for layer in range(1,21):
        data["layer "+str(layer)+" optional semesters"] = 0
    # iterate from zero to len(options_counter)
    for layer, value in options_counter.items():
        data["layer "+str(layer)+" optional semesters"] = value
    c = 1
    for a_star_config in a_star_results:
        data["A*_" + str(c) + " description"] = a_star_config
        data["A*_" + str(c) + " path"] = a_star_results[a_star_config][0]
        data["A*_" + str(c) + " path_with names"] = a_star_results[a_star_config][1]
        data["A*_" + str(c) + " semester count"] = a_star_results[a_star_config][2]
        data["A*_" + str(c) + " path credits"] = a_star_results[a_star_config][3]
        data["A*_" + str(c) + " time"] = round(a_star_results[a_star_config][4],3)
        c = c + 1
    # Write the results to a CSV file
    filename = f"experiments/results/" + file_name + ".csv"
    with open(filename, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        writer.writeheader()
        writer.writerow(data)

def init_results_csv(file_name, exp_dict, completed_courses_names, credit_left, credit_left_per_typ):
    # Create the results CSV file
    a_star_configurations = ["vanilla- h=credits left for graduation, g=weight",
            "h=importance, g=weight",
            "h=importance, g=zero",
            "h=credits left for graduation, g=zero",
            "h=credits left for graduation, g=inverse_weight",
            "h=zero g=inverse_weight"]
    data = {
        "id": exp_dict["id"],
        "description": exp_dict["description"],
        "academic background": exp_dict["academic background"],
        "max available courses": exp_dict["max available courses"],
        "time table conflicts": exp_dict["time table conflicts"],
        "tests conflicts": exp_dict["tests conflicts"],
        "pruning": exp_dict["pruning"],
        "limit available courses": exp_dict["limit available courses"],
        "develop options graph by priority": exp_dict["develop options graph by priority"],
        "completed courses": completed_courses_names,
        "credit left": credit_left,
        "credit left by type": credit_left_per_typ,
        "MAX_VALUE": Settings.get_instance().MAX_AVAILABLE_COURSES,
    }
    # Write the results to a CSV file
    for layer in range(1,21):
        data["layer "+str(layer)+" optional semesters"] = 0
    c = 1
    for a_star_config in a_star_configurations:
        data["A*_" + str(c) + " description"] = "timedout"
        data["A*_" + str(c) + " path"] = "timedout"
        data["A*_" + str(c) + " path_with names"] = "timedout"
        data["A*_" + str(c) + " semester count"] = "timedout"
        data["A*_" + str(c) + " path credits"] = "timedout"
        data["A*_" + str(c) + " time"] = "timedout"
        c = c + 1
    filename = f"experiments/results/" + file_name + ".csv"
    with open(filename, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        writer.writeheader()
        writer.writerow(data)

if __name__ == '__main__':
    # ----------------------- Initialization ----------------------------------- #
    ## experiments configurations for tuning and optimizations experiments
    # 1-255 are for tuning experiments and 256-1887 are for optimizations experiments
    # 255 = #num_of_students_in_students_examples * #num_of_options_for_max_available_courses
    # 1887 - 255 = 1632 = #num_of_students_in_students_examples * ( 2 ^ #num_of_flagged_optimizations )
    create_exp_config_files()

    # Create an argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("exp_id",nargs='?', type=int, help="Experiment ID")

    # Parse the command-line arguments
    args = parser.parse_args()
    # Check if the experiment ID is provided as a command-line argument
    if args.exp_id:
        exp_id = args.exp_id
    else:
        exp_id = input("Enter experiment id: ")

    folder_path = "experiments/config/"  # Path to the folder containing the files

    # List all files in the folder
    files = os.listdir(folder_path)

    # Filter files based on the exp_id
    matching_files = [filename for filename in files if filename.startswith(str(exp_id)+"_")]

    if len(matching_files) > 0:
        # Assuming you want to select the first matching file
        selected_file = matching_files[0]
        file_path = os.path.join(folder_path, selected_file)
        # Process the file as needed
        print(f"Selected file: {file_path}")
        with open(file_path, 'r') as file:
            exp_dict = json.load(file)
        file_name_with_extension = os.path.basename(file_path)
        file_name = os.path.splitext(file_name_with_extension)[0]
        initialization_start_time = time.time()
        completed_courses_names, credit_left, credit_left_per_typ = initialization(exp_dict)
        initialization_end_time = time.time()
        init_results_csv(file_name, exp_dict, completed_courses_names, credit_left, credit_left_per_typ)
        initialization_total_time = initialization_end_time - initialization_start_time

    # ----------------------- Courses Graph ----------------------------------- #
        courses_graph_start_time = time.time()
        CoursesGraph()
        CoursesGraph.get_instance().create_graph()
        # create list that the type of the cours is "חובה" and sort it by importance
        # hova = [course for course in Data.get_instance().courses_dict.values() if course.get_type() == "חובה"]
        # importance_sorted_courses_list = sorted(hova, key=lambda x: x.get_importance(), reverse=True)
        courses_graph_end_time = time.time()
        courses_graph_total_time = courses_graph_end_time - courses_graph_start_time

        # ----------------------- Options Graph ----------------------------------- #
        options_graph_start_time = time.time()
        OptionsGraph()
        OptionsGraph.get_instance().create_graph()
        options_graph_end_time = time.time()
        options_graph_total_time = options_graph_end_time - options_graph_start_time
        nodes = OptionsGraph.get_instance().get_number_of_nodes()
        edges = OptionsGraph.get_instance().get_number_of_edges()
        cut_counter = OptionsGraph.get_instance().get_cut_counter()
        options_counter = OptionsGraph.get_instance().get_options_counter()

        # ----------------------- A* algorithm + prints ----------------------------------- #
        a_star_configurations = {
            "vanilla- h=credits left for graduation, g=weight": (heuristic_points_to_graduation, "weight"),
            "h=importance, g=weight": (heuristic_importance, "weight"),
            "h=importance, g=zero": (heuristic_importance, "zero"),
            "h=credits left for graduation, g=zero": (heuristic_points_to_graduation, "zero"),
            "h=credits left for graduation, g=inverse_weight": (heuristic_points_to_graduation, "inverse_weight"),
            "h=zero g=inverse_weight": (None, "inverse_weight")}
        a_star_results = {}
        # print('------------------------------Astar------------------------------')
        for config_name, config in a_star_configurations.items():
            start_time = time.time()
            final_path = Astar.astar_path(OptionsGraph.get_instance().options_graph, "start", "end", config[0],
                                          config[1])
            end_time = time.time()
            a_star_total_time = end_time - start_time
            # print("----A* " + config_name + " :----")
            # Filter out non-tuple elements
            filtered_list = [item for item in final_path if isinstance(item, tuple)]
            # Create a nested list with only numbers
            cleaned_list = [[num for num in tup[0] if num.isdigit()] for tup in filtered_list]
            total_path_credits = 0
            print(cleaned_list)
            print("semester count: " + str(len(cleaned_list)))
            s = ''
            for i, semester in enumerate(cleaned_list, start=1):
                course_names = [Data.get_instance().courses_dict[course_id].get_name() for course_id in semester]
                semester_credits = sum(
                    [Data.get_instance().courses_dict[course_id].get_credit_points() for course_id in semester])
                total_path_credits += semester_credits
                # print(f"Semester {i}: {', '.join(course_names)}")
                # print(f"Semester {i} credits: {semester_credits}")
                s += f"Semester {i}: {', '.join(course_names)}\n"
                s += f"Semester {i} credits: {semester_credits}\n"
            # print(f"Total time: {a_star_total_time}")
            a_star_results[config_name] = (cleaned_list, s, len(cleaned_list), total_path_credits,
                                           a_star_total_time)
            total_path_credits = 0
        total_time = end_time - initialization_start_time
        # print times of the program in seconds and minutes
        # print("------------------------------times------------------------------")
        # print("total time: " + str(total_time) + " seconds" + " = " + str(total_time / 60) + " minutes")
        # print("initialization time: " + str(initialization_total_time) + " seconds" + " = " + str(
        #     initialization_total_time / 60) + " minutes")
        # print("courses graph time: " + str(courses_graph_total_time) + " seconds" + " = " + str(
        #     courses_graph_total_time / 60) + " minutes")
        # print("options graph time: " + str(options_graph_total_time) + " seconds" + " = " + str(
        #     options_graph_total_time / 60) + " minutes")
        # print("finish!")
        create_results_csv(file_name, exp_dict, completed_courses_names, credit_left, credit_left_per_typ, total_time,
                           initialization_total_time, courses_graph_total_time, options_graph_total_time, nodes, edges,
                           cut_counter, options_counter, a_star_results)
    else:
        print("No matching file found.")
