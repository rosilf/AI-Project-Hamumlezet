from datetime import date
from datetime import time
import requests
from Course import Course
from bs4 import BeautifulSoup
from settings import Settings
from TimeTableClasess import *
from typing import List, Dict
# -*- coding: utf-8 -*-

SEASON = Settings.get_instance().SEASON

def convert_inteval_time_str_to_time_obj(t: str) -> (time, time) or (None, None):
    if t == "\xa0":
        return None, None
    times = t.split('-')
    return [time(int(times[0].split(':')[0]), int(times[0].split(':')[1])),
            time(int(times[1].split(':')[0]), int(times[1].split(':')[1]))]


def print_matrix(matrix):
    # Determine the maximum length of any element in the matrix
    max_length = max(len(str(element)) for row in matrix for element in row)
    print('-' * (max_length * len(matrix[0]) + 1))
    print('-' * (max_length * len(matrix[0]) + 1))
    # Print each row with a frame and aligned cells
    for row in matrix:
        print("|", end="")
        for element in row:
            element_str = str(element).ljust(max_length)
            print(f" {element_str} |", end="")
        print()

        # Print a line after each row
        print("-" * (max_length + 3) * len(row))


def sort_by_key(lst: List[Dict], key: str) -> List[List[Dict]]:
    # sort the dictionary by the key "key"
    lst.sort(key=lambda x: x[key])
    # create list of list of dictionaries, each list contains dictionaries with the same key "קבוצת רישום"
    lst_of_lst = []
    for i in range(0, len(lst)):
        if i == 0:
            lst_of_lst.append([lst[i]])
        else:
            if lst[i][key] == lst[i - 1][key]:
                lst_of_lst[-1].append(lst[i])
            else:
                lst_of_lst.append([lst[i]])
    return lst_of_lst

    pass


def create_registering_groups(lst: List[List[List[Dict]]]) -> List[RegisteringGroup]:
    # create list of registering groups
    registering_groups = []
    for i in range(0, len(lst)):
        # create list of groups
        groups = []
        for j in range(0, len(lst[i])):
            # create list of classes
            classes = []
            for k in range(0, len(lst[i][j])):
                if lst[i][j][k]['קבוצת רישום'] == lst[i][j][0]['קבוצת רישום']:
                    classes.append(Class(lst[i][j][k]['חדר'], lst[i][j][k]['בניין'], lst[i][j][k]['מועד'][0],
                                         lst[i][j][k]['מועד'][1], lst[i][j][k]['יום'], lst[i][j][k]['מרצה'],
                                         lst[i][j][k]['תרגיל הרצאה'],lst[i][j][k]['מס.']))
            groups.append(Group(lst[i][j][0]['מס.'], classes))
        registering_groups.append(RegisteringGroup(lst[i][0][0]['קבוצת רישום'], groups))
    return registering_groups


