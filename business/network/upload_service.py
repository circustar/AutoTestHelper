import datetime

import requests
import os
from requests_toolbelt.multipart.encoder import MultipartEncoder
from dotenv import load_dotenv

# 加载 .env 文件，确保 API Key 受到保护
load_dotenv()

Upload_url = os.getenv("UPLOAD_URL")
Download_url = os.getenv("DOWNLOAD_URL")
Upload_Token_prefix = os.getenv("UPLOAD_TOKEN_PREFIX")

class UploadService() :
    def generateToken(self):
        # 当前日期YYYYMMDD
        dateStr = datetime.datetime.now().strftime("%Y%m%d")
        return Upload_Token_prefix + dateStr
    def upload(self, image_path: str):
        r"""将本地文件上传至服务器

        :param image_path: 本地图片保存路径
        :return: 图片上传后的下载地址
        :rtype: str
        """
        try:
            token = self.generateToken()
            filename = os.path.basename(image_path)
            # # 根据文件后缀名自动检测文件类型
            # content_type, _ = mimetypes.guess_type(image_path)
            # if not content_type:
            #     # 如果无法检测到类型，默认使用image/png
            #     content_type = 'image/png'
            timestamp_ms = str(datetime.datetime.now().timestamp() * 1000)
            boundary = "multipart/form-data; boundary=----WebKitFormBoundary" + timestamp_ms
            data= MultipartEncoder(
                fields={
                    'file': (filename, open(image_path, 'rb'), boundary)
                }
            )
            # 获取当前时间的时间戳（毫秒）

            headers = {
                "X-Upload-Token": token,
                "Content-Type": data.content_type
            }

            # 发送POST请求上传文件
            response = requests.post(Upload_url, data=data, headers=headers)

            # 检查响应状态码
            if response.status_code == 200:
                # 返回上传成功后的下载地址
                return Download_url + response.json()["data"]
            else:
                # 上传失败，抛出异常
                raise ValueError(f"上传失败，状态码: {response.status_code}, 原因: {response.reason}")
        except Exception as e:
            # 捕获并处理所有异常
            raise ValueError(f"文件上传过程中发生错误: {str(e)}")

# ===== 主程序入口 =====

if __name__ == "__main__":
    # 以标准 I/O 方式运行 MCP 服务器
    service = UploadService()
    responseText = service.upload("D:/TEMP/1.png")
    print(responseText)
