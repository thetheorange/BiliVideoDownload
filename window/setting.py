"""
Des 初始化设置窗口，绑定信号，处理任务队列
@Author thetheOrange
Time 2024/2/19
"""
import re
import sys
from datetime import datetime

import jsonpath
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QWidget, QPushButton, QComboBox, QApplication, QCheckBox, QProgressBar, QListWidget, \
    QLineEdit, QListWidgetItem, QMessageBox, QGraphicsDropShadowEffect
from PyQt5.uic import loadUi

from core.config import read_config
from core.global_signal import global_signal
from logger.Logger import app_logger


class settingWindow(QWidget):

    def __init__(self):
        super().__init__()
        loadUi("template/ui/setting.ui", self)
        # 读取配置文件
        self.config = read_config()
        login_status = self.config.get("login_status")
        if login_status == 1:
            self.setWindowTitle("设置窗口-用户已登录")
        else:
            self.setWindowTitle("设置窗口-用户未登录")
        # 设置图标
        self.setWindowIcon(QIcon("template/images/cat.png"))
        # 设置窗口边缘阴影
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setColor(QColor(0, 0, 0, 150))
        self.shadow.setOffset(0, 0)

        # 获取输入框
        self.input_url = self.findChild(QLineEdit, "videoUrl")
        # 获取任务队列视图并创建任务列表
        self.task_view = self.findChild(QListWidget, "taskWidget")
        self.task_list = []
        # ------------------登录设置------------------
        # 登录按钮
        self.login_btn = self.findChild(QPushButton, "loginBtn")
        # 登出按钮
        self.login_out_btn = self.findChild(QPushButton, "outBtn")
        # ------------------下载设置------------------
        # 视频格式
        self.video_format = self.findChild(QComboBox, "videoFormat")
        # 清晰度
        self.video_definition = self.findChild(QComboBox, "definition")
        # 加入队列按钮
        self.push_btn = self.findChild(QPushButton, "pushBtn")
        # 一键下载按钮
        self.download_btn = self.findChild(QPushButton, "downloadBtn")
        # 只下载音频选项
        self.only_audio_btn = self.findChild(QCheckBox, "onlyAudioBtn")
        # 音频格式
        self.audio_format = self.findChild(QComboBox, "audioFormat")
        # ------------------任务队列------------------
        # 删除按钮
        self.delete_task_btn = self.findChild(QPushButton, "deleteTask")
        # 提升按钮
        self.up_task_btn = self.findChild(QPushButton, "upTask")
        # 下降按钮
        self.down_task_btn = self.findChild(QPushButton, "downTask")
        # ------------------进度跟踪------------------
        # 进度条
        self.progress_bar = self.findChild(QProgressBar, "progressBar")

        # 控件列表
        self.controls_list = [
            self.input_url, self.task_view,
            self.login_btn, self.login_out_btn,
            self.video_format, self.video_definition,
            self.push_btn, self.download_btn,
            self.only_audio_btn, self.audio_format,
            self.delete_task_btn, self.up_task_btn,
            self.down_task_btn
        ]

        # 绑定信号与槽
        global_signal.TaskOperation.connect(self.__handle_task)
        global_signal.LoginStatus.connect(self.__check_login)
        global_signal.DownloadStatus.connect(self.__check_download_status)

        self.init_ui()
        self.__default_value()

    # 初始化ui
    def init_ui(self):
        # 改变光标显示模式
        for i in self.controls_list:
            i.setCursor(Qt.PointingHandCursor)

        self.task_view.setCursor(Qt.ArrowCursor)
        self.input_url.setCursor(Qt.IBeamCursor)

        # ------------------登录设置------------------
        # 登录按钮
        self.login_btn.clicked.connect(lambda: global_signal.Operation.emit("login"))
        # 登出按钮
        self.login_out_btn.clicked.connect(lambda: global_signal.Operation.emit("loginOut"))
        # ------------------下载设置------------------
        # 视频格式
        self.video_format.currentIndexChanged.connect(
            lambda: global_signal.Format.emit(self.video_format.currentText(), 1))
        # 清晰度
        self.video_definition.currentIndexChanged.connect(
            lambda: global_signal.Definition.emit(self.video_definition.currentText())
        )
        # 加入队列按钮
        self.push_btn.clicked.connect(lambda: global_signal.TaskOperation.emit("push"))
        # 一键下载按钮
        self.download_btn.clicked.connect(lambda: global_signal.Operation.emit("download"))
        # 只下载音频选项
        self.only_audio_btn.toggled.connect(lambda: global_signal.AudioOnly.emit(self.only_audio_btn.isChecked()))
        # 音频格式
        self.audio_format.currentIndexChanged.connect(
            lambda: global_signal.Format.emit(self.audio_format.currentText(), 2))
        # ------------------任务队列------------------
        # 删除按钮
        self.delete_task_btn.clicked.connect(lambda: global_signal.TaskOperation.emit("deleteTask"))
        # 提升按钮
        self.up_task_btn.clicked.connect(lambda: global_signal.TaskOperation.emit("upTask"))
        # 下降按钮
        self.down_task_btn.clicked.connect(lambda: global_signal.TaskOperation.emit("downTask"))
        # ------------------进度跟踪------------------
        self.progress_bar.setValue(0)
        # 文字居中
        self.progress_bar.setAlignment(Qt.AlignCenter)
        # 设置进度条文字格式
        self.progress_bar.setFormat('waiting...  %p%'.format(self.progress_bar.value() - self.progress_bar.minimum()))

    # 设置默认值
    def __default_value(self):
        video_format = self.config.get("video_format")
        audio_format = self.config.get("audio_format")
        qn = self.config.get("qn")

        video_format_list = ["mp4", "msa"]
        audio_format_list = ["mp3", "aac", "msa"]
        qn_list = [16, 32, 64, 80]

        self.video_format.setCurrentIndex(video_format_list.index(video_format))
        self.audio_format.setCurrentIndex(audio_format_list.index(audio_format))
        self.video_definition.setCurrentIndex(qn_list.index(qn))

    # 处理任务队列操作
    def __handle_task(self, op):
        # 加入退出队列
        if op == "push":
            self.__push_task()
        if op == "deleteTask":
            self.__delete_task()
        # 提升下降任务
        if op == "upTask":
            self.__up_task()
        if op == "downTask":
            self.__down_task()
        # 渲染视图
        self.__draw_view()

    # 加入任务列表
    def __push_task(self):
        url = self.input_url.text()
        # 任务队列最大上限
        max_length = 20
        # 检测URL的合法性
        pattern = re.compile("https://www.bilibili.com/video/BV.*/")
        if pattern.match(url):
            if len(self.task_list) >= max_length:
                self.__tip_window(info="任务数已达上限！",
                                  title="full list")
            else:
                self.task_list.append(url)
        else:
            app_logger.info("[task] not a legal url")
            self.__tip_window(info="不是一个合法的地址！",
                              title="error url")
        # 清空输入框
        self.input_url.setText("")

    # 删除任务（退出队列）
    def __delete_task(self):
        current_row = self.task_view.currentRow()
        if current_row is not None:
            # 移除列表中的项目
            self.task_list.pop(current_row)

    # 提升任务优先级
    def __up_task(self):
        current_row = self.task_view.currentRow()
        # 非第一份项目则交换顺序
        if current_row != 0:
            temp_item = self.task_list[current_row - 1]
            self.task_list[current_row - 1] = self.task_list[current_row]
            self.task_list[current_row] = temp_item

    # 下降任务优先级
    def __down_task(self):
        current_row = self.task_view.currentRow()
        # 非最后一份项目则交换顺序
        if current_row != len(self.task_list) - 1:
            temp_item = self.task_list[current_row + 1]
            self.task_list[current_row + 1] = self.task_list[current_row]
            self.task_list[current_row] = temp_item

    # 渲染任务视图（本质上将列表中的数据输出到视图上）
    def __draw_view(self):
        # 提取bv号
        bv_filter = re.compile("https://www.bilibili.com/video/(BV.*?)/")

        if len(self.task_list) >= 0:
            # 初始化视图
            self.task_view.clear()
            # 更新视图
            for index, i in enumerate(self.task_list, start=1):
                i = bv_filter.match(i).group(1)
                temp_item = QListWidgetItem(f"{index} {i} {datetime.now().strftime('%Y-%m-%d')}")
                self.task_view.addItem(temp_item)

    # 检测用户是否登录，并修改窗口标题
    def __check_login(self, status):
        if status == 1:
            self.setWindowTitle("设置窗口-用户已登录")
        if status == 0:
            self.setWindowTitle("设置窗口-用户未登录")

    # 检测是否处于下载状态
    def __check_download_status(self, status):
        if status:
            self.__tip_window(info="开始下载,请耐心等待...",
                              title="start download")

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


# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = settingWindow()
    window.show()
    app.exec()
