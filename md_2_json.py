#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re
import doctree.file_tool as ftool
from enum import Enum, unique

key_l1 = 'level1'
key_l2 = 'level2'
key_l3 = 'level3'
key_l4 = 'level4'
key_l5 = 'level5'
key_l6 = 'level6'


def supplement_level(data, level):
    """
    补充level，当上一级level不存在时需要补充
    :param data:
    :param level:
    :return:
    """
    if level == 1:
        if key_l1 not in data:
            data[key_l1] = list()
            data[key_l1].append(dict())
        else:
            return
    else:
        supplement_level(data, level - 1)
        if level == 2 and key_l2 not in data[key_l1][-1]:
            data[key_l1][-1][key_l2] = list()
            data[key_l1][-1][key_l2].append(dict())
        elif level == 3 and key_l3 not in data[key_l1][-1][key_l2][-1]:
            data[key_l1][-1][key_l2][-1][key_l3] = list()
            data[key_l1][-1][key_l2][-1][key_l3].append(dict())
        elif level == 4 and key_l4 not in data[key_l1][-1][key_l2][-1][key_l3][-1]:
            data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4] = list()
            data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4].append(dict())
        elif level == 5 and key_l5 not in data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1]:
            data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_l5] = list()
            data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_l5].append(dict())
        elif level == 6 and key_l6 not in data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_l5][-1]:
            data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_l5][-1][key_l6] = list()
            data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_l5][-1][key_l6].append(dict())


def parse(path, json_path):
    """
    解析
    :param path:
    :param json_path:
    :return:
    """
    data = dict()
    key_base_info = '基本信息'
    key_book_title = '书名'
    key_tidier = '整理者'

    key_title = 'title'
    last_l = -1
    key_content = 'content'
    key_type = 'type'
    key_list = 'list'
    # key_list = 'content'

    lines = ftool.read_lines(path, should_strip=False)
    for line_no, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        # print(line_no, line)
        form = check_format(line)

        if form == Md.BaseInfo and key_base_info not in data:
            data[key_base_info] = dict()
        elif form == Md.Title and key_book_title not in data[key_base_info]:
            data[key_base_info][key_book_title] = line[4:]
        elif form == Md.Tidier and key_tidier not in data[key_base_info]:
            data[key_base_info][key_tidier] = line[5:]

        elif form == Md.H1:
            if key_l1 not in data:
                data[key_l1] = list()
            l1_info = dict()
            l1_info[key_title] = cut_mark(line, 1)
            data[key_l1].append(l1_info)
            last_l = 1
        elif form == Md.H2:
            supplement_level(data, 1)
            if key_l2 not in data[key_l1][-1]:
                data[key_l1][-1][key_l2] = list()
            l2_info = dict()
            l2_info[key_title] = cut_mark(line, 2)
            data[key_l1][-1][key_l2].append(l2_info)
            last_l = 2
        elif form == Md.H3:
            supplement_level(data, 2)
            if key_l3 not in data[key_l1][-1][key_l2][-1]:
                data[key_l1][-1][key_l2][-1][key_l3] = list()
            l3_info = dict()
            l3_info[key_title] = cut_mark(line, 3)
            data[key_l1][-1][key_l2][-1][key_l3].append(l3_info)
            last_l = 3
        elif form == Md.H4:
            supplement_level(data, 3)
            if key_l4 not in data[key_l1][-1][key_l2][-1][key_l3][-1]:
                data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4] = list()
            l4_info = dict()
            l4_info[key_title] = cut_mark(line, 4)
            data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4].append(l4_info)
            last_l = 4
        elif form == Md.H5:
            supplement_level(data, 4)
            if key_l5 not in data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1]:
                data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_l5] = list()
            l5_info = dict()
            l5_info[key_title] = cut_mark(line, 5)
            data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_l5].append(l5_info)
            last_l = 5
        elif form == Md.H6:
            supplement_level(data, 5)
            if key_l6 not in data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_l5][-1]:
                data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_l5][-1][key_l6] = list()
            l6_info = dict()
            l6_info[key_title] = cut_mark(line, 6)
            data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_l5][-1][key_l6].append(l6_info)
            last_l = 6
        elif form == Md.Type:
            type_str = get_type(line)
            if last_l == 4:
                data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_type] = type_str
            elif last_l == 5:
                data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_l5][-1][key_type] = type_str
            elif last_l == 6:
                data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_l5][-1][key_l6][-1][key_type] = type_str
        elif form == Md.Content:
            if last_l == 4:
                original = data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1].get(key_content, "")
                if original:
                    original = original+"\n"
                data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_content] = original+line
            elif last_l == 5:
                original = data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_l5][-1].get(key_content, "")
                if original:
                    original = original+"\n"
                data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_l5][-1][key_content] = original+line
            elif last_l == 6:
                original = data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_l5][-1][key_l6][-1].get(key_content, "")
                if original:
                    original = original+"\n"
                data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_l5][-1][key_l6][-1][key_content] = original+line
        elif form == Md.List:
            if last_l == 4:
                if key_list not in data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1]:
                    data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_list] = list()
                data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_list].append(get_list_line(line))
            elif last_l == 5:
                if key_list not in data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_l5][-1]:
                    data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_l5][-1][key_list] = list()
                data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_l5][-1][key_list].append(get_list_line(line))
            elif last_l == 6:
                if key_list not in data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_l5][-1][key_l6][-1]:
                    data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_l5][-1][key_l6][-1][key_list] = list()
                data[key_l1][-1][key_l2][-1][key_l3][-1][key_l4][-1][key_l5][-1][key_l6][-1][key_list].append(get_list_line(line))

    ftool.write_json(data, json_path)


