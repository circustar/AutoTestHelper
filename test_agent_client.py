# client.py

import asyncio
import datetime
import json
import os
import random
from typing import Optional, Dict, List
from contextlib import AsyncExitStack

from openai import OpenAI
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from business.db.test_case import TestCase
from business.db.test_result import TestResult
from business.db.test_template import TestTemplate
from business.utils.list_queue import ListQueue

# 加载 .env 文件，确保 API Key 受到保护
load_dotenv()

class TestAgentClient:
    """MCP客户端，用于与OpenAI API交互并调用MCP工具"""

    def __init__(self):
        """初始化MCP客户端"""
        # 环境变量检查和初始化
        # self.openai_api_key = "sk-C8VZXLmlsjwj0wc120pQPA"
        # self.base_url = "http://10.251.30.30:80/v1"
        # self.model = "DeepSeek-R1-671B"

        # 获取操作系统的登录用户名
        self.vc_tools_response = None
        self.pw_tools_response = None
        self.available_tools = None
        self.db_tools_response = None
        self.username = os.getlogin()

        # deepseek
        # self.openai_api_key = os.getenv('DEEPSEEK_API_KEY')
        # self.base_url = os.getenv('DEEPSEEK_BASE_URL')
        # self.model = os.getenv('DEEPSEEK_MODEL')
        # bx deepseek
        self.openai_api_key = os.getenv('BX_DEEPSEEK_API_KEY')
        self.base_url = os.getenv('BX_DEEPSEEK_BASE_URL')
        self.model = os.getenv('BX_DEEPSEEK_MODEL')
        # kimi
        # self.openai_api_key = os.getenv('KIMI_API_KEY')
        # self.base_url = os.getenv('KIMI_BASE_URL')
        # self.model = os.getenv('KIMI_K2_MODEL')

        self.default_browser = os.getenv('DEFAULT_BROWSER', 'playwright').lower()
        self.browser_install_path = os.getenv('BROWSER_INSTALL_PATH').replace("\\", "/")
        self.screen_shot_dir = os.getenv('SCREEN_SHOT_DIR')
        self.work_dir = os.getenv('WORK_DIR')
        os.makedirs(name=self.work_dir, exist_ok=True)

        if not self.openai_api_key:
          raise ValueError(
            "❌ 未找到OpenAI API Key，请在.env文件中设置OPENAI_API_KEY"
        )
        # 初始化组件
        self.exit_stack = AsyncExitStack()
        self.client = OpenAI(api_key=self.openai_api_key, base_url=self.base_url)
        self.db_session = None
        self.browser_session = None
        self.verify_code_session = None
        self.resources_dict = {}
        self.task_queue :ListQueue = None
        self.initialized = False
        self.running_case_id = -1

    def clear_queue(self):
        if self.task_queue :
            self.task_queue.clear()

    def set_queue(self, init_queue : ListQueue):
        self.task_queue = init_queue

    def add_to_queue(self, test_case_id : int ):
        if self.task_queue is None:
            self.task_queue = ListQueue()
        # 如果test_case_id在task_queue中已存在,则不添加
        if self.task_queue.find(test_case_id) or self.running_case_id == test_case_id:
            return
        self.task_queue.put(test_case_id)

    def is_test_case_running(self, test_case_id : int ) -> bool:
        # 如果test_case_id在task_queue中已存在,则不添加
        if self.task_queue.find(test_case_id) or self.running_case_id == test_case_id:
            return True
        return False

    async def initialize(self):
        # asyncio.run(self.connect_to_verify_code_server())
        # asyncio.run(self.connect_to_database_server())
        # asyncio.run(self.connect_to_browser_server())
        await self.connect_to_browser_server()
        await self.connect_to_captcha_code_server()
        await self.connect_to_database_server()

        # 1. 获取可用工具
        # 获取所有可用工具（合并两个会话的工具）
        self.db_tools_response = await self.db_session.list_tools()
        self.pw_tools_response = await self.browser_session.list_tools()
        self.vc_tools_response = await self.verify_code_session.list_tools()
        all_tools = self.db_tools_response.tools + self.pw_tools_response.tools + self.vc_tools_response.tools

        tools_data = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,
                },
            }
            for tool in all_tools
        ]

        # 2. 转换工具格式
        self.available_tools = await self.transform_json(tools_data)
        print(self.available_tools)

        self.initialized = True

    async def connect_to_browser_server(self):
        """浏览器服务"""
        # 检查脚本类型
        print("connect_to_browser_server")
        command = "npx"

        if self.default_browser == "puppeteer":
            server_script_path = "@modelcontextprotocol/server-puppeteer"
            launch_env_options = {
                "PUPPETEER_LAUNCH_OPTIONS": "{ \"headless\": false, \"executablePath\": \"" + self.browser_install_path + "\", \"args\": [] }"
                , 'ALLOW_DANGEROUS': 'true'}
            add_args = []
        elif self.default_browser == "playwright":
            server_script_path = "@executeautomation/playwright-mcp-server"
            launch_env_options = None
            add_args = ["--timeout=120000"]
        else:
            server_script_path = "@angiejones/mcp-selenium"
            launch_env_options = None
            add_args = []

        # 设置服务器参数并建立连接
        server_params = StdioServerParameters(
            command=command, args=["-y", server_script_path] + add_args, env=launch_env_options
        )

        # 初始化连接和会话
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.browser_session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )
        await self.browser_session.initialize()
        print("browser_session initialized")

    async def connect_to_database_server(self):
        """连接到MCP服务器并初始化会话"""
        # 检查脚本类型
        print("connect_to_database_server")
        command = "python"
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # DatabaseMcpServer.py的绝对路径
        server_script_path = os.path.join(current_dir, "db_mcp_server.py")

        # 设置服务器参数并建立连接
        server_params = StdioServerParameters(
            command=command, args=[server_script_path], env=None
        )

        # 初始化连接和会话
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.db_session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )
        await self.db_session.initialize()
        print("db_session initialized")

    async def connect_to_captcha_code_server(self):
        """playwright服务"""
        # 检查脚本类型
        print("connect_to_captcha_code_server")
        command = "python"
        # 获取当前文件的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 拼接VerificationCodeMcpServer.py的绝对路径
        server_script_path = os.path.join(current_dir, "captcha_code_mcp_server.py")
        # server_script_path= "VerificationCodeMcpServer.py"

        # 设置服务器参数并建立连接
        server_params = StdioServerParameters(
            command=command, args=[server_script_path], env=None
        )

        # 初始化连接和会话
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.verify_code_session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )
        await self.verify_code_session.initialize()
        print("verify_code_session initialized")

    async def transform_json(self, tools_data: List[Dict]) -> List[Dict]:
        """将Claude Function calling格式转换为OpenAI格式"""
        result = []

        for item in tools_data:
            old_func = item["function"]

            # 构建新的function对象
            new_func = {
                "name": old_func["name"],
                "description": old_func["description"],
                "parameters": {},
            }

            # 转换input_schema为parameters
            if "input_schema" in old_func and isinstance(
                    old_func["input_schema"], dict
            ):
                schema = old_func["input_schema"]
                new_func["parameters"] = {
                    "type": schema.get("type", "object"),
                    "properties": schema.get("properties", {}),
                    "required": schema.get("required", []),
                }

            result.append({"type": item["type"], "function": new_func})

        return result


    async def process_query(self, test_case_id: int) -> str:
        if not test_case_id:
            print("❌ 必须输入测试用例ID")
            return "❌ 必须输入测试用例ID"

        if not self.initialized:
            await self.initialize()

        """处理用户查询并调用必要的工具"""
        if not self.db_session or not self.browser_session or not self.verify_code_session:
            print("❌ 未连接到MCP服务器")
            return "❌ 未连接到MCP服务器"

        test_result_id = None
        try:

            # 1.创建TEST_RESULT记录
            test_case = TestCase.get_by_id(test_case_id)
            if not test_case["success"]:
                return "❌ 测试用例不存在"
            test_case = test_case["data"]
            params1 = json.loads(test_case["PARAMS"])
            test_template = TestTemplate.get_by_id(test_case["TEST_TEMPLATE_ID"])["data"]
            params = json.loads(test_template["PARAMS"])
            params.update(params1)

            test_result = TestResult.create(
                {"TEST_CASE_ID" : test_case_id
                    ,"PARAMS" : json.dumps(params)})["data"]
            test_result_id = test_result["TEST_RESULT_ID"]
            if not test_result_id:
                return "❌ 创建测试结果记录失败"

            screenshot_dir = f"{self.screen_shot_dir}/{test_case_id}/{test_result['TEST_RESULT_ID']}"
            os.makedirs(name = screenshot_dir, exist_ok=True)

            TestResult.update(test_result_id,
                {"SCREEN_SHOT_PATH" : f"{screenshot_dir}"})

            # 3. 选择提示模板并应用
            prompt_text = f"""
# Role:你是一名资深软件测试人员
# Goal：你需要根据定义在flow.t_test_template_step表中的测试步骤，使用mcp提供的浏览器完成测试。
# 测试规则：
  1.根据用户输入的测试用例结果ID，找到所有的测试用例步骤。如果没找到步骤，提示用户测试用例步骤不存在
  2.使用mcp提供的浏览器依次执行这些步骤中描述的操作(TEST_CONTENT),测试过程中应优先参考HTML_SELECTOR的内容定位页面控件。
  3.每一步（除了第一个步骤）执行前都应该将当前浏览器页面截图保存到{screenshot_dir}目录下，文件名格式为step_[index].png。（index是001,002,003...）
  4.完成测试用例每一步步骤的操作后，应该检查执行结果与期望结果(EXPECTED_RESULT)是否一致，一致则继续下一个步骤，否则测试失败并终止测试
  5.如果所有测试步骤通过，则将测试结果RESULT_OK(1)保存到flow.t_test_result表。如果测试失败，将失败信息、失败步骤ID、测试结果RESULT_OK(0)保存到flow.t_test_result表
  6.**非常重要** : 调用mcp工具查找页面控件若未找到，应该尝试修改selector后重试，重试时不能使用已尝试过的selector。最多重试5次，重试5次后没找到，则认为测试失败
  7.**重要** : 完成每一个测试用例步骤后应该检查浏览器是否打开了新tab页或者弹出窗口，如果打开了，应切换到新tab页或弹出窗口继续执行后续步骤
  8.**其他事项** : 回答内容尽量简洁。测试完成后，关闭测试浏览器。
  9.测试过程中生成临时文件保存在 {self.work_dir} 目录下
# 用户输入的测试用例结果ID：{test_result_id}
            """
            print("\n 提示词: ", prompt_text)

            # 5. 发送请求到OpenAI
            messages = [{"role": "user", "content": prompt_text}]
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, tools=self.available_tools
            )
            print("测试开始：")
            print(response)

            # 6. 处理工具调用
            max_tool_calls = 200  # 限制工具调用次数
            call_count = 0

            while response.choices[0].message.tool_calls :
                # 添加助手消息（包含工具调用）
                assistant_message = response.choices[0].message.model_dump()
                messages.append(assistant_message)

                # 处理所有工具调用
                tool_responses = []
                for tool_call in response.choices[0].message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    # 调用工具
                    print(f"\n[正在调用工具 {tool_name}, 参数: {tool_args}]")
                    db_tool_names = [tool.name for tool in self.db_tools_response.tools]
                    vc_tool_names = [tool.name for tool in self.vc_tools_response.tools]

                    if tool_name in db_tool_names:
                        result = await self.db_session.call_tool(tool_name, tool_args)
                    elif tool_name in vc_tool_names:
                        result = await self.verify_code_session.call_tool(tool_name, tool_args)
                    else:
                        result = await self.browser_session.call_tool(tool_name, tool_args)

                    # 为每个工具调用添加对应的工具响应消息
                    tool_responses.append({
                        "role": "tool",
                        "content": result.content[0].text,
                        "tool_call_id": tool_call.id,
                    })

                # 将所有工具响应添加到消息列表
                messages.extend(tool_responses)

                # 再次请求OpenAI
                response = self.client.chat.completions.create(
                    model=self.model, messages=messages, tools=self.available_tools
                )
                print("模型响应：")
                print(response)
                call_count += 1
                if call_count >= max_tool_calls:
                    print(f"⚠️ 已调用工具 {max_tool_calls} 次，仍未完成所有工具调用，可能存在循环调用问题")
                    raise f"⚠️ 已调用工具 {max_tool_calls} 次，仍未完成所有工具调用，可能存在循环调用问题"

            # 7. 返回最终结果
            print("测试结束：")
            return response.choices[0].message.content

        except Exception as e:
            try :
                if test_result_id :
                    TestResult.update(test_result_id,{"RESULT_OK": "0"
                                                   , "ERROR_STEP_ID": 0
                                                   , "ERROR_STEP_NAME": "未知"
                                                   , "ERROR_INFO": str(e)
                                                })
            except Exception as e1:
                print(f"保存结果时报错了：{str(e1)}")
            return f"❌ 测试时出错: {str(e)}"

    async def chat_once(self, query : str):
        """运行交互式聊天循环"""
        try:
            if query == "" or query.lower() == "quit" or not query.isdigit():
                print("\n  参数错误，退出...")
                return

            print("\n  处理中...")
            response = await self.process_query(int(query))
            print(f"\n  回复: {response}")

        except Exception as e:
            print(f"\n⚠️ 发生错误: {str(e)}")

    async def chat_queue(self):
        # 从task_queue中取出test_case_id,依次执行测试
        formatted_time = ""
        while True:
            try:
                current_time = datetime.datetime.now()
                formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
                if self.task_queue is None or self.task_queue.empty():
                    await asyncio.sleep(random.randint(3, 10))
                    continue
                self.running_case_id = self.task_queue.get()
                print(f"\n {formatted_time}： 处理中...{self.running_case_id}")
                # await asyncio.sleep(10)
                response = await self.process_query(self.running_case_id)
                self.running_case_id = -1
                print(f"\n {formatted_time}：处理完毕{self.running_case_id} 回复: {response}")
            except Exception as e:
                print(f"\n⚠️ {formatted_time}： 发生错误: {str(e)}")

    async def cleanup(self):
        """清理资源"""
        if self.db_session:
            try:
                self.db_session.close()
            except Exception as e:
                pass
        if self.verify_code_session:
            try:
                self.verify_code_session.close()
            except Exception as e:
                pass
        if self.browser_session:
            try:
                self.browser_session.close()
            except Exception as e:
                pass
        if self.exit_stack:
            try:
                await self.exit_stack.aclose()
            except Exception as e:
                pass
        print("\n  已清理资源并断开连接")

# testAgentClient = TestAgentClient()
#
# async def main():
#     serve_path = ""
#     """主函数"""
#     try:
#
#         query = input("\n输入测试用例ID: ").strip()
#         # testAgentClient.add_to_queue(int(query))
#         await testAgentClient.chat_once(query)
#     except Exception as e:
#         print(f"\n⚠️ 程序出错: {str(e)}")
#     finally:
#         await testAgentClient.cleanup()
#
# if __name__ == "__main__":
#     asyncio.run(main())