def clean_matrix(matrix) -> List[RegisteringGroup]:
    # change the name of the column "קבוצתרישום" to "קבוצת רישום"
    for j in range(0, len(matrix[0])):
        if matrix[0][j] == 'קבוצתרישום':
            matrix[0][j] = 'קבוצת רישום'
    for j in range(0, len(matrix[0])):
        if matrix[0][j] == 'תרגילהרצאה':
            matrix[0][j] = 'תרגיל הרצאה'
    # Replace newline characters
    matrix = [[item.replace('\n', '') if isinstance(item, str) else item for item in row] for row in matrix]
    # mark rows that contains "מעבדה" or "תרגול" or "סמינר" or "הרצאה" or "פרויקט" and after the cell with these words,
    # check if all the cells in the row are empty (''), if so, to mark the row else, continue.
    temp_mat = []
    for i, row in enumerate(matrix):
        if all(val == '' for val in row[0:]):
            continue
        else:
            temp_mat.append(row)
    matrix = temp_mat
    temp_mat = []
    # delete rows that contains "מעבדה" or "תרגול" or "סמינר" or "הרצאה" or "פרויקט" and after
    # the that the cells are empty.
    for i, row in enumerate(matrix):
        for j, cell in enumerate(row):
            if cell == "מעבדה" or cell == "תרגול" or cell == "סמינר" or cell == "הרצאה" or cell == "פרויקט":
                if all(val == '' for val in row[:j]):
                    row.append('mark')
    for i, row in enumerate(matrix):
        if 'mark' not in row:
            temp_mat.append(row)
    matrix = temp_mat
    temp_mat = []
    # if cel is '' and the cell above contains "מעבדה" or "תרגול" or "סמינר" or "הרצאה" or "פרויקט",
    # copy the cell above to the cell
    for i, row in enumerate(matrix):
        for j, cell in enumerate(row):
            if cell == '' and (
                    matrix[i - 1][j] == "מעבדה" or matrix[i - 1][j] == "תרגול" or matrix[i - 1][j] == "סמינר" or
                    matrix[i - 1][j] == "הרצאה" or matrix[i - 1][j] == "פרויקט"):
                matrix[i][j] = matrix[i - 1][j]
    # if cel is '' and the cell above contains "מס." (like 11) or "קבוצת רישום" (like 10),
    # copy the cell above to the cell
    if "מס." in matrix[0]:
        j = matrix[0].index("מס.")
        for i, row in enumerate(matrix):
            if matrix[i][j] == '' and (matrix[i - 1][j] != '' or matrix[i - 1][j] != 'מס.'):
                matrix[i][j] = matrix[i - 1][j]
    if "קבוצת רישום" in matrix[0]:
        j = matrix[0].index("קבוצת רישום")
        for i, row in enumerate(matrix):
            if matrix[i][j] == '' and (matrix[i - 1][j] != '' or matrix[i - 1][j] != 'קבוצת רישום'):
                matrix[i][j] = matrix[i - 1][j]
    # if "תרגול הרצאה" cell and cell above is the same "תרגול הרצאה", copy the cell above to the cell
    if "תרגול הרצאה" in matrix[0]:
        j = matrix[0].index("תרגול הרצאה")
        for i, row in enumerate(matrix):
            if matrix[i][j] == matrix[i - 1][j]:
                matrix[i][j - 1] = matrix[i - 1][j - 1]
    # delete all the lines that after "מרצה" there are only empty cells.
    if "מרצה" in matrix[0]:
        j = matrix[0].index("מרצה")
        for i, row in enumerate(matrix):
            if all(val == '' for val in row[:j]):
                row.append('mark')
    for i, row in enumerate(matrix):
        if 'mark' not in row:
            temp_mat.append(row)
    matrix = temp_mat
    # if the values in row - "מרצה" and "מס." and "קבוצת רישום" arw equal with the above row,
    # the "מרצה" value will be set to above row.
    if "תרגיל הרצאה" in matrix[0] and "מס." in matrix[0] and "קבוצת רישום" in matrix[0] and "מרצה" in matrix[0]:
        j1 = matrix[0].index("תרגיל הרצאה")
        j2 = matrix[0].index("מס.")
        j3 = matrix[0].index("קבוצת רישום")
        j4 = matrix[0].index("מרצה")
        for i, row in enumerate(matrix):
            if matrix[i][j1] == matrix[i - 1][j1] and matrix[i][j2] == matrix[i - 1][j2] and matrix[i][j3] == \
                    matrix[i - 1][j3]:
                matrix[i][j4] = matrix[i - 1][j4]
    # fill the empty cells with 'None'
    for i, row in enumerate(matrix):
        for j, cell in enumerate(row):
            if cell == '':
                matrix[i][j] = 'לא ידוע'
    # convert 'מועד' that look like this for example: '08:30-12:30' to datetime.time object
    if "מועד" in matrix[0]:
        j = matrix[0].index("מועד")
        for i in range(1, len(matrix)):
            if matrix[i][j] != 'לא ידוע':
                matrix[i][j] = convert_inteval_time_str_to_time_obj(matrix[i][j])
    # print_matrix(matrix)
    # convert the matrix to a list of dictionaries
    dicts = []
    for row in matrix[1:]:
        dicts.append(dict(zip(matrix[0], row)))
    lst_sort_by_group = sort_by_key(dicts, 'קבוצת רישום')
    lst_sort_by_num = []
    for i, item in enumerate(lst_sort_by_group):
        lst_sort_by_num.append(sort_by_key(lst_sort_by_group[i], 'מס.'))
    return create_registering_groups(lst_sort_by_num)


