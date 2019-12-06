# encoding = utf-8
# =====================================================
#   Copyright (C) 2019 All rights reserved.
#
#   filename : main.py
#   version  : 0.1
#   author   : Jack Wang / 544907049@qq.com
#   date     : 2019/11/6 下午 11:05
#   desc     : 
# =====================================================

import sqlite3

from PyQt5.QtGui import QFont, QCloseEvent, QBrush, QColor
from PyQt5 import QtGui

import mysql
import bills

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
from PyQt5.QtWidgets import *

from ui import consume_ui, update_log_ui, add_person_ui, main_ui

import os
import time
import webbrowser
import requests
import images_rc

COLUMN = 6
CURRENT_VERSION = 'v1.5.1'

DATAPAGES = 0
BILLPAGES = 0

DATA_PER_PAGE = 1000
BILL_PER_PAGE = 1000


class MainWindow(QtWidgets.QMainWindow, main_ui.Ui_MainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        if not os.path.exists('data.db'):
            mysql.init_database()
        self.conn = sqlite3.connect('data.db')
        self.c = self.conn.cursor()

        self.sort_enable = False
        self.sort_enable_2 = True
        self.is_search = False
        self.is_card_search = False

        self.current_data_index = 0
        self.current_bill_index = 0

        self.load_initial_data()
        self.load_initial_bill()

        self.init_sign()
        self.init_view()

    def init_sign(self):

        self.toolButton_3.clicked.connect(self.add_person)
        self.toolButton_4.clicked.connect(self.add_more_person)
        self.pushButton_5.clicked.connect(self.search_data)
        self.toolButton_2.clicked.connect(self.invest)
        self.pushButton_6.clicked.connect(self.load_initial_data)
        self.toolButton.clicked.connect(self.consume)
        self.toolButton_5.clicked.connect(self.del_person)
        self.tabWidget.currentChanged.connect(self.change_tab)
        self.tableWidget_2.horizontalHeader().sectionClicked.connect(self.sort_row)
        self.tableWidget.horizontalHeader().sectionClicked.connect(self.sort_row_2)
        self.action1.triggered.connect(self.update_log)
        self.action_2.triggered.connect(self.about)
        self.action_3.triggered.connect(self.update_me)
        self.lineEdit.returnPressed.connect(self.search_data_by_card)
        self.action_4.triggered.connect(lambda: webbrowser.open('https://skycity233.github.io/DataManager/'))

        self.toolButton_6.clicked.connect(self.next_page_data)
        self.toolButton_7.clicked.connect(self.pre_page_data)
        self.toolButton_8.clicked.connect(self.next_page_bill)
        self.toolButton_9.clicked.connect(self.pre_page_bill)

        self.pushButton.clicked.connect(self.search_data_by_card)

    def init_view(self):
        # self.setWindowOpacity(0.9)  # 设置窗口透明度
        # self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        # self.setWindowFlag(QtCore.Qt.FramelessWindowHint)

        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)  # 允许右键产生子菜单
        self.tableWidget.customContextMenuRequested.connect(self.generate_menu)  # 右键菜单 消费设置
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置只能一行
        self.tableWidget.verticalHeader().setVisible(False)  # 不显示行号
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        self.tableWidget.cellDoubleClicked.connect(self.double_click_search)  # 切换界面)

        self.tableWidget_2.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置只能一行
        self.tableWidget_2.verticalHeader().setVisible(False)  # 不显示行号
        self.tableWidget_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget_2.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tableWidget_2.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        self.toolButton_7.setEnabled(False)
        if DATAPAGES <= 1:
            self.toolButton_6.setEnabled(False)
        self.label.setText(str(1) + '/' + str(DATAPAGES or 1))

        self.toolButton_9.setEnabled(False)
        if BILLPAGES <= 1:
            self.toolButton_8.setEnabled(False)
        self.label_2.setText(str(1) + '/' + str(BILLPAGES or 1))

    def double_click_search(self, i, j):
        if self.search_bill(id=self.tableWidget.item(i, 0).text()):
            self.tabWidget.setCurrentIndex(1)

    def closeEvent(self, QCloseEvent):
        reply = MyQMessageBox('温馨提示', '是否要退出应用程序？', '是', '否')
        if reply == 16384:
            self.c.close()
            self.conn.close()
            QCloseEvent.accept()
        else:
            QCloseEvent.ignore()

    def keyPressEvent(self, evt):
        if evt.key() == 16777268:  # F5
            self.pushButton_6.click()

    def next_page_data(self):
        if self.current_data_index + 1 < DATAPAGES:
            self.current_data_index += 1
            self.toolButton_7.setEnabled(True)
            self.label.setText(str(self.current_data_index + 1) + '/' + str(DATAPAGES))
            if self.current_data_index == DATAPAGES - 1:
                self.toolButton_6.setEnabled(False)
            self.load_initial_data()
            self.tableWidget.verticalScrollBar().setValue(0)

    def pre_page_data(self):
        if self.current_data_index - 1 >= 0:
            self.current_data_index -= 1
            self.toolButton_6.setEnabled(True)
            self.label.setText(str(self.current_data_index + 1) + '/' + str(DATAPAGES))
            if self.current_data_index == 0:
                self.toolButton_7.setEnabled(False)

            self.load_initial_data()
            self.tableWidget.verticalScrollBar().setValue(0)

    def next_page_bill(self):
        if self.current_bill_index + 1 < BILLPAGES:
            self.current_bill_index += 1
            self.toolButton_9.setEnabled(True)
            self.label_2.setText(str(self.current_bill_index + 1) + '/' + str(BILLPAGES))
            if self.current_bill_index == BILLPAGES - 1:
                self.toolButton_8.setEnabled(False)
            self.load_initial_bill()
            self.tableWidget.verticalScrollBar().setValue(0)

    def pre_page_bill(self):
        if self.current_bill_index - 1 >= 0:
            self.current_bill_index -= 1
            self.toolButton_8.setEnabled(True)
            self.label_2.setText(str(self.current_bill_index + 1) + '/' + str(BILLPAGES))
            if self.current_bill_index == 0:
                self.toolButton_9.setEnabled(False)

            self.load_initial_bill()
            self.tableWidget.verticalScrollBar().setValue(0)

    def check_page_data(self):
        self.c.execute('''SELECT * FROM user_tb ''')
        rows = self.c.fetchall()
        if len(rows) / DATA_PER_PAGE > 0:
            if len(rows) / DATA_PER_PAGE > int(len(rows) / DATA_PER_PAGE):
                length = int(len(rows) / DATA_PER_PAGE) + 1
            else:
                length = int(len(rows) / DATA_PER_PAGE)
            global DATAPAGES
            DATAPAGES = length

        if self.current_data_index >= DATAPAGES:
            self.current_data_index = DATAPAGES - 1

        if self.current_data_index >= DATAPAGES - 1:
            self.toolButton_6.setEnabled(False)
        else:
            self.toolButton_6.setEnabled(True)

        if self.current_data_index == 0:
            self.toolButton_7.setEnabled(False)
        if self.current_data_index > 0:
            self.toolButton_7.setEnabled(True)

        self.label.setText(str(self.current_data_index + 1) + '/' + str(DATAPAGES))

    def check_page_bill(self):
        self.c.execute('''SELECT * FROM bill_tb ''')
        rows = self.c.fetchall()
        if len(rows) / BILL_PER_PAGE > 0:
            if len(rows) / BILL_PER_PAGE > int(len(rows) / BILL_PER_PAGE):
                length = int(len(rows) / BILL_PER_PAGE) + 1
            else:
                length = int(len(rows) / BILL_PER_PAGE)
            global BILLPAGES
            BILLPAGES = length

        self.label_2.setText(str(self.current_bill_index + 1) + '/' + str(BILLPAGES))

        if self.current_bill_index >= BILLPAGES:
            self.current_bill_index = BILLPAGES - 1

        if self.current_bill_index >= BILLPAGES - 1:
            self.toolButton_8.setEnabled(False)
        else:
            self.toolButton_8.setEnabled(True)

        if self.current_bill_index == 0:
            self.toolButton_9.setEnabled(False)
        if self.current_bill_index > 0:
            self.toolButton_9.setEnabled(True)

        # self.tableWidget.verticalScrollBar().setValue(0)

    # def is_end(self, pos):
    #     if pos == self.tableWidget.verticalScrollBar().maximum():
    #         self.current_data_index += 1
    #         self.load_initial_data()
    #         self.tableWidget.verticalScrollBar().setValue(0)
    #         print('你已经到最低端了')

    def invest(self):
        index = self.tableWidget.currentRow()
        if index < 0:
            QMessageBox.information(self, "温馨提示", "请先选择充值的账户", QMessageBox.Yes)
            return
        value, ok = QInputDialog.getInt(self, "正在充值", "请输入充值金额:", 0, 0, 10000, 10)
        if ok:
            reply = MyQMessageBox("充值确认",
                                  "正在给 " + self.tableWidget.item(index, 1).text() + " 充值" + str(
                                      value) + '元，是否充值',
                                  '确认', '取消')
            if reply == 16384:
                person = mysql.query('user_tb', '_id', self.tableWidget.item(index, 0).text())
                balance = float(person[0][4]) + value
                mysql.update(self.tableWidget.item(index, 0).text(), 'balance', str(balance))
                QMessageBox.information(self, "温馨提示", "充值成功", QMessageBox.Yes)

                bills.bill_in(str(value), person[0][1], person[0][2], person[0][3], balance,
                              self.tableWidget.item(index, 0).text())
                if self.is_card_search:
                    self.search_data_by_card(str(person[0][3]))
                elif self.is_search:
                    self.search_data()
                else:
                    self.load_initial_data(self.tableWidget.verticalScrollBar().value())
                self.load_initial_bill()
                self.load_initial_bill()

    def consume(self):
        index = self.tableWidget.currentRow()
        if index < 0:
            messageBox = QMessageBox()
            messageBox.setWindowTitle('温馨提示')
            messageBox.setText('请先选择要消费的会员')
            messageBox.setStandardButtons(QMessageBox.Yes)
            buttonY = messageBox.button(QMessageBox.Yes)
            buttonY.setText('好的')
            messageBox.exec_()
            return
        value, ok = QInputDialog.getDouble(self, "正在消费", "请输入消费金额:", 0, 0, 1000000, 2)

        if ok:
            reply = MyQMessageBox("消费确认", "确认 " + self.tableWidget.item(index, 1).text() + " 消费了" + str(
                value) + '元?',
                                  '确认', '取消')

            if reply == 16384:
                person = mysql.query('user_tb', '_id', self.tableWidget.item(index, 0).text())
                balance = float(person[0][4]) - value
                if balance < 0:
                    QMessageBox.warning(self, "温馨提示", "余额不足，请充值")
                else:
                    mysql.update(self.tableWidget.item(index, 0).text(), 'balance', str(balance))
                    QMessageBox.information(self, "温馨提示", "消费成功", QMessageBox.Yes)

                    bills.bill_out(str(value), str(person[0][1]), str(person[0][2]), str(person[0][3]), balance,
                                   self.tableWidget.item(index, 0).text())

                    if self.is_card_search:
                        self.search_data_by_card(str(person[0][3]))
                    elif self.is_search:
                        self.search_data()
                    else:
                        self.load_initial_data(self.tableWidget.verticalScrollBar().value())
                    self.load_initial_bill()

    def add_person(self):
        max_card = mysql.max('bill_tb')[0][0] or 0
        AddWindow.lineEdit_2.setPlaceholderText('当前最高卡号：' + str(max_card) + '，推荐填' + str(int(max_card) + 1))
        AddWindow.lineEdit.setFocus()
        AddWindow.show()

    def add_more_person(self):
        max_card = mysql.max('bill_tb')[0][0] or 0
        AddMoreWindow.lineEdit_2.setPlaceholderText('当前最高卡号：' + str(max_card) + '，推荐填' + str(int(max_card) + 1))
        AddMoreWindow.show()

    def del_person(self):
        index = self.tableWidget.currentRow()
        if index < 0:
            QMessageBox.information(self, "温馨提示", "请先选择要删除的账户，可按Ctrl多选", QMessageBox.Yes)
            return
        items = self.tableWidget.selectedItems()
        reply = MyQMessageBox("提示", "确定删除已选中的会员？", '确认', '取消')
        if reply == 16384:
            for i in range(int((len(items) + 1) / COLUMN)):
                mysql.del_person(items[i * COLUMN].text())
                bills.person_out(str(float(items[i * COLUMN + 4].text())),
                                 items[i * COLUMN + 1].text(),
                                 items[i * COLUMN + 2].text(),
                                 items[i * COLUMN + 3].text(),
                                 0,
                                 items[i * COLUMN].text())
            MainWindow.check_page_data()
            MainWindow.load_initial_data()

    def search_data(self, card=None):
        if not card:
            line = self.lineEdit.text()
            if not line:
                QMessageBox.information(self, "温馨提示", "请输入姓名、手机号或卡号（支持模糊搜索）", QMessageBox.Yes)
                return

        if card:
            id = mysql.query('user_tb', 'card', card)
        else:
            id = mysql.like('user_tb', 'name', line) + mysql.like('user_tb', 'card', line)
            if len(line) >= 3:
                id += mysql.like('user_tb', 'phone', line)

        if not id:
            QMessageBox.information(self, "温馨提示", "未能找到对应的姓名、手机号或卡号", QMessageBox.Yes)
        else:
            for i in range(self.tableWidget.rowCount()):
                self.tableWidget.removeRow(0)

            for row in id:
                inx = id.index(row)
                self.tableWidget.insertRow(inx)
                for i in range(len(row)):
                    item = QTableWidgetItem()
                    if str(row[i]).isdigit:  # 使得数字排序能够正常的运行
                        item.setData(Qt.DisplayRole, row[i])
                    else:
                        item.setText(row[i])
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # 无法编辑
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget.setItem(inx, i, item)
                    del item
            self.tableWidget.sortItems(0, Qt.AscendingOrder)
            self.is_search = True
            self.horizontalFrame.hide()

    def search_bill(self, id=None, card=None):

        if id:
            id = mysql.query('bill_tb', 'id', id)
        elif card:
            id = mysql.query('bill_tb', 'card', card)
        else:
            line = self.lineEdit.text()
            if not line:
                QMessageBox.information(self, "温馨提示", "请输入姓名、手机号或卡号（支持模糊搜索）", QMessageBox.Yes)
                return
            id = mysql.like('bill_tb', 'name', line) + mysql.like('bill_tb', 'card', line)
            if len(line) >= 3:
                id += mysql.like('bill_tb', 'phone', line)

        if not id:
            QMessageBox.information(self, "温馨提示", "未能找到对应的姓名、手机号或卡号", QMessageBox.Yes)
            return False
        else:
            for i in range(self.tableWidget_2.rowCount()):
                self.tableWidget_2.removeRow(0)
            for row in id:
                inx = id.index(row)
                self.tableWidget_2.insertRow(inx)
                for i in range(len(row)):

                    item = QTableWidgetItem()
                    if str(row[i]).isdigit:  # 使得数字排序能够正常的运行
                        item.setData(Qt.DisplayRole, row[i])
                    else:
                        item.setText(row[i])
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # 无法编辑
                    item.setTextAlignment(Qt.AlignCenter)
                    if row[i] == '充值':
                        item.setForeground(QBrush(QColor(50, 205, 116)))
                    elif row[i] == '消费':
                        item.setForeground(QBrush(QColor(233, 96, 58)))
                    elif row[i] == '修改':
                        item.setForeground(QBrush(QColor(0, 0, 255)))

                    self.tableWidget_2.setItem(inx, i, item)
                    del item
            self.tableWidget_2.sortItems(0, Qt.DescendingOrder)
            self.is_search = True
            self.horizontalFrame_2.hide()
            return True

    def search_data_by_card(self, card=None):
        if not card:
            if self.lineEdit.text().isdigit():
                self.is_card_search = True
                self.search_data(card=self.lineEdit.text())
            else:
                QMessageBox.information(self, "温馨提示", "请输入正确的卡号，仅支持数字", QMessageBox.Yes)
        else:
            self.is_card_search = True
            self.search_data(card)

    def search_bill_by_card(self):
        if self.lineEdit.text().isdigit():
            self.search_bill(card=self.lineEdit.text())
        else:
            QMessageBox.information(self, "温馨提示", "请输入正确的卡号，仅支持数字", QMessageBox.Yes)

    def load_initial_data(self, last_index=None):
        self.horizontalFrame.show()

        for i in range(self.tableWidget.rowCount()):
            self.tableWidget.removeRow(0)

        self.c.execute('''SELECT * FROM user_tb ''')
        rows = self.c.fetchall()
        start = time.clock()

        if len(rows) / DATA_PER_PAGE > 0:
            srow = []
            if len(rows) / DATA_PER_PAGE > int(len(rows) / DATA_PER_PAGE):
                length = int(len(rows) / DATA_PER_PAGE) + 1
            else:
                length = int(len(rows) / DATA_PER_PAGE)
            global DATAPAGES
            DATAPAGES = length
            for i in range(length):
                srow.append(rows[i * DATA_PER_PAGE:DATA_PER_PAGE * (i + 1)])
            rows = srow
        if rows:
            try:
                for row in rows[self.current_data_index]:
                    inx = rows[self.current_data_index].index(row)
                    self.tableWidget.insertRow(inx)
                    for i in range(6):
                        item = QTableWidgetItem()
                        if str(row[i]).isdigit:  # 使得数字排序能够正常的运行
                            item.setData(Qt.DisplayRole, row[i])
                        else:
                            item.setText(row[i])
                        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # 无法编辑
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget.setItem(inx, i, item)
                        del item
                if last_index:
                    self.tableWidget.verticalScrollBar().setValue(last_index)
                    # self.tableWidget.setCurrentIndex(last_index)
            except:
                QMessageBox.information(self, "警告", "我们遇到点问题，正在刷新页面", QMessageBox.Yes)
                self.current_data_index = 0
                self.load_initial_data()
        self.is_card_search = False
        self.is_search = False
        end = time.clock()
        print((end - start))

    def load_initial_bill(self):
        self.horizontalFrame_2.show()

        for i in range(self.tableWidget_2.rowCount()):
            self.tableWidget_2.removeRow(0)

        self.c.execute('''SELECT * FROM bill_tb ''')
        rows = self.c.fetchall()

        if len(rows) / BILL_PER_PAGE > 0:
            srow = []
            if len(rows) / BILL_PER_PAGE > int(len(rows) / BILL_PER_PAGE):
                length = int(len(rows) / BILL_PER_PAGE) + 1
            else:
                length = int(len(rows) / BILL_PER_PAGE)
            global BILLPAGES
            BILLPAGES = length
            rows = rows[::-1]
            for i in range(length):
                srow.append(rows[i * BILL_PER_PAGE:BILL_PER_PAGE * (i + 1)])
            rows = srow
        if rows:
            try:
                for row in rows[self.current_bill_index]:
                    inx = rows[self.current_bill_index].index(row)
                    self.tableWidget_2.insertRow(inx)
                    for i in range(8):

                        item = QTableWidgetItem()
                        if str(row[i]).isdigit:  # 使得数字排序能够正常的运行
                            item.setData(Qt.DisplayRole, row[i])
                        else:
                            item.setText(row[i])

                        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # 无法编辑
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget_2.setItem(inx, i, item)
                        del item
            except:
                QMessageBox.information(self, "警告", "我们遇到点问题，正在刷新页面", QMessageBox.Yes)
                self.current_bill_index = 0
                self.load_initial_bill()
        self.tableWidget_2.sortItems(1, Qt.DescendingOrder)

    def generate_menu(self, pos):

        row_num = -1
        for i in self.tableWidget.selectionModel().selection().indexes():
            row_num = i.row()

        if row_num >= 0:
            menu = QMenu()
            item1 = menu.addAction(u"修改信息")
            item2 = menu.addAction(u"查看流水")
            item3 = menu.addAction(u"删除")

            action = menu.exec_(self.tableWidget.mapToGlobal(pos))
            if action == item1:
                DetailWindow.id = self.tableWidget.item(row_num, 0).text()
                DetailWindow.name = self.tableWidget.item(row_num, 1).text()
                DetailWindow.phone = self.tableWidget.item(row_num, 2).text()
                DetailWindow.card = self.tableWidget.item(row_num, 3).text()
                DetailWindow.balance = self.tableWidget.item(row_num, 4).text()
                DetailWindow.type = self.tableWidget.item(row_num, 5).text()
                DetailWindow.change()
                DetailWindow.show()

            elif action == item2:
                if self.search_bill(id=self.tableWidget.item(row_num, 0).text()):
                    self.tabWidget.setCurrentIndex(1)  # 切换界面


            elif action == item3:
                if float(self.tableWidget.item(row_num, 4).text()) == 0:
                    message = "确定删除？"
                else:
                    message = "检测到此会员尚有余额，删除会将余额清零，是否继续？"
                reply = MyQMessageBox("提示", message, '确认', '取消')
                if reply == 16384:
                    mysql.del_person(self.tableWidget.item(row_num, 0).text())
                    bills.person_out(str(float(self.tableWidget.item(row_num, 4).text())),
                                     self.tableWidget.item(row_num, 1).text(),
                                     self.tableWidget.item(row_num, 2).text(),
                                     self.tableWidget.item(row_num, 3).text(),
                                     0,
                                     self.tableWidget.item(row_num, 0).text())
                    self.check_page_data()
                    self.load_initial_data()
                    self.load_initial_bill()

            else:
                return

    def sort_row(self, index):
        if not self.sort_enable:
            self.tableWidget_2.sortItems(index, Qt.AscendingOrder)
            self.sort_enable = True
        else:
            self.tableWidget_2.sortItems(index, Qt.DescendingOrder)
            self.sort_enable = False

    def sort_row_2(self, index):
        if not self.sort_enable_2:
            self.tableWidget.sortItems(index, Qt.AscendingOrder)
            self.sort_enable_2 = True
        else:
            self.tableWidget.sortItems(index, Qt.DescendingOrder)
            self.sort_enable_2 = False

    def update_log(self):
        UpdateWindow.show()

    def update_me(self):

        def max_version(a, b):
            a = a[1:].split('.')
            b = b[1:].split('.')
            if a[0] > b[0]:
                return True
            if a[0] < b[0]:
                return False
            else:
                if a[1] > b[1]:
                    return True
                if a[1] < b[1]:
                    return False
                else:
                    if a[2] > b[2]:
                        return True
                    if a[2] < b[2]:
                        return False
                    else:
                        return False

        api = 'https://api.github.com/repos/skycity233/DataManager/releases'
        all_page = requests.get(api).json()  # 获取api页面(此时是以json返回的页面)并将该页面转换成字典形式（key-value的存储方式）
        cur_update = all_page[0]['tag_name']
        last_update = CURRENT_VERSION
        if max_version(cur_update, last_update):
            os.system('start 软件更新.exe ' + CURRENT_VERSION)

            QMessageBox.information(self, "提示", "发现新版本 " + cur_update)
        else:
            QMessageBox.information(self, "提示", "未检查到更新")

    def about(self):
        QMessageBox.information(self, "关于", "作者：王保键\n版本：" + CURRENT_VERSION + "\n更新日期：2019-11-8", QMessageBox.Yes)

    def change_tab(self):
        # if self.is_fresh:
        #     self.load_initial_data()
        #     self.load_initial_bill()
        # self.is_fresh = True
        if self.tabWidget.currentIndex() == 0:
            self.Qframe.show()
            self.pushButton_5.setText('搜索会员')
            try:
                self.pushButton.clicked.connect(self.search_data_by_card)
                self.pushButton.clicked.disconnect(self.search_bill_by_card)
                self.pushButton_5.clicked.connect(self.search_data)
                self.pushButton_5.clicked.disconnect(self.search_bill)
                self.lineEdit.returnPressed.connect(self.search_data_by_card)
                self.lineEdit.returnPressed.disconnect(self.search_bill_by_card)
                self.pushButton_6.clicked.connect(self.load_initial_data)
                self.pushButton_6.clicked.disconnect(self.load_initial_bill)
            except:
                pass
        elif self.tabWidget.currentIndex() == 1:
            self.Qframe.hide()
            self.pushButton_5.setText('搜索流水')
            try:
                self.pushButton.clicked.connect(self.search_bill_by_card)
                self.pushButton.clicked.disconnect(self.search_data_by_card)
                self.pushButton_5.clicked.connect(self.search_bill)
                self.pushButton_5.clicked.disconnect(self.search_data)
                self.lineEdit.returnPressed.connect(self.search_bill_by_card)
                self.lineEdit.returnPressed.disconnect(self.search_data_by_card)
                self.pushButton_6.clicked.connect(self.load_initial_bill)
                self.pushButton_6.clicked.disconnect(self.load_initial_data)
            except:
                pass


