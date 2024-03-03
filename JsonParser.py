import json
import ast
import re
import datetime  # please ignore this line, don't remove it!


class JsonParser:
    def __init__(self, json_file):
        self.__json_file = json_file

    def get_courses_dict(self):
        with open(self.__json_file, encoding="windows-1255") as f:
            data = json.load(f)
        for c in data['Courses']:
            for k in c.keys():
                if c[k] == 'None':
                    c[k] = None
                elif k == '_Course__credit_points':
                    c[k] = float(c[k])
                elif k == '_Course__subtype':
                    c[k] = ast.literal_eval(c[k])
                elif k == '_Course__prerequisites_courses' or k == '_Course__linked_courses' \
                        or k == '_Course__overlapping_courses' or k == '_Course__incorporated_courses':
                    c[k] = ast.literal_eval(c[k])
                elif k == '_Course__given_in_semester':
                    c[k] = ast.literal_eval(c[k])
                # if k == '_Course__time_table':
                #     c[k] = ast.literal_eval(c[k])
                elif k == '_Course__exam_dates':
                    # Define the regular expression pattern to match date strings
                    date_pattern = r"datetime.date\((\d{4}), (\d{1,2}), (\d{1,2})\)"
                    # Replace all date strings with datetime.date objects
                    c[k] = re.sub(date_pattern, lambda match: "datetime.date({}, {}, {})".format(*match.groups()), c[k])
                    # Evaluate the modified string as a Python expression
                    c[k] = eval(c[k])
        return data
