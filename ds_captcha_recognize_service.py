from idlelib.rpc import response_queue

import requests
import os
from dotenv import load_dotenv
import random
from requests_toolbelt import MultipartEncoder

# 加载 .env 文件，确保 API Key 受到保护
load_dotenv()

base_url = os.getenv("BWDS_BASE_URL")
api_url = os.getenv("BWDS_BASE_API_URL")
api_key = os.getenv("BWDS_CAPTCHA_REC_API_KEY")
api_id = os.getenv("BWDS_CAPTCHA_REC_APPID")

class DsCaptchaRecognizeService() :
    def upload_file_to_bwds(self, file_path: str) -> str:
        upload_url = api_url + "/common/file/upload"

        file_name = os.path.basename(file_path)
        data = {
            'data': '{"appId":"' + api_id +'"}',
            'bucketName': 'chat',
            'metadata': '{"chatId":"1234567895343212331"}',
        }
        print(data)

        # 创建 MultipartEncoder 实例
        with open(file_path, 'rb') as file:
            m = MultipartEncoder(
                fields={
                    **data,
                    'file': (file_name, file, 'text/plain')
                }
            )
            request_headers = {"User-Agent": "Mozilla/5.0", "Authorization": "Bearer " + api_key,
                               "Content-Type": m.content_type}
            response = requests.post(upload_url, headers=request_headers, data=m)

        print("上传文件响应:")
        print(response)
        # 检查响应
        if response.status_code == 200:
            print('文件上传成功')
            print(response.text)  # 打印响应内容
        else:
            raise Exception('文件上传失败, 状态码: {}, 错误原因: {}'.format(response.status_code, response.reason))

        return response.json()["data"]["previewUrl"]

    def recognize_captcha(self, file_path: str, prompt : str) -> str:
        r"""识别验证码

        :param file_path: 图片文件路径
        :return: : 响应结果
        :rtype: str
        """
        image_url = self.upload_file_to_bwds(file_path)
        return self.recognize_captcha_url(image_url, prompt)

    def recognize_captcha_url(self, image_url: str, prompt : str) -> str:
        r"""识别验证码

        :param image_url: 图片url
        :return: : 响应结果
        :rtype: str
        """
        send_message = {
          "messages" : [
              {
                "dataId": "oYDjGCVbREfIpZ2yL1TqWhMF",
                "hideInUI": False,
                "role": "user",
                "content": [
                  {
                    "type": "image_url",
                    "image_url": {
                      "url": image_url
                    }
                  },
                  {
                    "type": "text",
                    "text": prompt if prompt else "识别图中验证码"
                  }
                ]
              }
            ],
            "model": "Qwen-2.5-VL-7B",
            "id" : "12345678901222"
        }
        print('发送给BWDS的请求: ')
        print(send_message)

        request_headers = {"User-Agent": "Mozilla/5.0", "Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
        # 2.返回Qwen识别出的验证码
        response = requests.post(api_url + "/v1/chat/completions", json=send_message, headers=request_headers)

        print(response.status_code)  # 打印状态码
        print(response.json())  # 打印状态码
        if response.status_code == 200:
            response_text = response.json()["choices"][0]["message"]["content"] #response.json()
            if "验证码为" in response_text:
                split_str = "：" if "：" in response_text else ":"
                response_text = response_text.split(split_str)[1].strip()
            else :
                response_text = response_text.strip()
            return response_text
        else:
            raise ValueError("错误代码：" + str(response.status_code) + ", 错误原因:" + response.reason)


# ===== 主程序入口 =====

if __name__ == "__main__":
    # 以标准 I/O 方式运行 MCP 服务器
    service = DsCaptchaRecognizeService()
    # responseText = service.recognizeCaptcha("识别图中的4位验证码，只返回验证码即可","http://124.223.12.30:8086/download/GDtFU8-rJdA9jvS81AtFcZeOwGNANuRFDxC1juHEkQOUfR6kq1Z2T5tFb9HdHmSxbmpuHvKfuxQyh-aYS6kxYQ==")
    # responseText = service.recognizeCaptcha("识别图中验证码",
    #                                         "https://ds.baocloud.cn/xin3plat/api/common/file/read/1.png?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJidWNrZXROYW1lIjoiY2hhdCIsInRlYW1JZCI6IjY3ZjM4MTExODQ4MTU4MGEzMzQ2NGIyZCIsInVpZCI6IjY4MWRiZmYyOWJlYTczMTc2YTc0MmQyNCIsImZpbGVJZCI6IjY5NzFkYzQ5OGQzMDdiNTFhZTQ0ZjkwZSIsImV4cCI6MTc2OTY3NDQ0MSwiaWF0IjoxNzY5MDY5NjQxfQ.0X_dKpjNpm-dATy31oNvIrurI01rj5cH_tjzrvvcCig")
    # print(responseText)
    image_url = service.upload_file_to_bwds("D:/TEMP/1.png")
    print(image_url)
    responseText = service.recognize_captcha(image_url)
    print(responseText)