def MyQMessageBox(title, text, button1, button2=None):
    messageBox = QMessageBox()
    messageBox.setWindowTitle(title)
    messageBox.setText(text)
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


class AddWindow(QDialog, add_person_ui.Ui_Form):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.init_sign()

    def init_sign(self):
        self.pushButton.clicked.connect(self.add_person)
        max_card = mysql.max('bill_tb')[0][0] or 0
        self.lineEdit_2.setPlaceholderText('当前最高卡号：' + str(max_card) + '，推荐填' + str(int(max_card) + 1))
        # self.doubleSpinBox.valueChanged.connect(lambda: self.lineEdit_3.setText(self.doubleSpinBox.text()))
        self.lineEdit_1.textChanged.connect(lambda: self.label_4.setText(str(len(self.lineEdit_1.text())) + '/11位'))
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

    def add_person(self):
        name = self.lineEdit.text().strip()
        phone = self.lineEdit_1.text().strip()
        card = self.lineEdit_2.text().strip()
        balance = self.doubleSpinBox.text() or 0
        type = self.lineEdit_3.text().strip()

        if phone != '' and mysql.query_str('user_tb', 'phone', phone):
            QMessageBox.information(self, "温馨提示", "手机号已存在。", QMessageBox.Yes)
            return
        if card == '':
            QMessageBox.information(self, "温馨提示", "请填写卡号", QMessageBox.Yes)
            return
        if not card.isdigit():
            QMessageBox.information(self, "温馨提示", "请填写数字", QMessageBox.Yes)
            return
        if mysql.query('user_tb', 'card', card):
            QMessageBox.information(self, "温馨提示", "卡号已存在。", QMessageBox.Yes)
            return

        mysql.add_person(name, phone, card, balance, type)

        id = mysql.query('user_tb', 'card', card)

        if id:
            bills.person_in(str(balance), name, phone, card, balance, id[0][0])
        else:
            QMessageBox.information(self, "温馨提示", "请至少填写卡号或手机号", QMessageBox.Yes)
            return

        self.lineEdit.clear()
        self.lineEdit_1.clear()
        self.lineEdit_2.clear()
        self.doubleSpinBox.setValue(0)
        self.lineEdit_3.clear()
        self.lineEdit.setFocus()
        max_card = mysql.max('bill_tb')[0][0] or 0
        self.lineEdit_2.setPlaceholderText('当前最高卡号：' + str(max_card) + '，推荐填' + str(int(max_card) + 1))

        AddWindow.close()
        MainWindow.search_data_by_card(card)
        MainWindow.check_page_data()
        MainWindow.load_initial_bill()


