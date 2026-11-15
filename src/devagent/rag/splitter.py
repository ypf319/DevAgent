from typing import List

def split_text(
        content:str,
        chunk_size = 500,
        chunk_overlap = 100
) -> List[str]:

    if len(content) < chunk_size:
        return [content]

    chunks = []
    start = 0
    while start<len(content):
        end = start+chunk_size
        chunk = content[start:end]
        chunks.append(chunk)
        start += (chunk_size - chunk_overlap)

    return chunks

def split_files(
        files:list[dict[str, str]],
        chunk_size = 500,
        chunk_overlap = 100):
    all_chunks = []
    for file in files:
        file_path = file['file_path']
        content = file['content']
        chunks = split_text(content, chunk_size, chunk_overlap)

        for i, chunk in enumerate(chunks):
            all_chunks.append(
                {"file_path": file_path,
                 "content": chunk,
                 "chunk_index": i
                 }

            )

    return all_chunks
