import os
from ..exceptions import DevAgentBaseError


def read_file(path):
    if not os.path.exists(path):
        raise DevAgentBaseError("File not found: {}".format(path))

    if not os.path.isfile(path):
        raise DevAgentBaseError("its not file: {}".format(path))

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return content
    except Exception as e:
        raise DevAgentBaseError("文件读取失败: {}".format(e))

