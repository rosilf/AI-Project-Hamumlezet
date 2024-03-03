import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# merge csv files
def merge_csv_files(directory):
    file_extension = '.csv'
    csv_files = glob.glob(os.path.join(f'experiments/{directory}', f'*{file_extension}'))

    data = []

    for file in csv_files:
        df = pd.read_csv(file, encoding="utf-8-sig")
        data.append(df)

    merged_data = pd.concat(data, ignore_index=True, keys=None)

    # Sort the merged data by the 'id' column
    merged_data = merged_data.sort_values(by='id')

    output_file = f'experiments/merged_results_{directory}.csv'
    merged_data.to_csv(output_file, index=False, encoding="utf-8-sig")


def analayse_tuning_exp(directory):
    merge_csv_files(directory)
    # data = pd.read_csv(f'experiments/merged_results_{directory}.csv', low_memory=False) # low_memory=False to avoid DtypeWarning
    data = pd.read_csv(f'experiments/merged_results_{directory}.csv')
    # credit_left_groups = [(0, 23), (24, 46), (47, 79), (80, 112), (113, 200)]
    # credit_left_groups = [(0, 10.5), (11, 21.5), (22, 32.5), (33 ,43.5), (44, 54.5), (55 ,65.5), (66, 76.5), (77, 87.5), (88, 98.5), (99, 109.5), (110, 200)]
    # credit_left_groups = [(118.5, 120), (7.5,30), (34.5,51.5), (52,64), (73.5,81), (95.5,100)]
    # credit_left_groups = [(118,101), (100, 95), (82, 72), (64, 49), (46, 26), (28, 3)]
    # credit_left_groups = [(0, 27.5), (28,41.5), (42,59.5), (60,200)]
    credit_left_groups = [(0,30.5), (31,45.5),(46,60.5),(61,200)]

    # credit_left_groups = [(0, 10), (11, 21), (22, 32), (33, 43), (44, 54), (55, 65), (66, 76), (77, 87), (88, 98),
    #                       (99, 109), (110, 200)]
    num_rows = len(credit_left_groups)
    num_cols = 2
    num_rows = (len(credit_left_groups) + num_cols - 1) // num_cols

    fig, axes = plt.subplots(num_rows, num_cols, figsize=(20, 7 * num_rows))

    if num_rows == 1:
        axes = axes.reshape(1, -1)  # Reshape the axes to 2D array with one row

    # Add a large title at the top
    fig.suptitle("Mean Semester Count by Academic Background", fontsize=16, fontweight='bold')

    # Adjust the spacing between suptitle and subplots
    plt.subplots_adjust(top=0.85)

    for i, group in enumerate(credit_left_groups):
        row = i // num_cols
        col = i % num_cols

        group_data = data.loc[(data['credit left'] >= group[0]) & (data['credit left'] <= group[1])].copy()

        if group_data.empty:
            print(f"No data available for group: {group}. Skipping graph creation.")
            axes[row, col].remove()  # Remove the subplot from the axes array
            continue

        group_timedout_data = group_data.loc[group_data['A*_1 description'] == 'timedout'].copy()
        group_not_timedout_data = group_data.loc[group_data['A*_1 description'] != 'timedout'].copy()

        column_names = [f"A*_{i} semester count" for i in range(1, 7)]
        group_not_timedout_data.loc[:, column_names] = group_not_timedout_data.loc[:, column_names].astype(float)
        group_not_timedout_data['mean semester count'] = group_not_timedout_data.loc[:, column_names].mean(axis=1)
        columns_of_interest = ['academic background', 'max available courses', 'mean semester count', 'credit left']
        group_not_timedout_data = group_not_timedout_data[columns_of_interest]

        print(f"Group: {group}")
        print(group_not_timedout_data)

        ax = axes[row, col]
        sns.barplot(
            data=group_not_timedout_data,
            x='academic background',
            y='mean semester count',
            hue='max available courses',
            palette='viridis',
            ax=ax
        )

        ax.set_ylim(0, 10)
        ax.set_xlabel('Academic Background')
        ax.set_ylabel('Mean Semester Count')
        ax.set_title(f'credit left {group}')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

    # plt.tight_layout()
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    if not os.path.exists(f'experiments/{directory}_fig/'):
        os.makedirs(f'experiments/{directory}_fig/')
    plt.savefig(f'experiments/{directory}_fig/_credit_left_graphs_{credit_left_groups}.png')
    plt.show()

