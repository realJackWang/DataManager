# encoding = utf-8
# =====================================================
#   Copyright (C) 2019 All rights reserved.
#
#   filename : update.py
#   version  : 0.1
#   author   : Jack Wang / 544907049@qq.com
#   date     : 2019-12-06 下午 6:44
#   desc     : 
# =====================================================
'https://github.com/skycity233/DataManager/releases/download/v1.1.0/datamanager.exe'
import os
import sys
import time

import requests
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QMessageBox
import psutil
from ui import update_ui
import win32api
from shutil import copy


def exe_running():
    for proc in psutil.process_iter():
        if proc.name() == '会员管理系统.exe':
            return True
    return False


def MyQMessageBox(title, text, button1, button2=None):
    messageBox = QMessageBox()
    messageBox.setWindowTitle(title)
    messageBox.setText(text)
    messageBox.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    if button2:
        messageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        buttonY = messageBox.button(QMessageBox.Yes)
        buttonY.setText(button1)
        buttonN = messageBox.button(QMessageBox.No)
        buttonN.setText(button2)
    else:
        messageBox.setStandardButtons(QMessageBox.Yes)
        buttonY = messageBox.button(QMessageBox.Yes)
        buttonY.setText(button1)

    messageBox.exec_()
    if messageBox.clickedButton() == buttonY:
        return 16384
    else:
        return 0


class ConsumeWindow(QDialog, update_ui.Ui_Form):
    def __init__(self, version='检测失败'):
        QDialog.__init__(self)
        self.setupUi(self)
        self.toolButton.clicked.connect(self.close)
        self.toolButton_2.clicked.connect(self.submit)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        api = 'https://api.github.com/repos/skycity233/DataManager/releases'
        all_page = requests.get(api).json()  # 获取api页面(此时是以json返回的页面)并将该页面转换成字典形式（key-value的存储方式）
        cur_update = all_page[0]['tag_name']

        self.label.setText('当前版本：' + version)
        self.label_2.setText('最新版本：' + cur_update)

    def submit(self):
        if self.toolButton_2.text() == '安装':
            self.callback(101)
        else:
            self.toolButton_2.setEnabled(False)
            self.toolButton.setEnabled(False)
            self.toolButton_2.setText('正在下载')
            self.thread = Example()
            self.thread.signal.connect(self.callback)
            self.thread.start()  # 启动线程

        # x = "会员管理系统.exe"
        # win32api.ShellExecute(0, 'open', x, '', '', 1)

    def callback(self, p):
        if p <= 100:
            self.progressBar.setValue(p)
        if p > 100:
            self.progressBar.setValue(100)
            self.toolButton_2.setText('安装')
            self.toolButton.setEnabled(True)
            self.toolButton_2.setEnabled(True)
            reply = MyQMessageBox('下载完成', '是否现在进行安装？', '是', '否')
            if reply == 16384:
                while exe_running():
                    reply = MyQMessageBox('温馨提示', '检测到 会员管理系统 仍在运行，请手动关闭', '已关闭，继续安装', '取消安装')
                    if reply == 0:
                        return
                try:
                    copy('./download/会员管理系统.exe', './会员管理系统.exe')
                    os.remove('./download/会员管理系统.exe')
                    reply = MyQMessageBox('温馨提示', '更新成功！', '打开会员管理系统', '退出')
                    if reply == 0:
                        self.close()
                    else:
                        x = "会员管理系统.exe"
                        win32api.ShellExecute(0, 'open', x, '', '', 1)
                        self.close()

                except:
                    MyQMessageBox('温馨提示', '更新失败，请反馈', '关闭')


class Example(QtCore.QThread):
    signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()

    def run(self):
        if not os.path.exists('./download'):
            os.mkdir('./download')
        api = 'https://api.github.com/repos/skycity233/DataManager/releases'
        all_page = requests.get(api).json()  # 获取api页面(此时是以json返回的页面)并将该页面转换成字典形式（key-value的存储方式）
        cur_update = all_page[0]['tag_name']

        url = "https://github.com/skycity233/DataManager/releases/download/" + cur_update + "/default.exe"
        path = "./download/会员管理系统.exe"

        headers = {'Proxy-Connection': 'keep-alive'}
        r = requests.get(url, stream=True, headers=headers)
        length = float(r.headers['content-length'])
        f = open(path, 'wb')
        count = 0
        time1 = time.time()
        for chunk in r.iter_content(chunk_size=512):
            if chunk:
                f.write(chunk)
                count += len(chunk)
                if time.time() - time1 > 2:
                    p = count / length * 100
                    self.signal.emit(int(p))
                    time1 = time.time()
        f.close()
        self.signal.emit(101)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    try:
        consumeWindow = ConsumeWindow(sys.argv[1])
    except:
        consumeWindow = ConsumeWindow()
    consumeWindow.show()
    sys.exit(app.exec_())
