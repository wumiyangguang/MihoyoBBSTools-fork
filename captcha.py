from request import http
import setting
from loghelper import log
import config



api_url='http://api.rrocr.com/api/recognize.html' #接口地址       

def app_key():#接口appkey
    config.load_config()
    appkey = config.config.get('rrocr',{}).get('appkey', None)
    return appkey

appkey=app_key()
'''
def post_with_retry(api_url: str,data: dict,timeout=10,retry_delay = 5):
    while True:
        try:
            response = http.post(api_url,data=data,timeout=timeout)
            response.raise_for_status()  # 如果返回的状态码不是200，抛出HTTPError异常
            result = response.json()
            return result # 请求成功，返回response对象
        except TimeoutError:
            log.warning("请求超时，正在重试...")
        except RequestError as e:
            log.warning(f"请求失败：{e}")
        except Exception as e:
            log.warning(f"未知错误：{e}")
            return None  # 如果是其他请求错误，退出循环
        time.sleep(retry_delay)  # 等待重试延迟时间
        '''

def game_captcha(gt: str, challenge: str):
    appkey = app_key
    data = {
    'appkey': appkey,
    'gt': gt,
    'challenge': challenge,
    'referer': setting.cn_game_is_signurl,
    'ip': '',
    'host': ''
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

def bbs_captcha(gt: str, challenge: str):
    data = {
    'appkey': appkey,
    'gt': gt,
    'challenge': challenge,
    'referer': setting.bbs_get_captcha,
    'ip': '',
    'host': ''
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
    test=game_captcha(gt='d019a22590a54475b8e30eeb2854aab9',challenge='92e65680ceb0554c2410eac3cdcde3d5')
    #print(test.log)