def analayse_optimization_exp(directory):
    merge_csv_files(directory)
    data = pd.read_csv(f'experiments/merged_results_{directory}.csv')
    # Define the optimization configurations
    optimization_configs = ['time table conflicts', 'tests conflicts', 'pruning', 'limit available courses',
                            'develop options graph by priority']

    allowed_descriptions = [
        "",
        "limit available courses",
        "limit available courses & develop options graph by priority",
        "pruning & limit available courses & develop options graph by priority",
        "time table conflicts & limit available courses & develop options graph by priority",
        "time table conflicts & tests conflicts & limit available courses & develop options graph by priority",
        "time table conflicts & tests conflicts & pruning & limit available courses & develop options graph by priority"
    ]

    credit_left_groups = [(0, 30.5), (31, 45.5), (46, 60.5), (61, 200)]

    # Iterate over each credit left group
    for group in credit_left_groups:
        group_data = data.loc[(data['credit left'] >= group[0]) & (data['credit left'] <= group[1])].copy()

        # Initialize an empty list to store the summary table rows
        summary_rows = []

        # Iterate over each unique optimization configuration
        for config in group_data[optimization_configs].drop_duplicates().values:
            config_data = group_data[(group_data[optimization_configs] == config).all(axis=1)]
            timed_out = len(config_data[config_data['A*_1 description'] == 'timedout'])
            not_timed_out = len(config_data) - timed_out

            if not_timed_out > 0:
                mean_run_time = config_data[config_data['A*_1 description'] != 'timedout']['total time'].mean()
                mean_nodes = config_data[config_data['A*_1 description'] != 'timedout']['nodes'].mean()
                mean_edges = config_data[config_data['A*_1 description'] != 'timedout']['edges'].mean()
            else:
                mean_run_time = mean_nodes = mean_edges  = 0

            config_str = ' & '.join(optimization_configs[i] for i, val in enumerate(config) if val)

            if config_str not in allowed_descriptions:
                continue

            summary_rows.append({
                'Optimization Configuration': config_str,
                'Number of Experiments': len(config_data),
                'Timed Out': timed_out,
                'Successful Experiments Percentage': 100 - (timed_out / len(config_data) * 100),
                'Mean Run Time': mean_run_time,
                'Mean Number of Nodes': mean_nodes,
                'Mean Number of Edges': mean_edges
            })

        # Create a DataFrame from the summary table rows
        summary_df = pd.DataFrame(summary_rows, columns=['Optimization Configuration', 'Number of Experiments',
                                                         'Timed Out', 'Successful Experiments Percentage', 'Mean Run Time', 'Mean Number of Nodes',
                                                         'Mean Number of Edges'])

        # Write the summary table to a separate CSV file
        if not os.path.exists(f'experiments/{directory} tables/'):
            os.makedirs(f'experiments/{directory} tables/')
        summary_df.to_csv(f'experiments/{directory} tables/summary_table_credit_left_{group[0]}_{group[1]}.csv',
                          index=False)

    print("Summary tables generated successfully!")

