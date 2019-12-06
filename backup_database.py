# encoding = utf-8
# =====================================================
#   Copyright (C) 2019 All rights reserved.
#
#   filename : backup_database.py
#   version  : 0.1
#   author   : Jack Wang / 544907049@qq.com
#   date     : 2019-12-04 下午 4:22
#   desc     : 
# =====================================================

# import winreg
# import os
from shutil import copy
from time import strftime, localtime

import progressbar
from baidupcsapi import PCS


# def get_desktop():
#     key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
#     return str(winreg.QueryValueEx(key, "Personal")[0])
#
#
# def create_dir():
#     document = get_desktop()
#     if not os.path.exists(os.path.join(document, 'DataManager')):
#         os.mkdir(os.path.join(document, 'DataManager'))


class ProgressBar():

    def __init__(self):
        self.first_call = True

    def __call__(self, *args, **kwargs):
        if self.first_call:
            self.widgets = [progressbar.Percentage(), ' ',
                            progressbar.Bar(marker=progressbar.RotatingMarker('>')),
                            ' ', progressbar.ETA()]
            self.pbar = progressbar.ProgressBar(widgets=self.widgets, maxval=kwargs['size']).start()
            self.first_call = False

        if kwargs['size'] <= kwargs['progress']:
            self.pbar.finish()
        else:
            self.pbar.update(kwargs['progress'])


def backup():
    try:
        copy('./database/data.db',
             './database/data' + strftime("%Y-%m-%d %H:%M:%S", localtime()) + '.db')
    except IOError as e:
        print("Unable to copy file. %s" % e)


if __name__ == '__main__':

    pcs = PCS('wbj512291', 'ILY999@wbJ')
    print(pcs.quota().content)
    # test_file = open('data.db', 'rb').read()
    print(pcs.list_files('/').content)
    # ret = pcs.upload('/', test_file, 'data.db', callback=ProgressBar())
