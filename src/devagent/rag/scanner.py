import os
from encodings import utf_8
from typing import List,Dict
from ..exceptions import DevAgentBaseError


IGNORE_DIRS = {
    ".git", ".venv", "__pycache__", ".idea", ".vscode",
    "node_modules", "dist", "build"
}

ALLOWED_EXTENSIONS = {
    ".py", ".md", ".txt", ".toml", ".json", ".yaml", ".yml",
    ".js", ".ts", ".html", ".css", ".java", ".cpp", ".c", ".h"
}


def scan_repo(repo_path:str)-> List[Dict[str, str]]:

    if not os.path.isdir(repo_path):
        raise DevAgentBaseError(f"{repo_path} is not a directory")

    files = []

    for root, dirs, filenames in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for f in filenames:
            ext = os.path.splitext(f)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                continue
            file_path = os.path.join(root, f)

            try:
                with open(file_path, 'r', encoding="utf-8", errors='ignore') as file:
                    content = file.read()
                if content.strip():
                    files.append(
                        {
                            'file_path': file_path,
                            'content': content
                        }
                    )
            except Exception as e:
                print(f"[警告] 读取文件失败 {file_path}: {str(e)}")
                continue
    return files






