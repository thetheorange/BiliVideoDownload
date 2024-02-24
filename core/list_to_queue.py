"""
Des 将列表转成队列
@Author thetheOrange
Time 2024/2/22
"""


def list_to_queue(list_, queue_):
    if len(list_) > 0:
        for i in list_:
            queue_.put(i)
