from request import http
import setting
from loghelper import log
import yaml
import os

def get_config_path():
    path = os.path.dirname(os.path.realpath(__file__)) + "/config"
    if os.getenv("Captcha_config_path") is not None:
        path = os.getenv("Captcha_config_path")
    return f"{path}/captcha-config.yaml"

# 读取配置文件
def load_config():
    config_path = get_config_path()
    with open(config_path, 'r') as file:
        config_data = yaml.safe_load(file)
    return config_data

def app_key():
    config_data = load_config()
    appkey = config_data.get('ocr', {}).get('appkey', None)
    return appkey

def api_url():
    config_data = load_config()
    api_url = config_data.get('ocr', {}).get('api_url', None)
    return api_url

api_url = api_url()
appkey = app_key()

def game_captcha(gt: str, challenge: str,header: dict):
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


if __name__ == "__main__":
    print(app_key())
    #print(test.log)
