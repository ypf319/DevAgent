from ..rag.vector_store import vector_store

def search_codebase(query:str, top_k:int=3):

    results = vector_store.search(query, top_k)
    output_parts = []
    for i,result in enumerate(results):
        output_parts.append(
            f"""
        --- 相关片段 {i + 1} ---
        文件路径：{result['file_path']}
        相关度：{1 - result['distance']:.2f}
        内容：
        {result['content']}
                """.strip()
        )
    return "\n\n".join(output_parts)






