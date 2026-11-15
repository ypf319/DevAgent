from .file_tools import *
from .rag_tools import search_codebase

TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取本地指定路径的文本文件内容，用于查看代码文件、配置文件等文本内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "要读取的文件的路径，可以是相对路径或绝对路径"
                    }
                },
                "required": ["path"]  # 必填参数
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_codebase",
            "description": "在整个代码仓库中进行语义搜索，查找与问题最相关的代码片段。当不知道具体文件名、需要全局查找相关代码时使用",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索的关键词或问题描述"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "返回最相关的片段数量，默认3",
                        "default": 3
                    }
                },
                "required": ["query"]
            }
        }
    }
]

TOOL_FUNCTIONS = {
    "read_file":read_file,
    "search_codebase":search_codebase,
}