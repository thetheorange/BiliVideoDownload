"""
Des 读写配置文件
@Author thetheOrange
Time 2024/2/18
"""
import json
import os

from logger.Logger import app_logger

# 默认配置
init_config = {
    "app_lock": 0,
    "login_status": 0,
    "video_format": "mp4",
    "audio_format": "aac",
    "qn": 80,
    "cookies": "{}"
}
init_config = json.dumps(init_config)


# 读取配置文件
def read_config():
    try:
        if not os.path.exists("config.json"):
            with open("config.json", "w") as f:
                f.write(init_config)
        else:
            with open("config.json", "r") as f:
                content = f.read()
                content = json.loads(content)
                return content
    except FileNotFoundError as e:
        app_logger.error(e)


# 修改配置文件函数
def modify_config(key, value):
    try:
        if not os.path.exists("config.json"):
            with open("config.json", "w") as f:
                f.write(init_config)
        else:
            # 读取旧数据
            with open("config.json", "r") as f:
                content = json.load(f)

            if key in content:
                content[key] = value
            else:
                app_logger.info("not found key to update")

            # 写入新数据
            with open("config.json", "w") as f:
                json.dump(content, f, indent=2)
    except Exception as e:
        app_logger.error(f"[MODIFY CONFIG] ERROR: {e}")
