import os
import shutil
import json

allowed_descriptions = [
    "",
    "limit available courses",
    "limit available courses & develop options graph by priority",
    "pruning & limit available courses & develop options graph by priority",
    "time table conflicts & limit available courses & develop options graph by priority",
    "time table conflicts & tests conflicts & limit available courses & develop options graph by priority",
    "time table conflicts & tests conflicts & pruning & limit available courses & develop options graph by priority"
]

source_folder = "experiments/config"
destination_folder = "experiments/config/second_stage_optimization_exp"

counter = 1

for filename in os.listdir(source_folder):
    if filename.endswith(".json"):
        with open(os.path.join(source_folder, filename), "r") as file:
            data = json.load(file)
            description = data.get("description", "")

            if description in allowed_descriptions:
                new_filename = f"{counter}_{filename}"
                shutil.copy(os.path.join(source_folder, filename), os.path.join(destination_folder, new_filename))
                counter += 1