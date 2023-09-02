# -*- coding: utf-8 -*-
from datetime import datetime


def get_column_length(data_list, column):
    column_length = len(column)
    for item in data_list:
        if column_length < len(str(item[column])):
            column_length = len(str(item[column]))
    return column_length


def format_string_length(string, length):
    num_blank = (length - len(str(string)))
    blank_spaces = " " * num_blank
    return "{0}{1} |".format(string, blank_spaces)


def create_title_header(input_data, header_length, items_count):
    divisor = " " + ("*" * header_length)
    titlel1 = "|    log input: {0} => type: {1}".format(input_data["keyword"], input_data["type"])
    titlel1 += (header_length - len(titlel1)) * " "
    titlel2 = "|    log date: {0}".format(datetime.now())
    titlel2 += (header_length - len(titlel2)) * " "
    titlel3 = "|    log entries: {0}".format(items_count)
    titlel3 += (header_length - len(titlel2)) * " "
    return "{0}\n{1} |\n{2} |\n{3} |\n{4}".format(divisor, titlel1, titlel2, titlel3, divisor)


def create_table(header_list, data_list, input_data):
    header = [("| {0}".format(format_string_length(t, get_column_length(data_list, t)))).upper() for t in header_list]
    header_str = ""
    for i in header:
        header_str += i
    title = create_title_header(input_data, (len(header_str) - 2), len(data_list))
    lines = []
    for row in data_list:
        line = ["| {0}".format(format_string_length(row[item], get_column_length(data_list, item))) for item in header_list]
        lines.append(line)

    table = "{0}\n{1}\n{2}\n".format(title, header_str, "-" * len(header_str))

    for line in lines:
        line_str = ""
        for i in line:
            line_str += i
        table += "{0}\n".format(line_str)
    table += ("\n" + str("-" * len(header_str)))
    return table
