import re
import os
import shutil
from BD_tables import create_table
from BD_json import *


def get_header_json():
    return os.path.join(os.curdir, "log_headers.json")


def get_table_headers():
    h_json = get_header_json()
    header_data = read_json_file(h_json)
    if not header_data:
        print "error getting json header data!"
        return False
    return header_data["table_items"]


def format_dict_json_item(json_file):
    item_data = read_json_file(json_file)
    formatted_data = {
        "scene": re.findall(r'\w{3}_EP\d{3}_SC\d{4}', os.path.basename(json_file))[0],
        "animator": item_data["animator"],
        "version": item_data["version"],
        "status": item_data["status"],
        "step": item_data["step"],
        "queued": item_data["queued"],
        "queue_computer": item_data["extra"]["last_queue"],
        "started_at": item_data["started_at"],
    }
    return formatted_data


def list_log_files(keyword, folder_list):
    """return list of dictionaries with json scenes log information"""
    json_data_list = []
    for folder in folder_list:
        log_folder = os.path.join(folder, "_logs")
        if not os.path.exists(log_folder):
            print "ERROR! Log folder not found: {0}".format(log_folder)
            return False
        file_list = os.listdir(log_folder)
        counter = 0
        for json_f in file_list:
            if keyword in json_f:
                json_path = os.path.join(log_folder, json_f)
                json_data_list.append(format_dict_json_item(json_path))
                counter += 1
        print "{0} files found in folder: {1}".format(counter, folder)
    return sorted(json_data_list, key=lambda x: x["queued"])


def validate_input(keyword):
    """validate if input is valid and return type of log input"""
    input_regex = {
        "episode": r"^EP\d{3}$",
        "scene": r"^EP\d{3}_SC\d{4}$",
        "date": r"^(20\d{2}[0-1]\d[0-3]\d)$"
    }
    for item in input_regex:
        if bool(re.match(input_regex[item], keyword)):
            return [keyword, item]
    return False


def create_logs_tab(keyword, log_folders, input_data):
    """creates tables with logs found for input scene/ep/date"""
    table_headers = get_table_headers()
    if not table_headers:
        print "ERROR! Invalid header json file configured!"
        return False
    print "listing json queue files..."
    queue_data_list = list_log_files(keyword, log_folders)
    if not queue_data_list:
        return False

    print "creating table..."
    table = create_table(table_headers, queue_data_list, input_data)
    return table


def create_temp_log_file(file_name, table):
    temp_folder = os.path.join(os.getenv("TEMP"), "bot_birdo")
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder, ignore_errors=True)
    os.mkdir(temp_folder)
    temp_file = os.path.join(temp_folder, "{0}.txt".format(file_name))
    with open(temp_file, 'w') as f:
        f.write(table)
    return temp_file
