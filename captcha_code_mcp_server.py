import os
from typing import Dict, Any

from mcp.server.fastmcp import FastMCP

from ds_captcha_recognize_service import DsCaptchaRecognizeService

# 初始化 FastMCP 服务器
mcp = FastMCP("verification-code-server")

captcha_recognize_service = DsCaptchaRecognizeService()

# ===== 工具函数 =====
@mcp.tool(description="获取本地图片中的验证码")
def recognize_captcha(image_path: str, code_format: str = "") -> Dict[str, Any]:
    """
    识别验证码。

    参数:
    image_path (str): 本地图片文件路径。

    返回:
    验证码
    """
    prompt = "识别图中的验证码"
    if code_format!="":
        prompt = prompt + ", 验证码格式为" + code_format
    # 2.调用阿里云Qwen大模型，识别url中的验证码
    try :

        response = captcha_recognize_service.recognize_captcha(file_path=image_path, prompt=prompt)
        if response :
            return {"success": True, "data" : response, "message" : "识别成功"}
        else :
            raise {"success": False, "data": "", "message": "识别验证码失败了，识别结果为空"}
    except Exception as e:
        raise {"success": False, "data" : "", "message" : "识别验证码时报错，错误信息：" + e}

# ===== 主程序入口 =====

if __name__ == "__main__":
    # 以标准 I/O 方式运行 MCP 服务器
    mcp.run(transport='stdio')
