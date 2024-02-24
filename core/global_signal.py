"""
Des 全局信号
@Author thetheOrange
Time 2024/2/19
"""
# 自定义信号
from PyQt5.QtCore import QObject, pyqtSignal


class Signals(QObject):
    # 操作类型信号
    Operation = pyqtSignal(str)
    # 用户登录状态信号
    LoginStatus = pyqtSignal(int)
    # 文件格式信号 1为视频 2为音频
    Format = pyqtSignal(str, int)
    # 视频清晰度信号
    Definition = pyqtSignal(str)
    # 是否只下载音频
    AudioOnly = pyqtSignal(bool)
    # 对任务队列的操作信号
    TaskOperation = pyqtSignal(str)
    # 线程任务完成信号
    TaskStepDone = pyqtSignal(bool)
    # 已完成的任务数信号
    TaskDoneCount = pyqtSignal(int)
    # 程序下载状态信号
    DownloadStatus = pyqtSignal(bool)


# 全局信号
global_signal = Signals()
