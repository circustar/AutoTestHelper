import queue
import threading
from typing import List, Any


class ListQueue:
    """结合 list 和 queue 功能的混合类"""

    def __init__(self, maxsize=0):
        self._queue = queue.Queue(maxsize)
        self._list = []  # 用于存储所有元素的列表
        self._rlock = threading.RLock()

    def put(self, item: Any):
        with self._rlock:
            """入队"""
            self._queue.put(item)
            self._list.append(item)

    def get(self) -> Any:
        with self._rlock:
            """出队"""
            item = self._queue.get()
            # 从列表中移除第一个匹配项
            if item in self._list:
                self._list.remove(item)
            return item

    def __getitem__(self, index: int) -> Any:
        """支持索引访问"""
        return self._list[index]

    def __len__(self) -> int:
        return len(self._list)

    def find(self, condition) -> List[Any]:
        """查找满足条件的元素"""
        return [item for item in self._list if condition(item)]

    def clear(self):
        with self._rlock:
            """清空队列"""
            self._queue.queue.clear()
            self._list.clear()

    def empty(self) -> bool:
        """检查队列是否为空"""
        return self._queue.empty()

    def __contains__(self, item: Any) -> bool:
        return item in self._list

    def __str__(self) -> str:
        return str(self._list)

