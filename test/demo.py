import re
import subprocess

import requests
import jsonpath


# 获取cid
def get_cid(base_url):
    video_info_api = "https://api.bilibili.com/x/web-interface/view"
    pattern = re.compile(r"(BV.*)/")
    bv = pattern.findall(base_url)[0]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
        "Referer": base_url
    }
    r = requests.get(url=video_info_api,
                     params={"bvid": bv},
                     headers=headers)
    cid = jsonpath.jsonpath(r.json(), "$..cid")[0]
    return cid, bv


# 获取视频和音频下载地址
def get_url(base_url, bv, cid, cookies):
    play_url = "https://api.bilibili.com/x/player/wbi/playurl"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
        "Referer": base_url
    }
    r = requests.get(url=play_url,
                     params={
                         "bvid": bv,
                         "cid": cid,
                         "qn": 80,
                         "fnver": 0,
                         "fnval": 4048,
                         "fourk": 1
                     },
                     headers=headers,
                     cookies=cookies)
    video_url = jsonpath.jsonpath(r.json(), "$..video[0].baseUrl")[0]
    audio_url = jsonpath.jsonpath(r.json(), "$..audio[0].baseUrl")[0]

    return video_url, audio_url


# 下载音视频
def download(base_url, video_url, audio_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
        "Referer": base_url
    }
    video = requests.get(url=video_url,
                         headers=headers)
    audio = requests.get(url=audio_url,
                         headers=headers)

    with open("video.mp4", "wb") as v:
        v.write(video.content)

    with open("audio.mp3", "wb") as a:
        a.write(audio.content)


# 将音视频组合，生成完整视频
def generate_video():
    subprocess.run([
        "../ffmpeg/ffmpeg-6.1.1-essentials_build/bin/ffmpeg.exe", "-i", "video.mp4", "-i", "audio.mp3",
        "-map", "0:v:0", "-map", "1:a:0",
        "output.mp4", "-y"
    ])


# 程序入口
def main():
    cookie_str = ""
    cookies = {temp[:temp.find("=")]: temp[temp.find("=") + 1:] for temp in cookie_str.split("; ")}
    base_url = ""
    cid, bv = get_cid(base_url)
    video_url, audio_url = get_url(base_url, bv, cid, cookies)
    download(base_url, video_url, audio_url)
    generate_video()


if __name__ == "__main__":
    main()
