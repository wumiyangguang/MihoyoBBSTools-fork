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

api_url = api_url()
appkey = app_key()
result_url = result_url()

def send_post_request(url, data):
    """
    通用 POST 请求方法，处理请求和异常。
    """
    try:
        response = http.post(url, data=data)
        response.raise_for_status()  # 确保请求成功
        return response.json()
    except Exception as e:
        log.warning(f"HTTP 请求失败: {e}")
        return None


def captcha_recognition(api_url, result_url, gt, challenge):
    """
    通用的验证码识别函数，提交验证码请求并根据 resultid 查询结果。
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
        # 提交成功，获取 resultid
        resultid = result.get("resultid")
        if not resultid:
            log.warning("返回的结果中没有 resultid")
            return None

        # 每秒查询一次，最多查询 60 次
        for attempt in range(60):  # 最多等待 60 秒
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
                validate = query_result["data"].get("validate")
                log.info(f"验证码识别成功: validate={validate}")
                return validate

            elif query_result.get("status") == 1:  # 结果处理中
                log.info(f"第 {attempt + 1} 次查询：结果仍在处理中...")
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
    """
    游戏验证码识别模块。
    """
    return captcha_recognition(api_url, result_url, gt, challenge)


def bbs_captcha(gt: str, challenge: str):
    """
    BBS 验证码识别模块。
    """
    return captcha_recognition(api_url, result_url, gt, challenge)

if __name__ == "__main__":
    print(app_key())
    #print(test.log)
