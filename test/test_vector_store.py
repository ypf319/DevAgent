from src.devagent.rag.scanner import scan_repo
from src.devagent.rag.splitter import split_files
from src.devagent.rag.vector_store import vector_store


def test_vector_search():
    # 1. 扫描项目、切分块（复用我们上一节写的代码）
    print("=== 1. 扫描并切分代码 ===")
    files = scan_repo(".")
    chunks = split_files(files)
    print(f"共生成 {len(chunks)} 个文本块")

    # 2. 存入向量库
    print("\n=== 2. 存入向量数据库 ===")
    vector_store.add_document(chunks)

    # 3. 测试语义搜索
    print("\n=== 3. 测试语义搜索 ===")
    query = "配置文件和环境变量"
    print(f"搜索关键词：{query}")

    results = vector_store.search(query, top_k=2)

    print("\n搜索结果：")
    for i, res in enumerate(results):
        print(f"\n--- 结果 {i + 1}（相关度：{1 - res['distance']:.2f}）---")
        print(f"文件：{res['file_path']}")
        print(f"内容预览：{res['content'][:150]}...")


if __name__ == "__main__":
    test_vector_search()
