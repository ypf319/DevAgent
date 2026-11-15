import time


def get_answer_stream():
    yield "你"
    time.sleep(1)
    yield "好"
    time.sleep(1)
    yield "，"
    time.sleep(1)
    yield "我"
    time.sleep(1)
    yield "是"
    time.sleep(1)
    yield "助"
    time.sleep(1)
    yield "手"

for char in get_answer_stream():
    print(char)  # 逐行打出：你 好 ， 我 是 助 手

answer = "asgfskajksjad"
for char in answer:
    yield {"event": "message", "data": char}
