import copy
import glob
import os
import random
import re

# Define the desired order
MODALITY_ORDER = ["_T1w", "task-qct.*_bold", "task-bht.*_bold", "task_rest.*_bold", "_T2w"]

def define_order(file):
    """
    Extracts the session number from the given file name and returns a tuple containing the subject ID, modality priority,
    session type priority, and session number.

    Parameters:
    -----------
    file (str): The file name from which to extract the session number.

    Returns:
    --------
    tuple: A tuple containing the subject ID, modality priority, session type priority, and session number.

    The function first extracts the subject ID from the file name using a regular expression. It then extracts the modality
    from the file name and determines its priority based on its position in the MODALITY_ORDER list. If the modality is not
    found in the MODALITY_ORDER list, its priority is set to the length of the list.

    The function then checks for the presence of "ses-excl", "ses-pilot", or "ses-" in the file name using regular expressions.
    If any of these session types are found, the corresponding session type priority and session number are extracted.

    If none of the session types are found in the file name, the function returns a default value of (subject_id, modality_priority, 4, 0),
    where 4 is the priority for files without a session number.

    Note: This function assumes that the file name follows a specific naming convention and that the regular expressions used
    will correctly extract the required information.
    """
    subject_id = re.search(r'sub-(\w+)_', file).group(1)

    # Extract modality and get its priority based on its position in MODALITY_ORDER
    modality_priority = len(MODALITY_ORDER)
    for i, pattern in enumerate(MODALITY_ORDER):
        if re.search(pattern, file):
            modality_priority = i
            break

    run_match = re.search(r'run-(\w+)_', file)
    run_id = int(run_match.group(1)) if run_match else 0

    excl_match = re.search(r'ses-excl(\d+)_', file)
    if excl_match:
        return (subject_id, modality_priority, 1, int(excl_match.group(1)), run_id)  # Priority 1 for "ses-excl"
    
    pilot_match = re.search(r'ses-pilot(\d+)_', file)
    if pilot_match:
        return (subject_id, modality_priority, 2, int(pilot_match.group(1)), run_id)  # Priority 2 for "ses-pilot"
    
    session_match = re.search(r'ses-(\d+)_', file)
    if session_match:
        return (subject_id, modality_priority, 3, int(session_match.group(1)), run_id)  # Priority 3 for "ses-"

    return (subject_id, modality_priority, 4, 0, run_id)  # Default value for files without a session number


def list_individual_reports(path_reports, two_folders=False):
    """
    Returns the list of all html reports in path_reports

    Parameters
    ---------
    path_reports : str
        path of report to modify
    Returns
    -------
    List of reports
    """
    if two_folders:
        list_of_file_condition1 = [
            "/condition1/" + os.path.basename(filename)
            for filename in glob.glob(path_reports + "condition1/" + "sub-*.html")
        ]
        list_of_file_condition2 = [
            "/condition2/" + os.path.basename(filename)
            for filename in glob.glob(path_reports + "condition2/" + "sub-*.html")
        ]

        list_of_files = list_of_file_condition1 + list_of_file_condition2
    else:
        list_of_files = [
            os.path.basename(filename)
            for filename in glob.glob(path_reports + "/**/sub-*.html", recursive=True)
        ]
    
    #Re-order the list of files according to the desired order
    list_of_files.sort(key=define_order)

    return list_of_files


def shuffle_reports(list_of_files, random_seed):
    """
    Shuffle the list of reports

    Parameters
    ---------
    list_of_files: str list
        List of reports
    random_seed: int
        random seed used for the shuffling
    Returns
    -------
    shuffled list
    """
    random.seed(random_seed)
    shuffled_list = copy.deepcopy(list_of_files)
    random.shuffle(shuffled_list)
    return shuffled_list


def anonymize_reports(shuffled_list, dataset_name):
    """
    Anonymizes the list of reports

    Parameters
    ---------
    shuffled_list: str list
        list with original names
    dataset_name: str

    Returns
    -------
    shuffled list
    """
    anonymized_report_list = [
        "A-" + dataset_name + "_" + str(i) for i in range(1, len(shuffled_list) + 1)
    ]
    return anonymized_report_list


def repeat_reports(original_list, number_of_subjects_to_repeat, two_folders=False):
    day = 220830
    time = 543417
    random.seed(day + time)
    if two_folders:

        # Randomly select subjects that will be shown twice, the subjects are the same in the two sets
        list_condition1 = [s for s in original_list if "condition1" in s]
        sourceFile = open("demo.txt", "w")
        print(original_list, list_condition1, file=sourceFile)
        sourceFile.close()
        subset_rep_condition1 = random.sample(
            list_condition1, number_of_subjects_to_repeat
        )
        subset_rep_condition2 = [
            s.replace("condition1", "condition2") for s in subset_rep_condition1
        ]
        subset_rep = subset_rep_condition1 + subset_rep_condition2
    else:
        # Randomly select subjects that will be shown twice
        subset_rep = random.sample(original_list, number_of_subjects_to_repeat)

    original_list.extend(subset_rep)
    return original_list


if __name__ == "__main__":
    pass