def analayse_heuristic_results(directory):
    merge_csv_files(directory)
    data = pd.read_csv(f'experiments/merged_results_{directory}.csv')
    # Define the optimization configurations
    optimization_configs = ['time table conflicts', 'tests conflicts', 'pruning', 'limit available courses',
                            'develop options graph by priority']

    allowed_descriptions = [
        "",
        "limit available courses",
        "limit available courses & develop options graph by priority",
        "pruning & limit available courses & develop options graph by priority",
        "time table conflicts & limit available courses & develop options graph by priority",
        "time table conflicts & tests conflicts & limit available courses & develop options graph by priority",
        "time table conflicts & tests conflicts & pruning & limit available courses & develop options graph by priority"
    ]

    credit_left_groups = [(0, 30.5), (31, 45.5), (46, 60.5), (61, 200)]

    # Iterate over each credit left group
    for group in credit_left_groups:
        group_data = data.loc[(data['credit left'] >= group[0]) & (data['credit left'] <= group[1])].copy()

        # Initialize an empty list to store the summary table rows
        summary_rows = []

        # Iterate over each unique optimization configuration
        for config in group_data[optimization_configs].drop_duplicates().values:
            config_data = group_data[(group_data[optimization_configs] == config).all(axis=1)]
            timed_out = len(config_data[config_data['A*_1 description'] == 'timedout'])
            not_timed_out = len(config_data) - timed_out

            if not_timed_out > 0:
                config_data['A*_1 path credits'] = config_data['A*_1 path credits'].str.extract(r'(\d+\.\d+)').astype(
                    float)
                config_data['A*_2 path credits'] = config_data['A*_2 path credits'].str.extract(r'(\d+\.\d+)').astype(
                    float)
                config_data['A*_5 path credits'] = config_data['A*_5 path credits'].str.extract(r'(\d+\.\d+)').astype(
                    float)
                config_data['A*_1 semester count'] = config_data['A*_1 semester count'].str.extract(r'(\d+)').astype(
                    float)
                config_data['A*_2 semester count'] = config_data['A*_2 semester count'].str.extract(r'(\d+)').astype(
                    float)
                config_data['A*_5 semester count'] = config_data['A*_5 semester count'].str.extract(r'(\d+)').astype(
                    float)
                a1_description = config_data[config_data['A*_1 description'] != 'timedout']['A*_1 description'].iloc[0]
                a2_description = config_data[config_data['A*_1 description'] != 'timedout']['A*_2 description'].iloc[0]
                a5_description = config_data[config_data['A*_1 description'] != 'timedout']['A*_5 description'].iloc[0]
                a1_mean_semester_count = config_data[config_data['A*_1 description'] != 'timedout']['A*_1 semester count'].mean()
                #iterate over the series and caluclate the mean

                a2_mean_semester_count = config_data[config_data['A*_1 description'] != 'timedout']['A*_2 semester count'].mean()
                a5_mean_semester_count = config_data[config_data['A*_1 description'] != 'timedout']['A*_5 semester count'].mean()
                # x = config_data[config_data['A*_1 description'] != 'timedout']['A*_1 path credits']
                # if x == '35.018.023.535.025.531.530.540.520.028.0':
                #     print('here')
                a1_mean_path_credits = config_data[config_data['A*_1 description'] != 'timedout']['A*_1 path credits'].mean()
                a2_mean_path_credits = config_data[config_data['A*_1 description'] != 'timedout']['A*_2 path credits'].mean()
                a5_mean_path_credits = config_data[config_data['A*_1 description'] != 'timedout']['A*_5 path credits'].mean()
                mean_credit_left = config_data[config_data['A*_1 description'] != 'timedout']['credit left'].mean()
                a1_mean_credit_left_acuuracy = (config_data[config_data['A*_1 description'] != 'timedout']['A*_1 path credits']-
                                           config_data[config_data['A*_1 description'] != 'timedout']['credit left']).mean()
                a2_mean_credit_left_acuuracy = (config_data[config_data['A*_1 description'] != 'timedout']['A*_2 path credits']-
                                             config_data[config_data['A*_1 description'] != 'timedout']['credit left']).mean()
                a5_mean_credit_left_acuuracy = (config_data[config_data['A*_1 description'] != 'timedout']['A*_5 path credits']-
                                                config_data[config_data['A*_1 description'] != 'timedout']['credit left']).mean()
            else:
                a1_description = a2_description = a5_description = a1_mean_semester_count = a2_mean_semester_count = "-"
                a5_mean_semester_count = a1_mean_path_credits = a2_mean_path_credits = a5_mean_path_credits = "-"
                mean_credit_left = a1_mean_credit_left_acuuracy = a2_mean_credit_left_acuuracy = a5_mean_credit_left_acuuracy = "-"

            config_str = ' & '.join(optimization_configs[i] for i, val in enumerate(config) if val)

            if config_str not in allowed_descriptions:
                continue

            summary_rows.append({
                'Optimization Configuration': config_str,
                'Number of Experiments': len(config_data),
                'Timed Out': timed_out,
                'Successful Experiments Percentage': 100 - (timed_out / len(config_data) * 100),
                'A* Description 1': a1_description,
                'Mean Semester Count 1': a1_mean_semester_count,
                'Mean Path Credits 1': a1_mean_path_credits,
                'Mean error in credit left 1': a1_mean_credit_left_acuuracy,
                'A* Description 2': a2_description,
                'Mean Semester Count 2': a2_mean_semester_count,
                'Mean Path Credits 2': a2_mean_path_credits,
                'Mean error in credit left 2': a2_mean_credit_left_acuuracy,
                'A* Description 5': a5_description,
                'Mean Semester Count 5': a5_mean_semester_count,
                'Mean Path Credits 5': a5_mean_path_credits,
                'Mean error in credit left 5': a5_mean_credit_left_acuuracy,
            })

        # Create a DataFrame from the summary table rows
        summary_df = pd.DataFrame(summary_rows, columns=['Optimization Configuration', 'Number of Experiments',
                                                         'Timed Out', 'Successful Experiments Percentage',
                                                         'A* Description 1', 'Mean Semester Count 1', 'Mean Path Credits 1',
                                                         'Mean error in credit left 1', 'A* Description 2', 'Mean Semester Count 2',
                                                         'Mean Path Credits 2', 'Mean error in credit left 2', 'A* Description 5',
                                                         'Mean Semester Count 5', 'Mean Path Credits 5', 'Mean error in credit left 5'
                                                         ])

        # Write the summary table to a separate CSV file
        if not os.path.exists(f'experiments/{directory} tables/'):
            os.makedirs(f'experiments/{directory} tables/')
        summary_df.to_csv(f'experiments/{directory} tables/summary_table_credit_left_{group[0]}_{group[1]}.csv',
                          index=False)

    print("Summary tables generated successfully!")

def extract_exp_id(filename):
    # Extract the experiment ID from the filename
    return int(filename.split('_')[0])

def find_missing_exp_ids(directory):
    # Get a list of all files in the folder
    files = os.listdir(f'experiments/{directory}')

    # Extract the experiment IDs from the filenames
    exp_ids = [extract_exp_id(filename) for filename in files]

    # Find the range of expected IDs
    min_exp_id = min(exp_ids)
    max_exp_id = max(exp_ids)

    # Find the missing experiment IDs in the range
    missing_exp_ids = set(range(min_exp_id, max_exp_id + 1)) - set(exp_ids)

    return sorted(list(missing_exp_ids))


directory = 'relevant optimization results'
missing_exp_ids = find_missing_exp_ids(directory)
print("Missing exp_ids:", missing_exp_ids)

# analayse_optimization_exp(directory)
analayse_heuristic_results(directory)


# analayse_tuning_exp('tuning_exp_large_range_rerun')
# analayse_tuning_exp_by_time('tuning_exp_results - 10 students from Gen2 - max = 6,7,8,...,14,15 - Timeout = 30m')