class AddMoreWindow(QDialog, add_person_ui.Ui_Form):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.init_sign()

    def init_sign(self):
        _translate = QtCore.QCoreApplication.translate
        self.label_3.setText(_translate("Form",
                                        "<html><head/><body><p><img src=\":/main/充值.png\" width=\"30\" height=\"30\"/><span style=\" font-size:20pt; font-weight:600; vertical-align:super;\">余额</span></p></body></html>"))
        self.pushButton_2 = QtWidgets.QPushButton()
        self.pushButton_2.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 6, 2, 1, 1)
        max_card = mysql.max('bill_tb')[0][0] or 0
        self.lineEdit_2.setPlaceholderText('当前最高卡号：' + str(max_card) + '，推荐填' + str(int(max_card) + 1))
        self.lineEdit_1.textChanged.connect(lambda: self.label_4.setText(str(len(self.lineEdit_1.text())) + '/11位'))

        self.pushButton_2.clicked.connect(self.cancel)
        self.pushButton.clicked.connect(self.add_person)
        self.pushButton.setText('下一个')
        self.pushButton_2.setText('结束')

        self.setTabOrder(self.lineEdit, self.lineEdit_1)
        self.setTabOrder(self.lineEdit_1, self.lineEdit_2)
        self.setTabOrder(self.lineEdit_2, self.doubleSpinBox)
        self.setTabOrder(self.doubleSpinBox, self.lineEdit_3)
        self.setTabOrder(self.lineEdit_3, self.pushButton)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

    def cancel(self):
        AddMoreWindow.close()
        max_card = mysql.max('bill_tb')[0][0] or 0
        AddMoreWindow.lineEdit_2.setPlaceholderText('当前最高卡号：' + str(max_card) + '，推荐填' + str(int(max_card) + 1))

    def add_person(self):

        name = self.lineEdit.text().strip()
        phone = self.lineEdit_1.text().strip()
        card = self.lineEdit_2.text().strip()
        balance = self.doubleSpinBox.text() or 0
        type = self.lineEdit_3.text().strip()

        if phone != '' and mysql.query_str('user_tb', 'phone', phone):
            QMessageBox.information(self, "温馨提示", "手机号已存在。", QMessageBox.Yes)
            return
        if card == '':
            QMessageBox.information(self, "温馨提示", "请填写卡号", QMessageBox.Yes)
            return
        if not card.isdigit():
            QMessageBox.information(self, "温馨提示", "请填写数字", QMessageBox.Yes)
            return
        if mysql.query('user_tb', 'card', card):
            QMessageBox.information(self, "温馨提示", "卡号已存在。", QMessageBox.Yes)
            return

        mysql.add_person(name, phone, card, balance, type)

        id = mysql.query('user_tb', 'card', card)

        if id:
            bills.person_in(str(balance), name, phone, card, balance, id[0][0])
        else:
            QMessageBox.information(self, "温馨提示", "请至少填写卡号或手机号", QMessageBox.Yes)
            return
        MainWindow.search_data_by_card(card)
        MainWindow.check_page_data()
        MainWindow.load_initial_bill()
        self.is_search = True
        self.lineEdit.clear()
        self.lineEdit_1.clear()
        self.lineEdit_2.clear()
        self.doubleSpinBox.setValue(0)
        self.lineEdit_3.clear()
        self.lineEdit.setFocus()
        max_card = mysql.max('bill_tb')[0][0] or 0
        self.lineEdit_2.setPlaceholderText('当前最高卡号：' + str(max_card) + '，推荐填' + str(int(max_card) + 1))