def get_lec_tut_times(course_soup) -> List[RegisteringGroup] or None:
    table = course_soup.find('table', cellpadding="0", cellspacing="0", id="scheduling")
    if table is None:
        return None
    # Find the column headers of the table
    headers = []
    for th in table.find('tr').find_all('th'):
        headers.append(th.text.strip())
    # Find the data rows of the table
    data = []
    for row in table.find_all('tr')[1:]:
        data_row = {}
        cells = row.find_all(['td', 'th'])
        for i, cell in enumerate(cells):
            # Get the cell text and stripping any leading or trailing whitespace
            cell_text = cell.text.strip()
            # Check if this cell spans multiple rows or columns
            rowspan = int(cell.get('rowspan', 1))
            colspan = int(cell.get('colspan', 1))
            # Split the cell text into multiple cells if it contains newline characters
            cell_text_parts = cell_text.split('\n')
            num_newlines = len(cell_text_parts) - 1
            if num_newlines > 0:
                colspan = max(colspan, num_newlines + 1)
            # Loop over each row and column that the cell spans
            for j in range(rowspan):
                for k in range(colspan):
                    # Calculate the key for the current cell based on its position in the table
                    key = headers[i + k] if i + k < len(headers) else f"Column {i + k + 1}"
                    # If this is the first row and column that the cell spans,
                    # add its text content to the data dictionary
                    if j == 0 and k == 0:
                        # Check if the key is already in the dictionary; if not, initialize it to an empty string
                        if key not in data_row:
                            data_row[key] = ""
                        data_row[key] += cell_text_parts[0]
                    # If this is not the first row or column that the cell spans,
                    # append its text content to the existing data for the cell
                    else:
                        if key not in data_row:
                            data_row[key] = ""
                        if j < len(cell_text_parts):
                            data_row[key] += '\n' + cell_text_parts[j]
        # Add the row data to the list of data rows
        data.append(data_row)
    # Convert the list of dictionaries to a matrix
    matrix = [list(data[0].keys())]
    for row in data:
        matrix_row = []
        for key in matrix[0]:
            matrix_row.append(row.get(key, ''))
        matrix.append(matrix_row)
    return clean_matrix(matrix)


def create_course(id: str, html_path: str = None) -> Course or None:
    if html_path is None:
        url_page_course = "https://www.graduate.technion.ac.il/Subjects.Heb/?SUB=" + id
        html = requests.get(url_page_course)
        is_req_suc = html.status_code
        if is_req_suc != 200:
            return None
        course_soup = BeautifulSoup(html.content, 'html.parser')
    else:
        with open(html_path, 'r', encoding="windows-1255") as f:
            html = f.read()
        course_soup = BeautifulSoup(html, 'html.parser')
    name = get_name(course_soup)
    if name is None:
        return None
    credit_point, given_in_semester = get_given_in_semester_and_credit_point(course_soup)
    prerequisites_courses, linked_courses, overlapping_courses, incorporated_courses = get_pre_link_over_incor_courses(
        course_soup)
    exams_dates = None
    lec_tut_times = None
    if given_in_semester:
        exams_dates = get_exams_dates(course_soup)
    if given_in_semester:
        lec_tut_times = get_lec_tut_times(course_soup)
    return Course(id, name, credit_point, prerequisites_courses, linked_courses,
                  overlapping_courses, incorporated_courses, given_in_semester,
                  lec_tut_times, exams_dates)


def split_by_str_and_erase_him(lst: List, string: str) -> List[List]:
    size = len(lst)
    idx_list = [idx + 1 for idx, val in
                enumerate(lst) if val == string]
    res = [lst[i: j] for i, j in
           zip([0] + idx_list, idx_list +
               ([size] if idx_list[-1] != size else []))]
    for i in res:
        if string in i:
            i.remove(string)
    return res


def swap_positions(lst: List, pos1: int, pos2: int) -> List:
    lst[pos1], lst[pos2] = lst[pos2], lst[pos1]
    return lst


def reorder_general_info(general_info: List) -> List:
    for i in range(0, len(general_info)):
        if (general_info[i] == 'או') or (general_info[i] == 'מקצועות קדם') or (general_info[i] == 'מקצועות צמודים') or \
                (general_info[i] == 'מקצועות ללא זיכוי נוסף') or (general_info[i] == 'מקצועות ללא זיכוי נוסף (מוכלים)'):
            swap_positions(general_info, i, i - 1)
    return general_info


def sort_general_info(txt: List) -> List:
    general_info = []
    for i in txt:
        if (i.isnumeric()) or (i == 'או') or (i == 'מקצועות קדם') or (i == 'מקצועות צמודים') or \
                (i == 'מקצועות ללא זיכוי נוסף') or (i == 'מקצועות ללא זיכוי נוסף (מוכלים)'):
            general_info.append(i)
    return reorder_general_info(general_info)


