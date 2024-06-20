import requests


def req(url: str, method: str = 'GET', payload=None):
    response = None
    if method == 'POST':
        if payload is None:
            payload = {}
        response = requests.post(url, data=payload)

    if method == 'GET':
        response = requests.get(url)

    # 检查请求是否成功
    if response.status_code == 200:
        # 解析JSON响应
        data = response.json()
        return data
    else:
        return {"code": response.status_code}
