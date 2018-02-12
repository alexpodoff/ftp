# !/usr/bin/python3


import json
import os
import socket
import errno
from ftplib import FTP
from helper import *
import sys

__author__ = 'Pod'


usage_help = """
Usage: -g|--get <SE version>
       -c|--compare <old version> <new version>

    Example: ftp_check.py -g 1.5
             ftp_check.py -g 1.5.10
             ftp_check.py -g stable (or unstable)
        will pull the list of packages to compare

             ftp_check.py -c 1.5 1.5.10
             ftp_check.py -c unstable stable
             ftp_check.py -c unstable 1.5
        will compare package versions between 1.5 and 1.5.10
        (or current unstable version if version is not directly set)
    """

if len(sys.argv) == 1:
    print(usage_help)
    sys.exit(1)

try:
    version = get_current_version()
except socket.error as ftp_err:
    print("\nCouldn't connect to FTP: " + str(ftp_err) + '\n')
    sys.exit(2)

if sys.argv[2] in ['1.5', 'stable']:
    version = 'stable'

if sys.argv[2] in ['1.5.' + str(x) for x in range(1, 100)]:
    if sys.argv[2] != version:
        print("No repo for %s on FTP." % sys.argv[2])
        sys.exit(3)

# Smolensk stable repo pool
smol_stable_main = 'astra/stable/smolensk-1.5/mounted-iso-main/pool/'
smol_stable_dev = 'astra/stable/smolensk-1.5/mounted-iso-devel/pool/'

# Smolensk unstable repo pool
smol_unstable_main = 'astra/unstable/smolensk/mounted-iso-main/pool/'
smol_unstable_dev = 'astra/unstable/smolensk/mounted-iso-devel/pool/'

# local dirs for stable and unstable lists
se_stable = os.path.abspath(os.curdir) + '/' + version
se_unstable = os.path.abspath(os.curdir) + '/' + version

class PackList:

    def __init__(self, branch='main'):
        self.branch = branch
        self.main_pool = smol_unstable_main
        self.dev_pool = smol_unstable_dev
        self.main_pool_stable = smol_stable_main
        self.dev_pool_stable = smol_stable_dev

    def get_dir_list(self, path):
        """
        get a list of selected branch of a path
        :return: list
        """
        with FTP('192.168.32.1') as ftp:
            ftp.login()
            ftp.cwd(path + self.branch)
            return ftp.nlst()

    def get_sub_dir_list(self, path, dir_list):
        """
        get a list of sub dirs of selected branch of a path
        :return: list
        """
        sub_dir_list = []
        with FTP('192.168.32.1') as ftp:
            ftp.login()
            ftp.cwd(path + self.branch)
            for sub_dir in dir_list:
                ftp.cwd(sub_dir)
                sub_dir_list.append(ftp.nlst())
                ftp.cwd('..')
        return sub_dir_list

    def get_package_list(self, path, dir_list, sub_dir_list):
        """
        get a list all packages in selected branch of a path
        :return: list
        """
        package_list = []
        with FTP('192.168.32.1') as ftp:
            ftp.login()
            ftp.cwd(path + self.branch)
            for sub_dir in dir_list:
                ftp.cwd(sub_dir)
                for pack_dir in sub_dir_list[0]:
                    if pack_dir in sub_dir_list[0]:
                        ftp.cwd(pack_dir)
                        for package in ftp.nlst():
                            package_list.append(package)
                        ftp.cwd('..')
                    else:
                        ftp.cwd('..')
                sub_dir_list = sub_dir_list[1:]
                ftp.cwd('..')
        return package_list


