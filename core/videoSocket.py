"""
Des 程序核心，请求服务器音视频数据，并使用ffmpeg合成视频
@Author thetheOrange
Time 2024/2/18
"""
import json
import os
import random
import re
import subprocess
import threading
import time

import requests
import jsonpath

from core.config import read_config
from core.global_signal import global_signal
from logger.Logger import app_logger


# B站视频爬虫
class videoSocket:

    def __init__(self, base_url, qn, flag=False, cookies=""):
        self.base_url = base_url
        # 视频清晰度
        self.qn = qn
        self.cookies = cookies
        # 是否只下载音频标志
        self.flag = flag

        # 公共请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
            "Referer": self.base_url
        }

    # 爬虫开启入口
    def run(self):
        app_logger.info("[socket] socket start!")
        self.__get_cid()
        self.__get_url()
        # 下载音视频
        self.__download()
        # 发送完成信号
        global_signal.TaskStepDone.emit(True)

    # 获取bv和cid
    def __get_cid(self):
        video_info_api = "https://api.bilibili.com/x/web-interface/view"
        pattern = re.compile(r"(BV.*)/")
        self.bv = pattern.findall(self.base_url)[0]

        r = requests.get(url=video_info_api,
                         params={"bvid": self.bv},
                         headers=self.headers)
        self.cid = jsonpath.jsonpath(r.json(), "$..cid")[0]
        self.title = jsonpath.jsonpath(r.json(), "$..data.title")[0]
        # 发送完成信号
        global_signal.TaskStepDone.emit(True)

    # 获取音视频下载地址
    def __get_url(self):
        play_url = "https://api.bilibili.com/x/player/wbi/playurl"

        r = requests.get(url=play_url,
                         params={
                             "bvid": self.bv,
                             "cid": self.cid,
                             "qn": self.qn,  # 清晰度
                             "fnver": 0,
                             "fnval": 4048,
                             "fourk": 1
                         },
                         headers=self.headers,
                         cookies=self.cookies)

        self.video_url = jsonpath.jsonpath(r.json(), "$..video[0].baseUrl")[0]
        self.audio_url = jsonpath.jsonpath(r.json(), "$..audio[0].baseUrl")[0]
        # 发送完成信号
        global_signal.TaskStepDone.emit(True)

    # 下载音视频
    def __download(self):
        # 音视频文件名
        video_f = f"{random.randint(0, 9)}-{time.time()}-video.{read_config().get('video_format')}"
        audio_f = f"{time.time()}-{self.bv}-audio.{read_config().get('audio_format')}"
        output_f = f"{time.time()}-{self.bv}-output.{read_config().get('video_format')}"
        if self.flag is False:
            video = requests.get(url=self.video_url,
                                 headers=self.headers)
            audio = requests.get(url=self.audio_url,
                                 headers=self.headers)

            with open(f"temp/{video_f}", "wb") as v:
                v.write(video.content)

            with open(f"temp/{audio_f}", "wb") as a:
                a.write(audio.content)

            # 组合音视频
            subprocess.run([
                "ffmpeg/ffmpeg-6.1.1-essentials_build/bin/ffmpeg.exe", "-i", f"temp/{video_f}", "-i", f"temp/{audio_f}",
                "-map", "0:v:0", "-map", "1:a:0",
                f"video/{output_f}", "-y"
            ])
            # 清理缓存文件
            os.remove(f"temp/{video_f}")
            os.remove(f"temp/{audio_f}")
        else:
            audio = requests.get(url=self.audio_url,
                                 headers=self.headers)

            with open(f"audio/{audio_f}", "wb") as a:
                a.write(audio.content)