def check_format(text):
    """
    数行前#的个数
    :param text:
    :return:
    """
    print(text)
    if text == '# 基本信息':
        return Md.BaseInfo

    level_max = 6
    for i in range(level_max):
        level = level_max - i
        if text.startswith('#' * level):
            return Md(level)

    if text.startswith('- '):
        return Md.List

    oli = text.split('. ', 1)
    if len(oli)>1 and oli[0].isdigit():
        return Md.List

    key_title = '书名'
    key_tidier = '整理者'
    ds = re.split(r'[【】]\s*', text)
    if len(ds) > 2:
        if ds[1] == key_title:
            return Md.Title
        if ds[1] == key_tidier:
            return Md.Tidier

    ds = text.split('==')
    if len(ds) > 2:
        return Md.Type

    return Md.Content


def cut_mark(text, count):
    """
    切除文本前count个字符
    :param text:
    :param count:
    :return:
    """
    if not text or count < 1:
        raise Exception(text, count)
    return text[count + 1:].strip()


def get_type(text):
    """
    获取类型
    :param text:
    :return:
    """
    ds = text.split('==')
    if len(ds) < 3:
        raise Exception('获取类型数据有误')
    return ds[1]

def get_list_line(text):
    # print(text)
    if text.startswith('- '):
        return text[2:]

    oli = text.split('. ', 1)
    return oli[1].strip()

@unique
class Md(Enum):
    Content = 0
    H1 = 1
    H2 = 2
    H3 = 3
    H4 = 4
    H5 = 5
    H6 = 6
    List = 7
    Title = 8
    Tidier = 9
    Type = 10
    BaseInfo = 11


def main():
    args = sys.argv
    if len(args) < 2:
        print('！！！缺少参数：输入文件路径！')
        return
    md_path = args[1]
    if not os.path.isfile(md_path):
        print('！！！请您检查输入文件路径是否正确！')
        return
    if not md_path.endswith('.md'):
        print ('您输入的可能不是Markdown文档，请您检查文档是否正确！')
    
    json_path = md_path + '.json'
    if len(args) > 2:
        json_path = args[2]

    parse(md_path, json_path)


if __name__ == '__main__':
    main()