def create_lists_pre_link_over_incore(general_info: List) -> (List[str], List[str], List[str], List[str]):
    prerequisites_courses = []
    linked_courses = []
    overlapping_courses = []
    incorporated_courses = []
    curr = None
    for j in general_info:
        if j == 'מקצועות קדם':
            curr = prerequisites_courses
        elif j == 'מקצועות צמודים':
            curr = linked_courses
        elif j == 'מקצועות ללא זיכוי נוסף':
            curr = overlapping_courses
        elif j == 'מקצועות ללא זיכוי נוסף (מוכלים)':
            curr = incorporated_courses
        else:
            curr.append(j)
    if 'או' in prerequisites_courses:
        prerequisites_courses = split_by_str_and_erase_him(prerequisites_courses, 'או')
    else:
        prerequisites_courses = [prerequisites_courses]
    if len(prerequisites_courses) == 0:
        prerequisites_courses = None
    if len(linked_courses) == 0:
        linked_courses = None
    if len(overlapping_courses) == 0:
        overlapping_courses = None
    if len(incorporated_courses) == 0:
        incorporated_courses = None
    return prerequisites_courses, linked_courses, overlapping_courses, incorporated_courses


def convert_str_to_date(d: str) -> datetime.date or None:
    if d == '\xa0' or d == "":
        return None
    d = d.split('.')
    for i in range(0, len(d)):
        d[i] = d[i]
    return date(int(d[2]), int(d[1]), int(d[0]))


def get_given_in_semester(txt: List) -> Dict:
    dictionary = {'א': False, 'ב': False, 'ג': False}
    semesters = ['א', 'ב', 'ג']
    for sem in semesters:
        if sem in txt:
            dictionary[sem] = True
    # if all values are false, return None
    if any(dictionary.values()) is False:
        return None
    return dictionary


def get_exams_dates(course_soup) -> Dict or None:
    find_all = course_soup.find_all('table', cellpadding="0", class_="tab1", id="sylexam")
    if find_all.__len__() == 0:  # In case there aren't any exam dates.
        return None
    txt = find_all[0].get_text()
    txt = txt.split('\n')
    exam_dates = {'א': {'Day': None, 'Date': None, 'Examination time': None},
                  'ב': {'Day': None, 'Date': None, 'Examination time': None},
                  'ג': {'Day': None, 'Date': None, 'Examination time': None}}
    if 'חדר' not in txt:
        for i, j in zip(range(9, len(txt), 6), SEASON):
            (exam_dates[j])['Day'] = txt[i]
            i += 1
            (exam_dates[j])['Date'] = convert_str_to_date(txt[i])
            i += 1
    else:
        for i, j in zip(range(12, len(txt), 8), SEASON):
            i += 1
            (exam_dates[j])['Day'] = txt[i]
            i += 1
            (exam_dates[j])['Date'] = convert_str_to_date(txt[i])
            i += 1
            (exam_dates[j])['Season'] = txt[i]
    for i, j in zip(range(9, len(txt), 6), SEASON):
        if txt[i] == '\xa0':
            exam_dates[j] = {'Day': None, 'Date': None, 'Season': None, 'Examination time': None}
    # if all values are false, return None
    if any(exam_dates.values()) is False:
        return None
    return exam_dates


def get_pre_link_over_incor_courses(course_soup) -> (List[List[float]] or None, List[List[float]] or None,
                                                     List[List[float]] or None, List[List[float]]) or None:
    find_all = course_soup.find_all('table', class_="tab0", cellpadding="2", cellspacing="0", dir="ltr")
    if find_all.__len__() == 0:  # In case there aren't any prerequisites\ linked\ overlapping\ incorporated courses.
        return None, None, None, None
    txt = find_all[0].get_text()
    txt = txt.split('\n')
    # 'hi'
    return create_lists_pre_link_over_incore(sort_general_info(txt))


def get_name(course_soup: BeautifulSoup) -> str or None:
    find_all = course_soup.find_all('span', dir='rtl', style='color:#6d96bd;font-size:16px')
    if find_all.__len__() == 0:
        return None
    txt = find_all[0].get_text()
    txt = txt.split('\n')
    txt = txt[2]
    if '/' in txt:
        txt = txt.replace('/', '')
    if '"' in txt:
        txt = txt.replace('"', '')
    return txt


def get_given_in_semester_and_credit_point(course_soup: BeautifulSoup) -> (float, Dict):
    find_all = course_soup.find_all('table', cellpadding="0", cellspacing="0")
    txt = find_all[0].get_text()
    txt = txt.split('\n')
    credit_point = txt[8]
    txt = find_all[2].get_text()
    txt = txt.split('\n')
    txt = txt[5].split('+')
    return credit_point, get_given_in_semester(txt)
