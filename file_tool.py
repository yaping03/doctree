#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json


def read_lines(file_path, should_strip=False):
    """
    读文件
    :param file_path:
    :param should_strip:是否需要把每行数据strip
    :return:
    """
    if not os.path.isfile(file_path):
        raise Exception(file_path, '这不是一个文件！')

    lines = list()
    with open(file_path, encoding='utf-8') as f:
        coarse_lines = list(f)
        for cl in coarse_lines:
            if should_strip:
                cl = cl.strip()
            lines.append(cl)

    return lines


def write_json(content, json_path):
    """
    写json数据
    :param content:
    :param json_path:
    :return:
    """
    with open(json_path, 'w', encoding='utf-8')as f:
        json.dump(content, f, ensure_ascii=0)
