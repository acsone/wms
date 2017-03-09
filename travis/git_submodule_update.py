#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Download submodules from Github zip archive url
# Keep standard update form private repositories
# listed in `travis/private_repo`
#
import os
import shutil
from urllib import urlretrieve
import zipfile

from git import Repo

DL_DIR = 'download'
ZIP_PATH = '%s/submodule.zip' % DL_DIR

os.makedirs(DL_DIR)

with open('travis/private_repos') as f:
    private_repos = f.read()

os.system('git submodule init')

for sub in Repo('.').submodules:
    print "Getting submodule %s" % sub.path
    use_archive = sub.path not in private_repos
    if use_archive:
        url = sub.url
        if url.startswith('git@github.com:'):
            url = url.replace('git@github.com:', 'https://github.com/')
        # remove .git
        if url.endswith('.git'):
            url = url[:-4]
        archive_url = "%s/archive/%s.zip" % (url, sub.hexsha)
        urlretrieve(archive_url, ZIP_PATH)
        try:
            with zipfile.ZipFile(ZIP_PATH) as zf:
                zf.extractall(DL_DIR)
        except zf.BadZipfile:
            # fall back to standard download
            use_archive = False
            with open(ZIP_PATH) as f:
                print ("Getting archive failed with error %s. Falling back to "
                       "git clone." % f.read())
            os.remove(ZIP_PATH)
        except Exception as e:
            use_archive = False
            print ("Getting archive failed with error %s. Falling back to "
                   "git clone." % e.message)
        else:
            os.remove(ZIP_PATH)
            os.removedirs(sub.path)
            submodule_dir = os.listdir(DL_DIR)[0]
            shutil.move(os.path.join(DL_DIR, submodule_dir), sub.path)
    if not use_archive:
        os.system('git submodule update %s' % sub.path)
