#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/13 2:27
# @Author  : AMR
# @File    : file_share.py
# @Software: PyCharm


import requests
import os
import sys
import platform
import json
import io
import datetime


if platform.system() == 'Windows':
    SYS_WIN_FLAG = True
else:
    SYS_WIN_FLAG = False

LINK_TIMEOUT = 60*60*66 #temp link is 72 hrs timeout. reserve 6 hour for download so set 66 hours timeout
# LINK_TIMEOUT = 600
LINK_DATA_FILE = 'link_db.json'


def py2_jsondump(data, filename):
    with io.open(filename, 'w', encoding = 'utf-8') as f:
        f.write(json.dumps(data, f, ensure_ascii = False, sort_keys = True, indent = 2))


def py3_jsondump(data, filename):
    with io.open(filename, 'w', encoding = 'utf-8') as f:
        return json.dump(data, f, ensure_ascii = False, sort_keys = True, indent = 2)


def jsonload(filename):
    with io.open(filename, 'r', encoding = 'utf-8') as f:
        return json.load(f)

if sys.version_info[0] == 2:
    PY2_FLAG = True
    jsondump = py2_jsondump
elif sys.version_info[0] == 3:
    PY2_FLAG = False
    jsondump = py3_jsondump


def check_unicode(sdata):
    print(type(sdata))
    if isinstance(sdata, str) and PY2_FLAG:
        ret = sdata.decode('utf-8')
        return ret
    else:
        print('ret orignal')
        return sdata

class FileDataBase(object):
    def __init__(self, dbfile):
        self.dbfile = dbfile
        self.dblist = []
        self.timefmtstr = '%Y-%m-%d %H:%M:%S'
        self.nowtime = datetime.datetime.now()
        if not os.path.exists(dbfile):
            with open(dbfile, 'w+') as of:
                of.write('[]')
        else:
            try:
                self.load_data(self.dbfile)
            except:
                with open(dbfile, 'w+') as of:
                    of.write('[]')


    @staticmethod
    def save_data(filepath, jsdata):
        jsondump(jsdata, filepath)

    @staticmethod
    def load_data(filepath):
        jsdata = jsonload(filepath)
        return jsdata

    def update_db(self, newdata=None):
        newlist = []
        for item in self.dblist:
            ctime = datetime.datetime.strptime(item['ctime'], self.timefmtstr)
            tdsecs = (self.nowtime - ctime).total_seconds()
            # print(tdsecs)
            if tdsecs < LINK_TIMEOUT:
                newlist.append(item)
        self.dblist = newlist

        if newdata is not None:
            ddt = {}
            ddt['ctime'] = self.nowtime.strftime(self.timefmtstr)
            ddt['filename'] = check_unicode(newdata['filename'])
            ddt['url'] = newdata['url']
            self.dblist.append(ddt)

        self.save_data(self.dbfile, self.dblist)

    def check_tgfile(self, filename):
        self.dblist = self.load_data(self.dbfile)
        for item in self.dblist:
            if item['filename'] == check_unicode(filename):
                ctime = datetime.datetime.strptime(item['ctime'], self.timefmtstr)
                tdsecs = (self.nowtime - ctime).total_seconds()
                # print(tdsecs)
                if tdsecs < LINK_TIMEOUT:
                    return item
                else:
                    return None
        return None


'''
Note:
to use requests's post func with Chinese filename
must mod the urllib3's fields.py
if py2 change to this
    # value = email.utils.encode_rfc2231(value, 'utf-8')
    value = '%s="%s"' % (name, value.decode('utf-8'))

if py3 change to this
    # value = email.utils.encode_rfc2231(value, 'utf-8')
    value = '%s=%s' % (name, value)    
'''


class FileShare(object):
    def __init__(self):
        pass

    def tmplink(self, filepath):
        fdb = FileDataBase(LINK_DATA_FILE)
        res = fdb.check_tgfile(filepath)
        if res is not None:
            return res['url']
        fname = os.path.split(filepath)[-1]
        filepath = check_unicode(filepath)
        fname = check_unicode(fname)
        url = "http://tmp.link/openapi/v1"
        files = {
            'model': (None, 1),
            'action': (None, 'upload'),
            'file': (fname, open(filepath, 'rb'))
        }

        r = requests.post(url, files=files)
        rd = r.json()

        if rd['status'] == 0:
            newdata = {}
            newdata['filename'] = check_unicode(filepath)
            newdata['url'] = rd['data']['url']
            fdb.update_db(newdata)
            return rd['data']['url']
        else:
            None


if __name__ == "__main__":

    fn = r'aabbccd.txt'
    fs = FileShare()
    url = fs.tmplink(fn)
    print(url)

