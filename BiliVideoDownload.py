"""
Des 程序主文件，联系前端ui和后端爬虫数据，如程序无法运行，请修改config。jsonp
@Author thetheOrange
Time 2024/2/21
"""
import json
import os
import sys
import threading

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox

from core.config import modify_config, read_config
from core.global_signal import global_signal
from core.videoSocket import videoSocket
from logger.Logger import app_logger
from window.login import loginWindow
from window.setting import settingWindow
from window.tray import TrayMenu


# 等待任务的输入
class handleTask(threading.Thread):

    def __init__(self, q, only_audio):
        super().__init__()
        self.q = q
        self.only_audio = only_audio

    def run(self):
        while True:
            if len(self.q) > 0:
                for url in self.q:
                    download = videoSocket(
                        base_url=url,
                        qn=read_config().get("qn"),
                        flag=self.only_audio,
                        cookies=json.loads(read_config().get("cookies"))
                    )
                    download.run()
                break
            else:
                break


class App(QWidget):

    def __init__(self, sys_arg):
        super().__init__()

        # 获取项目对象
        self.__app = QApplication(sys_arg)
        self.__app.setQuitOnLastWindowClosed(False)

        # 加载登录和设置窗口
        self.login_w = loginWindow()
        self.setting_w = settingWindow()
        # 获取托盘
        self.tray = TrayMenu()
        # 获取设置窗口控件
        self.controls = self.setting_w.controls_list

        # 初始化进度条
        self.setting_w.progress_bar.setValue(0)
        self.setting_w.progress_bar.setRange(0, 0)

        self.done_task_count = 0

        # 绑定信号与槽
        global_signal.Operation.connect(self.__handle_op)
        global_signal.Format.connect(self.__handle_format)
        global_signal.Definition.connect(self.__handle_definition)
        global_signal.AudioOnly.connect(self.__handle_audio_only)
        global_signal.TaskStepDone.connect(self.__check_task_done)

        # 是否只下载音频标志位
        self.only_audio = False

    # 处理操作信号
    def __handle_op(self, op):
        # 下载
        if op == "download":
            for c in self.controls:
                c.setEnabled(False)

            # 初始化任务计数器
            self.done_task_count = 0
            # 初始化进度条
            self.setting_w.progress_bar.setValue(0)
            self.setting_w.progress_bar.setRange(0, len(self.setting_w.task_list) * 3)

            global_signal.DownloadStatus.emit(True)
            # 创建子线程，等待，处理任务
            self.handle_t = handleTask(self.setting_w.task_list, self.only_audio)
            self.handle_t.start()

        # 打开设置窗口
        if op == "SettingWindow":
            self.setting_w.show()

        # 退出整个程序
        if op == "Exit":
            print("quit")
            self.__exit_app()

    # 处理文件格式信号
    @staticmethod
    def __handle_format(file_format, file_type):
        # 1为视频 2为音频
        if file_type == 1:
            modify_config(key="video_format",
                          value=file_format)
        if file_type == 2:
            modify_config(key="audio_format",
                          value=file_format)

    # 处理视频清晰度信号
    def __handle_definition(self, qn):
        if qn == "360p":
            self.qn = 16
        if qn == "480p":
            self.qn = 32
        if qn == "720p":
            self.qn = 64
        if qn == "1080p":
            self.qn = 80
        modify_config(key="qn",
                      value=self.qn)

    # 处理是否只下载音频信号
    def __handle_audio_only(self, flag):
        if flag:
            self.only_audio = True
        elif flag is False:
            self.only_audio = False

    # 记录已下载的任务数,同时更新进度条
    def __check_task_done(self, flag):
        if flag:
            self.done_task_count += 1
            global_signal.DownloadStatus.emit(False)

            # 更新进度条
            self.setting_w.progress_bar.setValue(self.done_task_count)

            if self.done_task_count == len(self.setting_w.task_list) * 3:
                self.__tip_window(info="下载完成！",
                                  title="download done")
                # 初始化进度条
                self.setting_w.progress_bar.setValue(0)
                self.setting_w.progress_bar.setRange(0, 0)
                for c in self.controls:
                    c.setEnabled(True)

    # 退出程序
    def __exit_app(self):
        try:
            self.setting_w.close()
            self.tray.quit()
            raise KeyboardInterrupt
        except Exception as e:
            app_logger.error(f"[exit] exit error {e}")

    # 提示用户窗口
    @staticmethod
    def __tip_window(info, title):
        success_message = QMessageBox()
        success_message.setIcon(QMessageBox.Information)
        success_message.setText(info)
        success_message.setWindowTitle(title)
        success_message.setWindowIcon(QIcon("template/images/cat.png"))
        success_message.exec_()


# 测试代码
if __name__ == "__main__":
    # 设置实例锁，防止程序多开
    def app_lock(func):
        # 计数器，记录程序运行次数
        ctn = 0

        def lock():
            nonlocal ctn
            ctn = 1
            pid = os.getpid()
            if ctn == 1:
                func()
            else:
                cmd = f"taskkill /pid {pid} /f"
                os.system(cmd)
                app_logger.info("[exit] extra process exit!")
        return lock


    # 程序入口函数
    @app_lock
    def main():
        app = QApplication(sys.argv)
        window = App(sys_arg=sys.argv)
        window.setting_w.show()
        app.exec()


    try:
        main()
    except Exception as e:
        app_logger.error(f"[exit] exit error {e}")
