""" 统一请求封装 """
import requests
import logging
import json
from datetime import datetime

# ============== 日志输出、配置 =================
def print_log(msg):
    """统一打印日志：由pytest.ini控制输出文件/格式"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{now}] {msg}"
    # print(log_msg)  # 控制台打印
    # 只通过logging输出，控制台/文件由pytest配置统一管控
    logging.info(log_msg)


class RequestUtil:

    session = requests.Session()  # 持久会话，自动保存 Cookie、Token、连接池

    """ 发送所有请求 """
    def send_all_request(self, **kwargs):


        # 发送请求  request() 通用方法，支持 get/post/put/delete，由 method 变量控制
        res = RequestUtil.session.request(**kwargs)  # **kwargs 包含了params、json、method等参数

        # ========== 统一在这里格式化打印响应，解决unicode问题 ==========
        """该问题待解决"""
        content_type = res.headers.get("Content-Type", "").lower()
        if "application/json" in content_type:
            try:
                resp_str = json.dumps(res.json(), ensure_ascii=False)
            except Exception:
                resp_str = res.text
        else:
            resp_str = res.text
        print_log(f"响应结果为{resp_str}")


        return res