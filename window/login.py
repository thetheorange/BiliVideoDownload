"""
Des 初始化登录界面
@Author thetheOrange
Time 2024/2/21
"""
import json
import threading
import time

import jsonpath
import qrcode
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QTextBrowser, QMessageBox
from PyQt5.uic import loadUi

from core.config import modify_config
from core.global_signal import global_signal
from logger.Logger import app_logger


# 检测二维码是否过期已经是否登录成功
class checkQRCode(threading.Thread):

    def __init__(self, window, token):
        super().__init__()
        self.w = window
        self.token = token
        self.check_url = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
            "Referer": "https://www.bilibili.com/"
        }

    def run(self):
        ctn = 0
        while ctn < 180:
            cookies, code = self.get_code()
            if code == 0:
                app_logger.info("[login] QRCode Scan success! login!")
                self.w.close()
                # 获取cookie，将其写入配置文件
                modify_config(key="cookies",
                              value=json.dumps(cookies))
                # 提示登录成功
                global_signal.LoginStatus.emit(1)
                break
            elif code == 86090:
                app_logger.info("[login] QRCode has been scan but not verify")
            elif code == 86101:
                app_logger.info("[login] QRCode has not been scan")
            elif code == 86038:
                app_logger.info("[login] QRCode out of time")
                # 提示二维码失效
                self.w.setWindowTitle("二维码已失效,请重新登录")
                global_signal.LoginStatus.emit(-1)
                break

            ctn += 1
            time.sleep(1)

    # 获取状态码
    def get_code(self):
        r = requests.get(url=self.check_url,
                         params={"qrcode_key": self.token},
                         headers=self.headers)
        # 获取状态码和cookie
        code = jsonpath.jsonpath(r.json(), "$..data.code")[0]
        return r.cookies.get_dict(), code


class loginWindow(QWidget):

    def __init__(self):
        super().__init__()
        loadUi("template/ui/login.ui", self)
        # 设置标题、图标
        self.setWindowTitle("扫码登录")
        self.setWindowIcon(QIcon("template/images/cat.png"))
        self.container = self.findChild(QTextBrowser, "textBrowser")

        # 标志位，防止重复请求
        self.flag = True

        # 绑定操作信号
        global_signal.Operation.connect(self.__handle_login)
        global_signal.LoginStatus.connect(self.__login_status)

    # 处理登录登出操作
    def __handle_login(self, op):
        if not self.isVisible():
            self.flag = True
        if op == "login":
            # 防止重复发送请求
            self.show()
            if self.isVisible():
                if self.flag:
                    self.__login()
                self.flag = False

        if op == "loginOut":
            self.__login_out()

    # 生成登录用的二维码，并检测用户是否登录
    def __login(self):
        url = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate?source=main-fe-header"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
            "Referer": "https://www.bilibili.com/"
        }
        data = requests.get(url=url,
                            headers=headers)
        data = data.json()
        # 判断是否成功生成二维码
        if data.get("code") == 0:
            # 获取二维码URL和token
            self.code_url = jsonpath.jsonpath(data, "$.data.url")[0]
            self.code_token = jsonpath.jsonpath(data, "$.data.qrcode_key")[0]

            app_logger.info("[login] get QRCode success!")
            # 生成二维码
            qr = qrcode.QRCode(
                version=5,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4
            )
            qr.add_data(self.code_url)
            qr.make(fit=True)
            # 保存二维码图片
            code_img = qr.make_image(fill_color="black")
            code_img.save("template/images/code.jpg")

            # 将二维码图片显示在容器里
            self.container.setHtml('<img src="template/images/code.jpg">')
            # 检测二维码状态
            check_t = checkQRCode(self, self.code_token)
            check_t.daemon = True
            check_t.start()

    # 判断用户登录状态
    def __login_status(self, value):
        # 登录成功
        if value == 1:
            self.__tip_window(info="登录成功",
                              title="login")
            modify_config(key="login_status",
                          value=1)
        # 登出成功
        if value == 0:
            self.__tip_window(info="登出成功！",
                              title="login out")
            modify_config(key="login_status",
                          value=0)
        # 二维码失效
        if value == -1:
            self.__tip_window(info="二维码过期",
                              title="out date")

    # 用户登出, 清除cookie
    @staticmethod
    def __login_out():
        modify_config(key="cookies",
                      value="{}")
        # 提示登出成功
        global_signal.LoginStatus.emit(0)

    # 提示用户窗口
    @staticmethod
    def __tip_window(info, title):
        success_message = QMessageBox()
        success_message.setWindowFlags(Qt.WindowStaysOnTopHint)
        success_message.setIcon(QMessageBox.Information)
        success_message.setText(info)
        success_message.setWindowTitle(title)
        success_message.setWindowIcon(QIcon("template/images/cat.png"))
        success_message.exec_()