class DetailWindow(QDialog, add_person_ui.Ui_Form):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.init_sign()
        self.setWindowTitle('修改信息')
        # self.doubleSpinBox.setEnabled(False)

    def init_sign(self):
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.pushButton.clicked.connect(self.add_person)
        self.pushButton.setText('修改')
        self.lineEdit_1.textChanged.connect(lambda: self.label_4.setText(str(len(self.lineEdit_1.text())) + '/11位'))

    def change(self):
        self.lineEdit.setText(self.name)
        self.lineEdit_1.setText(self.phone)
        self.lineEdit_2.setText(self.card)
        self.doubleSpinBox.setValue(float(self.balance))
        self.lineEdit_3.setText(self.type)

    def add_person(self):

        name = self.lineEdit.text().strip()
        phone = self.lineEdit_1.text().strip()
        card = self.lineEdit_2.text().strip()
        balance = self.doubleSpinBox.text()
        type = self.lineEdit_3.text().strip()

        if phone != '' and mysql.query_str('user_tb', 'phone', phone) and phone != DetailWindow.phone:
            QMessageBox.information(self, "温馨提示", "手机号已存在。", QMessageBox.Yes)
            return
        if mysql.query('user_tb', 'card', card) and card != DetailWindow.card:
            QMessageBox.information(self, "温馨提示", "卡号已存在。", QMessageBox.Yes)
            return
        if self.name != name:
            mysql.update(self.id, 'name', name)
            mysql.update_bill(self.id, 'name', name)
        if self.phone != phone:
            mysql.update(self.id, 'phone', phone)
            mysql.update_bill(self.id, 'phone', phone)
        if self.card != card:
            mysql.update(self.id, 'card', card)
            mysql.update_bill(self.id, 'card', card)
        if self.type != type:
            mysql.update(self.id, 'type', type)
            # mysql.update_bill(self.id, 'type', type)
        if self.balance != balance:
            mysql.update(self.id, 'balance', balance)
            cost = round(float(balance) - float(self.balance), 2)
            bills.bill_change(cost, name, phone, card, balance, self.id)

        QMessageBox.information(self, "温馨提示", "修改成功！", QMessageBox.Yes)
        DetailWindow.close()

        if MainWindow.is_search:
            MainWindow.search_data_by_card(card)
        else:
            MainWindow.load_initial_data(MainWindow.tableWidget.verticalScrollBar().value())
        MainWindow.load_initial_bill()