if __name__ == '__main__':

    main_list = PackList()
    nonfree_list = PackList('non-free')
    contrib_list = PackList('contrib')

    if sys.argv[1] in ['-g', '--get']:
        if sys.argv[2] in ['1.5', 'stable']:
            make_tree(se_stable)
            print("Pulling %s package list from FTP ... please, stand by ..." %  sys.argv[2])

            s_main_pack = main_list.get_package_list(
                          smol_stable_main,
                          main_list.get_dir_list(smol_stable_main),
                          main_list.get_sub_dir_list(smol_stable_main,
                                                     main_list.get_dir_list(smol_stable_main)))

            s_nonfree_pack = nonfree_list.get_package_list(
                             smol_stable_main,
                             nonfree_list.get_dir_list(smol_stable_main),
                             nonfree_list.get_sub_dir_list(smol_stable_main,
                                                           nonfree_list.get_dir_list(smol_stable_main)))

            s_contrib_pack = contrib_list.get_package_list(
                             smol_stable_main,
                             contrib_list.get_dir_list(smol_stable_main),
                             contrib_list.get_sub_dir_list(smol_stable_main,
                                                           contrib_list.get_dir_list(smol_stable_main)))

            s_dev_main_pack = main_list.get_package_list(
                              smol_stable_dev,
                              main_list.get_dir_list(smol_stable_dev),
                              main_list.get_sub_dir_list(smol_stable_dev,
                                                         main_list.get_dir_list(smol_stable_dev)))

            s_dev_nonfree_pack = nonfree_list.get_package_list(
                                 smol_stable_dev,
                                 nonfree_list.get_dir_list(smol_stable_dev),
                                 nonfree_list.get_sub_dir_list(smol_stable_dev,
                                                               nonfree_list.get_dir_list(smol_stable_dev)))


            packs_to_file(se_stable, make_dic(s_main_pack), '/main/main')
            packs_to_file(se_stable, make_dic(s_nonfree_pack), '/main/non-free')
            packs_to_file(se_stable, make_dic(s_contrib_pack), '/main/contrib')
            packs_to_file(se_stable, make_dic(s_dev_main_pack), '/devel/main')
            packs_to_file(se_stable, make_dic(s_dev_nonfree_pack), '/devel/non-free')

            print("Operation complete")

        elif sys.argv[2] in ['unstable', version]:
            make_tree(se_unstable)
            print("Pulling %s package list from FTP ... please, stand by ..." %  sys.argv[2])

            us_main_pack = main_list.get_package_list(
                           smol_unstable_main, main_list.get_dir_list(smol_unstable_main),
                           main_list.get_sub_dir_list(smol_unstable_main,
                                                      main_list.get_dir_list(smol_unstable_main)))

            us_nonfree_pack = nonfree_list.get_package_list(
                              smol_unstable_main, nonfree_list.get_dir_list(smol_unstable_main),
                              nonfree_list.get_sub_dir_list(smol_unstable_main,
                                                            nonfree_list.get_dir_list(smol_unstable_main)))

            us_contrib_pack = contrib_list.get_package_list(
                              smol_unstable_main, contrib_list.get_dir_list(smol_unstable_main),
                              contrib_list.get_sub_dir_list(smol_unstable_main,
                                                            contrib_list.get_dir_list(smol_unstable_main)))

            us_dev_main_pack = main_list.get_package_list(
                               smol_unstable_dev, main_list.get_dir_list(smol_unstable_dev),
                               main_list.get_sub_dir_list(smol_unstable_dev,
                                                          main_list.get_dir_list(smol_unstable_dev)))

            us_dev_nonfree_pack = nonfree_list.get_package_list(
                                  smol_unstable_dev, nonfree_list.get_dir_list(smol_unstable_dev),
                                  nonfree_list.get_sub_dir_list(smol_unstable_dev,
                                                                nonfree_list.get_dir_list(smol_unstable_dev)))

            us_dev_contrib_pack = contrib_list.get_package_list(
                                  smol_unstable_dev, contrib_list.get_dir_list(smol_unstable_dev),
                                  contrib_list.get_sub_dir_list(smol_unstable_dev,
                                                                contrib_list.get_dir_list(smol_unstable_dev)))


            packs_to_file(se_unstable, make_dic(us_main_pack), '/main/main')
            packs_to_file(se_unstable, make_dic(us_nonfree_pack), '/main/non-free')
            packs_to_file(se_unstable, make_dic(us_contrib_pack), '/main/contrib')
            packs_to_file(se_unstable, make_dic(us_dev_main_pack), '/devel/main')
            packs_to_file(se_unstable, make_dic(us_dev_nonfree_pack), '/devel/non-free')
            packs_to_file(se_unstable, make_dic(us_dev_contrib_pack), '/devel/contrib')

            print("Operation complete")

    elif sys.argv[1] in ['-c', '--compare']:
        stable_list = ['1.5', 'stable']
        unstable_list = ['1.5.' + str(x) for x in range(1, 100)]
        if len(sys.argv) == 3:
            if sys.argv[2] in stable_list:
                print("Can't compare %s with itself..." % sys.argv[2])
                sys.exit(5)
            elif sys.argv[2] in unstable_list:
                list1, list2 = 'stable', sys.argv[2]
            else:
                print(usage_help)
                sys.exit(1)
        elif len(sys.argv) == 4:
            for i in range(0, len(sys.argv[2:])):
                if sys.argv[i+2] == '1.5':
                    sys.argv[i+2] = 'stable'
                if sys.argv[i+2] == 'unstable':
                    sys.argv[i+2] = version
            print(sys.argv)
            if sys.argv[2] == sys.argv[3]:
                print("Can't compare %s with itself" % sys.argv[2])
                sys.exit(5)
            elif sys.argv[2] in stable_list and sys.argv[3] in stable_list:
                print("Can't compare 1.5 with itself...blead")
                sys.exit(5)
            elif sys.argv[2] in unstable_list and sys.argv[3] in unstable_list:
                list1, list2 = sys.argv[2], sys.argv[3]
            elif sys.argv[2] in unstable_list and sys.argv[3] in stable_list or \
                 sys.argv[2] in stable_list and sys.argv[3] in unstable_list:
                list1, list2 = sys.argv[2], sys.argv[3]
            else:
                print(usage_help)
                sys.exit(1)

        check_lists(list1, list2)
        main1, dev1 = get_pack_list(list1)
        main2, dev2 = get_pack_list(list2)

        print("Compairing %s and %s ... please, stand by ..." % (list1, list2))

        diff = os.path.abspath(os.curdir + '/diff_'+ list1 + '_' + list2)
        if os.path.exists(diff):
            os.remove(diff)

        m1, m2, m3, m4 = compare_pack_lists(main1, main2)
        d1, d2, d3, d4 = compare_pack_lists(dev1, dev2)
        moved, dev_moved = [], []

        with open(diff, 'a') as f:
            f.write("Comparison between %s and %s:\n" % (list1, list2))
            f.write("\nnot in: " + str(len(m1+d1)) + \
                       "\nversion: " + str(len(m2+d2)) + \
                       "\nnew: " +  str(len(m3+d3)) + \
                       "\nsame: " + str(len(m4+d4)) + '\n\n')

            f.write("MAIN brunch:\n")
            for i in sorted(m1):
                if i not in dev2:
                    f.write(str(i) + " not in " + str(list2) + '\n')
                else:
                    moved.append(i)
            for i in sorted(moved):
                f.write(str(i) + " moved to devel disk of " + str(list2) + '\n')

            for i in sorted(m2):
                f.write(str(i) + " version " + main1[i] + " changed in " + \
                           str(list2) + ' to version ' + main2[i] + '\n')

            for i in sorted(m3):
                f.write(str(i) + " is a new pack in " + str(list2) + '\n')

            for i in sorted(m4):
                f.write(str(i) + " not changed " + '\n')

            f.write("\nDEVEL brunch:\n")
            for i in sorted(d1):
                if i not in main2:
                    f.write(str(i) + " not in " + str(list2) + '\n')
                else:
                    dev_moved.append(i)

            for i in sorted(dev_moved):
                f.write(str(i) + " moved to main disk of " + str(list2) + '\n')

            for i in sorted(d2):
                f.write(str(i) + " version " + dev1[i] + " changed in " + \
                           str(list2) + " to version " + dev2[i] + '\n')

            for i in sorted(d3):
                f.write(str(i) + " is a new pack in " + str(list2) + '\n')

            for i in sorted(d4):
                f.write(str(i) + " not changed " + '\n')

        print("Compare completed. See results in %s" % diff)
    else:
        print(usage_help)
        sys.exit(1)
