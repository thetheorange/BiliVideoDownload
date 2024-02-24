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
    cookie_str = "nostalgia_conf=-1; _uuid=A6CD253D-10958-AC510-C662-A62BBF9752C181733infoc; buvid_fp=e539f0e67670e66a942f189f404e5f10; buvid3=5FA73BC1-383F-E18A-B539-3D015E64BE4284112infoc; buvid4=E973217A-57A6-EF60-9238-7FB72CA817C884170-023060617-L5Q1kH26y1aAQnTJXzhtuA%3D%3D; b_nut=1702607453; CURRENT_FNVAL=4048; rpdid=|(kmJYl)m|YY0J'uY)Y|RkY)m; i-wanna-go-back=-1; b_ut=5; FEED_LIVE_VERSION=V8; header_theme_version=CLOSE; home_feed_column=5; browser_resolution=1536-703; bp_video_offset_1780794180=899064035198107649; CURRENT_QUALITY=80; fingerprint=e539f0e67670e66a942f189f404e5f10; buvid_fp_plain=undefined; hit-new-style-dyn=1; hit-dyn-v2=1; LIVE_BUVID=AUTO2316861462458256; PVID=1; CURRENT_BLACKGAP=0; is-2022-channel=1; enable_web_push=DISABLE; SESSDATA=c5608d91%2C1723618810%2C71f6b%2A22CjCMOrXaiFO45bZdVrb9g7gLfF6OxsybEm13jJVTVH_29CsQ4s9sRdNBhWzRfUzajdoSVi03MFVNbGlWRjVqYlgxNTFQdENiZGdHOFRlMndPWEFfWjQtdllBR3RsUllnOFc1YngzbXdra20yenBIWVNzZFJRMWZZeU82R0RIR3poQXpFdEF0Y1N3IIEC; bili_jct=9f82a70d8335600f3fbae7fe05cbaf45; DedeUserID=1780794180; DedeUserID__ckMd5=6adafff5be6d2849; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDgzMjYwMTcsImlhdCI6MTcwODA2Njc1NywicGx0IjotMX0.x6iVJLxXskyhK8-4-CqUjZ5WU6zEUxtvKgwrmRLEmxk; bili_ticket_expires=1708325957; b_lsid=8423DB3A_18DB7623DBB; sid=4yqn4426"
    cookies = {temp[:temp.find("=")]: temp[temp.find("=") + 1:] for temp in cookie_str.split("; ")}
    base_url = "https://www.bilibili.com/video/BV1E4411G7m5/?spm_id_from=333.337.search-card.all.click&vd_source=1975c316afe56823772171b01ff0e77f"
    cid, bv = get_cid(base_url)
    video_url, audio_url = get_url(base_url, bv, cid, cookies)
    download(base_url, video_url, audio_url)
    generate_video()


if __name__ == "__main__":
    main()
