# config.py 自定义配置,包括阅读次数、推送token的填写
import json
import re
from pathlib import Path

"""
运行配置
默认读取 Docker 挂载目录 /app/config/config.json，本地运行时读取 ./config/config.json
"""

CONFIG_PATHS = (
    Path("/app/config/config.json"),
    Path(__file__).resolve().parent / "config" / "config.json",
)


def load_runtime_config():
    for config_path in CONFIG_PATHS:
        if config_path.is_file():
            with config_path.open("r", encoding="utf-8") as config_file:
                loaded_config = json.load(config_file)
                return loaded_config if isinstance(loaded_config, dict) else {}
    return {}


runtime_config = load_runtime_config()


def get_config(key, default=None):
    value = runtime_config.get(key, default)
    return default if value is None else value


def get_int_config(key, default):
    value = get_config(key, default)
    if value in (None, ""):
        return default
    return int(value)


# 阅读次数 默认40次/20分钟
READ_NUM = get_int_config("READ_NUM", 40)
# 需要推送时可选，可选pushplus、wxpusher、telegram、serverchan、gotify
PUSH_METHOD = get_config("PUSH_METHOD", "")
# pushplus推送时需填
PUSHPLUS_TOKEN = get_config("PUSHPLUS_TOKEN", "")
# telegram推送时需填
TELEGRAM_BOT_TOKEN = get_config("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = get_config("TELEGRAM_CHAT_ID", "")
# wxpusher推送时需填
WXPUSHER_SPT = get_config("WXPUSHER_SPT", "")
# SeverChan推送时需填
SERVERCHAN_SPT = get_config("SERVERCHAN_SPT", "")
# Gotify推送时需填
GOTIFY_URL = get_config("GOTIFY_URL", "")
GOTIFY_TOKEN = get_config("GOTIFY_TOKEN", "")
GOTIFY_PRIORITY = get_int_config("GOTIFY_PRIORITY", 5)
# Telegram代理，可选
HTTP_PROXY = get_config("http_proxy", get_config("HTTP_PROXY", ""))
HTTPS_PROXY = get_config("https_proxy", get_config("HTTPS_PROXY", ""))


# read接口的bash命令，也可以改用配置文件里的headers、cookies字段
curl_str = get_config("WXREAD_CURL_BASH", "")

# headers、cookies是一个省略模版，本地或者docker部署时对应替换
cookies = {
    'RK': 'oxEY1bTnXf',
    'ptcz': '53e3b35a9486dd63c4d06430b05aa169402117fc407dc5cc9329b41e59f62e2b',
    'pac_uid': '0_e63870bcecc18',
    'iip': '0',
    '_qimei_uuid42': '183070d3135100ee797b08bc922054dc3062834291',
    'wr_avatar': 'https%3A%2F%2Fthirdwx.qlogo.cn%2Fmmopen%2Fvi_32%2FeEOpSbFh2Mb1bUxMW9Y3FRPfXwWvOLaNlsjWIkcKeeNg6vlVS5kOVuhNKGQ1M8zaggLqMPmpE5qIUdqEXlQgYg%2F132',
    'wr_gender': '0',
}

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,ko;q=0.5',
    'baggage': 'sentry-environment=production,sentry-release=dev-1730698697208,sentry-public_key=ed67ed71f7804a038e898ba54bd66e44,sentry-trace_id=1ff5a0725f8841088b42f97109c45862',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
}


# 书籍
book = [
    "36d322f07186022636daa5e","6f932ec05dd9eb6f96f14b9","43f3229071984b9343f04a4","d7732ea0813ab7d58g0184b8",
    "3d03298058a9443d052d409","4fc328a0729350754fc56d4","a743220058a92aa746632c0","140329d0716ce81f140468e",
    "1d9321c0718ff5e11d9afe8","ff132750727dc0f6ff1f7b5","e8532a40719c4eb7e851cbe","9b13257072562b5c9b1c8d6"
]

# 章节
chapter = [
    "ecc32f3013eccbc87e4b62e","a87322c014a87ff679a21ea","e4d32d5015e4da3b7fbb1fa","16732dc0161679091c5aeb1",
    "8f132430178f14e45fce0f7","c9f326d018c9f0f895fb5e4","45c322601945c48cce2e120","d3d322001ad3d9446802347",
    "65132ca01b6512bd43d90e3","c20321001cc20ad4d76f5ae","c51323901dc51ce410c121b","aab325601eaab3238922e53",
    "9bf32f301f9bf31c7ff0a60","c7432af0210c74d97b01b1c","70e32fb021170efdf2eca12","6f4322302126f4922f45dec"
]

"""
建议保留区域|默认读三体，其它书籍自行测试时间是否增加
"""
data = {
    "appId": "wb182564874603h266381671",
    "b": "ce032b305a9bc1ce0b0dd2a",
    "c": "7f632b502707f6ffaa6bf2e",
    "ci": 27,
    "co": 389,
    "sm": "19聚会《三体》网友的聚会地点是一处僻静",
    "pr": 74,
    "rt": 15,
    "ts": 1744264311434,
    "rn": 466,
    "sg": "2b2ec618394b99deea35104168b86381da9f8946d4bc234e062fa320155409fb",
    "ct": 1744264311,
    "ps": "4ee326507a65a465g015fae",
    "pc": "aab32e207a65a466g010615",
    "s": "36cc0815"
}


def convert(curl_command):
    """提取bash接口中的headers与cookies
    支持 -H 'Cookie: xxx' 和 -b 'xxx' 两种方式的cookie提取
    """
    # 提取 headers
    headers_temp = {}
    for match in re.findall(r"-H '([^:]+): ([^']+)'", curl_command):
        headers_temp[match[0]] = match[1]

    # 提取 cookies
    cookies = {}
    
    # 从 -H 'Cookie: xxx' 提取
    cookie_header = next((v for k, v in headers_temp.items() 
                         if k.lower() == 'cookie'), '')
    
    # 从 -b 'xxx' 提取
    cookie_b = re.search(r"-b '([^']+)'", curl_command)
    cookie_string = cookie_b.group(1) if cookie_b else cookie_header
    
    # 解析 cookie 字符串
    if cookie_string:
        for cookie in cookie_string.split('; '):
            if '=' in cookie:
                key, value = cookie.split('=', 1)
                cookies[key.strip()] = value.strip()
    
    # 移除 headers 中的 Cookie/cookie
    headers = {k: v for k, v in headers_temp.items() 
              if k.lower() != 'cookie'}

    return headers, cookies


configured_data = get_config("data", {})
if isinstance(configured_data, dict):
    data.update(configured_data)

configured_book = get_config("book", [])
if isinstance(configured_book, list) and configured_book:
    book = configured_book

configured_chapter = get_config("chapter", [])
if isinstance(configured_chapter, list) and configured_chapter:
    chapter = configured_chapter

configured_headers = get_config("headers", get_config("HEADERS", {}))
configured_cookies = get_config("cookies", get_config("COOKIES", {}))

if curl_str:
    headers, cookies = convert(curl_str)
else:
    if isinstance(configured_headers, dict) and configured_headers:
        headers = configured_headers
    if isinstance(configured_cookies, dict) and configured_cookies:
        cookies = configured_cookies
