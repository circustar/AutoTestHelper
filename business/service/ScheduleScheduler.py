import schedule
import time
import datetime
import threading
from typing import Callable, Any


class ScheduleScheduler:
    """基于 schedule 库的高级调度器"""

    def __init__(self):
        self.running = False
        self.thread = None

    def add_job(self, func: Callable, schedule_str: str, *args, **kwargs):
        """
        添加任务

        参数:
            func: 要执行的函数
            schedule_str: 调度字符串，格式如:
                - "every(10).seconds"  # 每10秒
                - "every().day.at('10:30')"  # 每天10:30
                - "every().monday.at('09:00')"  # 每周一9:00
                - "every().hour"  # 每小时
            *args, **kwargs: 传递给函数的参数
        """
        # 解析调度字符串并执行
        try:
            eval(f"schedule.{schedule_str}.do(self._wrap_func, func, *args, **kwargs)")
            print(f"任务添加成功: {schedule_str}")
        except Exception as e:
            print(f"添加任务失败: {e}")

    def _wrap_func(self, func: Callable, *args, **kwargs):
        """包装函数，添加异常处理"""
        try:
            func(*args, **kwargs)
        except Exception as e:
            print(f"任务执行失败: {e}")

    def run_pending(self):
        """运行待执行任务"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def start(self, background: bool = False):
        """启动调度器"""
        self.running = True

        if background:
            # 在后台线程中运行
            self.thread = threading.Thread(target=self.run_pending, daemon=True)
            self.thread.start()
            print("调度器已在后台启动")
        else:
            # 在前台运行（阻塞）
            print("调度器启动（前台运行）")
            self.run_pending()

    def stop(self):
        """停止调度器"""
        self.running = False
        schedule.clear()
        print("调度器已停止")

    def list_jobs(self):
        """列出所有任务"""
        jobs = schedule.get_jobs()
        if jobs:
            print(f"当前有 {len(jobs)} 个任务:")
            for job in jobs:
                print(f"  - {job}")
        else:
            print("当前没有任务")


# 使用示例
def schedule_example():
    """schedule 库示例"""

    def backup_database():
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] 备份数据库...")

    def send_email_report():
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] 发送邮件报告...")

    def cleanup_temp_files(path):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] 清理临时文件: {path}")

    # 创建调度器
    scheduler = ScheduleScheduler()

    # 添加各种任务
    scheduler.add_job(backup_database, "every(5).seconds")
    scheduler.add_job(send_email_report, "every(10).seconds")
    scheduler.add_job(cleanup_temp_files, "every(15).seconds", "/tmp")

    # 列出任务
    scheduler.list_jobs()

    # 启动调度器（后台运行）
    scheduler.start(background=True)

    # 主线程继续执行其他工作
    print("主线程继续执行...")

    try:
        # 运行一段时间
        for i in range(30):
            print(f"主线程工作中... ({i + 1}/30)")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n收到中断信号")
    finally:
        scheduler.stop()

# schedule_example()
if __name__ == "__main__":
    schedule_example()