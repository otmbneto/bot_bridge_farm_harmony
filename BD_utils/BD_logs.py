# -*- coding: utf-8 -*-
import re
import os
import shutil
from datetime import datetime
from .BD_tables import create_table
from .BD_json import *


def get_header_json():
    return os.path.join(os.path.dirname(__file__), "log_headers.json")


def write_header_list(headers_file, h_list):
    with open(headers_file, "w") as f:
        f.writelines([','.join(h_list) + "\n", "\n",
                      "# listar os nomes de cada item possivel para usar no cabecalho da tabela de log gerado pelo bot !log (separado por virgula)"])
    return "project header list updated!"


def get_table_headers():
    """retorna os possiveis headers para a tabela"""
    h_json = get_header_json()
    header_data = read_json_file(h_json)
    if not header_data:
        print("error getting json header data!")
        return False
    return header_data["table_items"]


def get_project_header_txt(fazendinha_folder):
    headers_file = os.path.join(os.path.dirname(re.sub(r'(\\|\/)$', "", fazendinha_folder)), "log_headers.txt")
    # cria o arquivo txt com lista de items do projeto caso ainda nao exista
    if not os.path.exists(headers_file):
        available_headers = get_table_headers()
        if not available_headers:
            return False
        print(write_header_list(headers_file, available_headers))
    return headers_file


def get_project_headers(fazendinha_folder):
    """retorna a lista de itens do header usados no projeto"""
    headers_file = get_project_header_txt(fazendinha_folder)
    if not headers_file:
        print("fail to get headers list!")
        return False
    with open(headers_file, "r") as f:
        line = f.readlines()
    return line[0].replace("\n", "").split(",")


def format_dict_json_item(json_file, search_filter=None):
    item_data = read_json_file(json_file)
    if search_filter and search_filter not in str(item_data):
        return False
    if "extra" in item_data:
        comp_queue = item_data["extra"]["last_queue"] if "last_queue" in item_data["extra"] else None
    else:
        comp_queue = None
    formatted_data = {
        "scene": re.findall(r'\w{3}_EP\d{3}_SC\d{4}', os.path.basename(json_file))[0],
        "animator": item_data["animator"].encode('utf-8').strip() if "animator" in item_data else None,
        "version": item_data["version"] if "version" in item_data else None,
        "status": item_data["status"] if "status" in item_data else None,
        "step": item_data["step"] if "step" in item_data else None,
        "queued": item_data["queued"] if "queued" in item_data else None,
        "queue_computer": comp_queue,
        "started_at": item_data["started_at"] if "started_at" in item_data else None,
        "render_tries": len(item_data["_render_tries"]) if "_render_tries" in item_data else None,
        "render_type": item_data["render_type"] if "render_type" in item_data else None
    }
    return formatted_data


def list_log_files(keyword, folder_list, search_filter=None):
    """return list of dictionaries with json scenes log information"""
    json_data_list = []
    for folder in folder_list:
        log_folder = os.path.join(folder, "_logs")
        if not os.path.exists(log_folder):
            print("ERROR! Log folder not found: {0}".format(log_folder))
            return False
        file_list = os.listdir(log_folder)
        counter = 0
        for json_f in file_list:
            if keyword == "user" or keyword in json_f:
                json_path = os.path.join(log_folder, json_f)
                formatted_data = format_dict_json_item(json_path, search_filter)
                if not formatted_data:
                    continue
                json_data_list.append(formatted_data)
                counter += 1
    return sorted(json_data_list, key=lambda x: datetime.strptime(x["queued"], "%d/%m/%Y, %H:%M:%S"))


def validate_input(keyword):
    """validate if input is valid and return type of log input"""
    input_regex = {
        "episode": r"^EP\d{3}(:.+)?$",
        "scene": r"^EP\d{3}_SC\d{4}(:.+)?$",
        "date": r"^(20\d{2}[0-1]\d[0-3]\d)$",
        "user": r"^user(:.+)?",
        "header": r"^header:?(add:\w+|remove:\w+|\w+:\d+)?$"
    }
    output = {
        "keyword": None,
        "filter": None,
        "type": None
    }
    for item in input_regex:
        if bool(re.match(input_regex[item], keyword)):
            output["type"] = item
            s = keyword.split(":")
            output["filter"] = s[1] if len(s) == 2 else None
            output["keyword"] = keyword if output["filter"] == None else s[0]
            return output
    return False


def create_logs_tab(log_folders, input_data):
    """creates tables with logs found for input scene/ep/date"""
    table_headers = get_project_headers(log_folders[0])
    if not table_headers:
        print("ERROR! Invalid header json file configured!")
        return False
    queue_data_list = list_log_files(input_data["keyword"], log_folders, input_data["filter"])
    if not queue_data_list:
        return False

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


def print_header_list(fazendinha_folder):
    p_headers = get_project_headers(fazendinha_folder)
    g_headers = get_table_headers()
    h_str = " ** HEADERS IN PROJECT **\n"
    i = 0
    for item in p_headers:
        h_str += "[{0}] - {1}\n".format(i, item)
        i += 1
    h_str += "\n ** UNUSED ITEMS **\n - {0}\n".format("\n - ".join(list(set(g_headers) - set(p_headers))))
    h_str += "\nHeaders commands are:\n - header => 'print commands'\n"
    h_str += " - header:add:<item> => 'add item from unused items list to project headers list'\n"
    h_str += " - header:remove:<item> => 'remove item from project headers list'\n"
    h_str += " - header:<item>:<index> => 'change item index in header list order'\n"
    return h_str


def add_item_header(item, fazendinha_folder):
    """add item to header project txt file"""
    h_list = get_project_headers(fazendinha_folder)
    if item in h_list:
        return "item '{0}' is already at headers list!".format(item)
    h_list.append(item)
    return write_header_list(get_project_header_txt(fazendinha_folder), h_list)


def remove_item_header(item, fazendinha_folder):
    """remove item from header project txt file"""
    p_h_list = get_project_headers(fazendinha_folder)
    if not p_h_list:
        return "ERROR! can't read project headers file!"
    if item not in p_h_list:
        return "Item {0} is not in current project headers list!"
    p_h_list.remove(item)
    return write_header_list(get_project_header_txt(fazendinha_folder), p_h_list)


def update_item_index(item, my_list, new_index):
    """atualiza o index do item na lista e retorna nova lista"""
    current_index = my_list.index(item)
    element = my_list.pop(current_index)
    my_list.insert(new_index, element)
    return my_list


def header_action(header_cmd, fazendinha_folder):
    """funcao de acao dos comandos de header"""
    cmds = header_cmd.split(":")
    if len(cmds) == 1:
        return print_header_list(fazendinha_folder)
    elif len(cmds) < 3:
        return "ERROR! Invalid command! Insufficient parameters!"

    # add action
    if cmds[1] == "add":
        available_headers = get_table_headers()
        if not available_headers:
            return "ERROR! can't read headers file!"
        if not cmds[2] in available_headers:
            return "ERRO! add value is not in valid header's list!"
        return add_item_header(cmds[2], fazendinha_folder)

    # remove action
    elif cmds[1] == "remove":
        return remove_item_header(cmds[2], fazendinha_folder)

    # change item index action
    else:
        return "-- funcao em construcao! -- "
