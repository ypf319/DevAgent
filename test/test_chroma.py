import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="test")
print("集合创建成功：", collection.name)

#
# collection.add(
#     documents=[
#         "函数 read_file 用于读取本地文件内容，支持 utf-8 编码",
#         "LLMClient 用于调用大模型 API，封装了 requests 和重试逻辑",
#         "ToolAgent 实现了 Function Calling 循环，能自动决定调用工具",
#         "配置模块用 pydantic-settings 从 .env 读取环境变量"
#     ],
#     metadatas=[
#             {"file_path": "src/devagent/tools/file_tools.py", "type": "code"},
#             {"file_path": "src/devagent/llm_client.py", "type": "code"},
#             {"file_path": "src/devagent/agent/tool_agent.py", "type": "code"},
#             {"file_path": "src/devagent/config.py", "type": "code"},
#         ],
#         ids=[
#             "doc1", "doc2", "doc3", "doc4"
#         ]
# )

results = collection.query(
    query_texts=["怎么读取文件？"],  # 用户的问题
    n_results=2  # 返回最相似的前 2 条
)

print(results)

