from request import http
import time
from loghelper import log
import yaml
import os

_config_data = None

def get_config_path():
    """
    获取配置文件路径，支持环境变量自定义配置路径
    """
    path = os.path.dirname(os.path.realpath(__file__)) + "/config"
    if os.getenv("Captcha_config_path"):
        path = os.getenv("Captcha_config_path")
    config_path = os.path.join(path, "captcha-config.yaml")
    
    # 检查配置文件是否存在，不存在则生成默认配置文件
    if not os.path.exists(config_path):
        default_config = {
            'ocr': {
                'appkey': 'your_default_appkey',
                'api_url': 'your_default_api_url',
                'result_url': 'your_default_result_url'
            }
        }
        os.makedirs(path, exist_ok=True)
        with open(config_path, 'w') as file:
            yaml.dump(default_config, file)
    
    return config_path

def load_config():
    """
    读取配置文件内容，支持缓存配置内容以避免多次读取
    """
    global _config_data
    if _config_data is None:
        config_path = get_config_path()
        with open(config_path, 'r') as file:
            _config_data = yaml.safe_load(file)
    return _config_data

def get_config_value(key, default=None):
    """
    获取配置中的指定值，如果不存在返回默认值
    """
    config_data = load_config()
    return config_data.get('ocr', {}).get(key, default)

def app_key():
    """获取 appkey"""
    return get_config_value('appkey')

def api_url():
    """获取 api_url"""
    return get_config_value('api_url')

def result_url():
    """获取 result_url"""
    return get_config_value('result_url')

# 使用示例
api_url = api_url()
appkey = app_key()
result_url = result_url()

'''def game_captcha(gt: str, challenge: str,header: dict):
    data = {
    'appkey': appkey,
    'gt': gt,
    'challenge': challenge,
    'itemid': 388
}
    try:
        response = http.post(api_url,data=data)
        result = response.json()
        if result.get("status") == 0 and result.get("msg") == "识别成功":
            validate = result["data"].get("validate")
            return validate
        else:
        # 识别失败，返回None或其他提示
            log.warning(f"{result.get('msg')}")
            #print(result)
            return None
    except Exception as e:
        log.warning(f'出现错误：{e}')
        return None

def game_captcha(gt: str, challenge: str, header: dict):
    if not all([gt, challenge, header]):
        log.warning("参数缺失：gt、challenge 或 header 不可为空")
        return None

    # 第一步：提交验证码信息
    submit_data = {
        'appkey': appkey,
        'gt': gt,
        'challenge': challenge,
        'itemid': 37
    }
    
    try:
        submit_response = http.post(api_url, data=submit_data, headers=header)
        if submit_response.status_code != 200:
            log.warning(f"提交验证码信息失败，HTTP状态码：{submit_response.status_code}")
            return None

        submit_result = submit_response.json()
        if submit_result.get("status") != 1 or "resultid" not in submit_result:
            log.warning(f"提交验证码失败，返回信息：{submit_result}")
            return None
        
        resultid = submit_result["resultid"]
        log.info(f"提交成功，resultid：{resultid}")
    
    except Exception as e:
        log.warning(f"提交验证码信息时出现错误：{e}")
        return None

    # 第二步：使用 resultid 查询识别结果
    max_attempts = 5  # 设置最大查询次数
    for attempt in range(max_attempts):
        try:
            query_data = {'resultid': resultid, 'appkey': appkey}
            query_response = http.post(result_url, data=query_data, headers=header)

            if query_response.status_code != 200:
                log.warning(f"查询验证码结果失败，HTTP状态码：{query_response.status_code}")
                continue

            query_result = query_response.json()
            if query_result.get("status") == 1 and "validate" in query_result:
                validate = query_result["validate"]
                log.info(f"验证码识别成功，validate：{validate}")
                return validate
            elif query_result.get("status") == 0:
                log.info(f"识别未完成，尝试第 {attempt + 1}/{max_attempts} 次查询...")
            else:
                log.warning(f"查询验证码失败，返回信息：{query_result}")
                return None

        except Exception as e:
            log.warning(f"查询验证码结果时出现错误：{e}")

        # 每次查询后等待 1 秒
        if attempt < max_attempts - 1:
            time.sleep(1)

    log.warning("超过最大查询次数，验证码识别失败")
    return None

def bbs_captcha(gt: str, challenge: str,header: dict):
    #headers = urllib.parse.quote(header.get('User-Agent'))
    data = {
    'appkey': appkey,
    'gt': gt,
    'challenge': challenge,
    'itemid': 388
}
    try:
        response = http.post(api_url,data=data)
        result = response.json()
        if result.get("status") == 0 and result.get("msg") == "识别成功":
            validate = result["data"].get("validate")
            return validate
        else:
        # 识别失败，返回None或其他提示
            log.warning(f"{result.get('msg')}")
            return None
    except Exception as e:
        log.warning(f'出现错误：{e}')
        return None
'''
def send_post_request(url, data, headers=None):
    """
    发送 POST 请求的通用方法，处理请求和返回的异常。
    """
    try:
        response = http.post(url, data=data, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()
    except Exception as e:
        log.warning(f"HTTP 请求失败: {e}")
        return None


def captcha_recognition(api_url, result_url, gt, challenge):
    """
    通用的验证码识别函数，包含每秒查询一次的限制。
    提交识别请求并根据 resultid 查询结果，返回识别结果的 validate 字段。
    """
    if not gt or not challenge:
        log.warning("gt 或 challenge 参数缺失")
        return None

    # 提交验证码识别请求
    data = {
        'appkey': appkey,
        'gt': gt,
        'challenge': challenge,
        'itemid': 388
    }
    result = send_post_request(api_url, data)

    if result is None:
        log.warning("验证码识别请求失败")
        return None

    if result.get("status") == 1 and result.get("msg") == "提交成功":
        # 提交成功后，获取 resultid 用于查询结果
        resultid = result.get("resultid")
        if not resultid:
            log.warning("返回的结果中没有 resultid")
            return None

        # 每秒查询一次，直到获取结果或超时
        for attempt in range(30):  # 最多查询 30 次（30 秒超时）
            time.sleep(1)  # 每秒查询一次

            query_data = {
                'appkey': appkey,
                'resultid': resultid
            }
            query_result = send_post_request(result_url, query_data)

            if query_result is None:
                log.warning(f"第 {attempt + 1} 次查询失败")
                continue

            if query_result.get("status") == 0 and query_result.get("msg") == "识别成功":
                return query_result["data"].get("validate")

            elif query_result.get("status") == 1:  # 结果仍在处理中
                log.info(f"第 {attempt + 1} 次查询：结果处理中...")
                continue

            else:  # 其他错误或失败情况
                log.warning(f"识别失败：{query_result.get('msg')}")
                return None

        log.warning("查询超时，识别结果未返回")
        return None
    else:
        log.warning(f"验证码提交失败：{result.get('msg')}")
        return None


def game_captcha(gt: str, challenge: str):
    """调用通用验证码识别函数，传入游戏验证码相关的 API URL 和结果查询 URL"""
    return captcha_recognition(api_url, result_url, gt, challenge)


def bbs_captcha(gt: str, challenge: str):
    """调用通用验证码识别函数，传入 BBS 验证码相关的 API URL 和结果查询 URL"""
    return captcha_recognition(api_url, result_url, gt, challenge)

if __name__ == "__main__":
    print(app_key())
    #print(test.log)
