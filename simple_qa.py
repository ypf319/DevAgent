from src.devagent.tools.file_tools import read_file
from src.devagent.llm_client import llm_client




def simple_file_qa(question, path=None):
    if not path:
        content = ""
    else:
        print("正在读取文件。。。")
        content = read_file(path)



    print("正在调用大模型分析。。。")
    messages = [
        {
            "role":"user",
            "content":f"""
            请根据以下内容回答问题：
            文件内容：
            {content}
            问题：
            {question}
            """
        }
    ]

    result = llm_client.chat(messages)
    answers = result["choices"][0]["message"]["content"]
    return answers

if __name__ == '__main__':
    ans = simple_file_qa(path = "/Users/mac/Documents/DevAgent/src/devagent/config.py", question="从最基础的底层原理解释一下这段代码，500字以内")
    ans2 = simple_file_qa(question="距离跨年还有几天")
    print(ans2)
