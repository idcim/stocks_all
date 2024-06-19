import os
from os import getenv
from dotenv import load_dotenv

load_dotenv()


# 获取环境变量
def env(key, default_value: str = None):
    if getenv(key) is None:
        print(f"未配置环境变量{key}")
        return False
    else:
        return getenv(key)


# mysql配置
def db():
    config = {
        'host': env('DB_HOST'),
        'user': env('DB_USER'),
        'password': env('DB_PASSWORD'),
        'db': env('DB_NAME'),
        'charset': 'utf8mb4'
    }
    return config
