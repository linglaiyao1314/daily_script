"""
1. 构造requests data
2. 生成headers必备字段
3. 请求接口并保存数据为json待后续分析,数据下载到
"""

import execjs
import time
import requests
import json

URL = "https://wchat.enmonster.com/applet/nss/search/v2"

# sign生成必备的key
DEFAULT_WX_SIGN_KEY = "AOCAQ8AMIIBCgKCAQEAgXuz"
DEFAULT_SIGN_KEY = "Enmonster1565778653XuAMIIBCOCAQ8AgKCAQE"

# 抽出来的加密代码
ENCRYPT_FUNC_PATH = "monster_encrypt.js"

# 读取加密逻辑js代码备用
with open(ENCRYPT_FUNC_PATH, "r") as f:
    source = f.read()
    js_funcs = execjs.compile(source)


# 加密函数
def hex_md5(raw: str):
    return js_funcs.call("hexMD5", raw)


# 请求参数排序
def ksort(request_data: dict):
    return [(k, request_data[k]) for k in sorted(request_data.keys()) if request_data[k] is not None]


# 请求参数拼接,为后续生成sign做准备, x-sign 与 x-wx-sign
def make_data_str(request_data: dict, version="wx"):
    if version == "wx":
        return "&".join([f"{item[0]}={item[1]}" for item in ksort(request_data)])
    else:
        return "".join([f"{item[0]}{item[1]}" for item in ksort(request_data) if item[1] != ""])


# x-sign的nonce生成逻辑
def make_nonce():
    return hex_md5(str(int(time.time() * 1000)))


# 生成X-WX-SIGN
def make_wx_sign_key(request_data: dict, default_sign_key: str = "AOCAQ8AMIIBCgKCAQEAgXuz"):
    s = make_data_str(request_data, "wx")
    return hex_md5(hex_md5(s) + default_sign_key)


# 生成X-SIGN
def make_sign_key(request_data: dict, nonce: str, default_sign_key: str = "Enmonster1565778653XuAMIIBCOCAQ8AgKCAQE"):
    s = make_data_str(request_data, "x")
    s = hex_md5(nonce) + s + default_sign_key
    return hex_md5(s)


def write_result(filename, data: dict):
    if len(data) <= 0:
        return
    with open(filename, "r") as file_obj:
        json.dump(data, file_obj)


# 主要为了方便, 提前准备好nonce和token，免去模拟登录的过程
def crawl_by_token(nonce, token):
    session = requests.session()
    request_data = {"latitude": "31.22114",
                    "longitude": "121.54409",
                    "locatedLatitude": "31.22114",
                    "locatedLongitude": "121.54409",
                    "platform": 1,
                    "queryCabtAvailable": 1,
                    "pageIndex": 1,
                    "pageSize": 15,
                    "hasCabinet": 1,
                    "activityId": ""}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.4.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat",
        "Referer": "https://servicewechat.com/wxb57627a2a7e9cb59/208/page-frame.html",
        "X-WX-TOKEN": token,
        "X-NONCE": nonce,
        "X-MAC": hex_md5(nonce)
    }
    start_page = 1
    max_page = 1000
    # 抓取流程
    while start_page <= max_page:
        request_data.update({"token": token})
        sign = make_sign_key(request_data, nonce)
        headers.update({"X-SIGN": sign})
        page_result = session.post(URL,
                                   headers=headers, data=request_data).json()
        write_result(f"page_{start_page}.json", page_result)
        time.sleep(10)
        start_page += 1
        request_data["pageIndex"] = start_page
        # 更新最新页数
        max_page = request_data.get("data", {"total_count": 1})["total_count"]


if __name__ == '__main__':
    nonce = "xxx"
    token = "xxx"
    crawl_by_token(nonce, token)