class ConsumeWindow(QDialog, consume_ui.Ui_Form):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)

        self.pushButton.clicked.connect(self.submit)

    def check_checkbox(self):
        self.cost = 0

    def submit(self):

        reply = QMessageBox.information(self, "消费确认",
                                        self.name + "消费" + str(self.cost) + '元？', QMessageBox.Yes | QMessageBox.No)
        if reply == 16384:
            person = mysql.query('user_tb', '_id', self.id)
            balance = float(person[0][4]) - self.cost
            if balance < 0:
                QMessageBox.information(self, "温馨提示", "余额不足，请充值", QMessageBox.Yes)
            else:
                mysql.update(self.id, 'balance', str(balance))
                QMessageBox.information(self, "温馨提示", "消费成功", QMessageBox.Yes)

                bills.bill_out(str(self.cost), str(person[0][1]), str(person[0][2]), str(person[0][3]), balance,
                               self.id)
                MainWindow.load_initial_data()
                MainWindow.load_initial_bill()
        self.close()


class UpdateWindow(QDialog, update_log_ui.Ui_Form):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)


def show_loading(vip):
    # 其实这个加载动画是假的，但是挺好看的，谁知道呢，哈哈哈哈

    # 创建QSplashScreen对象实例
    splash = QtWidgets.QSplashScreen(QtGui.QPixmap(":/main/data.png"))
    # 设置画面中的文字的字体
    splash.setFont(QFont('Microsoft YaHei UI', 10))
    # 显示画面
    splash.show()
    # 显示信息
    splash.showMessage("启动中", QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom, QtCore.Qt.white)

    if not vip:
        for i in range(7):
            time.sleep(0.1)
            splash.showMessage("正在加载样式表..." + str(i * 2) + "%", QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom,
                               QtCore.Qt.white)
        time.sleep(1)
        for i in range(13):
            time.sleep(0.1)
            splash.showMessage("正在加载样式表..." + str(12 + i * 2) + "%", QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom,
                               QtCore.Qt.white)
        for i in range(10):
            time.sleep(0.1)
            splash.showMessage("正在加载数据库..." + str(40 + i * 2) + "%", QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom,
                               QtCore.Qt.white)
        time.sleep(0.5)
        for i in range(20):
            time.sleep(0.1)
            splash.showMessage("正在测试数据库..." + str(58 + i * 2) + "%", QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom,
                               QtCore.Qt.white)

        splash.showMessage("正在测试数据库...99%", QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom, QtCore.Qt.white)
        time.sleep(2)

    splash.finish(MainWindow)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MainWindow()
    AddWindow = AddWindow()
    AddMoreWindow = AddMoreWindow()
    DetailWindow = DetailWindow()
    UpdateWindow = UpdateWindow()
    ConsumeWindow = ConsumeWindow()
    show_loading(vip=True)  # 显示启动加载页面
    MainWindow.show()  # 当主界面显示后销毁启动画面
    sys.exit(app.exec_())
