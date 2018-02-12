# !/usr/bin/python3

import os
import sys
from ftplib import FTP


def get_current_version():
    with FTP('192.168.32.1') as ftp:
        ftp.login()
        ftp.cwd('astra/unstable/smolensk/mounted-iso-main/')
        return ftp.nlst()[-1].split('-')[1][:-5]

def make_dic(pack_list):
    pack_dic = {}
    for i in pack_list:
        name = i.split('_')[0]
        last_part = i.split('_')[1:]
        version = ''
        for p in range(len(last_part)):
            version += last_part[p] + '_'
        if version[-5:] != 'udeb_':
            pack_dic[name] = version[:-5]
    return pack_dic

def packs_to_file(dist, pack_dic, file_name):
    with open(dist + file_name, 'w') as lst:
        for k in sorted(pack_dic.keys()):
            lst.write(k + '  ' + pack_dic[k] + '\n')

def check_lists(list1, list2=None):
    if not os.path.exists(os.curdir + '/' + list1):
        print("There is no package list for %s; pull it fist" % list1)
        sys.exit(2)
    if list2:
        if not os.path.exists(os.curdir + '/' + list2):
            print("There is no package list for %s; pull it fist" % list2)
            sys.exit(2)

def make_tree(version):
    if not os.path.exists(version):
        for d in ('main', 'devel'):
            try:
                os.makedirs(version + '/' + d)
            except OSError as mkdir_err:
                if mkdir_err.errno == errno.EACCES:
                    print("Can't create directory %s: acces denied!" % (
                          os.path.abspath(os.curdir) + version + d))
                elif mkdir_err.errno == errno.EEXIST:
                    continue
                else:
                    raise

def remove_dot(l):
    [l.remove(i) for i in l if i.startswith('.')]

def get_pack_list(list):
    """
    Returns 2 dicts {name:version} of main and devel
    branches of OS. Takes os.listdir list as param
    :param list: list
    :return: list
    """
    # gets list of content in dir
    dirs = sorted([i for i in os.listdir(list)])
    remove_dot(dirs) # get rid of .svn
    # gets lists of subdirs in dirs
    sub = [os.listdir(os.path.abspath(list + '/' + i)) for i in dirs]
    for i in sub:
        remove_dot(i) # get rid of .svn in subdir list
    main, devel = {}, {}
    # make 2 dicts for main and devel brunches
    for i in range(len(dirs)):
        for k in sub[i]:
            with open(os.path.abspath(list + '/' + dirs[i] + '/' + k), 'r') as p:
                    for l in p.readlines():
                        x = (l.split())
                        if dirs[i] == 'main':
                            main[x[0]] = x[1]
                        else:
                            devel[x[0]] = x[0]

    return main, devel

def compare_pack_lists(dic1, dic2):
    """
    Compare 2 dictionaries, returns 4 lists
    a - item in dic1, not in dic2
    b - item in dic1 and dic2
        versions missmatch
    c - item in dic2, not in dic1
    d - item in dic1 and dic2
        name and version matches
    :param dic: dict
    :return: list
    """
    a, b, c, d = [], [], [], []
    for i in dic1:
        if i not in dic2:
            a.append(i)
        else:
            if dic1[i] != dic2[i]:
                b.append(i)
            else:
                d.append(i)
    for i in dic2:
        if i not in dic1:
            c.append(i)
    return a, b, c, d

