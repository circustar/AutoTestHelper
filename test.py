from ds_captcha_recognize_service import DsCaptchaRecognizeService
from typing import Dict, Any
from business.service.ScheduleScheduler import ScheduleScheduler
import time

from dotenv import load_dotenv
import os
from business.db.test_case import TestCase
from test_agent_client import TestAgentClient
from multiprocessing.pool import ThreadPool

# 测试代码
# 加载 .env 文件，确保数据库连接信息受到保护
load_dotenv()
thread_count = os.getenv("TASK_THREAD_COUNT", 4)

def schedule():
    def run_all():
        print("开始执行")
        run_all_test_case.run_all_test_case()

    # 创建调度器
    scheduler = ScheduleScheduler()

    # 添加各种任务
    scheduler.add_job(run_all, "every().day.at('00:00')")

    # 列出任务
    scheduler.list_jobs()

    # 启动调度器（后台运行）
    scheduler.start(background=True)

    # 主线程继续执行其他工作
    print("主线程执行...")

    try:
        # 运行一段时间
        while(True):
            print(f"主线程工作中...")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n收到中断信号")
    finally:
        scheduler.stop()

def run_all_test_case():
    """测试所有的用例"""

    # 创建线程池
    pool = ThreadPool(processes=int(thread_count))  # processes 参数实际上是线程数

    # 提交任务
    res = TestCase.get_all(where_clause="STATUS = 'SCHEDULED'")
    if not res["success"] :
        return
    items = res["data"]["records"]

    # apply_async - 异步提交单个任务
    async_results = []
    for item in items:
        result = pool.apply_async(run_one_case, (item,))
        async_results.append(result)

    # 获取结果
    print("异步提交结果:")
    for result in async_results:
        result.get()

    # map 方法
    print("\n使用 map 方法:")
    map_results = pool.map(run_one_case, items)
    for result in map_results:
        print(result)

    # 关闭线程池
    pool.close()
    pool.join()

def run_one_case( test_case : Dict[str, Any]) :
    """主函数"""
    test_case_id = None
    test_agent_client = None
    try:
        test_agent_client = TestAgentClient()
        test_case_id = test_case["TEST_CASE_ID"]
        print("测试用例ID: " + str(test_case_id))
        test_agent_client.chat_once(str(test_case_id))
    except Exception as e:
        print(f"\n⚠️ 测试{test_case_id}失败: {str(e)}")
    finally:
        if test_agent_client:
            test_agent_client.cleanup()

if __name__ == "__main__":
    sevice = DsCaptchaRecognizeService()
    response = sevice.recognize_captcha(file_path="D:/TEMP/screenshot/1/11/step_2-2026-01-26T06-49-20-107Z.png", prompt="识别验证码")
    print(response)
