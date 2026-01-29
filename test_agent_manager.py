import asyncio
import os

from test_agent_client import TestAgentClient
from business.utils.list_queue import ListQueue


class TestAgentManager:

    def __init__(self, test_pool_size : int, schedule_pool_size : int):

        self.test_agents = []

        if test_pool_size > 0 :
            self.test_task_queue = ListQueue(maxsize=test_pool_size)
            for i in range(test_pool_size):
                client = TestAgentClient()
                client.set_queue(self.test_task_queue)
                self.test_agents.append(client)

        if schedule_pool_size > 0 :
            self.schedule_task_queue = ListQueue(maxsize=schedule_pool_size)
            for i in range(schedule_pool_size):
                client = TestAgentClient()
                client.set_queue(self.schedule_task_queue)
                self.test_agents.append(client)

    def add_to_test_queue(self, test_case_id : int):
        if self.test_task_queue and self.test_task_queue.find(test_case_id):
            return
        self.test_task_queue.put(test_case_id)

    def clear_test_queue(self):
        if self.test_task_queue:
            self.test_task_queue.clear()

    def add_to_schedule_queue(self, test_case_id : int):
        if self.schedule_task_queue and self.schedule_task_queue.find(test_case_id):
            return
        self.schedule_task_queue.put(test_case_id)

    def clear_schedule_queue(self):
        if self.schedule_task_queue:
            self.schedule_task_queue.clear()

    async def run(self):
        idx = 0
        task = []
        for agent in self.test_agents:
            print("task_queue run:{}".format(idx))
            idx = idx + 1
            task.append(asyncio.create_task(agent.chat_queue()))

        await asyncio.gather(*task)


test_thread_count = int(os.getenv("TEST_TASK_THREAD_COUNT", 4))
schedule_thread_count = int(os.getenv("SCHEDULE_TASK_THREAD_COUNT", 4))
test_agent = TestAgentManager(test_thread_count, schedule_thread_count)

def get_test_agent():
    return test_agent