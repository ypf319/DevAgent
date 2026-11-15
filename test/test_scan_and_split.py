from src.devagent.rag.scanner import scan_repo
from src.devagent.rag.splitter import split_files


def test_scan_and_split():
    # 扫描我们自己的项目目录
    print("正在扫描项目...")
    files = scan_repo(".")
    print(f"扫描完成，共找到 {len(files)} 个有效文件")

    # 打印前5个文件路径
    print("\n前5个文件：")
    for f in files[:5]:
        print(f"- {f['file_path']}")

    # 批量分块
    print("\n正在切分文本块...")
    chunks = split_files(files, chunk_size=500, chunk_overlap=100)
    print(f"切分完成，共生成 {len(chunks)} 个文本块")

    # 打印第一个块的信息
    print("\n第一个块的信息：")
    first_chunk = chunks[0]
    print(f"所属文件：{first_chunk['file_path']}")
    print(f"块序号：{first_chunk['chunk_index']}")
    print(f"内容预览：{first_chunk['content'][:100]}...")


if __name__ == "__main__":
    test_scan_and_split()
