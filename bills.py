# encoding = utf-8
# =====================================================
#   Copyright (C) 2019 All rights reserved.
#
#   filename : bills.py
#   version  : 0.1
#   author   : Jack Wang / 544907049@qq.com
#   date     : 2019/11/7 下午 7:04
#   desc     : 
# =====================================================

import time
import mysql


def bill_in(cost, name, phone, card, balance, id):
    # balance = float(mysql.query('balance_tb', '_id', '1')[0][2])
    # balance += float(cost)
    mysql.add_bill(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                   '充值', '+' + str(cost), str(balance), str(name), str(phone), str(card), id)
    # mysql.change_balance(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), str(balance))


def bill_out(cost, name, phone, card, balance, id):
    # balance = float(mysql.query('balance_tb', '_id', '1')[0][2])
    # balance -= float(cost)
    mysql.add_bill(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                   '消费', '-' + str(cost), str(balance), str(name), str(phone), str(card), id)
    # mysql.change_balance(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), str(balance))


def person_out(cost, name, phone, card, balance, id):
    # balance = float(mysql.query('balance_tb', '_id', '1')[0][2])
    # balance -= float(cost)
    mysql.add_bill(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                   '销户', '-' + str(cost), str(balance), str(name), str(phone), str(card), id)
    # mysql.change_balance(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), str(balance))


def person_in(cost, name, phone, card, balance, id):
    # balance = float(mysql.query('balance_tb', '_id', '1')[0][2])
    # balance -= float(cost)
    mysql.add_bill(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                   '建户', '+' + str(cost), str(balance), str(name), str(phone), str(card), id)
    # mysql.change_balance(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), str(balance))


def bill_change(cost, name, phone, card, balance, id):
    if cost > 0:
        mysql.add_bill(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                       '修改', '+' + str(cost), str(balance), str(name), str(phone), str(card), id)
    if cost <= 0:
        mysql.add_bill(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                       '修改', str(cost), str(balance), str(name), str(phone), str(card), id)
